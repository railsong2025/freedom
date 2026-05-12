"""Tests for shared constants."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from interface.constants import (
    BENCHMARK_SYMBOLS,
    CHINESE_NAME_TO_TICKER,
    DEFAULT_BETA_MAP,
    DEFAULT_RISK_PER_TRADE_PCT,
    DEFAULT_SLIPPAGE_USD,
    FEE_PER_TRADE_USD,
    INDEX_PROXY_ETF_TO_BENCHMARK,
    MARKET_INDEX_BENCHMARKS,
    NON_TRADABLE_INDEX_SYMBOLS,
    SECTOR_ETF_SYMBOLS,
    SECTOR_RATING_THRESHOLDS,
    SECTOR_WEIGHTS,
    SHORT_TERM_THRESHOLDS,
    SHORT_TERM_WEIGHTS,
    SINGLE_STOCK_CAP_PCT,
    STOCK_TIER_THRESHOLDS,
    STOCK_WEIGHTS,
    TICKER_SECTOR_MAP,
    VETO_CONDITIONS,
)


class TestFeeConstants(unittest.TestCase):
    def test_fee(self):
        self.assertEqual(FEE_PER_TRADE_USD, 5.0)

    def test_slippage(self):
        self.assertEqual(DEFAULT_SLIPPAGE_USD, 0.05)


class TestRiskBudgetConstants(unittest.TestCase):
    def test_risk_per_trade(self):
        self.assertEqual(DEFAULT_RISK_PER_TRADE_PCT, 2.0)

    def test_single_stock_cap(self):
        self.assertEqual(SINGLE_STOCK_CAP_PCT, 25.0)


class TestScoringWeights(unittest.TestCase):
    def test_sector_weights_sum_to_100(self):
        self.assertEqual(sum(SECTOR_WEIGHTS.values()), 100)

    def test_stock_weights_sum_to_100(self):
        self.assertEqual(sum(STOCK_WEIGHTS.values()), 100)

    def test_short_term_weights_sum_to_100(self):
        self.assertEqual(sum(SHORT_TERM_WEIGHTS.values()), 100)

    def test_sector_weight_count(self):
        self.assertEqual(len(SECTOR_WEIGHTS), 8)

    def test_stock_weight_count(self):
        self.assertEqual(len(STOCK_WEIGHTS), 8)

    def test_short_term_weight_count(self):
        self.assertEqual(len(SHORT_TERM_WEIGHTS), 7)


class TestThresholds(unittest.TestCase):
    def test_sector_thresholds_ordered(self):
        scores = [t[0] for t in SECTOR_RATING_THRESHOLDS]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_stock_thresholds_ordered(self):
        scores = [t[0] for t in STOCK_TIER_THRESHOLDS]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_short_term_thresholds_ordered(self):
        scores = [t[0] for t in SHORT_TERM_THRESHOLDS]
        self.assertEqual(scores, sorted(scores, reverse=True))


class TestTickerSectorMap(unittest.TestCase):
    def test_known_tickers(self):
        self.assertEqual(TICKER_SECTOR_MAP["MU"], "semiconductor")
        self.assertEqual(TICKER_SECTOR_MAP["KO"], "consumer_staples")
        self.assertEqual(TICKER_SECTOR_MAP["MSFT"], "technology")

    def test_etf_in_map(self):
        self.assertEqual(TICKER_SECTOR_MAP["SMH"], "semiconductor")
        self.assertEqual(TICKER_SECTOR_MAP["SPY"], "broad_market")

    def test_market_indexes_in_map(self):
        self.assertEqual(TICKER_SECTOR_MAP["IXIC"], "broad_market_index")
        self.assertEqual(TICKER_SECTOR_MAP["SPX"], "broad_market_index")


class TestSectorETFs(unittest.TestCase):
    def test_semiconductor(self):
        self.assertIn("SMH", SECTOR_ETF_SYMBOLS["semiconductor"])
        self.assertIn("SOXX", SECTOR_ETF_SYMBOLS["semiconductor"])


class TestBenchmarks(unittest.TestCase):
    def test_benchmarks(self):
        self.assertIn("SPY", BENCHMARK_SYMBOLS)
        self.assertIn("QQQ", BENCHMARK_SYMBOLS)

    def test_index_proxy_mapping(self):
        self.assertIn("IXIC", NON_TRADABLE_INDEX_SYMBOLS)
        self.assertEqual(INDEX_PROXY_ETF_TO_BENCHMARK["QQQ"], "Nasdaq 100 / Nasdaq growth proxy")
        self.assertEqual(MARKET_INDEX_BENCHMARKS["NASDAQ_COMPOSITE"]["index_code"], "IXIC")
        self.assertEqual(MARKET_INDEX_BENCHMARKS["SP500"]["tradable_proxy"], "SPY")


class TestChineseNameMap(unittest.TestCase):
    def test_known_names(self):
        self.assertEqual(CHINESE_NAME_TO_TICKER["微软"], "MSFT")
        self.assertEqual(CHINESE_NAME_TO_TICKER["可口可乐"], "KO")
        self.assertEqual(CHINESE_NAME_TO_TICKER["英伟达"], "NVDA")

    def test_index_names_resolve_to_tradable_proxy(self):
        self.assertEqual(CHINESE_NAME_TO_TICKER["标普"], "SPY")
        self.assertEqual(CHINESE_NAME_TO_TICKER["纳斯达克"], "QQQ")


class TestVetoConditions(unittest.TestCase):
    def test_veto_count(self):
        self.assertGreaterEqual(len(VETO_CONDITIONS), 10)


class TestBetaMap(unittest.TestCase):
    def test_known_betas(self):
        self.assertEqual(DEFAULT_BETA_MAP["SPY"], 1.0)
        self.assertGreater(DEFAULT_BETA_MAP["NVDA"], 1.0)
        self.assertLess(DEFAULT_BETA_MAP["KO"], 1.0)


if __name__ == "__main__":
    unittest.main()
