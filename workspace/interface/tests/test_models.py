"""Tests for shared data models."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from interface.models import (
    FeeAdjustedRR,
    Position,
    Portfolio,
    PortfolioPnL,
    PositionPnL,
    PostTradePnL,
    RiskBudget,
    SectorScoreResult,
    ShortTermScoreResult,
    StressScenario,
    StockScoreResult,
    Trade,
    TradeVerdict,
    ValidationResult,
)


class TestPosition(unittest.TestCase):
    def test_create_position(self):
        p = Position(symbol="MSFT", shares=18, avg_cost=506.96, currency="USD")
        self.assertEqual(p.symbol, "MSFT")
        self.assertEqual(p.shares, 18)
        self.assertEqual(p.avg_cost, 506.96)
        self.assertEqual(p.currency, "USD")

    def test_default_currency(self):
        p = Position(symbol="KO", shares=30, avg_cost=77.52)
        self.assertEqual(p.currency, "USD")

    def test_frozen(self):
        p = Position(symbol="KO", shares=30, avg_cost=77.52)
        with self.assertRaises(AttributeError):
            p.shares = 40


class TestPortfolio(unittest.TestCase):
    def test_create_portfolio(self):
        positions = (
            Position("KO", 30, 77.52),
            Position("MSFT", 18, 506.96),
        )
        pf = Portfolio(positions=positions, cash=13247.11)
        self.assertEqual(len(pf.positions), 2)
        self.assertEqual(pf.cash, 13247.11)

    def test_empty_portfolio(self):
        pf = Portfolio(positions=(), cash=50000.0)
        self.assertEqual(len(pf.positions), 0)


class TestTrade(unittest.TestCase):
    def test_buy_trade(self):
        t = Trade(symbol="MU", action="BUY", shares=10, limit_price=600.0)
        self.assertEqual(t.action, "BUY")
        self.assertEqual(t.shares, 10)

    def test_sell_trade(self):
        t = Trade(symbol="MSFT", action="SELL", shares=5, limit_price=415.0)
        self.assertEqual(t.action, "SELL")


class TestPositionPnL(unittest.TestCase):
    def test_profit(self):
        pnl = PositionPnL(
            symbol="NVDA", shares=7, avg_cost=184.23,
            current_price=215.20, market_value=1506.40,
            cost_basis=1289.61, unrealized_pnl=216.79,
            unrealized_pnl_pct=16.81,
        )
        self.assertEqual(pnl.symbol, "NVDA")
        self.assertAlmostEqual(pnl.unrealized_pnl, 216.79, places=1)

    def test_no_price(self):
        pnl = PositionPnL(
            symbol="TCEHY", shares=400, avg_cost=549.0,
            current_price=None, market_value=None,
            cost_basis=219600.0, unrealized_pnl=None,
            unrealized_pnl_pct=None,
        )
        self.assertIsNone(pnl.current_price)
        self.assertIsNone(pnl.unrealized_pnl)


class TestRiskBudget(unittest.TestCase):
    def test_defaults(self):
        rb = RiskBudget(equity=30000.0)
        self.assertEqual(rb.max_risk_per_trade_pct, 2.0)
        self.assertEqual(rb.max_position_pct, 25.0)
        self.assertEqual(rb.min_position_pct, 5.0)
        self.assertEqual(rb.stop_loss_min_pct, 3.0)


class TestFeeAdjustedRR(unittest.TestCase):
    def test_basic(self):
        rr = FeeAdjustedRR(
            symbol="MU", entry=600.0, stop=570.0, target_1=660.0,
            target_2=None, fee_per_side=5.0, slippage=0.05,
            rr_target_1=1.68, rr_target_2=None,
            break_even_price=600.10, verdict="positive_expectancy",
        )
        self.assertEqual(rr.symbol, "MU")
        self.assertEqual(rr.verdict, "positive_expectancy")


class TestSectorScoreResult(unittest.TestCase):
    def test_ratings(self):
        for score, expected in [(85, "overweight"), (75, "tactical_overweight"),
                                 (65, "neutral"), (50, "underweight"), (30, "avoid")]:
            result = SectorScoreResult(
                sector="semiconductor", scores={}, weighted_score=score,
                rating=expected,
            )
            self.assertEqual(result.rating, expected)


class TestValidationResult(unittest.TestCase):
    def test_passed(self):
        vr = ValidationResult(passed=True, errors=(), warnings=(), details={})
        self.assertTrue(vr.passed)

    def test_failed(self):
        vr = ValidationResult(
            passed=False, errors=("exceeds 25% cap",), warnings=(), details={},
        )
        self.assertFalse(vr.passed)
        self.assertEqual(len(vr.errors), 1)


if __name__ == "__main__":
    unittest.main()