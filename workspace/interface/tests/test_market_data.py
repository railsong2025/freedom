"""Tests for public market data adapters."""

from __future__ import annotations

import datetime as dt
import json
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from interface.market_data import (
    AkShareMarketDataProvider,
    AkToolsMarketDataProvider,
    CompositeMarketDataClient,
    CsvMarketDataProvider,
    DailyBar,
    HttpApiMarketDataProvider,
    MarketDataError,
    MarketDataTimeoutError,
    MarketDataResult,
    SourceAttempt,
    StooqMarketDataProvider,
    _Cache,
    _CircuitBreaker,
    _RateLimiter,
    _retry,
    _trading_days_between,
    TimeoutError,
)


class TestHttpApiMarketDataProvider(unittest.TestCase):
    def test_http_provider_filters_and_sorts_requested_date_range(self):
        payload = {
            "bars": [
                {"date": "2026-05-09", "close": 9},
                {"date": "2026-05-08", "close": 8},
                {"date": "2026-05-10", "close": 10},
            ]
        }

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps(payload).encode("utf-8")

        with patch("urllib.request.urlopen", return_value=Response()):
            provider = HttpApiMarketDataProvider("https://example.com/{symbol}?start={start}&end={end}")
            bars = provider.daily_bars("MSFT", dt.date(2026, 5, 8), dt.date(2026, 5, 9))

        self.assertEqual(["2026-05-08", "2026-05-09"], [bar.date for bar in bars])


class TestAkShareMarketDataProvider(unittest.TestCase):
    def test_akshare_provider_prefers_stock_us_hist_and_merges_spot_snapshot(self):
        class Frame:
            def __init__(self, records):
                self._records = records
                self.empty = not bool(records)

            def to_dict(self, orient):
                return self._records

        class FakeAk:
            def __init__(self):
                self.hist_symbol = None

            def stock_us_spot_em(self):
                return Frame([
                    {
                        "代码": "105.AAPL",
                        "最新价": 13.0,
                        "今开": 12.1,
                        "最高": 13.2,
                        "最低": 11.9,
                        "昨收": 12.0,
                        "涨跌幅": 8.33,
                        "涨跌额": 1.0,
                        "振幅": 10.83,
                        "成交量": 2500,
                        "成交额": 32500,
                        "量比": 1.4,
                        "换手率": 0.5,
                    }
                ])

            def stock_us_hist(self, symbol, period, start_date, end_date, adjust):
                self.hist_symbol = symbol
                return Frame([
                    {
                        "日期": "2026-05-08",
                        "开盘": 11,
                        "收盘": 12,
                        "最高": 12.5,
                        "最低": 10.5,
                        "成交量": 2000,
                        "成交额": 24000,
                        "振幅": 16.67,
                        "涨跌幅": 9.09,
                        "涨跌额": 1,
                        "换手率": 0.3,
                    }
                ])

            def stock_us_daily(self, symbol, adjust):
                raise AssertionError("stock_us_daily should only be used as a fallback")

        fake_ak = FakeAk()
        with patch.dict(sys.modules, {"akshare": fake_ak}):
            provider = AkShareMarketDataProvider(rate_limit_min_interval=0)
            bars = provider.daily_bars("AAPL", dt.date(2026, 5, 8), dt.date(2026, 5, 8))

        self.assertEqual("105.AAPL", fake_ak.hist_symbol)
        self.assertEqual(1, len(bars))
        self.assertEqual("AAPL", bars[0].symbol)
        self.assertEqual(13.0, bars[0].current_price)
        self.assertEqual(12.0, bars[0].close)
        self.assertEqual(12.1, bars[0].open)
        self.assertEqual(12.0, bars[0].prev_close)
        self.assertEqual(8.33, bars[0].pct_change)
        self.assertEqual(1.0, bars[0].change_amount)
        self.assertEqual(10.83, bars[0].amplitude)
        self.assertEqual(32500.0, bars[0].amount)
        self.assertEqual(1.4, bars[0].volume_ratio)
        self.assertEqual(0.5, bars[0].turnover_rate)


class TestAkToolsMarketDataProvider(unittest.TestCase):
    def test_aktools_provider_merges_spot_snapshot_with_stock_us_hist(self):
        spot_payload = [
            {
                "代码": "105.AAPL",
                "最新价": 12.5,
                "今开": 11.5,
                "最高": 13.5,
                "最低": 10.5,
                "昨收": 11,
                "涨跌幅": 13.64,
                "涨跌额": 1.5,
                "振幅": 27.27,
                "成交量": 2200,
                "成交额": 27500,
                "量比": 1.6,
                "换手率": 0.4,
            }
        ]
        hist_payload = [
            {"date": "2026-05-07T00:00:00.000", "open": 10, "high": 12, "low": 9, "close": 11, "volume": 1000},
            {
                "date": "2026-05-08T00:00:00.000",
                "open": 11,
                "high": 13,
                "low": 10,
                "close": 12,
                "volume": 2000,
                "prev_close": 11,
                "pct_change": 9.09,
                "change_amount": 1,
                "amplitude": 27.27,
                "amount": 24000,
            },
            {"date": "2026-05-10T00:00:00.000", "close": 14},
        ]
        requested_urls = []

        class Response:
            def __init__(self, payload):
                self.payload = payload

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps(self.payload).encode("utf-8")

        def fake_urlopen(request, timeout=10):
            requested_urls.append(request.full_url)
            if "stock_us_spot_em" in request.full_url:
                return Response(spot_payload)
            return Response(hist_payload)

        with patch("urllib.request.urlopen", side_effect=fake_urlopen):
            provider = AkToolsMarketDataProvider("http://127.0.0.1:8080")
            bars = provider.daily_bars("aapl", dt.date(2026, 5, 7), dt.date(2026, 5, 8))

        self.assertEqual(["2026-05-07", "2026-05-08"], [bar.date for bar in bars])
        self.assertEqual("AAPL", bars[0].symbol)
        self.assertEqual("aktools_http", bars[0].source)
        self.assertEqual(12.5, bars[-1].current_price)
        self.assertEqual(12.0, bars[-1].close)
        self.assertEqual(11.5, bars[-1].open)
        self.assertEqual(13.5, bars[-1].high)
        self.assertEqual(10.5, bars[-1].low)
        self.assertEqual(11.0, bars[-1].prev_close)
        self.assertEqual(13.64, bars[-1].pct_change)
        self.assertEqual(1.5, bars[-1].change_amount)
        self.assertEqual(27.27, bars[-1].amplitude)
        self.assertEqual(27500.0, bars[-1].amount)
        self.assertEqual(1.6, bars[-1].volume_ratio)
        self.assertEqual(0.4, bars[-1].turnover_rate)
        self.assertIn("/api/public/stock_us_spot_em", requested_urls[0])
        self.assertIn("/api/public/stock_us_hist?", requested_urls[1])
        self.assertIn("symbol=105.AAPL", requested_urls[1])

    def test_aktools_provider_accepts_chinese_field_names(self):
        payload = {
            "data": [
                {
                    "日期": "20260508",
                    "开盘": 10,
                    "最高": 13,
                    "最低": 9,
                    "收盘": 12,
                    "昨收": 11,
                    "涨跌幅": 9.09,
                    "涨跌额": 1,
                    "振幅": 36.36,
                    "成交量": 2000,
                    "成交额": 24000,
                    "量比": 1.6,
                    "换手率": 0.4,
                },
            ]
        }

        class Response:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def read(self):
                return json.dumps(payload).encode("utf-8")

        with patch("urllib.request.urlopen", return_value=Response()):
            provider = AkToolsMarketDataProvider("http://127.0.0.1:8080/")
            bars = provider.daily_bars("600000", dt.date(2026, 5, 8), dt.date(2026, 5, 8))

        self.assertEqual("2026-05-08", bars[0].date)
        self.assertEqual(12.0, bars[0].close)
        self.assertEqual(2000.0, bars[0].volume)
        self.assertEqual(11.0, bars[0].prev_close)
        self.assertEqual(9.09, bars[0].pct_change)
        self.assertEqual(1.0, bars[0].change_amount)
        self.assertEqual(36.36, bars[0].amplitude)
        self.assertEqual(24000.0, bars[0].amount)
        self.assertEqual(1.6, bars[0].volume_ratio)
        self.assertEqual(0.4, bars[0].turnover_rate)


class TestRetry(unittest.TestCase):
    def test_retry_succeeds_on_first_attempt(self):
        result = _retry(lambda: 42, max_attempts=3, base_delay=0.01)
        self.assertEqual(result, 42)

    def test_retry_retries_on_retryable_error(self):
        attempts = [0]

        def flaky():
            attempts[0] += 1
            if attempts[0] < 3:
                raise ConnectionError("transient")
            return "ok"

        result = _retry(flaky, max_attempts=5, base_delay=0.01, max_delay=0.1, retryable=(ConnectionError,))
        self.assertEqual(result, "ok")
        self.assertEqual(attempts[0], 3)

    def test_retry_raises_non_retryable_immediately(self):
        with self.assertRaises(ValueError):
            _retry(lambda: (_ for _ in ()).throw(ValueError("bad")), max_attempts=3, base_delay=0.01,
                   retryable=(ConnectionError,))

    def test_retry_exhausts_attempts(self):
        def always_fail():
            raise ConnectionError("down")

        with self.assertRaises(ConnectionError):
            _retry(always_fail, max_attempts=2, base_delay=0.01, max_delay=0.1,
                   retryable=(ConnectionError,))


class TestRateLimiter(unittest.TestCase):
    def test_rate_limiter_no_delay_with_zero_interval(self):
        rl = _RateLimiter(min_interval=0.0, jitter=0.0)
        start = time.monotonic()
        rl.wait()
        rl.wait()
        elapsed = time.monotonic() - start
        self.assertLess(elapsed, 0.5)

    def test_rate_limiter_enforces_minimum_interval(self):
        rl = _RateLimiter(min_interval=0.05, jitter=0.0)
        start = time.monotonic()
        rl.wait()
        rl.wait()
        elapsed = time.monotonic() - start
        self.assertGreaterEqual(elapsed, 0.04)


class TestCircuitBreaker(unittest.TestCase):
    def test_closed_to_open_after_threshold(self):
        cb = _CircuitBreaker(failure_threshold=3, cooldown_seconds=60.0)
        self.assertTrue(cb.is_available("p1"))
        cb.record_failure("p1", "e1")
        cb.record_failure("p1", "e2")
        self.assertTrue(cb.is_available("p1"))
        cb.record_failure("p1", "e3")
        self.assertFalse(cb.is_available("p1"))

    def test_open_to_half_open_after_cooldown(self):
        cb = _CircuitBreaker(failure_threshold=2, cooldown_seconds=0.05)
        cb.record_failure("p1", "e1")
        cb.record_failure("p1", "e2")
        self.assertFalse(cb.is_available("p1"))
        time.sleep(0.1)
        self.assertTrue(cb.is_available("p1"))  # HALF_OPEN

    def test_half_open_to_closed_on_success(self):
        cb = _CircuitBreaker(failure_threshold=2, cooldown_seconds=0.05)
        cb.record_failure("p1", "e1")
        cb.record_failure("p1", "e2")
        time.sleep(0.1)
        self.assertTrue(cb.is_available("p1"))
        cb.record_success("p1")
        self.assertTrue(cb.is_available("p1"))
        status = cb.get_status()
        self.assertEqual(status["p1"], _CircuitBreaker.CLOSED)

    def test_half_open_to_open_on_failure(self):
        cb = _CircuitBreaker(failure_threshold=2, cooldown_seconds=0.05)
        cb.record_failure("p1", "e1")
        cb.record_failure("p1", "e2")
        time.sleep(0.1)
        self.assertTrue(cb.is_available("p1"))  # HALF_OPEN
        cb.record_failure("p1", "e3")
        self.assertFalse(cb.is_available("p1"))  # Back to OPEN

    def test_independent_providers(self):
        cb = _CircuitBreaker(failure_threshold=2, cooldown_seconds=60.0)
        cb.record_failure("a", "e1")
        cb.record_failure("a", "e2")
        self.assertFalse(cb.is_available("a"))
        self.assertTrue(cb.is_available("b"))

    def test_reset(self):
        cb = _CircuitBreaker(failure_threshold=2, cooldown_seconds=60.0)
        cb.record_failure("p1", "e1")
        cb.record_failure("p1", "e2")
        cb.reset("p1")
        self.assertTrue(cb.is_available("p1"))

    def test_get_status(self):
        cb = _CircuitBreaker(failure_threshold=2, cooldown_seconds=60.0)
        cb.record_failure("a", "e1")
        cb.record_failure("a", "e2")
        status = cb.get_status()
        self.assertEqual(status["a"], _CircuitBreaker.OPEN)


class TestCache(unittest.TestCase):
    def test_put_and_get(self):
        cache = _Cache(ttl=60.0, max_entries=10)
        bars = [DailyBar("MU", "2026-01-01", 10, 11, 9, 10, 1000, "test", {})]
        cache.put("MU", dt.date(2026, 1, 1), dt.date(2026, 1, 31), bars)
        result = cache.get("MU", dt.date(2026, 1, 1), dt.date(2026, 1, 31))
        self.assertEqual(result, bars)

    def test_cache_miss_different_key(self):
        cache = _Cache(ttl=60.0, max_entries=10)
        bars = [DailyBar("MU", "2026-01-01", 10, 11, 9, 10, 1000, "test", {})]
        cache.put("MU", dt.date(2026, 1, 1), dt.date(2026, 1, 31), bars)
        self.assertIsNone(cache.get("MU", dt.date(2026, 2, 1), dt.date(2026, 2, 28)))

    def test_cache_expiry(self):
        cache = _Cache(ttl=0.05, max_entries=10)
        bars = [DailyBar("MU", "2026-01-01", 10, 11, 9, 10, 1000, "test", {})]
        cache.put("MU", dt.date(2026, 1, 1), dt.date(2026, 1, 31), bars)
        self.assertIsNotNone(cache.get("MU", dt.date(2026, 1, 1), dt.date(2026, 1, 31)))
        time.sleep(0.1)
        self.assertIsNone(cache.get("MU", dt.date(2026, 1, 1), dt.date(2026, 1, 31)))

    def test_cache_max_entries_eviction(self):
        cache = _Cache(ttl=60.0, max_entries=2)
        cache.put("A", dt.date(2026, 1, 1), dt.date(2026, 1, 31), [])
        time.sleep(0.01)
        cache.put("B", dt.date(2026, 1, 1), dt.date(2026, 1, 31), [])
        time.sleep(0.01)
        cache.put("C", dt.date(2026, 1, 1), dt.date(2026, 1, 31), [])
        self.assertIsNone(cache.get("A", dt.date(2026, 1, 1), dt.date(2026, 1, 31)))
        self.assertIsNotNone(cache.get("B", dt.date(2026, 1, 1), dt.date(2026, 1, 31)))
        self.assertIsNotNone(cache.get("C", dt.date(2026, 1, 1), dt.date(2026, 1, 31)))

    def test_cache_disabled_with_zero_ttl(self):
        cache = _Cache(ttl=0.0, max_entries=10)
        cache.put("A", dt.date(2026, 1, 1), dt.date(2026, 1, 31), [])
        # TTL=0 means immediately expired
        self.assertIsNone(cache.get("A", dt.date(2026, 1, 1), dt.date(2026, 1, 31)))

    def test_cache_clear(self):
        cache = _Cache(ttl=60.0, max_entries=10)
        cache.put("A", dt.date(2026, 1, 1), dt.date(2026, 1, 31), [])
        cache.clear()
        self.assertIsNone(cache.get("A", dt.date(2026, 1, 1), dt.date(2026, 1, 31)))


class TestTradingDays(unittest.TestCase):
    def test_weekday_to_weekday(self):
        # Mon May 4 to Fri May 8 = 4 trading days (Tue, Wed, Thu, Fri)
        gap = _trading_days_between(dt.date(2026, 5, 4), dt.date(2026, 5, 8))
        self.assertEqual(gap, 4)

    def test_across_weekend(self):
        # Fri May 1 to Mon May 4 = 1 trading day (Mon)
        gap = _trading_days_between(dt.date(2026, 5, 1), dt.date(2026, 5, 4))
        self.assertEqual(gap, 1)

    def test_sunday_to_friday(self):
        # Sun May 3 to Fri May 8 = 5 trading days (Mon-Fri)
        gap = _trading_days_between(dt.date(2026, 5, 3), dt.date(2026, 5, 8))
        self.assertEqual(gap, 5)

    def test_same_day(self):
        gap = _trading_days_between(dt.date(2026, 5, 4), dt.date(2026, 5, 4))
        self.assertEqual(gap, 0)

    def test_consecutive_days(self):
        # Mon to Tue = 1 trading day
        gap = _trading_days_between(dt.date(2026, 5, 4), dt.date(2026, 5, 5))
        self.assertEqual(gap, 1)


class TestCompositeClientCache(unittest.TestCase):
    def test_cache_hit_returns_cache_source(self):
        class WorkingProvider:
            name = "test"
            def daily_bars(self, symbol, start, end):
                return [DailyBar(symbol, "2026-05-08", 10, 11, 9, 10, 1000, self.name, {})]

        client = CompositeMarketDataClient(
            [WorkingProvider()], timeout_seconds=0, cache_ttl=60.0
        )
        r1 = client.daily_bars("MU", dt.date(2026, 5, 1), dt.date(2026, 5, 8))
        self.assertEqual(r1.source, "test")
        r2 = client.daily_bars("MU", dt.date(2026, 5, 1), dt.date(2026, 5, 8))
        self.assertEqual(r2.source, "cache")

    def test_cache_disabled_by_default(self):
        call_count = [0]

        class CountingProvider:
            name = "test"
            def daily_bars(self, symbol, start, end):
                call_count[0] += 1
                return [DailyBar(symbol, "2026-05-08", 10, 11, 9, 10, 1000, self.name, {})]

        client = CompositeMarketDataClient([CountingProvider()], timeout_seconds=0)
        client.daily_bars("MU", dt.date(2026, 5, 1), dt.date(2026, 5, 8))
        client.daily_bars("MU", dt.date(2026, 5, 1), dt.date(2026, 5, 8))
        self.assertEqual(call_count[0], 2)


class TestCompositeClientCircuitBreaker(unittest.TestCase):
    def test_circuit_breaker_trips_and_recovers(self):
        call_count = [0]

        class FlakeyProvider:
            name = "flakey"
            def daily_bars(self, symbol, start, end):
                call_count[0] += 1
                if call_count[0] <= 2:
                    raise MarketDataError("transient")
                return [DailyBar(symbol, "2026-05-08", 10, 11, 9, 10, 1000, self.name, {})]

        class BackupProvider:
            name = "backup"
            def daily_bars(self, symbol, start, end):
                return [DailyBar(symbol, "2026-05-08", 20, 21, 19, 20, 2000, self.name, {})]

        client = CompositeMarketDataClient(
            [FlakeyProvider(), BackupProvider()],
            timeout_seconds=0,
            circuit_breaker_failure_threshold=2,
            circuit_breaker_cooldown_seconds=0.05,
        )
        r1 = client.daily_bars("X", dt.date(2026, 5, 1), dt.date(2026, 5, 8))
        self.assertEqual(r1.source, "backup")  # flakey fails, backup works
        r2 = client.daily_bars("X", dt.date(2026, 5, 1), dt.date(2026, 5, 8))
        self.assertEqual(r2.source, "backup")  # flakey still fails
        # Now flakey circuit is open
        status = client.get_circuit_status()
        self.assertEqual(status.get("flakey"), _CircuitBreaker.OPEN)

    def test_get_circuit_status(self):
        class FailProvider:
            name = "fail"
            def daily_bars(self, symbol, start, end):
                raise MarketDataError("fail")

        client = CompositeMarketDataClient([FailProvider()], timeout_seconds=0)
        client.daily_bars("X", dt.date(2026, 5, 1), dt.date(2026, 5, 8))
        status = client.get_circuit_status()
        self.assertIn("fail", status)


class TestCompositeClientParallelBatch(unittest.TestCase):
    def test_parallel_batch_returns_same_results(self):
        class TestProvider:
            name = "test"
            def daily_bars(self, symbol, start, end):
                return [DailyBar(symbol, "2026-05-08", 10, 11, 9, 10, 1000, self.name, {})]

        client = CompositeMarketDataClient([TestProvider()], timeout_seconds=0)
        symbols = ["MU", "NVDA", "AMD", "TSM"]
        seq = client.daily_bars_batch(symbols, dt.date(2026, 5, 1), dt.date(2026, 5, 8))
        par = client.daily_bars_batch(symbols, dt.date(2026, 5, 1), dt.date(2026, 5, 8), max_workers=2)
        self.assertEqual(set(seq.keys()), set(par.keys()))
        for s in symbols:
            self.assertEqual(seq[s].source, par[s].source)
            self.assertEqual(len(seq[s].bars), len(par[s].bars))

    def test_parallel_batch_deduplicates(self):
        class TestProvider:
            name = "test"
            def daily_bars(self, symbol, start, end):
                return [DailyBar(symbol, "2026-05-08", 10, 11, 9, 10, 1000, self.name, {})]

        client = CompositeMarketDataClient([TestProvider()], timeout_seconds=0)
        results = client.daily_bars_batch(["MU", "mu", "AMD"], dt.date(2026, 5, 1), dt.date(2026, 5, 8), max_workers=2)
        self.assertEqual(set(results.keys()), {"MU", "AMD"})


class TestCompositeClientValidation(unittest.TestCase):
    def test_cross_source_validation_consistent(self):
        class P1:
            name = "p1"
            def daily_bars(self, symbol, start, end):
                return [DailyBar(symbol, "2026-05-08", 100, 101, 99, 100, 1000, self.name, {})]

        class P2:
            name = "p2"
            def daily_bars(self, symbol, start, end):
                return [DailyBar(symbol, "2026-05-08", 100, 101, 99, 100, 1000, self.name, {})]

        client = CompositeMarketDataClient([P1(), P2()], timeout_seconds=0, cache_ttl=0, validation_threshold_pct=5.0)
        r = client.daily_bars("X", dt.date(2026, 5, 1), dt.date(2026, 5, 8), validate=True)
        self.assertTrue(r.ok)
        validation_warnings = [a for a in r.attempts if "cross-source validation" in (a.error or "")]
        self.assertEqual(len(validation_warnings), 0)

    def test_cross_source_validation_inconsistent(self):
        class P1:
            name = "p1"
            def daily_bars(self, symbol, start, end):
                return [DailyBar(symbol, "2026-05-08", 100, 101, 99, 100, 1000, self.name, {})]

        class P2:
            name = "p2"
            def daily_bars(self, symbol, start, end):
                return [DailyBar(symbol, "2026-05-08", 120, 121, 119, 120, 1000, self.name, {})]

        client = CompositeMarketDataClient([P1(), P2()], timeout_seconds=0, cache_ttl=0, validation_threshold_pct=5.0)
        r = client.daily_bars("X", dt.date(2026, 5, 1), dt.date(2026, 5, 8), validate=True)
        self.assertTrue(r.ok)
        self.assertEqual(r.source, "p1")
        validation_warnings = [a for a in r.attempts if "cross-source validation" in (a.error or "")]
        self.assertEqual(len(validation_warnings), 1)


class TestTimeoutErrorAlias(unittest.TestCase):
    def test_timeout_error_is_market_data_timeout_error(self):
        self.assertIs(TimeoutError, MarketDataTimeoutError)


class TestStalenessWithTradingDays(unittest.TestCase):
    def test_stale_provider_rejected_with_trading_day_gap(self):
        class StaleProvider:
            name = "stale"
            def daily_bars(self, symbol, start, end):
                # Latest bar May 3 (Sunday), end is May 8 (Friday)
                # Trading days between: 5 > 3, so stale
                return [
                    DailyBar(symbol, "2026-05-02", 10, 11, 9, 10, 1000, self.name, {}),
                    DailyBar(symbol, "2026-05-03", 12, 13, 11, 12, 2000, self.name, {}),
                ]

        class FreshProvider:
            name = "fresh"
            def daily_bars(self, symbol, start, end):
                return [DailyBar(symbol, "2026-05-08", 13, 14, 12, 13, 3000, self.name, {})]

        client = CompositeMarketDataClient(
            [StaleProvider(), FreshProvider()],
            timeout_seconds=0,
        )
        result = client.daily_bars("AMD", dt.date(2026, 5, 1), dt.date(2026, 5, 8))
        self.assertTrue(result.ok)
        self.assertEqual(result.source, "fresh")

    def test_fresh_provider_accepted_within_trading_day_threshold(self):
        class RecentProvider:
            name = "recent"
            def daily_bars(self, symbol, start, end):
                # Thursday May 7 to Friday May 8 = 1 trading day, within threshold of 3
                return [DailyBar(symbol, "2026-05-07", 12, 13, 11, 12, 2000, self.name, {})]

        client = CompositeMarketDataClient([RecentProvider()], timeout_seconds=0)
        result = client.daily_bars("AMD", dt.date(2026, 5, 1), dt.date(2026, 5, 8))
        self.assertTrue(result.ok)
        self.assertEqual(result.source, "recent")


if __name__ == "__main__":
    unittest.main()
