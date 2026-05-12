"""Tests for technical_indicators module."""

import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from intelligence.technical_indicators import (
    atr,
    compute_indicator_summary,
    exponential_moving_average,
    high_low_range,
    moving_average,
    n_day_return,
    relative_strength,
    rsi,
    volatility,
    volume_ratio,
    vwap_approximation,
)


@dataclass
class FakeBar:
    symbol: str
    date: str
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: float | None
    source: str = "test"
    raw: dict = None
    current_price: float | None = None
    amount: float | None = None
    prev_close: float | None = None
    pct_change: float | None = None
    change_amount: float | None = None
    amplitude: float | None = None
    turnover_rate: float | None = None
    volume_ratio: float | None = None

    def __post_init__(self):
        if self.raw is None:
            self.raw = {}


def _make_bars(closes: list[float], start_date: str = "2026-04-01", base_vol: float = 1000000.0) -> list[FakeBar]:
    """Create FakeBar list from close prices with synthetic OHLCV."""
    bars = []
    for i, c in enumerate(closes):
        d = f"2026-04-{i + 1:02d}"
        bars.append(FakeBar(
            symbol="TEST", date=d,
            open=c * 0.995, high=c * 1.01, low=c * 0.99, close=c,
            volume=base_vol + i * 10000, source="test",
        ))
    return bars


class TestMovingAverage(unittest.TestCase):
    def test_sma_basic(self):
        bars = _make_bars([10, 20, 30, 40, 50])
        self.assertAlmostEqual(moving_average(bars, 5), 30.0)

    def test_sma_insufficient(self):
        bars = _make_bars([10, 20, 30])
        self.assertIsNone(moving_average(bars, 5))

    def test_sma_empty(self):
        self.assertIsNone(moving_average([], 5))

    def test_sma_20(self):
        bars = _make_bars(list(range(1, 31)))
        self.assertAlmostEqual(moving_average(bars, 20), sum(range(11, 31)) / 20)


class TestEMA(unittest.TestCase):
    def test_ema_basic(self):
        # Use longer series so EMA converges above SMA seed
        bars = _make_bars([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
        ema_val = exponential_moving_average(bars, 5)
        self.assertIsNotNone(ema_val)
        # With a long uptrend, EMA should be well above the SMA seed
        self.assertGreater(ema_val, 50)

    def test_ema_insufficient(self):
        bars = _make_bars([10, 20])
        self.assertIsNone(exponential_moving_average(bars, 5))


class TestATR(unittest.TestCase):
    def test_atr_basic(self):
        bars = _make_bars([100, 102, 101, 103, 105, 104, 106, 108, 107, 109,
                           108, 110, 112, 111, 113])
        atr_val = atr(bars, 14)
        self.assertIsNotNone(atr_val)
        self.assertGreater(atr_val, 0)

    def test_atr_insufficient(self):
        bars = _make_bars([100, 102])
        self.assertIsNone(atr(bars, 14))


class TestRSI(unittest.TestCase):
    def test_rsi_all_up(self):
        bars = _make_bars(list(range(50, 71)))  # 21 bars, all up
        rsi_val = rsi(bars, 14)
        self.assertIsNotNone(rsi_val)
        self.assertGreater(rsi_val, 90)  # Should be near 100

    def test_rsi_all_down(self):
        bars = _make_bars(list(range(70, 49, -1)))  # 21 bars, all down
        rsi_val = rsi(bars, 14)
        self.assertIsNotNone(rsi_val)
        self.assertLess(rsi_val, 10)  # Should be near 0

    def test_rsi_flat_series_is_neutral(self):
        bars = _make_bars([100] * 21)
        self.assertEqual(rsi(bars, 14), 50.0)

    def test_rsi_insufficient(self):
        bars = _make_bars([100, 102])
        self.assertIsNone(rsi(bars, 14))


class TestVWAP(unittest.TestCase):
    def test_vwap_basic(self):
        bars = _make_bars([100, 110, 120])
        vwap_val = vwap_approximation(bars)
        self.assertIsNotNone(vwap_val)
        # VWAP should be between low and high of range
        self.assertGreater(vwap_val, 90)
        self.assertLess(vwap_val, 125)

    def test_vwap_empty(self):
        self.assertIsNone(vwap_approximation([]))


class TestVolumeRatio(unittest.TestCase):
    def test_volume_ratio_normal(self):
        bars = _make_bars([100] * 20, base_vol=1000000.0)
        # Last bar has volume 1000000 + 19*10000 = 1190000, avg = 1095000
        vr = volume_ratio(bars, 20)
        self.assertIsNotNone(vr)
        self.assertAlmostEqual(vr, 1190000 / 1095000, places=3)

    def test_volume_ratio_insufficient(self):
        bars = _make_bars([100] * 5)
        self.assertIsNone(volume_ratio(bars, 20))


class TestVolatility(unittest.TestCase):
    def test_volatility_20d(self):
        bars = _make_bars([100, 101, 99, 102, 101, 103, 104, 102, 105, 107, 106, 108, 110, 109, 111, 113, 112, 115, 114, 116, 118])

        value = volatility(bars, 20)

        self.assertIsNotNone(value)
        self.assertGreater(value, 0)

    def test_volatility_insufficient(self):
        bars = _make_bars([100, 101, 102])
        self.assertIsNone(volatility(bars, 20))


class TestHighLowRange(unittest.TestCase):
    def test_high_low(self):
        bars = _make_bars(list(range(90, 111)))  # 21 bars
        high, low = high_low_range(bars, 20)
        self.assertIsNotNone(high)
        self.assertIsNotNone(low)
        self.assertGreater(high, low)

    def test_insufficient(self):
        bars = _make_bars([100])
        high, low = high_low_range(bars, 20)
        self.assertIsNone(high)
        self.assertIsNone(low)


class TestNDayReturn(unittest.TestCase):
    def test_positive_return(self):
        bars = _make_bars([100, 102, 104, 106, 108, 110])
        ret = n_day_return(bars, 5)
        self.assertAlmostEqual(ret, 10.0, places=1)  # (110-100)/100 * 100

    def test_negative_return(self):
        bars = _make_bars([110, 108, 106, 104, 102, 100])
        ret = n_day_return(bars, 5)
        self.assertAlmostEqual(ret, -9.09, places=1)

    def test_insufficient(self):
        bars = _make_bars([100, 102])
        self.assertIsNone(n_day_return(bars, 5))


class TestRelativeStrength(unittest.TestCase):
    def test_outperform(self):
        stock_bars = _make_bars([100, 105, 110, 115, 120, 125])
        bench_bars = _make_bars([100, 102, 104, 106, 108, 110])
        rs = relative_strength(stock_bars, bench_bars, 5)
        self.assertIsNotNone(rs)
        self.assertGreater(rs, 1.0)  # Stock outperformed

    def test_underperform(self):
        stock_bars = _make_bars([100, 102, 104, 106, 108, 110])
        bench_bars = _make_bars([100, 105, 110, 115, 120, 125])
        rs = relative_strength(stock_bars, bench_bars, 5)
        self.assertIsNotNone(rs)
        self.assertLess(rs, 1.0)

    def test_no_benchmark(self):
        stock_bars = _make_bars([100, 105, 110])
        self.assertIsNone(relative_strength(stock_bars, [], 5))


class TestComputeIndicatorSummary(unittest.TestCase):
    def test_summary_basic(self):
        bars = _make_bars(list(range(50, 71)))  # 21 bars
        summary = compute_indicator_summary(bars, symbol="TEST")
        self.assertEqual(summary["symbol"], "TEST")
        self.assertEqual(summary["ticker"], "TEST")
        self.assertEqual(summary["bar_count"], 21)
        self.assertEqual(summary["current_price"], 70)
        self.assertEqual(summary["close"], 70)
        self.assertEqual(summary["previous_close"], 69)
        self.assertAlmostEqual(summary["change_amount"], 1.0)
        self.assertAlmostEqual(summary["pct_change"], 1 / 69 * 100, places=4)
        self.assertIsNotNone(summary["amplitude"])
        self.assertIsNotNone(summary["amount"])
        self.assertTrue(summary["amount_is_estimated"])
        self.assertEqual(summary["market_source"], "test")
        self.assertIsNotNone(summary["ma_5"])
        self.assertIsNotNone(summary["ma_20"])
        self.assertEqual(summary["ma5"], summary["ma_5"])
        self.assertEqual(summary["ma10"], summary["ma_10"])
        self.assertEqual(summary["ma20"], summary["ma_20"])
        self.assertIsNotNone(summary["price_vs_ma5"])
        self.assertIsNotNone(summary["price_vs_ma10"])
        self.assertIsNotNone(summary["price_vs_ma20"])
        self.assertIsNotNone(summary["high_20d"])
        self.assertIsNotNone(summary["low_20d"])
        self.assertIsNotNone(summary["range_position_20d"])
        self.assertIsNotNone(summary["return_1d"])
        self.assertIsNotNone(summary["atr_14"])
        self.assertIsNotNone(summary["volatility_20d"])
        self.assertIsNotNone(summary["rsi_14"])
        self.assertIsNotNone(summary["return_5d"])
        self.assertIn("field_source_map", summary)
        self.assertIn("field_timestamp_map", summary)
        self.assertIn("relative_strength_spy", summary)
        self.assertFalse(summary["usable_for_current_trade"])
        self.assertEqual("ZEUS_FIELD_FAILURE", summary["zeus_field_status"])

    def test_summary_prefers_source_market_tape_fields(self):
        bars = _make_bars([100] * 20)
        latest = bars[-1]
        bars[-1] = FakeBar(
            symbol="TEST",
            date=latest.date,
            open=101,
            high=110,
            low=100,
            close=108,
            volume=3000000,
            source="aktools_http",
            current_price=109,
            amount=324000000,
            prev_close=100,
            pct_change=8.0,
            change_amount=8.0,
            amplitude=10.0,
            turnover_rate=2.5,
            volume_ratio=1.8,
        )

        summary = compute_indicator_summary(bars, symbol="TEST")

        self.assertEqual(summary["market_source"], "aktools_http")
        self.assertEqual(summary["current_price"], 109)
        self.assertEqual(summary["previous_close"], 100)
        self.assertEqual(summary["pct_change"], 8.0)
        self.assertEqual(summary["change_amount"], 8.0)
        self.assertEqual(summary["amplitude"], 10.0)
        self.assertEqual(summary["amount"], 324000000)
        self.assertFalse(summary["amount_is_estimated"])
        self.assertEqual(summary["volume_ratio"], 1.8)
        self.assertEqual(summary["volume_ratio_source"], "source_field")
        self.assertEqual(summary["turnover_rate"], 2.5)

    def test_summary_current_strategy_field_pack_complete_with_benchmarks(self):
        bars = _make_bars(list(range(100, 121)))
        spy = _make_bars(list(range(100, 121)))
        qqq = _make_bars(list(range(98, 119)))
        smh = _make_bars(list(range(95, 116)))
        soxx = _make_bars(list(range(90, 111)))
        latest = bars[-1]
        bars[-1] = FakeBar(
            symbol="TEST",
            date=latest.date,
            open=119,
            high=122,
            low=118,
            close=121,
            volume=2_000_000,
            source="financeBusiness_mcp",
            raw={"name": "Test Corp", "update_time": "2026-04-21 04:00:00", "statusDescription": "已收盘"},
            current_price=121,
            amount=242_000_000,
            prev_close=120,
            pct_change=0.8333,
            change_amount=1,
            amplitude=3.3333,
            turnover_rate=1.2,
            volume_ratio=1.5,
        )

        summary = compute_indicator_summary(
            bars,
            relative_benchmark_bars={"SPY": spy, "QQQ": qqq, "SMH": smh, "SOXX": soxx},
            symbol="TEST",
        )

        self.assertEqual("Test Corp", summary["name"])
        self.assertEqual("2026-04-21 04:00:00", summary["quote_time"])
        self.assertEqual("已收盘", summary["trade_status"])
        self.assertIsNotNone(summary["relative_strength_spy"])
        self.assertIsNotNone(summary["relative_strength_qqq"])
        self.assertIsNotNone(summary["relative_strength_smh"])
        self.assertIsNotNone(summary["relative_strength_soxx"])
        self.assertEqual([], summary["missing_fields"])
        self.assertEqual("complete", summary["zeus_field_status"])
        self.assertTrue(summary["usable_for_current_trade"])

    def test_index_proxy_etf_allows_nonblocking_name_and_turnover_gaps(self):
        bars = _make_bars(list(range(100, 121)))
        spy = _make_bars(list(range(100, 121)))
        qqq = _make_bars(list(range(100, 121)))
        smh = _make_bars(list(range(95, 116)))
        soxx = _make_bars(list(range(90, 111)))
        latest = bars[-1]
        bars[-1] = FakeBar(
            symbol="QQQ",
            date=latest.date,
            open=119,
            high=122,
            low=118,
            close=121,
            volume=2_000_000,
            source="financeBusiness_mcp_cached_csv",
            raw={"update_time": "2026-04-21", "statusDescription": "已收盘"},
            current_price=121,
            prev_close=120,
            pct_change=0.8333,
            change_amount=1,
            amplitude=3.3333,
        )

        summary = compute_indicator_summary(
            bars,
            relative_benchmark_bars={"SPY": spy, "QQQ": qqq, "SMH": smh, "SOXX": soxx},
            symbol="QQQ",
        )

        self.assertEqual("tradable_index_proxy_etf", summary["instrument_type"])
        self.assertEqual("Nasdaq 100 / Nasdaq growth proxy", summary["market_proxy_for"])
        self.assertIn("name", summary["non_blocking_missing_fields"])
        self.assertIn("turnover_rate", summary["non_blocking_missing_fields"])
        self.assertNotIn("name", summary["blocking_missing_fields"])
        self.assertNotIn("turnover_rate", summary["blocking_missing_fields"])
        self.assertEqual("computed_latest_volume_vs_20bar_average", summary["volume_ratio_source"])
        self.assertTrue(summary["usable_for_current_trade"])

    def test_non_tradable_index_is_market_regime_usable_not_tradeable(self):
        bars = [
            FakeBar(
                symbol="IXIC",
                date=f"2026-04-{i + 1:02d}",
                open=25000 + i * 10,
                high=25100 + i * 10,
                low=24900 + i * 10,
                close=25050 + i * 10,
                volume=6_000_000_000 + i * 1000,
                source="financeBusiness_mcp_stock_index_list",
            )
            for i in range(6)
        ]

        summary = compute_indicator_summary(bars, symbol="IXIC")

        self.assertEqual("non_tradable_index", summary["instrument_type"])
        self.assertEqual("Nasdaq Composite", summary["market_proxy_for"])
        self.assertEqual("QQQ", summary["tradable_proxy"])
        self.assertEqual([], summary["blocking_missing_fields"])
        self.assertTrue(summary["market_regime_usable"])
        self.assertFalse(summary["usable_for_current_trade"])
        self.assertEqual("non_tradable_index_context", summary["zeus_field_status"])

    def test_summary_empty(self):
        summary = compute_indicator_summary([], symbol="EMPTY")
        self.assertEqual(summary["bar_count"], 0)
        self.assertIsNone(summary["current_price"])
        self.assertIsNone(summary["ma_5"])


if __name__ == "__main__":
    unittest.main()
