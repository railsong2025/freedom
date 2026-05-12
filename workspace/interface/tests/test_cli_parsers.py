"""Tests for shared CLI parser helpers."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from interface.cli_parsers import (  # noqa: E402
    parse_position_items,
    parse_price_items,
    parse_stop_items,
    parse_trade_items,
)


class TestCliParsers(unittest.TestCase):
    def test_price_items_accept_colon_equal_lists_and_duplicates(self):
        prices = parse_price_items(["MSFT:100", "nvda=200,MSFT=101"])
        self.assertEqual({"MSFT": 101.0, "NVDA": 200.0}, prices)

    def test_price_items_skip_invalid_and_non_positive(self):
        prices = parse_price_items("MSFT:not-a-number,NVDA=-1,KO=77.5")
        self.assertEqual({"KO": 77.5}, prices)

    def test_stop_items_share_price_parser(self):
        self.assertEqual({"MSFT": 95.0}, parse_stop_items(["MSFT=95"]))

    def test_trade_items_accept_colon_equal_semicolon_and_validate(self):
        trades = parse_trade_items(["MSFT:BUY:2:100;nvda=SELL:1:200", "BAD:HOLD:1:1;ZERO:BUY:0:1"])
        self.assertEqual(2, len(trades))
        self.assertEqual(("MSFT", "BUY", 2, 100.0), (trades[0].symbol, trades[0].action, trades[0].shares, trades[0].limit_price))
        self.assertEqual(("NVDA", "SELL", 1, 200.0), (trades[1].symbol, trades[1].action, trades[1].shares, trades[1].limit_price))

    def test_position_items_accept_colon_equal_and_validate(self):
        positions = parse_position_items(["MSFT:2:100,NVDA=1:200", "BAD:0:1;IGNORED"])
        self.assertEqual(("MSFT", "NVDA"), tuple(p.symbol for p in positions))
        self.assertEqual((2, 1), tuple(p.shares for p in positions))


if __name__ == "__main__":
    unittest.main()
