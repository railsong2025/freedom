"""Tests for pnl_audit module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from interface.constants import FEE_PER_TRADE_USD
from interface.models import (
    Portfolio,
    PortfolioPnL,
    Position,
    PositionPnL,
    PostTradePnL,
    Trade,
)

from verification.pnl_audit import (
    audit_fee_application,
    audit_portfolio_pnl,
    audit_position_pnl,
    audit_post_trade_pnl,
)


class TestAuditPositionPnL(unittest.TestCase):
    def test_valid_position(self):
        pos = Position("NVDA", 7, 184.23)
        result = audit_position_pnl(pos, 215.20)
        self.assertTrue(result.passed)
        self.assertEqual(len(result.errors), 0)

    def test_fractional_shares(self):
        pos = Position("NVDA", 7.5, 184.23)
        result = audit_position_pnl(pos, 215.20)
        self.assertFalse(result.passed)
        self.assertTrue(any("positive integer" in e for e in result.errors))

    def test_zero_shares(self):
        pos = Position("NVDA", 0, 184.23)
        result = audit_position_pnl(pos, 215.20)
        self.assertFalse(result.passed)

    def test_negative_avg_cost(self):
        pos = Position("NVDA", 7, -100.0)
        result = audit_position_pnl(pos, 215.20)
        self.assertFalse(result.passed)
        self.assertTrue(any("avg_cost must be positive" in e for e in result.errors))

    def test_market_value_mismatch(self):
        pos = Position("NVDA", 7, 184.23)
        reported = PositionPnL(
            symbol="NVDA", shares=7, avg_cost=184.23,
            current_price=215.20, market_value=9999.0,
            cost_basis=1289.61, unrealized_pnl=216.69, unrealized_pnl_pct=16.81,
        )
        result = audit_position_pnl(pos, 215.20, reported)
        self.assertFalse(result.passed)
        self.assertTrue(any("market_value mismatch" in e for e in result.errors))

    def test_unrealized_pnl_mismatch(self):
        pos = Position("KO", 30, 77.52)
        reported = PositionPnL(
            symbol="KO", shares=30, avg_cost=77.52,
            current_price=78.42, market_value=2352.60,
            cost_basis=2325.60, unrealized_pnl=-999.0, unrealized_pnl_pct=0.39,
        )
        result = audit_position_pnl(pos, 78.42, reported)
        self.assertFalse(result.passed)
        self.assertTrue(any("unrealized_pnl mismatch" in e for e in result.errors))

    def test_cost_basis_mismatch(self):
        pos = Position("MSFT", 18, 506.96)
        reported = PositionPnL(
            symbol="MSFT", shares=18, avg_cost=506.96,
            current_price=415.12, market_value=7472.16,
            cost_basis=9999.0, unrealized_pnl=-1652.16, unrealized_pnl_pct=-18.14,
        )
        result = audit_position_pnl(pos, 415.12, reported)
        self.assertFalse(result.passed)
        self.assertTrue(any("cost_basis mismatch" in e for e in result.errors))

    def test_no_price_skips_pnl_check(self):
        pos = Position("NVDA", 7, 184.23)
        result = audit_position_pnl(pos, None)
        self.assertTrue(result.passed)


class TestAuditPortfolioPnL(unittest.TestCase):
    def test_consistent_portfolio(self):
        positions = (
            Position("KO", 30, 77.52),
            Position("MSFT", 18, 506.96),
        )
        portfolio = Portfolio(positions=positions, cash=10000.0)
        prices = {"KO": 78.42, "MSFT": 415.12}
        result = audit_portfolio_pnl(portfolio, prices)
        self.assertTrue(result.passed)

    def test_total_cost_basis_mismatch(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=10000.0)
        prices = {"KO": 78.42}
        reported = PortfolioPnL(
            positions=(), total_market_value=2352.60,
            total_cost_basis=9999.0, total_unrealized_pnl=27.0,
            total_unrealized_pnl_pct=1.16, total_equity=12352.60, cash=10000.0,
            valuation_notes="test",
        )
        result = audit_portfolio_pnl(portfolio, prices, reported)
        self.assertFalse(result.passed)
        self.assertTrue(any("total_cost_basis mismatch" in e for e in result.errors))

    def test_total_market_value_mismatch(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=10000.0)
        prices = {"KO": 78.42}
        reported = PortfolioPnL(
            positions=(), total_market_value=9999.0,
            total_cost_basis=2325.60, total_unrealized_pnl=27.0,
            total_unrealized_pnl_pct=1.16, total_equity=19999.0, cash=10000.0,
            valuation_notes="test",
        )
        result = audit_portfolio_pnl(portfolio, prices, reported)
        self.assertFalse(result.passed)
        self.assertTrue(any("total_market_value mismatch" in e for e in result.errors))


class TestAuditPostTradePnL(unittest.TestCase):
    def test_valid_buy(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=10000.0)
        trades = [Trade("MSFT", "BUY", 1, 415.00)]
        prices = {"KO": 78.42, "MSFT": 415.00}
        result = audit_post_trade_pnl(portfolio, trades, prices)
        self.assertTrue(result.passed)

    def test_fractional_shares_in_trade(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=100000.0)
        trades = [Trade("MSFT", "BUY", 1.5, 415.00)]
        prices = {"KO": 78.42, "MSFT": 415.00}
        result = audit_post_trade_pnl(portfolio, trades, prices)
        self.assertFalse(result.passed)
        self.assertTrue(any("positive integer" in e for e in result.errors))

    def test_zero_limit_price(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=100000.0)
        trades = [Trade("MSFT", "BUY", 1, 0)]
        prices = {"KO": 78.42, "MSFT": 415.00}
        result = audit_post_trade_pnl(portfolio, trades, prices)
        self.assertFalse(result.passed)
        self.assertTrue(any("limit_price must be positive" in e for e in result.errors))

    def test_fee_mismatch_reported(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=10000.0)
        trades = [Trade("MSFT", "BUY", 1, 415.00)]
        prices = {"KO": 78.42, "MSFT": 415.00}
        reported = PostTradePnL(
            trades=tuple(trades), realized_pnl=0.0, total_fees=999.0,
            remaining_positions=(), remaining_cash=9580.0,
            remaining_portfolio_pnl=None, post_trade_equity=None,
        )
        result = audit_post_trade_pnl(portfolio, trades, prices, reported)
        self.assertFalse(result.passed)
        self.assertTrue(any("total_fees mismatch" in e for e in result.errors))

    def test_buy_avg_cost_must_include_fee(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=10000.0)
        trades = [Trade("MSFT", "BUY", 1, 415.00)]
        prices = {"KO": 78.42, "MSFT": 415.00}
        reported = PostTradePnL(
            trades=tuple(trades),
            realized_pnl=0.0,
            total_fees=5.0,
            remaining_positions=(
                Position("KO", 30, 77.52),
                Position("MSFT", 1, 415.00),
            ),
            remaining_cash=9580.0,
            remaining_portfolio_pnl=None,
            post_trade_equity=None,
        )
        result = audit_post_trade_pnl(portfolio, trades, prices, reported)
        self.assertFalse(result.passed)
        self.assertTrue(any("avg_cost mismatch" in e for e in result.errors))

    def test_remaining_position_currency_is_audited(self):
        positions = (Position("0700.HK", 400, 549.0, currency="HKD"),)
        portfolio = Portfolio(positions=positions, cash=10000.0)
        trades = [Trade("MSFT", "BUY", 1, 100.00)]
        prices = {"MSFT": 100.00}
        reported = PostTradePnL(
            trades=tuple(trades),
            realized_pnl=0.0,
            total_fees=5.0,
            remaining_positions=(
                Position("0700.HK", 400, 549.0, currency="USD"),
                Position("MSFT", 1, 105.00),
            ),
            remaining_cash=9895.0,
            remaining_portfolio_pnl=None,
            post_trade_equity=None,
        )
        result = audit_post_trade_pnl(portfolio, trades, prices, reported)
        self.assertFalse(result.passed)
        self.assertTrue(any("currency mismatch" in e for e in result.errors))

    def test_non_usd_cash_trade_is_audit_failure(self):
        portfolio = Portfolio(positions=(Position("MSFT", 1, 100.0),), cash=10000.0, cash_currency="HKD")
        trades = [Trade("MSFT", "BUY", 1, 100.0)]
        result = audit_post_trade_pnl(portfolio, trades, {"MSFT": 100.0})
        self.assertFalse(result.passed)
        self.assertTrue(any("cash currency HKD" in e for e in result.errors))


class TestAuditFeeApplication(unittest.TestCase):
    def test_correct_fees(self):
        trades = [Trade("MSFT", "BUY", 1, 415.00), Trade("KO", "SELL", 5, 78.42)]
        result = audit_fee_application(trades, FEE_PER_TRADE_USD, 10.0)
        self.assertTrue(result.passed)

    def test_incorrect_fees(self):
        trades = [Trade("MSFT", "BUY", 1, 415.00), Trade("KO", "SELL", 5, 78.42)]
        result = audit_fee_application(trades, FEE_PER_TRADE_USD, 15.0)
        self.assertFalse(result.passed)
        self.assertTrue(any("fee mismatch" in e for e in result.errors))

    def test_no_trades(self):
        result = audit_fee_application([], FEE_PER_TRADE_USD, 0.0)
        self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()
