"""Technical indicator computations for the Zeus Intelligence Division.

All functions consume ``list[DailyBar]`` from
``workspace.interface.market_data`` and return plain values
or ``None`` when data is insufficient. This matches the graceful-None pattern
of ``five_day_return()`` in market_data.py.
"""

from __future__ import annotations

import math
from typing import Any

# Local import of DailyBar; use late import to avoid circular deps at module level.
from dataclasses import dataclass

from interface.constants import (
    INDEX_PROXY_ETF_TO_BENCHMARK,
    MARKET_INDEX_BENCHMARKS,
    NON_TRADABLE_INDEX_SYMBOLS,
)


def _bars_close(bars: list[Any], min_count: int) -> list[float]:
    """Extract non-None close prices from bars, return empty if insufficient."""
    closes = [b.close for b in bars[-min_count:] if b.close is not None]
    return closes if len(closes) >= min_count else []


def _bars_hlc(bars: list[Any], min_count: int) -> list[tuple[float, float, float]]:
    """Extract (high, low, close) tuples from bars with all fields present."""
    result = []
    for b in bars[-min_count:]:
        if b.high is not None and b.low is not None and b.close is not None:
            result.append((b.high, b.low, b.close))
    return result if len(result) >= min_count else []


def moving_average(bars: list[Any], period: int, field: str = "close") -> float | None:
    """Simple moving average over the last ``period`` bars."""
    if period <= 0 or len(bars) < period:
        return None
    values = [getattr(b, field, None) for b in bars[-period:]]
    if any(v is None for v in values):
        return None
    return sum(values) / period


def exponential_moving_average(bars: list[Any], period: int, field: str = "close") -> float | None:
    """Exponential moving average over the last ``period`` bars."""
    if period <= 0 or len(bars) < period:
        return None
    values = [getattr(b, field, None) for b in bars]
    if any(v is None for v in values[:period]):
        return None
    k = 2.0 / (period + 1)
    ema = sum(values[:period]) / period
    for val in values[period:]:
        if val is None:
            return None
        ema = val * k + ema * (1 - k)
    return ema


def atr(bars: list[Any], period: int = 14) -> float | None:
    """Average True Range using Wilder smoothing.

    TR = max(H - L, |H - prev_close|, |L - prev_close|).
    """
    if period <= 0 or len(bars) < period + 1:
        return None
    true_ranges: list[float] = []
    for i in range(1, len(bars)):
        h, l, c_prev = bars[i].high, bars[i].low, bars[i - 1].close
        if h is None or l is None or c_prev is None:
            continue
        tr = max(h - l, abs(h - c_prev), abs(l - c_prev))
        true_ranges.append(tr)
    if len(true_ranges) < period:
        return None
    # Wilder smoothing: first ATR = SMA of first `period` TRs
    atr_val = sum(true_ranges[:period]) / period
    for tr in true_ranges[period:]:
        atr_val = (atr_val * (period - 1) + tr) / period
    return atr_val


def rsi(bars: list[Any], period: int = 14) -> float | None:
    """Relative Strength Index using Wilder smoothing."""
    if period <= 0 or len(bars) < period + 1:
        return None
    changes: list[float] = []
    for i in range(1, len(bars)):
        if bars[i].close is None or bars[i - 1].close is None:
            continue
        changes.append(bars[i].close - bars[i - 1].close)
    if len(changes) < period:
        return None
    gains = [c if c > 0 else 0.0 for c in changes[:period]]
    losses = [-c if c < 0 else 0.0 for c in changes[:period]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    for change in changes[period:]:
        gain = change if change > 0 else 0.0
        loss = -change if change < 0 else 0.0
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
    if avg_gain == 0 and avg_loss == 0:
        return 50.0
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def vwap_approximation(bars: list[Any]) -> float | None:
    """VWAP approximation from daily bars.

    True VWAP requires intraday data; this computes cumulative (close * volume)
    / total volume as a daily proxy.
    """
    total_pv = 0.0
    total_vol = 0.0
    for b in bars:
        if b.close is None or b.volume is None or b.volume <= 0:
            continue
        total_pv += b.close * b.volume
        total_vol += b.volume
    return total_pv / total_vol if total_vol > 0 else None


def volume_ratio(bars: list[Any], period: int = 20) -> float | None:
    """Latest volume / average volume over ``period`` bars."""
    if period <= 0 or len(bars) < period:
        return None
    recent = bars[-period:]
    volumes = [b.volume for b in recent if b.volume is not None]
    if len(volumes) < period:
        return None
    latest_vol = volumes[-1]
    avg_vol = sum(volumes) / len(volumes)
    return latest_vol / avg_vol if avg_vol > 0 else None


def volatility(bars: list[Any], period: int = 20) -> float | None:
    """Annualized volatility from close-to-close daily returns."""
    if period <= 1 or len(bars) < period + 1:
        return None
    returns: list[float] = []
    recent = bars[-(period + 1):]
    for previous, current in zip(recent, recent[1:]):
        if previous.close in (None, 0) or current.close is None:
            return None
        returns.append(current.close / previous.close - 1.0)
    if len(returns) < period:
        return None
    mean_return = sum(returns) / len(returns)
    variance = sum((item - mean_return) ** 2 for item in returns) / len(returns)
    return math.sqrt(variance) * math.sqrt(252) * 100.0


def _round(value: float | None, digits: int = 4) -> float | None:
    return round(value, digits) if value is not None else None


def _raw_value(raw: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    for alias in aliases:
        if alias in raw and raw[alias] not in (None, "", "None", "null"):
            return raw[alias]
    return None


def _latest_market_tape(bars: list[Any]) -> dict[str, Any]:
    if not bars:
        return {
            "ticker": None,
            "name": None,
            "current_price": None,
            "open": None,
            "high": None,
            "low": None,
            "close": None,
            "previous_close": None,
            "change_amount": None,
            "pct_change": None,
            "amplitude": None,
            "volume": None,
            "amount": None,
            "amount_is_estimated": False,
            "volume_ratio": None,
            "volume_ratio_source": None,
            "turnover_rate": None,
            "market_source": None,
            "quote_time": None,
            "trade_status": None,
            "field_source_map": {},
            "field_timestamp_map": {},
            "estimated_fields": [],
        }

    latest = bars[-1]
    raw = getattr(latest, "raw", {}) or {}
    previous = bars[-2] if len(bars) >= 2 else None
    close = getattr(latest, "close", None)
    current_price = getattr(latest, "current_price", None)
    if current_price is None:
        current_price = close
    high = getattr(latest, "high", None)
    low = getattr(latest, "low", None)
    volume = getattr(latest, "volume", None)
    previous_close = getattr(latest, "prev_close", None)
    if previous_close is None and previous is not None:
        previous_close = getattr(previous, "close", None)

    change_amount = getattr(latest, "change_amount", None)
    if change_amount is None and close is not None and previous_close not in (None, 0):
        change_amount = close - previous_close

    pct_change = getattr(latest, "pct_change", None)
    if pct_change is None and change_amount is not None and previous_close not in (None, 0):
        pct_change = change_amount / previous_close * 100.0

    amplitude = getattr(latest, "amplitude", None)
    if amplitude is None and high is not None and low is not None and previous_close not in (None, 0):
        amplitude = (high - low) / previous_close * 100.0

    amount = getattr(latest, "amount", None)
    amount_is_estimated = False
    estimated_fields: list[str] = []
    if amount is None and current_price is not None and volume is not None:
        amount = current_price * volume
        amount_is_estimated = True
        estimated_fields.append("amount")

    direct_volume_ratio = getattr(latest, "volume_ratio", None)
    computed_volume_ratio = volume_ratio(bars, 20)
    resolved_volume_ratio = direct_volume_ratio if direct_volume_ratio is not None else computed_volume_ratio
    volume_ratio_source = (
        "source_field"
        if direct_volume_ratio is not None
        else ("computed_latest_volume_vs_20bar_average" if computed_volume_ratio is not None else None)
    )
    if direct_volume_ratio is None and computed_volume_ratio is not None:
        estimated_fields.append("volume_ratio")

    market_source = getattr(latest, "source", None)
    quote_time = _raw_value(raw, ("update_time", "quote_time", "datetime", "date", "Date", "时间")) or getattr(latest, "date", None)
    field_source_map = {
        "current_price": market_source,
        "close": market_source,
        "previous_close": market_source if getattr(latest, "prev_close", None) is not None else "previous_bar_close",
        "open": market_source,
        "high": market_source,
        "low": market_source,
        "pct_change": market_source if getattr(latest, "pct_change", None) is not None else "computed_from_close_and_previous_close",
        "change_amount": market_source if getattr(latest, "change_amount", None) is not None else "computed_from_close_and_previous_close",
        "amplitude": market_source if getattr(latest, "amplitude", None) is not None else "computed_from_high_low_previous_close",
        "volume": market_source,
        "amount": market_source if not amount_is_estimated else "computed_current_price_times_volume",
        "volume_ratio": market_source if direct_volume_ratio is not None else volume_ratio_source,
        "turnover_rate": market_source,
        "market_source": "provider_metadata",
        "quote_time": "provider_metadata",
        "trade_status": "provider_metadata",
    }
    field_timestamp_map = {field: quote_time for field in field_source_map}

    return {
        "ticker": getattr(latest, "symbol", None),
        "name": _raw_value(raw, ("name", "名称", "股票名称")),
        "current_price": current_price,
        "open": getattr(latest, "open", None),
        "high": high,
        "low": low,
        "close": close,
        "previous_close": previous_close,
        "change_amount": _round(change_amount),
        "pct_change": _round(pct_change),
        "amplitude": _round(amplitude),
        "volume": volume,
        "amount": _round(amount, 2),
        "amount_is_estimated": amount_is_estimated,
        "volume_ratio": _round(resolved_volume_ratio),
        "volume_ratio_source": volume_ratio_source,
        "turnover_rate": getattr(latest, "turnover_rate", None),
        "market_source": market_source,
        "quote_time": quote_time,
        "trade_status": _raw_value(raw, ("statusDescription", "trade_status", "交易状态")),
        "field_source_map": field_source_map,
        "field_timestamp_map": field_timestamp_map,
        "estimated_fields": estimated_fields,
    }


def high_low_range(bars: list[Any], period: int = 20) -> tuple[float | None, float | None]:
    """(period_high, period_low) from the last ``period`` bars."""
    if period <= 0 or len(bars) < period:
        return None, None
    recent = bars[-period:]
    highs = [b.high for b in recent if b.high is not None]
    lows = [b.low for b in recent if b.low is not None]
    return (max(highs) if highs else None, min(lows) if lows else None)


def n_day_return(bars: list[Any], days: int = 5) -> float | None:
    """Return percentage over the last ``days`` bars (close-to-close)."""
    if days <= 0 or len(bars) < days + 1:
        return None
    first = bars[-(days + 1)].close
    last = bars[-1].close
    if first is None or last is None or first == 0:
        return None
    return (last / first - 1.0) * 100.0


def relative_strength(
    bars: list[Any],
    benchmark_bars: list[Any],
    period: int = 20,
) -> float | None:
    """Ratio of stock return to benchmark return over ``period`` bars.

    Returns >1.0 if stock outperformed, <1.0 if underperformed.
    """
    stock_ret = n_day_return(bars, period)
    bench_ret = n_day_return(benchmark_bars, period)
    if stock_ret is None or bench_ret is None:
        return None
    # Convert to simple return ratio
    stock_simple = 1.0 + stock_ret / 100.0
    bench_simple = 1.0 + bench_ret / 100.0
    if bench_simple == 0:
        return None
    return stock_simple / bench_simple


def _pct_vs(value: float | None, base: float | None) -> float | None:
    if value is None or base in (None, 0):
        return None
    return (value / base - 1.0) * 100.0


def _range_position(value: float | None, low: float | None, high: float | None) -> float | None:
    if value is None or low is None or high is None or high == low:
        return None
    return (value - low) / (high - low) * 100.0


def _instrument_metadata(symbol: str) -> dict[str, Any]:
    ticker = symbol.upper()
    if ticker in NON_TRADABLE_INDEX_SYMBOLS:
        benchmark = None
        proxy = None
        for item in MARKET_INDEX_BENCHMARKS.values():
            candidates = tuple(str(code).upper() for code in item.get("index_code_candidates", ()))
            if ticker in candidates:
                benchmark = str(item.get("name"))
                proxy = str(item.get("tradable_proxy"))
                break
        return {
            "instrument_type": "non_tradable_index",
            "market_proxy_for": benchmark,
            "tradable_proxy": proxy,
            "is_tradable": False,
        }
    if ticker in INDEX_PROXY_ETF_TO_BENCHMARK:
        return {
            "instrument_type": "tradable_index_proxy_etf",
            "market_proxy_for": INDEX_PROXY_ETF_TO_BENCHMARK[ticker],
            "tradable_proxy": ticker,
            "is_tradable": True,
        }
    return {
        "instrument_type": "equity_or_sector_etf",
        "market_proxy_for": None,
        "tradable_proxy": None,
        "is_tradable": True,
    }


def _quality_fields(result: dict[str, Any]) -> None:
    required = (
        "ticker",
        "name",
        "current_price",
        "close",
        "previous_close",
        "open",
        "high",
        "low",
        "pct_change",
        "change_amount",
        "amplitude",
        "volume",
        "amount",
        "volume_ratio",
        "turnover_rate",
        "market_source",
        "quote_time",
        "trade_status",
        "ma5",
        "ma10",
        "ma20",
        "price_vs_ma5",
        "price_vs_ma10",
        "price_vs_ma20",
        "high_20d",
        "low_20d",
        "range_position_20d",
        "return_1d",
        "return_5d",
        "return_10d",
        "return_20d",
        "atr_14",
        "volatility_20d",
        "relative_strength_spy",
        "relative_strength_qqq",
        "relative_strength_smh",
        "relative_strength_soxx",
    )
    missing = [field for field in required if result.get(field) is None]
    symbol = str(result.get("ticker") or result.get("symbol") or "").upper()
    metadata = _instrument_metadata(symbol)
    result.update(metadata)

    if metadata["instrument_type"] == "non_tradable_index":
        index_blocking = {
            "ticker",
            "current_price",
            "close",
            "previous_close",
            "open",
            "high",
            "low",
            "pct_change",
            "change_amount",
            "amplitude",
            "volume",
            "market_source",
            "quote_time",
        }
        blocking_missing = [field for field in missing if field in index_blocking]
    elif metadata["instrument_type"] == "tradable_index_proxy_etf":
        etf_non_blocking = {"name", "turnover_rate"}
        blocking_missing = [field for field in missing if field not in etf_non_blocking]
    else:
        blocking_missing = missing

    non_blocking_missing = [field for field in missing if field not in blocking_missing]
    result["missing_fields"] = missing
    result["blocking_missing_fields"] = blocking_missing
    result["non_blocking_missing_fields"] = non_blocking_missing
    estimated = list(dict.fromkeys(result.get("estimated_fields", [])))
    result["estimated_fields"] = estimated
    result["primary_source_status"] = "complete" if not blocking_missing else "missing_fields"
    result["second_source_status"] = "not_checked_by_indicators_cli"
    result["data_conflicts"] = []
    result["market_regime_usable"] = not blocking_missing
    if metadata["instrument_type"] == "non_tradable_index":
        result["confidence"] = "medium" if not blocking_missing else "low"
        result["zeus_field_status"] = "non_tradable_index_context" if not blocking_missing else "ZEUS_FIELD_FAILURE"
        result["usable_for_current_trade"] = False
    elif not blocking_missing:
        result["confidence"] = "high" if not estimated else "medium"
        result["zeus_field_status"] = "complete" if not estimated else "fallback_filled"
        result["usable_for_current_trade"] = True
    else:
        result["confidence"] = "low"
        result["zeus_field_status"] = "ZEUS_FIELD_FAILURE"
        result["usable_for_current_trade"] = False


def compute_indicator_summary(
    bars: list[Any],
    benchmark_bars: list[Any] | None = None,
    sector_bars: list[Any] | None = None,
    relative_benchmark_bars: dict[str, list[Any]] | None = None,
    symbol: str = "",
) -> dict[str, Any]:
    """Compute all available indicators for one symbol.

    Returns a plain dict suitable for JSON output or Markdown tables.
    """
    result: dict[str, Any] = {"symbol": symbol, "ticker": symbol, "bar_count": len(bars)}
    result.update(_latest_market_tape(bars))
    if bars:
        latest = bars[-1]
        result["latest_date"] = latest.date
        result["latest_close"] = latest.close
        result["latest_volume"] = latest.volume

    current_price = result.get("current_price") if result.get("current_price") is not None else result.get("close")
    result["ma_5"] = moving_average(bars, 5)
    result["ma_10"] = moving_average(bars, 10)
    result["ma_20"] = moving_average(bars, 20)
    result["ma5"] = result["ma_5"]
    result["ma10"] = result["ma_10"]
    result["ma20"] = result["ma_20"]
    result["price_vs_ma5"] = _round(_pct_vs(current_price, result["ma5"]))
    result["price_vs_ma10"] = _round(_pct_vs(current_price, result["ma10"]))
    result["price_vs_ma20"] = _round(_pct_vs(current_price, result["ma20"]))
    result["ema_12"] = exponential_moving_average(bars, 12)
    result["ema_26"] = exponential_moving_average(bars, 26)
    result["atr_14"] = _round(atr(bars, 14))
    result["rsi_14"] = rsi(bars, 14)
    result["vwap"] = vwap_approximation(bars)
    result["volume_ratio_20"] = volume_ratio(bars, 20)

    high_20, low_20 = high_low_range(bars, 20)
    result["high_20"] = high_20
    result["low_20"] = low_20
    result["high_20d"] = high_20
    result["low_20d"] = low_20
    result["range_position_20d"] = _round(_range_position(current_price, low_20, high_20))

    result["return_1d"] = n_day_return(bars, 1)
    result["return_5d"] = n_day_return(bars, 5)
    result["return_10d"] = n_day_return(bars, 10)
    result["return_20d"] = n_day_return(bars, 20)
    result["volatility_20d"] = _round(volatility(bars, 20))

    if benchmark_bars:
        result["rs_vs_benchmark_20"] = relative_strength(bars, benchmark_bars, 20)
        result["benchmark_return_20"] = n_day_return(benchmark_bars, 20)
    else:
        result["rs_vs_benchmark_20"] = None
        result["benchmark_return_20"] = None

    if sector_bars:
        result["rs_vs_sector_20"] = relative_strength(bars, sector_bars, 20)
        result["sector_return_20"] = n_day_return(sector_bars, 20)
    else:
        result["rs_vs_sector_20"] = None
        result["sector_return_20"] = None

    for benchmark in ("SPY", "QQQ", "SMH", "SOXX"):
        key = f"relative_strength_{benchmark.lower()}"
        benchmark_map = relative_benchmark_bars or {}
        result[key] = relative_strength(bars, benchmark_map.get(benchmark, []), 20)

    _quality_fields(result)
    return result
