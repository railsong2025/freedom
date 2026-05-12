"""Tests for position_sizing module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.position_sizing import (
    atr_based_stop,
    compute_sizing_summary,
    fee_adjusted_entry_cost,
    fee_adjusted_sell_proceeds,
    kelly_fraction,
    position_pct,
    position_size_check,
    risk_based_shares,
)


class TestRiskBasedShares(unittest.TestCase):
    def test_basic(self):
        # Equity 30000, risk 2%, entry 600, stop 570
        shares = risk_based_shares(30000, 2.0, 600, 570)
        # Max risk = 600, risk_per_share = 30 + round-trip slippage 0.10
        # shares = (600 - 10) / 30.10 = 19.6 -> 19
        self.assertGreater(shares, 0)
        self.assertLessEqual(shares, 20)

    def test_no_risk(self):
        shares = risk_based_shares(30000, 2.0, 600, 600)
        self.assertEqual(shares, 0)

    def test_tight_stop(self):
        shares = risk_based_shares(30000, 2.0, 600, 595)
        # risk_per_share = 5 + 0.10 round-trip slippage
        # shares = (600 - 10) / 5.10 = 115.6 -> 115
        self.assertGreater(shares, 100)

    def test_zero_equity(self):
        shares = risk_based_shares(0, 2.0, 600, 570)
        self.assertEqual(shares, 0)

    def test_cash_caps_position_size(self):
        shares = risk_based_shares(30000, 2.0, 100, 95, cash=250)
        self.assertEqual(shares, 2)


class TestATRBasedStop(unittest.TestCase):
    def test_normal(self):
        stop = atr_based_stop(600, 20, 1.5)
        self.assertAlmostEqual(stop, 570.0, places=1)

    def test_zero_atr(self):
        stop = atr_based_stop(600, 0, 1.5)
        self.assertEqual(stop, 0.0)

    def test_large_atr(self):
        stop = atr_based_stop(600, 100, 1.5)
        self.assertEqual(stop, 450.0)


class TestPositionSizeCheck(unittest.TestCase):
    def test_within_cap(self):
        self.assertTrue(position_size_check(5, 600, 30000, 25.0))
        # 5 * 600 / 30000 = 10% < 25%

    def test_exceeds_cap(self):
        self.assertFalse(position_size_check(100, 600, 100000, 25.0))
        # 100 * 600 / 100000 = 60% > 25%


class TestPositionPct(unittest.TestCase):
    def test_basic(self):
        pct = position_pct(5, 600, 30000)
        self.assertAlmostEqual(pct, 10.0, places=1)

    def test_zero_equity(self):
        pct = position_pct(5, 600, 0)
        self.assertEqual(pct, 0.0)


class TestKellyFraction(unittest.TestCase):
    def test_positive_edge(self):
        f = kelly_fraction(0.6, 200, 100)
        # f* = 0.6 - 0.4/2 = 0.6 - 0.2 = 0.4
        self.assertAlmostEqual(f, 0.4, places=2)

    def test_no_edge(self):
        f = kelly_fraction(0.5, 100, 100)
        self.assertAlmostEqual(f, 0.0, places=2)

    def test_negative_edge(self):
        f = kelly_fraction(0.3, 100, 100)
        self.assertEqual(f, 0.0)  # Capped at 0

    def test_zero_loss(self):
        f = kelly_fraction(0.6, 200, 0)
        self.assertEqual(f, 0.0)


class TestFeeAdjustedCosts(unittest.TestCase):
    def test_entry_cost(self):
        cost = fee_adjusted_entry_cost(10, 600, fee=5)
        self.assertEqual(cost, 6005)

    def test_sell_proceeds(self):
        proceeds = fee_adjusted_sell_proceeds(10, 600, fee=5)
        self.assertEqual(proceeds, 5995)


class TestComputeSizingSummary(unittest.TestCase):
    def test_basic(self):
        summary = compute_sizing_summary(
            equity=30000, entry=600, stop=570,
            risk_per_trade_pct=2.0,
        )
        self.assertGreater(summary["max_risk_shares"], 0)
        self.assertGreater(summary["position_pct"], 0)
        self.assertIn("stop_distance_pct", summary)
        self.assertIn("single_stock_cap_ok", summary)

    def test_summary_reports_cash_sufficiency(self):
        summary = compute_sizing_summary(
            equity=30000, entry=600, stop=570,
            risk_per_trade_pct=2.0, cash=1000,
        )
        self.assertFalse(summary["cash_sufficient"])


if __name__ == "__main__":
    unittest.main()
