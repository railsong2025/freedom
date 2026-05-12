"""Data quality validation for the Zeus Intelligence Division.

Validates market data for staleness, gaps, outliers, and cross-source agreement.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any


@dataclass(frozen=True)
class QualityReport:
    symbol: str
    is_stale: bool
    staleness_days: int | None
    missing_bars: list[str]
    outliers: list[dict[str, Any]]
    source_agreement: float | None
    issues: list[str]
    quality_score: float  # 0.0 to 1.0


def detect_staleness(bars: list[Any], max_staleness_days: int = 2, reference_date: date | None = None) -> tuple[bool, int | None]:
    """Check if the latest bar date is within ``max_staleness_days`` of reference_date."""
    if not bars:
        return True, None
    latest_date_str = bars[-1].date
    if not latest_date_str:
        return True, None
    try:
        latest = date.fromisoformat(latest_date_str[:10])
    except (ValueError, IndexError):
        return True, None
    ref = reference_date or date.today()
    delta = (ref - latest).days
    return delta > max_staleness_days, delta


def detect_missing_bars(
    bars: list[Any],
    start: date,
    end: date,
    exclude_weekends: bool = True,
) -> list[str]:
    """Return ISO date strings for expected trading days missing from bars."""
    if not bars:
        return []
    bar_dates = set()
    for b in bars:
        if b.date:
            bar_dates.add(b.date[:10])
    missing: list[str] = []
    current = start
    while current <= end:
        if exclude_weekends and current.weekday() >= 5:
            current += timedelta(days=1)
            continue
        iso = current.isoformat()
        if iso not in bar_dates:
            missing.append(iso)
        current += timedelta(days=1)
    return missing


def detect_outliers(bars: list[Any], z_threshold: float = 4.0) -> list[dict[str, Any]]:
    """Return bars where daily return exceeds ``z_threshold`` standard deviations."""
    if len(bars) < 3:
        return []
    returns: list[tuple[float, str, float | None, float | None]] = []
    for i in range(1, len(bars)):
        prev_close = bars[i - 1].close
        curr_close = bars[i].close
        if prev_close and curr_close and prev_close != 0:
            ret = (curr_close - prev_close) / prev_close
            returns.append((ret, bars[i].date, curr_close, bars[i].volume))
    if len(returns) < 2:
        return []
    mean_ret = sum(r[0] for r in returns) / len(returns)
    variance = sum((r[0] - mean_ret) ** 2 for r in returns) / len(returns)
    std_ret = math.sqrt(variance)
    if std_ret == 0:
        return []
    outliers: list[dict[str, Any]] = []
    for ret, dt, close, vol in returns:
        z = abs(ret - mean_ret) / std_ret
        if z > z_threshold:
            outliers.append({
                "date": dt,
                "close": close,
                "daily_return_pct": round(ret * 100, 2),
                "z_score": round(z, 2),
                "volume": vol,
            })
    return outliers


def cross_source_agreement(
    results: list[Any],
    tolerance_pct: float = 1.0,
) -> float | None:
    """Score 0.0-1.0 on how closely multiple MarketDataResult sources agree on closing prices.

    Compares the latest close from each result. Returns None if fewer than 2 sources.
    """
    closes: list[float] = []
    for r in results:
        if r.ok and r.bars:
            latest_close = r.bars[-1].close
            if latest_close is not None:
                closes.append(latest_close)
    if len(closes) < 2:
        return None
    avg_close = sum(closes) / len(closes)
    if avg_close == 0:
        return None
    max_deviation = max(abs(c - avg_close) / avg_close * 100 for c in closes)
    if max_deviation <= tolerance_pct:
        return 1.0
    agreement = max(0.0, 1.0 - (max_deviation - tolerance_pct) / tolerance_pct)
    return round(min(1.0, agreement), 4)


def validate_data_quality(
    bars: list[Any],
    start: date,
    end: date,
    symbol: str = "",
    cross_results: list[Any] | None = None,
    max_staleness_days: int = 2,
    z_threshold: float = 4.0,
) -> QualityReport:
    """Orchestrate all quality checks for a single symbol."""
    issues: list[str] = []
    is_stale, staleness_days = detect_staleness(bars, max_staleness_days)
    if is_stale:
        if staleness_days is not None:
            issues.append(f"Data is {staleness_days} days stale (max {max_staleness_days})")
        else:
            issues.append("Data staleness cannot be determined")

    missing = detect_missing_bars(bars, start, end)
    if missing:
        issues.append(f"Missing {len(missing)} trading day(s): {', '.join(missing[:5])}")

    outliers = detect_outliers(bars, z_threshold)
    if outliers:
        issues.append(f"{len(outliers)} outlier day(s) detected (z > {z_threshold})")

    agreement = None
    if cross_results:
        agreement = cross_source_agreement(cross_results)
        if agreement is not None and agreement < 0.8:
            issues.append(f"Cross-source agreement is low: {agreement:.2f}")

    # Quality score: start at 1.0, deduct for each issue
    score = 1.0
    if is_stale:
        score -= 0.3
    score -= min(0.2, len(missing) * 0.02)
    score -= min(0.2, len(outliers) * 0.05)
    if agreement is not None and agreement < 0.8:
        score -= 0.2
    score = max(0.0, min(1.0, score))

    return QualityReport(
        symbol=symbol,
        is_stale=is_stale,
        staleness_days=staleness_days,
        missing_bars=missing,
        outliers=outliers,
        source_agreement=agreement,
        issues=issues,
        quality_score=round(score, 4),
    )