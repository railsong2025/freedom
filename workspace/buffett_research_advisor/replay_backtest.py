#!/usr/bin/env python3
"""Replay strong-cycle Buffett decisions on historical daily bars."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from market_data import (
    CompositeMarketDataClient,
    CsvMarketDataProvider,
    MarketDataResult,
    five_day_return,
)


@dataclass(frozen=True)
class ReplayTrade:
    symbol: str
    decision_return_pct: float
    excess_vs_spy_pct: float
    excess_vs_sector_pct: float
    entry_price: float
    exit_price: float
    shares: int
    gross_pnl_usd: float
    total_fees_usd: float
    net_pnl_usd: float
    net_return_pct: float
    verdict: str


@dataclass(frozen=True)
class ReplayReport:
    lookback_start: str
    decision_date: str
    exit_date: str
    benchmark_return_pct: float
    sector_return_pct: float
    selected_symbols: list[str]
    trades: list[ReplayTrade]
    net_pnl_usd: float
    profitable: bool
    assumptions: dict[str, Any]


def _bar_close(result: MarketDataResult, target_date: dt.date) -> float:
    for bar in result.bars:
        if bar.date == target_date.isoformat() and bar.close is not None:
            return bar.close
    raise ValueError(f"{result.symbol} missing close for {target_date.isoformat()}")


def _load(client: CompositeMarketDataClient, symbol: str, start: dt.date, end: dt.date) -> MarketDataResult:
    result = client.daily_bars(symbol, start, end)
    if not result.ok:
        errors = "; ".join(f"{attempt.source}: {attempt.error}" for attempt in result.attempts)
        raise ValueError(f"no bars for {symbol}: {errors}")
    return result


def replay_strong_cycle_starter(
    *,
    client: CompositeMarketDataClient,
    symbols: list[str],
    lookback_start: dt.date,
    decision_date: dt.date,
    exit_date: dt.date,
    benchmark_symbol: str = "SPY",
    sector_symbol: str = "SMH",
    fee_usd: float = 5.0,
    shares: int = 1,
    equity_usd: float | None = None,
    position_pct: float = 5.0,
    min_excess_vs_spy_pct: float = 10.0,
    require_sector_outperformance: bool = True,
) -> ReplayReport:
    if shares < 1:
        raise ValueError("shares must be at least 1")
    if exit_date <= decision_date:
        raise ValueError("exit_date must be after decision_date")

    full_start = lookback_start
    full_end = exit_date
    benchmark = _load(client, benchmark_symbol, full_start, full_end)
    sector = _load(client, sector_symbol, full_start, full_end)
    benchmark_return = five_day_return(
        MarketDataResult(
            benchmark_symbol,
            [bar for bar in benchmark.bars if bar.date <= decision_date.isoformat()],
            benchmark.source,
            benchmark.attempts,
        )
    )
    sector_return = five_day_return(
        MarketDataResult(
            sector_symbol,
            [bar for bar in sector.bars if bar.date <= decision_date.isoformat()],
            sector.source,
            sector.attempts,
        )
    )
    if benchmark_return is None or sector_return is None:
        raise ValueError("benchmark and sector need at least two lookback bars")

    selected: list[str] = []
    trades: list[ReplayTrade] = []
    for symbol in symbols:
        result = _load(client, symbol, full_start, full_end)
        lookback_bars = [bar for bar in result.bars if bar.date <= decision_date.isoformat()]
        decision_return = five_day_return(MarketDataResult(symbol, lookback_bars, result.source, result.attempts))
        if decision_return is None:
            continue
        excess_vs_spy = decision_return - benchmark_return
        excess_vs_sector = decision_return - sector_return
        if excess_vs_spy < min_excess_vs_spy_pct:
            continue
        if require_sector_outperformance and excess_vs_sector <= 0:
            continue

        entry_price = _bar_close(result, decision_date)
        exit_price = _bar_close(result, exit_date)
        trade_shares = shares
        if equity_usd is not None:
            trade_shares = max(1, math.floor(equity_usd * (position_pct / 100.0) / entry_price))
        gross_pnl = (exit_price - entry_price) * trade_shares
        total_fees = fee_usd * 2
        net_pnl = gross_pnl - total_fees
        cash_used = entry_price * trade_shares + fee_usd
        net_return = net_pnl / cash_used * 100.0
        verdict = "profitable" if net_pnl > 0 else "not_profitable"
        selected.append(symbol)
        trades.append(
            ReplayTrade(
                symbol=symbol,
                decision_return_pct=round(decision_return, 4),
                excess_vs_spy_pct=round(excess_vs_spy, 4),
                excess_vs_sector_pct=round(excess_vs_sector, 4),
                entry_price=entry_price,
                exit_price=exit_price,
                shares=trade_shares,
                gross_pnl_usd=round(gross_pnl, 2),
                total_fees_usd=round(total_fees, 2),
                net_pnl_usd=round(net_pnl, 2),
                net_return_pct=round(net_return, 4),
                verdict=verdict,
            )
        )

    net_pnl = round(sum(trade.net_pnl_usd for trade in trades), 2)
    return ReplayReport(
        lookback_start=lookback_start.isoformat(),
        decision_date=decision_date.isoformat(),
        exit_date=exit_date.isoformat(),
        benchmark_return_pct=round(benchmark_return, 4),
        sector_return_pct=round(sector_return, 4),
        selected_symbols=selected,
        trades=trades,
        net_pnl_usd=net_pnl,
        profitable=net_pnl > 0,
        assumptions={
            "entry": "decision_date close",
            "exit": "exit_date close",
            "fee_usd_each_side": fee_usd,
            "selection_rule": "candidate excess return vs SPY >= threshold and outperforms sector ETF",
            "min_excess_vs_spy_pct": min_excess_vs_spy_pct,
            "require_sector_outperformance": require_sector_outperformance,
            "shares": shares,
            "equity_usd": equity_usd,
            "position_pct": position_pct if equity_usd is not None else None,
        },
    )


def _parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache-dir", required=True, type=Path)
    parser.add_argument("--lookback-start", required=True, type=_parse_date)
    parser.add_argument("--decision-date", required=True, type=_parse_date)
    parser.add_argument("--exit-date", required=True, type=_parse_date)
    parser.add_argument("--symbols", nargs="+", required=True)
    parser.add_argument("--shares", type=int, default=1)
    parser.add_argument("--fee-usd", type=float, default=5.0)
    parser.add_argument("--equity-usd", type=float)
    parser.add_argument("--position-pct", type=float, default=5.0)
    parser.add_argument("--min-excess-vs-spy-pct", type=float, default=10.0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    client = CompositeMarketDataClient([CsvMarketDataProvider(args.cache_dir)], timeout_seconds=0)
    report = replay_strong_cycle_starter(
        client=client,
        symbols=[symbol.upper() for symbol in args.symbols],
        lookback_start=args.lookback_start,
        decision_date=args.decision_date,
        exit_date=args.exit_date,
        fee_usd=args.fee_usd,
        shares=args.shares,
        equity_usd=args.equity_usd,
        position_pct=args.position_pct,
        min_excess_vs_spy_pct=args.min_excess_vs_spy_pct,
    )
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
