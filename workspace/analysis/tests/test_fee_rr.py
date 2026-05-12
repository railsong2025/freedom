"""Tests for fee_rr module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.fee_rr import (
    break_even_price,
    fee_adjusted_rr,
    multi_target_rr,
    rr_verdict,
)
from interface.constants import FEE_PER_TRADE_USD


class TestFeeAdjustedRR(unittest.TestCase):
    def test_positive_rr(self):
        # Entry 600, stop 570, target 660
        rr = fee_adjusted_rr(600, 570, 660)
        # Reward = 60 - 10 - 0.10 = 49.90, Risk = 30 + 10 + 0.10 = 40.10
        self.assertGreater(rr, 1.2)
        self.assertLess(rr, 1.3)

    def test_marginal_rr(self):
        # Entry 100, stop 97, target 103
        rr = fee_adjusted_rr(100, 97, 103)
        # Reward is negative because round-trip fees eat the profit.
        self.assertLess(rr, 0)

    def test_invalid_stop(self):
        rr = fee_adjusted_rr(100, 105, 110)  # stop > entry
        self.assertLess(rr, 0)

    def test_equal_entry_target(self):
        rr = fee_adjusted_rr(100, 95, 100)  # target == entry
        self.assertLess(rr, 0)

    def test_good_rr(self):
        # Entry 400, stop 380, target 450
        rr = fee_adjusted_rr(400, 380, 450)
        self.assertGreater(rr, 1.3)

    def test_multiple_shares_spreads_fixed_fees(self):
        one_share = fee_adjusted_rr(100, 95, 115, shares=1)
        ten_shares = fee_adjusted_rr(100, 95, 115, shares=10)
        self.assertGreater(ten_shares, one_share)


class TestBreakEvenPrice(unittest.TestCase):
    def test_basic(self):
        be = break_even_price(100, fee_per_side=5, slippage=0.05, shares=1)
        # be = 100 + (2*5 + 2*0.05) / 1 = 100 + 10.10 = 110.10
        self.assertAlmostEqual(be, 110.10, places=2)

    def test_multiple_shares(self):
        be = break_even_price(100, fee_per_side=5, slippage=0.05, shares=10)
        # be = 100 + 10.10 / 10 = 100 + 1.01 = 101.01
        self.assertAlmostEqual(be, 101.01, places=2)


class TestMultiTargetRR(unittest.TestCase):
    def test_two_targets(self):
        results = multi_target_rr(600, 570, [660, 720], symbol="MU", shares=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].symbol, "MU")
        self.assertEqual(results[0].shares, 2)
        self.assertIsNotNone(results[0].rr_target_1)
        self.assertIsNotNone(results[1].rr_target_1)

    def test_single_target(self):
        results = multi_target_rr(400, 380, [450], symbol="TSM")
        self.assertEqual(len(results), 1)


class TestRRVerdict(unittest.TestCase):
    def test_positive_expectancy(self):
        self.assertEqual(rr_verdict(2.5), "positive_expectancy")

    def test_marginal(self):
        self.assertEqual(rr_verdict(1.5), "marginal")

    def test_insufficient(self):
        self.assertEqual(rr_verdict(0.5), "insufficient")

    def test_invalid(self):
        self.assertEqual(rr_verdict(None), "invalid")
        self.assertEqual(rr_verdict(-1), "invalid")

    def test_boundary(self):
        self.assertEqual(rr_verdict(2.0), "positive_expectancy")
        self.assertEqual(rr_verdict(1.0), "marginal")


if __name__ == "__main__":
    unittest.main()
