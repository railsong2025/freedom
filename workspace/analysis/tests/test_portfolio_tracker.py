"""Tests for portfolio_tracker module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from interface.models import Portfolio, Position, Trade
from analysis.portfolio_tracker import (
    compute_portfolio_pnl,
    compute_position_pnl,
    compute_post_trade_pnl,
    parse_base_short_positions,
    portfolio_pnl_to_markdown,
)


BASE_SHORT_TEXT = """# Buffett 短线交易基础记录

## record 17操作后持仓

- 腾讯控股：400 股，成本 549 港元
- 可口可乐：30 股，成本 77.52 美元
- 微软：18 股，成本 506.96 美元
- 英伟达：7 股，成本 184.23 美元
- 标普 500 ETF：3 股，成本 679.31 美元
- 超威半导体：1股，成本 413.23美元
- 台积电：6股，成本 416.71美元
- ANET：5股，成本 142.78美元

## 可用资金

- 103754 港元，可投资港股或美股
"""


class TestParseBaseShort(unittest.TestCase):
    def test_parse_usd_positions(self):
        portfolio = parse_base_short_positions(BASE_SHORT_TEXT)
        usd_positions = [p for p in portfolio.positions if p.currency == "USD"]
        self.assertGreaterEqual(len(usd_positions), 6)  # KO, MSFT, NVDA, SPY, AMD, TSM, ANET

    def test_parse_hkd_positions(self):
        portfolio = parse_base_short_positions(BASE_SHORT_TEXT)
        hkd_positions = [p for p in portfolio.positions if p.currency == "HKD"]
        self.assertGreaterEqual(len(hkd_positions), 1)  # Tencent

    def test_parse_cash(self):
        portfolio = parse_base_short_positions(BASE_SHORT_TEXT)
        self.assertEqual(portfolio.cash, 103754.0)
        self.assertEqual(portfolio.cash_currency, "HKD")

    def test_parse_inline_cash_line(self):
        text = """# Buffett 短线交易基础记录

## 初始持仓

- 微软：18 股，成本 506.96 美元
- 剩余可用资金103754 港元，可投资港股或美股
"""
        portfolio = parse_base_short_positions(text)
        self.assertEqual(portfolio.cash, 103754.0)
        self.assertEqual(portfolio.cash_currency, "HKD")

    def test_parse_tencent(self):
        portfolio = parse_base_short_positions(BASE_SHORT_TEXT)
        tencent = [p for p in portfolio.positions if "0700" in p.symbol or "腾讯" in p.symbol or p.symbol == "0700.HK"]
        self.assertGreaterEqual(len(tencent), 1)

    def test_parse_msft(self):
        portfolio = parse_base_short_positions(BASE_SHORT_TEXT)
        msft = [p for p in portfolio.positions if p.symbol == "MSFT"]
        self.assertEqual(len(msft), 1)
        self.assertEqual(msft[0].shares, 18)
        self.assertAlmostEqual(msft[0].avg_cost, 506.96, places=2)

    def test_parse_uses_latest_record_section_not_initial_holdings(self):
        text = """# Buffett 短线交易基础记录

## 初始持仓

- 微软：53 股，成本 447.49 美元
- 特斯拉：5 股，成本 667 美元

## record 16操作后持仓

- 微软：20 股，成本 500.00 美元

## record 17操作后持仓

- 微软：18 股，成本 506.96 美元
- 可口可乐：30 股，成本 77.52 美元

## 可用资金

- 103754 港元，可投资港股或美股
"""
        portfolio = parse_base_short_positions(text)
        positions = {p.symbol: p for p in portfolio.positions}

        self.assertEqual(set(positions), {"MSFT", "KO"})
        self.assertEqual(positions["MSFT"].shares, 18)
        self.assertAlmostEqual(positions["MSFT"].avg_cost, 506.96, places=2)
        self.assertNotIn("TSLA", positions)


class TestComputePositionPnL(unittest.TestCase):
    def test_profit(self):
        pos = Position("NVDA", 7, 184.23)
        pnl = compute_position_pnl(pos, 215.20)
        self.assertAlmostEqual(pnl.market_value, 7 * 215.20, places=2)
        self.assertAlmostEqual(pnl.cost_basis, 7 * 184.23, places=2)
        self.assertGreater(pnl.unrealized_pnl, 0)
        self.assertGreater(pnl.unrealized_pnl_pct, 0)

    def test_loss(self):
        pos = Position("MSFT", 18, 506.96)
        pnl = compute_position_pnl(pos, 415.12)
        self.assertLess(pnl.unrealized_pnl, 0)
        self.assertLess(pnl.unrealized_pnl_pct, 0)

    def test_no_price(self):
        pos = Position("0700.HK", 400, 549.0, currency="HKD")
        pnl = compute_position_pnl(pos, None)
        self.assertIsNone(pnl.market_value)
        self.assertIsNone(pnl.unrealized_pnl)


class TestComputePortfolioPnL(unittest.TestCase):
    def test_full_portfolio(self):
        positions = (
            Position("KO", 30, 77.52),
            Position("MSFT", 18, 506.96),
            Position("NVDA", 7, 184.23),
        )
        portfolio = Portfolio(positions=positions, cash=13247.11)
        prices = {"KO": 78.42, "MSFT": 415.12, "NVDA": 215.20}
        pnl = compute_portfolio_pnl(portfolio, prices)
        self.assertIsNotNone(pnl.total_market_value)
        self.assertIsNotNone(pnl.total_unrealized_pnl)
        self.assertEqual(len(pnl.positions), 3)

    def test_missing_prices(self):
        positions = (Position("KO", 30, 77.52), Position("UNKNOWN", 10, 100.0))
        portfolio = Portfolio(positions=positions, cash=5000.0)
        prices = {"KO": 78.42}
        pnl = compute_portfolio_pnl(portfolio, prices)
        # KO should have P&L, UNKNOWN should not
        ko_pnl = [p for p in pnl.positions if p.symbol == "KO"][0]
        self.assertIsNotNone(ko_pnl.unrealized_pnl)
        unk_pnl = [p for p in pnl.positions if p.symbol == "UNKNOWN"][0]
        self.assertIsNone(unk_pnl.unrealized_pnl)
        self.assertAlmostEqual(pnl.total_cost_basis, 30 * 77.52, places=2)

    def test_mixed_currency_and_unpriced_positions_do_not_pollute_usd_totals(self):
        portfolio = parse_base_short_positions(BASE_SHORT_TEXT)
        prices = {"MSFT": 415.12}
        pnl = compute_portfolio_pnl(portfolio, prices)

        self.assertAlmostEqual(pnl.total_market_value, 18 * 415.12, places=2)
        self.assertAlmostEqual(pnl.total_cost_basis, 18 * 506.96, places=2)
        self.assertAlmostEqual(pnl.priced_usd_market_value, pnl.total_market_value, places=2)
        self.assertEqual(pnl.cash_currency, "HKD")
        self.assertTrue(any("0700.HK" in item for item in pnl.excluded_positions))
        self.assertIn("HKD position", pnl.valuation_notes)
        self.assertIn("USD positions without current prices", pnl.valuation_notes)


class TestComputePostTradePnL(unittest.TestCase):
    def test_buy_with_cash(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=10000.0)
        trades = [Trade("MSFT", "BUY", 1, 415.00)]
        prices = {"KO": 78.42, "MSFT": 415.00}
        post = compute_post_trade_pnl(portfolio, trades, prices)
        self.assertEqual(len(post.trades), 1)
        self.assertAlmostEqual(post.remaining_cash, 10000.0 - 415.00 - 5.0, places=2)
        self.assertEqual(post.total_fees, 5.0)
        msft = [p for p in post.remaining_positions if p.symbol == "MSFT"][0]
        self.assertAlmostEqual(msft.avg_cost, 420.00, places=2)

    def test_add_buy_avg_cost_includes_one_trade_fee(self):
        positions = (Position("MSFT", 2, 100.0),)
        portfolio = Portfolio(positions=positions, cash=10000.0)
        trades = [Trade("MSFT", "BUY", 2, 110.00)]
        prices = {"MSFT": 110.00}
        post = compute_post_trade_pnl(portfolio, trades, prices)
        msft = [p for p in post.remaining_positions if p.symbol == "MSFT"][0]
        expected_avg_cost = (2 * 100.0 + 2 * 110.0 + 5.0) / 4
        self.assertAlmostEqual(msft.avg_cost, expected_avg_cost, places=2)

    def test_post_trade_preserves_non_usd_position_currency(self):
        positions = (Position("0700.HK", 400, 549.0, currency="HKD"),)
        portfolio = Portfolio(positions=positions, cash=10000.0)
        trades = [Trade("MSFT", "BUY", 1, 100.00)]
        prices = {"MSFT": 100.00}
        post = compute_post_trade_pnl(portfolio, trades, prices)
        tencent = [p for p in post.remaining_positions if p.symbol == "0700.HK"][0]
        self.assertEqual(tencent.currency, "HKD")

    def test_sell_realizes_pnl(self):
        positions = (Position("MSFT", 18, 506.96),)
        portfolio = Portfolio(positions=positions, cash=1000.0)
        trades = [Trade("MSFT", "SELL", 5, 415.00)]
        prices = {"MSFT": 415.00}
        post = compute_post_trade_pnl(portfolio, trades, prices)
        # Realized P&L = (415 - 506.96) * 5 - 5 = -459.80 - 5 = -464.80
        self.assertAlmostEqual(post.realized_pnl, -464.80, places=2)
        self.assertEqual(post.total_fees, 5.0)

    def test_insufficient_cash_skips_buy(self):
        positions = (Position("KO", 30, 77.52),)
        portfolio = Portfolio(positions=positions, cash=100.0)
        trades = [Trade("MSFT", "BUY", 1, 415.00)]
        prices = {"KO": 78.42, "MSFT": 415.00}
        post = compute_post_trade_pnl(portfolio, trades, prices)
        self.assertEqual(len(post.trades), 0)  # Trade skipped
        self.assertEqual(post.total_fees, 0.0)
        self.assertTrue(post.skipped_trades)

    def test_non_usd_cash_skips_us_trade_projection(self):
        portfolio = Portfolio(positions=(Position("MSFT", 1, 100.0),), cash=10000.0, cash_currency="HKD")
        trades = [Trade("MSFT", "BUY", 1, 100.0)]
        post = compute_post_trade_pnl(portfolio, trades, {"MSFT": 100.0})
        self.assertEqual(len(post.trades), 0)
        self.assertIn("cash currency HKD", post.skipped_trades[0])

    def test_sell_more_than_held(self):
        positions = (Position("MSFT", 5, 506.96),)
        portfolio = Portfolio(positions=positions, cash=1000.0)
        trades = [Trade("MSFT", "SELL", 10, 415.00)]  # Trying to sell 10 but only hold 5
        prices = {"MSFT": 415.00}
        post = compute_post_trade_pnl(portfolio, trades, prices)
        self.assertEqual(len(post.trades), 0)  # Trade skipped


class TestPortfolioPnLMarkdown(unittest.TestCase):
    def test_markdown_output(self):
        positions = (Position("KO", 30, 77.52), Position("MSFT", 18, 506.96))
        portfolio = Portfolio(positions=positions, cash=13247.11)
        prices = {"KO": 78.42, "MSFT": 415.12}
        pnl = compute_portfolio_pnl(portfolio, prices)
        md = portfolio_pnl_to_markdown(pnl)
        self.assertIn("KO", md)
        self.assertIn("MSFT", md)
        self.assertIn("Total", md)


if __name__ == "__main__":
    unittest.main()
