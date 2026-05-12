"""Tests for compliance module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from interface.constants import FEE_PER_TRADE_USD
from interface.models import Portfolio, Position, RiskBudget, Trade

from verification.compliance import (
    check_cash_sufficiency,
    check_integer_shares,
    check_position_range,
    check_risk_budget,
    check_single_stock_cap,
    check_stop_loss_distance,
    run_full_compliance,
)


class TestCheckSingleStockCap(unittest.TestCase):
    def test_within_cap(self):
        result = check_single_stock_cap(5000, 30000, 25.0)
        self.assertTrue(result.passed)

    def test_exceeds_cap(self):
        result = check_single_stock_cap(10000, 30000, 25.0)
        self.assertFalse(result.passed)
        self.assertTrue(any("cap exceeded" in e for e in result.errors))

    def test_near_cap_warning(self):
        result = check_single_stock_cap(6250, 30000, 25.0)  # 20.83% — >80% of 25%
        self.assertTrue(result.passed)
        self.assertTrue(len(result.warnings) > 0)

    def test_zero_equity(self):
        result = check_single_stock_cap(5000, 0, 25.0)
        self.assertFalse(result.passed)


class TestCheckRiskBudget(unittest.TestCase):
    def test_within_budget(self):
        # 10 shares, entry 600, stop 570, equity 30000, risk 2%
        # total risk = 10 * (30 + 0.10 round-trip slippage) + two $5 fees = 311.0, max = 600
        result = check_risk_budget(10, 600, 570, 30000, 2.0)
        self.assertTrue(result.passed)
        self.assertAlmostEqual(result.details["total_risk_usd"], 311.0, places=2)

    def test_exceeds_budget(self):
        # 100 shares, risk = 100 * 30.10 + two $5 fees = 3020, max = 600
        result = check_risk_budget(100, 600, 570, 30000, 2.0)
        self.assertFalse(result.passed)
        self.assertTrue(any("risk budget exceeded" in e for e in result.errors))

    def test_fee_is_charged_per_side_not_per_share(self):
        result = check_risk_budget(3, 100, 95, 10000, 2.0, fee=5.0, slippage=0.0)
        self.assertTrue(result.passed)
        self.assertEqual(result.details["total_risk_usd"], 25.0)
        self.assertEqual(result.details["round_trip_fee_usd"], 10.0)

    def test_stop_above_entry(self):
        result = check_risk_budget(10, 600, 610, 30000, 2.0)
        self.assertFalse(result.passed)
        self.assertTrue(any("must be below" in e for e in result.errors))

    def test_zero_equity(self):
        result = check_risk_budget(10, 600, 570, 0, 2.0)
        self.assertFalse(result.passed)


class TestCheckStopLossDistance(unittest.TestCase):
    def test_valid_stop(self):
        result = check_stop_loss_distance(600, 575)  # 4.17%
        self.assertTrue(result.passed)

    def test_too_tight(self):
        result = check_stop_loss_distance(600, 598)  # 0.33%
        self.assertFalse(result.passed)
        self.assertTrue(any("too tight" in e for e in result.errors))

    def test_too_wide(self):
        result = check_stop_loss_distance(600, 550)  # 8.33%
        self.assertFalse(result.passed)
        self.assertTrue(any("too wide" in e for e in result.errors))

    def test_exact_max_stop_passes(self):
        result = check_stop_loss_distance(1.0, 0.95)
        self.assertTrue(result.passed)

    def test_stop_at_entry(self):
        result = check_stop_loss_distance(600, 600)
        self.assertFalse(result.passed)


class TestCheckPositionRange(unittest.TestCase):
    def test_in_range(self):
        result = check_position_range(6.5, 5.0, 8.0)
        self.assertTrue(result.passed)

    def test_below_range(self):
        result = check_position_range(3.0, 5.0, 8.0)
        self.assertFalse(result.passed)
        self.assertTrue(any("too small" in e for e in result.errors))

    def test_above_range(self):
        result = check_position_range(10.0, 5.0, 8.0)
        self.assertFalse(result.passed)
        self.assertTrue(any("too large" in e for e in result.errors))


class TestCheckCashSufficiency(unittest.TestCase):
    def test_sufficient_cash(self):
        trade = Trade("MSFT", "BUY", 1, 415.00)
        result = check_cash_sufficiency(10000.0, trade)
        self.assertTrue(result.passed)

    def test_buy_requires_usd_cash(self):
        trade = Trade("MSFT", "BUY", 1, 415.00)
        result = check_cash_sufficiency(10000.0, trade, cash_currency="HKD")
        self.assertFalse(result.passed)
        self.assertTrue(any("cash currency must be USD" in e for e in result.errors))

    def test_insufficient_cash(self):
        trade = Trade("MSFT", "BUY", 10, 415.00)
        result = check_cash_sufficiency(100.0, trade)
        self.assertFalse(result.passed)
        self.assertTrue(any("insufficient cash" in e for e in result.errors))

    def test_sell_always_passes(self):
        trade = Trade("MSFT", "SELL", 10, 415.00)
        result = check_cash_sufficiency(0.0, trade)
        self.assertTrue(result.passed)

    def test_near_minimum_warning(self):
        trade = Trade("MSFT", "BUY", 1, 415.00)
        result = check_cash_sufficiency(421.0, trade)  # 415 + 5 = 420, 421 is < 420 * 1.1
        self.assertTrue(result.passed)
        self.assertTrue(len(result.warnings) > 0)


class TestCheckIntegerShares(unittest.TestCase):
    def test_valid_integer(self):
        result = check_integer_shares(7)
        self.assertTrue(result.passed)

    def test_fractional(self):
        result = check_integer_shares(7.5)
        self.assertFalse(result.passed)

    def test_zero(self):
        result = check_integer_shares(0)
        self.assertFalse(result.passed)

    def test_negative(self):
        result = check_integer_shares(-1)
        self.assertFalse(result.passed)


class TestRunFullCompliance(unittest.TestCase):
    def test_explicit_equity_overrides_auto_estimate_for_position_caps(self):
        portfolio = Portfolio(positions=(Position("MSFT", 18, 100.0),), cash=0.0, cash_currency="HKD")
        trades = [Trade("MSFT", "BUY", 1, 100.0)]
        prices = {"MSFT": 100.0}
        stops = {"MSFT": 95.0}
        results = run_full_compliance(portfolio, trades, prices, stops, RiskBudget(equity=10000.0))
        cap_errors = [
            error
            for result in results
            for error in result.errors
            if "single stock cap exceeded" in error
        ]
        self.assertEqual([], cap_errors)

    def test_compliant_trades(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=50000.0)
        trades = [Trade("MSFT", "BUY", 5, 415.00)]
        prices = {"KO": 78.42, "MSFT": 415.00}
        stops = {"MSFT": 400.00}
        results = run_full_compliance(portfolio, trades, prices, stops)
        # Most should pass; position range may warn depending on equity
        self.assertGreater(len(results), 0)

    def test_non_compliant_trade(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=100.0)
        trades = [Trade("MSFT", "BUY", 100, 415.00)]
        prices = {"KO": 78.42, "MSFT": 415.00}
        stops = {"MSFT": 410.00}  # Very tight stop
        results = run_full_compliance(portfolio, trades, prices, stops)
        failed = [r for r in results if not r.passed]
        self.assertGreater(len(failed), 0)

    def test_empty_trades(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=10000.0)
        prices = {"KO": 78.42}
        results = run_full_compliance(portfolio, [], prices, {})
        # Should only have existing position cap checks
        self.assertGreater(len(results), 0)

    def test_multiple_buys_use_running_cash(self):
        portfolio = Portfolio(positions=(), cash=1000.0)
        trades = [Trade("MSFT", "BUY", 5, 100.0), Trade("NVDA", "BUY", 5, 100.0)]
        results = run_full_compliance(portfolio, trades, {"MSFT": 100.0, "NVDA": 100.0}, {})
        errors = [e for result in results for e in result.errors]
        self.assertTrue(any("insufficient cash" in e for e in errors))

    def test_post_trade_merged_position_cap_is_checked(self):
        portfolio = Portfolio(positions=(Position("MSFT", 20, 100.0),), cash=10000.0)
        trades = [Trade("MSFT", "BUY", 10, 100.0)]
        results = run_full_compliance(
            portfolio,
            trades,
            {"MSFT": 100.0},
            {"MSFT": 95.0},
            RiskBudget(equity=10000.0),
        )
        errors = [e for result in results for e in result.errors]
        self.assertTrue(any("post-trade MSFT" in e and "single stock cap exceeded" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
