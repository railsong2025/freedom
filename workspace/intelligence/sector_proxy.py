"""Sector classification and relative performance for the Zeus Intelligence Division.

Maps tickers to sectors, computes sector-relative performance, and builds
sector leadership tables.
"""

from __future__ import annotations

from typing import Any

from interface.constants import (
    INDEX_PROXY_ETF_TO_BENCHMARK,
    MARKET_INDEX_BENCHMARKS,
    NON_TRADABLE_INDEX_SYMBOLS,
    SECTOR_ETF_SYMBOLS,
    TICKER_SECTOR_MAP,
)

from .technical_indicators import n_day_return, relative_strength


def ticker_sector(ticker: str) -> str | None:
    """Return the sector name for a ticker, using TICKER_SECTOR_MAP."""
    return TICKER_SECTOR_MAP.get(ticker.upper())


def ticker_instrument_metadata(ticker: str) -> dict[str, Any]:
    """Classify tickers for Buffett market-regime versus trade-action logic."""
    symbol = ticker.upper()
    if symbol in NON_TRADABLE_INDEX_SYMBOLS:
        benchmark = None
        proxy = None
        for item in MARKET_INDEX_BENCHMARKS.values():
            candidates = tuple(str(code).upper() for code in item.get("index_code_candidates", ()))
            if symbol in candidates:
                benchmark = str(item.get("name"))
                proxy = str(item.get("tradable_proxy"))
                break
        return {
            "instrument_type": "non_tradable_index",
            "market_proxy_for": benchmark,
            "tradable_proxy": proxy,
            "is_tradable": False,
        }
    if symbol in INDEX_PROXY_ETF_TO_BENCHMARK:
        return {
            "instrument_type": "tradable_index_proxy_etf",
            "market_proxy_for": INDEX_PROXY_ETF_TO_BENCHMARK[symbol],
            "tradable_proxy": symbol,
            "is_tradable": True,
        }
    return {
        "instrument_type": "equity_or_sector_etf",
        "market_proxy_for": None,
        "tradable_proxy": None,
        "is_tradable": True,
    }


def sector_etf_symbols(sector: str) -> list[str]:
    """Return sector ETF symbol(s) for a given sector name."""
    return list(SECTOR_ETF_SYMBOLS.get(sector, ()))


def sector_relative_performance(
    bars: list[Any],
    sector_bars: list[Any],
    period: int = 20,
) -> float | None:
    """Stock return minus sector ETF return over ``period`` bars (percentage points)."""
    stock_ret = n_day_return(bars, period)
    sector_ret = n_day_return(sector_bars, period)
    if stock_ret is None or sector_ret is None:
        return None
    return stock_ret - sector_ret


def sector_leadership_table(
    bars_by_symbol: dict[str, list[Any]],
    benchmark_bars: list[Any],
    period: int = 20,
) -> list[dict[str, Any]]:
    """Rank stocks by relative strength vs benchmark, grouped by sector.

    Returns a list of dicts sorted by relative strength descending.
    """
    rows: list[dict[str, Any]] = []
    for symbol, bars in bars_by_symbol.items():
        rs = relative_strength(bars, benchmark_bars, period)
        ret = n_day_return(bars, period)
        sector = ticker_sector(symbol) or "unknown"
        metadata = ticker_instrument_metadata(symbol)
        rows.append({
            "symbol": symbol,
            "sector": sector,
            "instrument_type": metadata["instrument_type"],
            "market_proxy_for": metadata["market_proxy_for"],
            "return_pct": round(ret, 2) if ret is not None else None,
            "relative_strength": round(rs, 4) if rs is not None else None,
        })
    rows.sort(key=lambda r: r["relative_strength"] or 0, reverse=True)
    return rows


def build_sector_summary(
    bars_by_symbol: dict[str, list[Any]],
    benchmark_bars: list[Any] | None = None,
    sector_etf_bars: dict[str, list[Any]] | None = None,
    period: int = 20,
) -> dict[str, Any]:
    """Build sector map + relative performance + leadership table for all symbols.

    Returns a dict with keys: sector_map, leadership, sector_performance.
    """
    sector_map: dict[str, list[str]] = {}
    for symbol in bars_by_symbol:
        sector = ticker_sector(symbol) or "unknown"
        sector_map.setdefault(sector, []).append(symbol)

    leadership = sector_leadership_table(
        bars_by_symbol,
        benchmark_bars or [],
        period,
    ) if benchmark_bars else []

    sector_performance: list[dict[str, Any]] = []
    if sector_etf_bars:
        for sector_name, etf_bars in sector_etf_bars.items():
            ret = n_day_return(etf_bars, period)
            bench_ret = n_day_return(benchmark_bars, period) if benchmark_bars else None
            rel = None
            if ret is not None and bench_ret is not None:
                rel = round(ret - bench_ret, 2)
            sector_performance.append({
                "sector": sector_name,
                "etf_return_pct": round(ret, 2) if ret is not None else None,
                "vs_benchmark_pct": rel,
            })

    return {
        "sector_map": sector_map,
        "leadership": leadership,
        "sector_performance": sector_performance,
    }
