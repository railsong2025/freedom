"""Tests for sector_proxy module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from intelligence.sector_proxy import (
    build_sector_summary,
    sector_etf_symbols,
    sector_leadership_table,
    sector_relative_performance,
    ticker_instrument_metadata,
    ticker_sector,
)
from intelligence.technical_indicators import n_day_return


class TestTickerSector(unittest.TestCase):
    def test_known_tickers(self):
        self.assertEqual(ticker_sector("MU"), "semiconductor")
        self.assertEqual(ticker_sector("KO"), "consumer_staples")
        self.assertEqual(ticker_sector("MSFT"), "technology")
        self.assertEqual(ticker_sector("NVDA"), "semiconductor")

    def test_case_insensitive(self):
        self.assertEqual(ticker_sector("mu"), "semiconductor")
        self.assertEqual(ticker_sector("ko"), "consumer_staples")

    def test_unknown_ticker(self):
        self.assertIsNone(ticker_sector("UNKNOWN_TICKER"))


class TestTickerInstrumentMetadata(unittest.TestCase):
    def test_non_tradable_index(self):
        metadata = ticker_instrument_metadata("IXIC")
        self.assertEqual(metadata["instrument_type"], "non_tradable_index")
        self.assertEqual(metadata["market_proxy_for"], "Nasdaq Composite")
        self.assertEqual(metadata["tradable_proxy"], "QQQ")
        self.assertFalse(metadata["is_tradable"])

    def test_tradable_index_proxy_etf(self):
        metadata = ticker_instrument_metadata("SPY")
        self.assertEqual(metadata["instrument_type"], "tradable_index_proxy_etf")
        self.assertEqual(metadata["market_proxy_for"], "S&P 500")
        self.assertEqual(metadata["tradable_proxy"], "SPY")
        self.assertTrue(metadata["is_tradable"])


class TestSectorETF(unittest.TestCase):
    def test_semiconductor(self):
        etfs = sector_etf_symbols("semiconductor")
        self.assertIn("SMH", etfs)
        self.assertIn("SOXX", etfs)

    def test_technology(self):
        etfs = sector_etf_symbols("technology")
        self.assertIn("XLK", etfs)

    def test_unknown_sector(self):
        etfs = sector_etf_symbols("unknown_sector")
        self.assertEqual(etfs, [])


class TestSectorRelativePerformance(unittest.TestCase):
    def test_outperform(self):
        from dataclasses import dataclass

        @dataclass
        class Bar:
            symbol: str
            date: str
            open: float | None
            high: float | None
            low: float | None
            close: float | None
            volume: float | None
            source: str = "test"
            raw: dict = None

        # Stock goes up 10%, sector goes up 5%
        stock_bars = [Bar("MU", f"2026-04-{i+1:02d}", 100, 101, 99, 100 + i * 2, 1000) for i in range(21)]
        sector_bars = [Bar("SMH", f"2026-04-{i+1:02d}", 100, 101, 99, 100 + i, 1000) for i in range(21)]
        rel = sector_relative_performance(stock_bars, sector_bars, 20)
        self.assertIsNotNone(rel)
        self.assertGreater(rel, 0)  # Stock outperformed sector

    def test_insufficient_data(self):
        rel = sector_relative_performance([], [], 20)
        self.assertIsNone(rel)


class TestSectorLeadershipTable(unittest.TestCase):
    def test_ranking(self):
        from dataclasses import dataclass

        @dataclass
        class Bar:
            symbol: str
            date: str
            open: float | None
            high: float | None
            low: float | None
            close: float | None
            volume: float | None
            source: str = "test"
            raw: dict = None

        # MU up 20%, KO up 5%
        mu_bars = [Bar("MU", f"2026-04-{i+1:02d}", 100, 101, 99, 100 + i * 2, 1000) for i in range(21)]
        ko_bars = [Bar("KO", f"2026-04-{i+1:02d}", 100, 101, 99, 100 + i * 0.5, 1000) for i in range(21)]
        spy_bars = [Bar("SPY", f"2026-04-{i+1:02d}", 100, 101, 99, 100 + i, 1000) for i in range(21)]

        table = sector_leadership_table(
            {"MU": mu_bars, "KO": ko_bars},
            spy_bars,
            period=20,
        )
        self.assertEqual(len(table), 2)
        # MU should rank higher than KO
        self.assertEqual(table[0]["symbol"], "MU")

    def test_instrument_metadata_in_rows(self):
        from dataclasses import dataclass

        @dataclass
        class Bar:
            symbol: str
            date: str
            open: float | None
            high: float | None
            low: float | None
            close: float | None
            volume: float | None
            source: str = "test"
            raw: dict = None

        qqq_bars = [Bar("QQQ", f"2026-04-{i+1:02d}", 100, 101, 99, 100 + i, 1000) for i in range(21)]
        spy_bars = [Bar("SPY", f"2026-04-{i+1:02d}", 100, 101, 99, 100 + i, 1000) for i in range(21)]

        table = sector_leadership_table({"QQQ": qqq_bars}, spy_bars, period=20)

        self.assertEqual("tradable_index_proxy_etf", table[0]["instrument_type"])
        self.assertEqual("Nasdaq 100 / Nasdaq growth proxy", table[0]["market_proxy_for"])


class TestBuildSectorSummary(unittest.TestCase):
    def test_empty(self):
        summary = build_sector_summary({}, None, None)
        self.assertEqual(summary["sector_map"], {})
        self.assertEqual(summary["leadership"], [])
        self.assertEqual(summary["sector_performance"], [])


if __name__ == "__main__":
    unittest.main()
