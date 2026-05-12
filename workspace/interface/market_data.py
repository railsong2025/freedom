#!/usr/bin/env python3
"""Public market data adapters for project-local research tools.

The adapters keep external data access explicit, time-bounded, and auditable.
They are intentionally small: workflow-specific modules decide how to use the
data, while this module standardizes source metadata and fallback behavior.
"""

from __future__ import annotations

import csv
import json
import os
import random
import signal
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, replace
from datetime import date, timedelta
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Protocol, TypeVar

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class MarketDataError(RuntimeError):
    """Raised when a market data provider cannot return usable data."""


class MarketDataTimeoutError(MarketDataError):
    """Raised when a provider exceeds its allowed runtime."""


# Backward-compatible alias: some code imports TimeoutError from this module.
TimeoutError = MarketDataTimeoutError


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DailyBar:
    symbol: str
    date: str
    open: float | None
    high: float | None
    low: float | None
    close: float | None
    volume: float | None
    source: str
    raw: dict[str, Any]
    current_price: float | None = None
    amount: float | None = None
    prev_close: float | None = None
    pct_change: float | None = None
    change_amount: float | None = None
    amplitude: float | None = None
    turnover_rate: float | None = None
    volume_ratio: float | None = None


@dataclass(frozen=True)
class SourceAttempt:
    source: str
    ok: bool
    rows: int = 0
    error: str | None = None


@dataclass(frozen=True)
class MarketDataResult:
    symbol: str
    bars: list[DailyBar]
    source: str | None
    attempts: list[SourceAttempt]

    @property
    def ok(self) -> bool:
        return bool(self.bars)


class MarketDataProvider(Protocol):
    name: str

    def daily_bars(self, symbol: str, start: date, end: date) -> list[DailyBar]:
        ...


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_T = TypeVar("_T")


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, str):
        text = value.strip().replace(",", "")
        if text in {"", "-", "--", "N/A", "NaN", "nan", "None", "null"}:
            return None
        if text.endswith("%"):
            text = text[:-1]
        value = text
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _value_by_alias(record: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for alias in aliases:
        if alias in record:
            return record[alias]
    return None


def _date_by_alias(record: dict[str, Any]) -> str:
    value = _value_by_alias(record, ("date", "日期", "Date", "datetime", "时间"))
    text = str(value or "").strip()
    if not text:
        return ""
    if len(text) >= 10 and text[4:5] == "-" and text[7:8] == "-":
        return text[:10]
    if len(text) >= 8 and text[:8].isdigit():
        return f"{text[:4]}-{text[4:6]}-{text[6:8]}"
    return text[:10]


def _daily_bar_from_record(symbol: str, record: dict[str, Any], source: str) -> DailyBar:
    ticker = symbol.upper()
    current_price = _to_float(_value_by_alias(record, ("current_price", "latest_price", "最新价", "现价", "price", "Price", "Last Price")))
    close = _to_float(_value_by_alias(record, ("close", "收盘", "收盘价", "Close")))
    if close is None:
        close = current_price
    return DailyBar(
        symbol=ticker,
        date=_date_by_alias(record),
        open=_to_float(_value_by_alias(record, ("open", "开盘", "今开", "开盘价", "Open"))),
        high=_to_float(_value_by_alias(record, ("high", "最高", "最高价", "High"))),
        low=_to_float(_value_by_alias(record, ("low", "最低", "最低价", "Low"))),
        close=close,
        volume=_to_float(_value_by_alias(record, ("volume", "成交量", "Volume"))),
        source=source,
        raw=dict(record),
        current_price=current_price,
        amount=_to_float(_value_by_alias(record, ("amount", "成交额", "成交金额", "成交额(元)", "Amount"))),
        prev_close=_to_float(_value_by_alias(record, ("prev_close", "previous_close", "pre_close", "昨收", "昨收价", "Previous Close"))),
        pct_change=_to_float(_value_by_alias(record, ("pct_change", "change_pct", "涨跌幅", "涨幅", "Change Percent"))),
        change_amount=_to_float(_value_by_alias(record, ("change_amount", "price_change", "涨跌额", "涨额", "Change"))),
        amplitude=_to_float(_value_by_alias(record, ("amplitude", "振幅", "Amplitude"))),
        turnover_rate=_to_float(_value_by_alias(record, ("turnover_rate", "换手率", "Turnover Rate"))),
        volume_ratio=_to_float(_value_by_alias(record, ("volume_ratio", "量比", "Volume Ratio"))),
    )


def _symbol_from_us_spot_record(record: dict[str, Any]) -> str | None:
    for key in ("ticker", "symbol", "股票代码"):
        value = record.get(key)
        if value:
            return str(value).upper()
    code = str(record.get("代码") or record.get("code") or "").strip()
    if not code:
        return None
    return code.rsplit(".", 1)[-1].upper()


def _find_us_spot_record(symbol: str, records: list[dict[str, Any]]) -> dict[str, Any] | None:
    ticker = symbol.upper()
    for record in records:
        if _symbol_from_us_spot_record(record) == ticker:
            return record
    return None


def _merge_latest_bar_with_snapshot(
    bars: list[DailyBar],
    snapshot: dict[str, Any] | None,
    source: str,
) -> list[DailyBar]:
    if not bars or not snapshot:
        return bars
    latest = bars[-1]
    snapshot_bar = _daily_bar_from_record(latest.symbol, snapshot, source)
    merged = replace(
        latest,
        current_price=snapshot_bar.current_price if snapshot_bar.current_price is not None else latest.current_price,
        open=snapshot_bar.open if snapshot_bar.open is not None else latest.open,
        high=snapshot_bar.high if snapshot_bar.high is not None else latest.high,
        low=snapshot_bar.low if snapshot_bar.low is not None else latest.low,
        close=latest.close if latest.close is not None else snapshot_bar.close,
        volume=snapshot_bar.volume if snapshot_bar.volume is not None else latest.volume,
        amount=snapshot_bar.amount if snapshot_bar.amount is not None else latest.amount,
        prev_close=snapshot_bar.prev_close if snapshot_bar.prev_close is not None else latest.prev_close,
        pct_change=snapshot_bar.pct_change if snapshot_bar.pct_change is not None else latest.pct_change,
        change_amount=snapshot_bar.change_amount if snapshot_bar.change_amount is not None else latest.change_amount,
        amplitude=snapshot_bar.amplitude if snapshot_bar.amplitude is not None else latest.amplitude,
        turnover_rate=snapshot_bar.turnover_rate if snapshot_bar.turnover_rate is not None else latest.turnover_rate,
        volume_ratio=snapshot_bar.volume_ratio if snapshot_bar.volume_ratio is not None else latest.volume_ratio,
        raw={**latest.raw, "_spot_snapshot": dict(snapshot)},
    )
    return [*bars[:-1], merged]


def _with_timeout(seconds: float, fn: Callable[[], list[DailyBar]]) -> list[DailyBar]:
    if seconds <= 0:
        return fn()

    import platform
    if platform.system() == "Windows":
        return fn()

    # SIGALRM is per-process and not thread-safe; skip in worker threads.
    if threading.current_thread() is not threading.main_thread():
        return fn()

    def _raise_timeout(signum: int, frame: object) -> None:
        raise MarketDataTimeoutError(f"market data provider timed out after {seconds:g}s")

    previous = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, _raise_timeout)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        return fn()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


def _retry(
    fn: Callable[[], _T],
    *,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retryable: tuple[type[Exception], ...] = (
        ConnectionError,
        TimeoutError,
        MarketDataTimeoutError,
    ),
) -> _T:
    """Retry *fn* with exponential backoff and jitter on retryable errors."""
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except retryable as exc:
            last_exc = exc
            if attempt < max_attempts - 1:
                delay = min(base_delay * 2 ** attempt, max_delay)
                jitter = random.uniform(0, base_delay)
                time.sleep(delay + jitter)
    raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# User-Agent rotation
# ---------------------------------------------------------------------------

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def _random_user_agent() -> str:
    return random.choice(_USER_AGENTS)


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------


class _RateLimiter:
    """Enforces a minimum interval plus random jitter between requests."""

    def __init__(self, min_interval: float = 0.5, jitter: float = 0.3) -> None:
        self._min_interval = min_interval
        self._jitter = jitter
        self._last_request_time: float = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        time.sleep(random.uniform(0, self._jitter))
        self._last_request_time = time.monotonic()


# ---------------------------------------------------------------------------
# Circuit breaker
# ---------------------------------------------------------------------------


class _CircuitBreaker:
    """Per-provider circuit breaker with CLOSED / OPEN / HALF_OPEN states.

    Adapted from daily_stock_analysis's CircuitBreaker but simplified for
    daily-bar fetching (no record_inconclusive).
    """

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

    def __init__(
        self,
        failure_threshold: int = 3,
        cooldown_seconds: float = 300.0,
        half_open_max_calls: int = 1,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._cooldown_seconds = cooldown_seconds
        self._half_open_max_calls = half_open_max_calls
        self._states: dict[str, dict[str, Any]] = {}
        self._lock = threading.Lock()

    def _get_state(self, name: str) -> dict[str, Any]:
        if name not in self._states:
            self._states[name] = {
                "state": self.CLOSED,
                "failures": 0,
                "last_failure_time": 0.0,
                "half_open_calls": 0,
            }
        return self._states[name]

    def is_available(self, name: str) -> bool:
        with self._lock:
            info = self._get_state(name)
            state = info["state"]

            if state == self.CLOSED:
                return True

            if state == self.OPEN:
                if time.monotonic() - info["last_failure_time"] >= self._cooldown_seconds:
                    info["state"] = self.HALF_OPEN
                    info["half_open_calls"] = 0
                    info["half_open_calls"] += 1
                    return True
                return False

            # HALF_OPEN
            if info["half_open_calls"] < self._half_open_max_calls:
                info["half_open_calls"] += 1
                return True
            if time.monotonic() - info["last_failure_time"] >= self._cooldown_seconds:
                info["half_open_calls"] = 1
                info["last_failure_time"] = time.monotonic()
                return True
            return False

    def record_success(self, name: str) -> None:
        with self._lock:
            info = self._get_state(name)
            info["state"] = self.CLOSED
            info["failures"] = 0
            info["half_open_calls"] = 0

    def record_failure(self, name: str, error: str | None = None) -> None:
        with self._lock:
            info = self._get_state(name)
            info["failures"] += 1
            info["last_failure_time"] = time.monotonic()

            if info["state"] == self.HALF_OPEN:
                info["state"] = self.OPEN
            elif info["failures"] >= self._failure_threshold:
                info["state"] = self.OPEN

    def get_status(self) -> dict[str, str]:
        with self._lock:
            return {name: info["state"] for name, info in self._states.items()}

    def reset(self, name: str | None = None) -> None:
        with self._lock:
            if name is None:
                self._states.clear()
            elif name in self._states:
                del self._states[name]


# ---------------------------------------------------------------------------
# In-memory cache with TTL
# ---------------------------------------------------------------------------


class _Cache:
    """Thread-safe in-memory cache for DailyBar results with TTL eviction."""

    def __init__(self, ttl: float = 300.0, max_entries: int = 256) -> None:
        self._ttl = ttl
        self._max_entries = max_entries
        self._store: dict[str, tuple[float, list[DailyBar]]] = {}
        self._lock = threading.Lock()

    def get(self, symbol: str, start: date, end: date) -> list[DailyBar] | None:
        key = f"{symbol}|{start.isoformat()}|{end.isoformat()}"
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            ts, bars = entry
            if time.monotonic() - ts > self._ttl:
                del self._store[key]
                return None
            return bars

    def put(self, symbol: str, start: date, end: date, bars: list[DailyBar]) -> None:
        key = f"{symbol}|{start.isoformat()}|{end.isoformat()}"
        with self._lock:
            self._store[key] = (time.monotonic(), bars)
            if len(self._store) > self._max_entries:
                oldest_key = min(self._store, key=lambda k: self._store[k][0])
                del self._store[oldest_key]

    def clear(self) -> None:
        with self._lock:
            self._store.clear()


# ---------------------------------------------------------------------------
# Trading-day helpers
# ---------------------------------------------------------------------------


def _trading_days_between(d1: date, d2: date) -> int:
    """Count weekdays between *d1* (exclusive) and *d2* (inclusive).

    Simple approximation that skips weekends.  A full US-market holiday
    calendar is out of scope for stdlib-only code.
    """
    count = 0
    current = d1 + timedelta(days=1)
    while current <= d2:
        if current.weekday() < 5:  # Mon=0 .. Fri=4
            count += 1
        current += timedelta(days=1)
    return count


# ---------------------------------------------------------------------------
# Providers
# ---------------------------------------------------------------------------


class AkShareMarketDataProvider:
    name = "akshare"

    def __init__(self, *, adjust: str = "", rate_limit_min_interval: float = 2.0) -> None:
        self.adjust = adjust
        self._rate_limiter = _RateLimiter(min_interval=rate_limit_min_interval, jitter=1.0)
        self._spot_records_cache: tuple[float, list[dict[str, Any]]] | None = None
        self._spot_lock = threading.Lock()

    def _us_spot_records(self, ak: Any) -> list[dict[str, Any]]:
        now = time.monotonic()
        with self._spot_lock:
            if self._spot_records_cache and now - self._spot_records_cache[0] < 60.0:
                return self._spot_records_cache[1]
        frame = ak.stock_us_spot_em()
        records = frame.to_dict("records") if frame is not None and not frame.empty else []
        records = [dict(item) for item in records if isinstance(item, dict)]
        with self._spot_lock:
            self._spot_records_cache = (now, records)
        return records

    def daily_bars(self, symbol: str, start: date, end: date) -> list[DailyBar]:
        try:
            import akshare as ak
        except ImportError as exc:
            raise MarketDataError("akshare is not installed") from exc

        self._rate_limiter.wait()

        def _fetch() -> list[DailyBar]:
            ticker = symbol.upper()
            spot_record: dict[str, Any] | None = None
            hist_symbol = ticker
            try:
                spot_record = _find_us_spot_record(ticker, self._us_spot_records(ak))
                if spot_record and spot_record.get("代码"):
                    hist_symbol = str(spot_record["代码"]).strip()
            except Exception:
                spot_record = None

            frame = None
            hist_error: Exception | None = None
            try:
                frame = ak.stock_us_hist(
                    symbol=hist_symbol,
                    period="daily",
                    start_date=start.strftime("%Y%m%d"),
                    end_date=end.strftime("%Y%m%d"),
                    adjust=self.adjust,
                )
            except Exception as exc:
                hist_error = exc

            if frame is None or frame.empty:
                try:
                    frame = ak.stock_us_daily(symbol=ticker, adjust=self.adjust)
                except Exception as exc:
                    raise MarketDataError(f"akshare failed for {ticker}: {hist_error or exc}") from exc

            if frame is None or frame.empty:
                raise MarketDataError(f"akshare returned no rows for {ticker}")

            rows: list[DailyBar] = []
            for record in frame.to_dict("records"):
                record_date = _date_by_alias(record)
                if not record_date:
                    continue
                if record_date < start.isoformat() or record_date > end.isoformat():
                    continue
                rows.append(_daily_bar_from_record(ticker, record, self.name))
            if not rows:
                raise MarketDataError(f"akshare returned no rows for {ticker} in requested range")
            rows = sorted(rows, key=lambda bar: bar.date)
            return _merge_latest_bar_with_snapshot(rows, spot_record, self.name)

        return _retry(_fetch, retryable=(ConnectionError, TimeoutError, MarketDataTimeoutError))


def _payload_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        raw_items = payload
    elif isinstance(payload, dict):
        for key in ("data", "result", "records", "rows", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                raw_items = value
                break
        else:
            raise MarketDataError("aktools_http response must be a JSON array or contain a data/result/records/rows/items list")
    else:
        raise MarketDataError("aktools_http response must be JSON")
    return [dict(item) for item in raw_items if isinstance(item, dict)]


class AkToolsMarketDataProvider:
    """AKTools HTTP provider for AKShare endpoints.

    AKTools exposes AKShare functions as HTTP endpoints such as:
    http://127.0.0.1:8080/api/public/stock_us_daily?symbol=AAPL&adjust=
    """

    name = "aktools_http"

    def __init__(
        self,
        base_url: str,
        *,
        endpoint: str = "stock_us_daily",
        hist_endpoint: str = "stock_us_hist",
        spot_endpoint: str = "stock_us_spot_em",
        adjust: str = "",
        rate_limit_min_interval: float = 0.2,
    ) -> None:
        base = base_url.rstrip("/")
        self.public_api_url = base if base.endswith("/api/public") else f"{base}/api/public"
        self.endpoint = endpoint.strip("/")
        self.hist_endpoint = hist_endpoint.strip("/")
        self.spot_endpoint = spot_endpoint.strip("/")
        self.adjust = adjust
        self._rate_limiter = _RateLimiter(min_interval=rate_limit_min_interval, jitter=0.1)
        self._spot_records_cache: tuple[float, list[dict[str, Any]]] | None = None
        self._spot_lock = threading.Lock()

    def _endpoint_payload(self, endpoint: str, params: dict[str, Any]) -> Any:
        encoded_params = urllib.parse.urlencode(params)
        suffix = f"?{encoded_params}" if encoded_params else ""
        url = f"{self.public_api_url}/{urllib.parse.quote(endpoint)}{suffix}"
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": _random_user_agent(),
                "Accept": "application/json,text/plain,*/*",
            },
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    def _us_spot_records(self) -> list[dict[str, Any]]:
        now = time.monotonic()
        with self._spot_lock:
            if self._spot_records_cache and now - self._spot_records_cache[0] < 60.0:
                return self._spot_records_cache[1]
        records = _payload_records(self._endpoint_payload(self.spot_endpoint, {}))
        with self._spot_lock:
            self._spot_records_cache = (now, records)
        return records

    def daily_bars(self, symbol: str, start: date, end: date) -> list[DailyBar]:
        ticker = symbol.upper()
        self._rate_limiter.wait()

        def _fetch() -> list[DailyBar]:
            spot_record: dict[str, Any] | None = None
            hist_symbol = ticker
            try:
                spot_record = _find_us_spot_record(ticker, self._us_spot_records())
                if spot_record and spot_record.get("代码"):
                    hist_symbol = str(spot_record["代码"]).strip()
            except Exception:
                spot_record = None

            payload = None
            hist_error: Exception | None = None
            try:
                payload = self._endpoint_payload(
                    self.hist_endpoint,
                    {
                        "symbol": hist_symbol,
                        "period": "daily",
                        "start_date": start.strftime("%Y%m%d"),
                        "end_date": end.strftime("%Y%m%d"),
                        "adjust": self.adjust,
                    },
                )
            except Exception as exc:
                hist_error = exc

            if payload is None:
                try:
                    payload = self._endpoint_payload(self.endpoint, {"symbol": ticker, "adjust": self.adjust})
                except Exception as exc:
                    raise MarketDataError(f"aktools_http failed for {ticker}: {hist_error or exc}") from exc

            def _rows_from_payload(raw_payload: Any) -> list[DailyBar]:
                parsed_rows: list[DailyBar] = []
                for record in _payload_records(raw_payload):
                    record_date = _date_by_alias(record)
                    if not record_date:
                        continue
                    if record_date < start.isoformat() or record_date > end.isoformat():
                        continue
                    parsed_rows.append(_daily_bar_from_record(ticker, record, self.name))
                return parsed_rows

            rows = _rows_from_payload(payload)
            if not rows:
                try:
                    fallback_payload = self._endpoint_payload(self.endpoint, {"symbol": ticker, "adjust": self.adjust})
                    rows = _rows_from_payload(fallback_payload)
                except Exception as exc:
                    if hist_error is not None:
                        raise MarketDataError(f"aktools_http failed for {ticker}: {hist_error}") from exc
            if not rows:
                raise MarketDataError(f"aktools_http returned no rows for {ticker} in requested range")
            rows = sorted(rows, key=lambda bar: bar.date)
            return _merge_latest_bar_with_snapshot(rows, spot_record, self.name)

        return _retry(_fetch, retryable=(ConnectionError, TimeoutError, MarketDataTimeoutError))


class HttpApiMarketDataProvider:
    """Generic JSON HTTP provider for user-supplied quote services.

    The URL template may include {symbol}, {start}, and {end}. The response can
    either be a list of bar objects or an object with a "bars" list.
    """

    name = "http_api"

    def __init__(self, url_template: str, *, rate_limit_min_interval: float = 0.2) -> None:
        self.url_template = url_template
        self._rate_limiter = _RateLimiter(min_interval=rate_limit_min_interval, jitter=0.1)

    def daily_bars(self, symbol: str, start: date, end: date) -> list[DailyBar]:
        self._rate_limiter.wait()

        def _fetch() -> list[DailyBar]:
            url = self.url_template.format(
                symbol=urllib.parse.quote(symbol.upper()),
                start=start.isoformat(),
                end=end.isoformat(),
            )
            request = urllib.request.Request(
                url,
                headers={"User-Agent": _random_user_agent()},
            )
            with urllib.request.urlopen(request, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
            data = payload.get("bars", payload) if isinstance(payload, dict) else payload
            if not isinstance(data, list):
                raise MarketDataError("http_api response must be a list or contain a bars list")

            bars = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                record_date = _date_by_alias(item)
                if not record_date or not (start.isoformat() <= record_date <= end.isoformat()):
                    continue
                bars.append(_daily_bar_from_record(symbol, item, self.name))
            if not bars:
                raise MarketDataError(f"http_api returned no rows for {symbol} in requested range")
            return sorted(bars, key=lambda bar: bar.date)

        return _retry(_fetch, retryable=(ConnectionError, TimeoutError, MarketDataTimeoutError))


class YFinanceMarketDataProvider:
    """Yahoo Finance historical bars via optional yfinance dependency."""

    name = "yfinance_last_resort"

    def daily_bars(self, symbol: str, start: date, end: date) -> list[DailyBar]:

        def _fetch() -> list[DailyBar]:
            try:
                import pandas as pd
                import yfinance as yf
            except ImportError as exc:
                raise MarketDataError("yfinance is not installed") from exc

            ticker = symbol.upper()
            try:
                download_kwargs: dict[str, Any] = dict(
                    tickers=ticker,
                    start=start.isoformat(),
                    end=(end + timedelta(days=1)).isoformat(),
                    progress=False,
                    auto_adjust=False,
                )
                try:
                    yf_version = tuple(int(x) for x in yf.__version__.split(".")[:3])
                except (AttributeError, ValueError):
                    yf_version = (0, 0, 0)
                if yf_version >= (0, 2, 31):
                    download_kwargs["multi_level_index"] = True
                frame = yf.download(**download_kwargs)
            except Exception as exc:
                raise MarketDataError(f"yfinance failed for {ticker}: {exc}") from exc

            if frame is None or frame.empty:
                raise MarketDataError(f"yfinance returned no rows for {ticker}")

            if isinstance(frame.columns, pd.MultiIndex):
                if ticker in frame.columns.get_level_values(-1):
                    frame = frame.xs(ticker, axis=1, level=-1, drop_level=True)
                else:
                    frame.columns = [
                        "_".join(str(part) for part in col if part)
                        for col in frame.columns.to_flat_index()
                    ]

            rows: list[DailyBar] = []
            for record in frame.reset_index().to_dict("records"):
                record_date = str(record.get("Date") or record.get("date") or "")[:10]
                if record_date < start.isoformat() or record_date > end.isoformat():
                    continue
                rows.append(_daily_bar_from_record(ticker, dict(record), self.name))
            if not rows:
                raise MarketDataError(f"yfinance returned no rows for {ticker} in requested range")
            return rows

        return _retry(_fetch, retryable=(ConnectionError, TimeoutError, MarketDataTimeoutError))


class StooqMarketDataProvider:
    """No-key Stooq daily CSV fallback for US stocks and ETFs."""

    name = "stooq"

    def __init__(self, *, rate_limit_min_interval: float = 1.0) -> None:
        self._rate_limiter = _RateLimiter(min_interval=rate_limit_min_interval, jitter=0.5)

    def daily_bars(self, symbol: str, start: date, end: date) -> list[DailyBar]:
        self._rate_limiter.wait()

        def _fetch() -> list[DailyBar]:
            ticker = symbol.upper()
            stooq_symbol = f"{ticker.lower()}.us"
            url = f"https://stooq.com/q/d/l/?s={urllib.parse.quote(stooq_symbol)}&i=d"
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": _random_user_agent(),
                    "Accept": "text/plain,text/csv,*/*",
                },
            )
            try:
                with urllib.request.urlopen(request, timeout=10) as response:
                    payload = response.read().decode("utf-8", "ignore").strip()
            except Exception as exc:
                raise MarketDataError(f"stooq failed for {ticker}: {exc}") from exc

            if not payload or payload.upper().startswith("NO DATA"):
                raise MarketDataError(f"stooq returned no rows for {ticker}")

            rows: list[DailyBar] = []
            reader = csv.DictReader(StringIO(payload))
            for record in reader:
                record_date = str(record.get("Date") or record.get("date") or "")
                if not record_date:
                    continue
                if record_date < start.isoformat() or record_date > end.isoformat():
                    continue
                rows.append(_daily_bar_from_record(ticker, dict(record), self.name))
            if not rows:
                raise MarketDataError(f"stooq returned no rows for {ticker} in requested range")
            return rows

        return _retry(_fetch, retryable=(ConnectionError, TimeoutError, MarketDataTimeoutError))


class CsvMarketDataProvider:
    name = "csv_cache"

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    def daily_bars(self, symbol: str, start: date, end: date) -> list[DailyBar]:
        path = self.directory / f"{symbol.upper()}.csv"
        if not path.exists():
            raise MarketDataError(f"csv cache missing {path}")

        rows: list[DailyBar] = []
        with path.open("r", encoding="utf-8", newline="") as handle:
            for record in csv.DictReader(handle):
                record_date = str(record.get("date", ""))
                if not record_date:
                    continue
                if record_date < start.isoformat() or record_date > end.isoformat():
                    continue
                rows.append(_daily_bar_from_record(symbol, record, self.name))
        if not rows:
            raise MarketDataError(f"csv cache returned no rows for {symbol}")
        return rows


# ---------------------------------------------------------------------------
# Composite client
# ---------------------------------------------------------------------------


class CompositeMarketDataClient:
    def __init__(
        self,
        providers: list[MarketDataProvider],
        *,
        timeout_seconds: float = 8.0,
        provider_failure_threshold: int = 3,
        circuit_breaker_failure_threshold: int | None = None,
        circuit_breaker_cooldown_seconds: float = 300.0,
        staleness_trading_days: int = 3,
        cache_ttl: float = 0.0,
        cache_max_entries: int = 256,
        validation_threshold_pct: float = 5.0,
    ) -> None:
        self.providers = providers
        self.timeout_seconds = timeout_seconds

        # Backward compat: provider_failure_threshold maps to circuit breaker
        cb_threshold = (
            circuit_breaker_failure_threshold
            if circuit_breaker_failure_threshold is not None
            else provider_failure_threshold
        )
        self._circuit_breaker = _CircuitBreaker(
            failure_threshold=cb_threshold,
            cooldown_seconds=circuit_breaker_cooldown_seconds,
        )
        self.staleness_trading_days = staleness_trading_days
        self._cache = _Cache(ttl=cache_ttl, max_entries=cache_max_entries) if cache_ttl > 0 else None
        self.validation_threshold_pct = validation_threshold_pct

    # -- observability -------------------------------------------------------

    def get_circuit_status(self) -> dict[str, str]:
        """Return current circuit-breaker state per provider."""
        return self._circuit_breaker.get_status()

    # -- core fetch ----------------------------------------------------------

    def daily_bars(
        self,
        symbol: str,
        start: date,
        end: date,
        *,
        validate: bool = False,
    ) -> MarketDataResult:
        # Check cache first
        if self._cache is not None:
            cached = self._cache.get(symbol, start, end)
            if cached is not None:
                return MarketDataResult(symbol.upper(), cached, "cache", [])

        attempts: list[SourceAttempt] = []
        primary_result: MarketDataResult | None = None

        for provider in self.providers:
            if not self._circuit_breaker.is_available(provider.name):
                attempts.append(
                    SourceAttempt(
                        provider.name,
                        False,
                        error="provider circuit-open, cooling down",
                    )
                )
                continue
            try:
                bars = _with_timeout(
                    self.timeout_seconds,
                    lambda provider=provider: provider.daily_bars(symbol, start, end),
                )
            except Exception as exc:
                self._circuit_breaker.record_failure(provider.name, str(exc))
                attempts.append(SourceAttempt(provider.name, False, error=str(exc)))
                continue
            bars = sorted(bars, key=lambda bar: bar.date)
            latest_date = max((bar.date[:10] for bar in bars if bar.date), default="")
            # Trading-day-aware staleness check
            if latest_date:
                try:
                    latest = date.fromisoformat(latest_date)
                except ValueError:
                    latest = end
                trading_gap = _trading_days_between(latest, end)
                if trading_gap > self.staleness_trading_days:
                    self._circuit_breaker.record_failure(
                        provider.name,
                        f"stale latest date {latest_date} is more than {self.staleness_trading_days} trading days before {end.isoformat()}",
                    )
                    attempts.append(
                        SourceAttempt(
                            provider.name,
                            False,
                            rows=len(bars),
                            error=f"stale latest date {latest_date} is more than {self.staleness_trading_days} trading days before {end.isoformat()}",
                        )
                    )
                    continue
            self._circuit_breaker.record_success(provider.name)
            attempts.append(SourceAttempt(provider.name, True, rows=len(bars)))

            result = MarketDataResult(symbol.upper(), bars, provider.name, attempts)
            primary_result = result

            # Cache the successful result
            if self._cache is not None:
                self._cache.put(symbol, start, end, bars)

            # Cross-source validation (opt-in)
            if validate:
                self._validate_against_secondary(
                    symbol, start, end, provider.name, bars, attempts
                )

            return result

        return MarketDataResult(symbol.upper(), [], None, attempts)

    def _validate_against_secondary(
        self,
        symbol: str,
        start: date,
        end: date,
        primary_name: str,
        primary_bars: list[DailyBar],
        attempts: list[SourceAttempt],
    ) -> None:
        """Try one more provider and compare the latest close price."""
        if not primary_bars:
            return
        primary_close = primary_bars[-1].close
        if primary_close is None or primary_close <= 0:
            return

        for provider in self.providers:
            if provider.name == primary_name:
                continue
            if not self._circuit_breaker.is_available(provider.name):
                continue
            try:
                secondary_bars = _with_timeout(
                    self.timeout_seconds,
                    lambda p=provider: p.daily_bars(symbol, start, end),
                )
                if not secondary_bars:
                    continue
                secondary_close = secondary_bars[-1].close
                if secondary_close is None or secondary_close <= 0:
                    continue
                pct_diff = abs(primary_close - secondary_close) / primary_close * 100.0
                if pct_diff > self.validation_threshold_pct:
                    attempts.append(
                        SourceAttempt(
                            provider.name,
                            True,
                            rows=len(secondary_bars),
                            error=f"cross-source validation: close price {primary_close} vs {secondary_close} differs by {pct_diff:.1f}% (threshold {self.validation_threshold_pct}%)",
                        )
                    )
                return  # Only check one secondary source
            except Exception:
                continue  # Best-effort validation

    def daily_bars_batch(
        self,
        symbols: list[str],
        start: date,
        end: date,
        *,
        max_workers: int | None = None,
    ) -> dict[str, MarketDataResult]:
        results: dict[str, MarketDataResult] = {}

        if max_workers is not None and max_workers >= 1:
            # Parallel batch fetching
            normalized_map: dict[str, str] = {}
            for symbol in symbols:
                normalized = symbol.upper()
                if normalized not in normalized_map:
                    normalized_map[normalized] = symbol

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.daily_bars, norm, start, end): norm
                    for norm in normalized_map
                }
                for future in as_completed(futures):
                    norm = futures[future]
                    try:
                        results[norm] = future.result()
                    except Exception as exc:
                        results[norm] = MarketDataResult(
                            norm, [], None, [SourceAttempt("batch_worker", False, error=str(exc))]
                        )
        else:
            # Sequential (backward-compatible default)
            for symbol in symbols:
                normalized = symbol.upper()
                if normalized in results:
                    continue
                results[normalized] = self.daily_bars(normalized, start, end)

        return results


# ---------------------------------------------------------------------------
# Factory and utility functions
# ---------------------------------------------------------------------------


def default_client(
    *,
    cache_dir: Path | None = None,
    aktools_api_url: str | None = None,
    http_api_url: str | None = None,
    timeout_seconds: float = 8.0,
    disable_yfinance: bool | None = None,
    cache_ttl: float = 300.0,
    batch_max_workers: int | None = None,
) -> CompositeMarketDataClient:
    providers: list[MarketDataProvider] = [AkShareMarketDataProvider()]
    aktools_url = aktools_api_url or os.getenv("FREEDOM_AKTOOLS_API_URL") or os.getenv("AKTOOLS_API_URL")
    if aktools_url:
        providers.append(AkToolsMarketDataProvider(aktools_url))
    api_url = http_api_url or os.getenv("FREEDOM_MARKET_DATA_API_URL")
    if api_url:
        providers.append(HttpApiMarketDataProvider(api_url))
    providers.append(StooqMarketDataProvider())
    if cache_dir:
        providers.append(CsvMarketDataProvider(cache_dir))
    if disable_yfinance is None:
        disable_yfinance = os.getenv("FREEDOM_DISABLE_YFINANCE", "").strip().lower() in {
            "1",
            "true",
            "yes",
        }
    if not disable_yfinance:
        providers.append(YFinanceMarketDataProvider())
    return CompositeMarketDataClient(
        providers,
        timeout_seconds=timeout_seconds,
        cache_ttl=cache_ttl,
    )


def five_day_return(result: MarketDataResult) -> float | None:
    if len(result.bars) < 2:
        return None
    first = result.bars[0].close
    last = result.bars[-1].close
    if first in (None, 0) or last is None:
        return None
    return (last / first - 1.0) * 100.0


def batch_summary(results: dict[str, MarketDataResult]) -> list[dict[str, Any]]:
    summary: list[dict[str, Any]] = []
    for symbol, result in results.items():
        latest = result.bars[-1] if result.bars else None
        previous = result.bars[-2] if len(result.bars) >= 2 else None
        current_price = None
        if latest:
            current_price = latest.current_price if latest.current_price is not None else latest.close
        previous_close = latest.prev_close if latest and latest.prev_close is not None else (previous.close if previous else None)
        change_amount = latest.change_amount if latest and latest.change_amount is not None else None
        if change_amount is None and latest and latest.close is not None and previous_close not in (None, 0):
            change_amount = latest.close - previous_close
        pct_change = latest.pct_change if latest and latest.pct_change is not None else None
        if pct_change is None and change_amount is not None and previous_close not in (None, 0):
            pct_change = change_amount / previous_close * 100.0
        amplitude = latest.amplitude if latest and latest.amplitude is not None else None
        if amplitude is None and latest and latest.high is not None and latest.low is not None and previous_close not in (None, 0):
            amplitude = (latest.high - latest.low) / previous_close * 100.0
        amount = latest.amount if latest and latest.amount is not None else None
        amount_is_estimated = False
        if amount is None and latest and current_price is not None and latest.volume is not None:
            amount = current_price * latest.volume
            amount_is_estimated = True
        summary.append(
            {
                "symbol": symbol,
                "ok": result.ok,
                "source": result.source,
                "rows": len(result.bars),
                "start_date": result.bars[0].date if result.bars else None,
                "end_date": result.bars[-1].date if result.bars else None,
                "current_price": current_price,
                "open": latest.open if latest else None,
                "high": latest.high if latest else None,
                "low": latest.low if latest else None,
                "close": latest.close if latest else None,
                "latest_close": latest.close if latest else None,
                "previous_close": previous_close,
                "change_amount": round(change_amount, 4) if change_amount is not None else None,
                "pct_change": round(pct_change, 4) if pct_change is not None else None,
                "amplitude": round(amplitude, 4) if amplitude is not None else None,
                "volume": latest.volume if latest else None,
                "latest_volume": latest.volume if latest else None,
                "amount": round(amount, 2) if amount is not None else None,
                "amount_is_estimated": amount_is_estimated,
                "volume_ratio": latest.volume_ratio if latest else None,
                "turnover_rate": latest.turnover_rate if latest else None,
                "market_source": latest.source if latest else result.source,
                "period_return_pct": five_day_return(result),
                "attempts": [attempt.__dict__ for attempt in result.attempts],
            }
        )
    return summary


def write_csv_cache(results: dict[str, MarketDataResult], directory: Path) -> dict[str, Any]:
    """Persist successful bar results as CSV files plus a manifest."""
    directory.mkdir(parents=True, exist_ok=True)
    written_files: list[str] = []
    for symbol, result in sorted(results.items()):
        if not result.ok:
            continue
        path = directory / f"{symbol.upper()}.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "date",
                    "open",
                    "high",
                    "low",
                    "close",
                    "current_price",
                    "prev_close",
                    "pct_change",
                    "change_amount",
                    "amplitude",
                    "volume",
                    "amount",
                    "volume_ratio",
                    "turnover_rate",
                    "source",
                ],
            )
            writer.writeheader()
            for bar in result.bars:
                writer.writerow(
                    {
                        "date": bar.date,
                        "open": bar.open,
                        "high": bar.high,
                        "low": bar.low,
                        "close": bar.close,
                        "current_price": bar.current_price,
                        "prev_close": bar.prev_close,
                        "pct_change": bar.pct_change,
                        "change_amount": bar.change_amount,
                        "amplitude": bar.amplitude,
                        "volume": bar.volume,
                        "amount": bar.amount,
                        "volume_ratio": bar.volume_ratio,
                        "turnover_rate": bar.turnover_rate,
                        "source": bar.source,
                    }
                )
        written_files.append(str(path))

    manifest = {
        "cache_dir": str(directory),
        "written_files": written_files,
        "summary": batch_summary(results),
    }
    (directory / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return manifest
