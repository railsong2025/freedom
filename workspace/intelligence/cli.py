"""CLI entry point for Zeus Intelligence Division tools."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

# Allow imports from workspace root
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from intelligence.technical_indicators import compute_indicator_summary
from intelligence.data_quality import validate_data_quality
from intelligence.sector_proxy import (
    build_sector_summary,
    sector_etf_symbols,
    ticker_instrument_metadata,
    ticker_sector,
)


def _safe_float(val: str | None) -> float | None:
    """Convert a CSV value to float, returning None for missing/invalid values."""
    if not val or val.strip() in ("N/A", "NaN", "null", "-", "None", ""):
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _load_bars_from_csv(csv_path: Path) -> list:
    """Load DailyBar-like objects from a CSV file (date,open,high,low,close,volume)."""
    from interface.market_data import DailyBar

    bars: list[DailyBar] = []
    if not csv_path.exists():
        return bars
    import csv
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            bars.append(DailyBar(
                symbol=row.get("symbol", csv_path.stem).upper(),
                date=row.get("date", ""),
                open=_safe_float(row.get("open")),
                high=_safe_float(row.get("high")),
                low=_safe_float(row.get("low")),
                close=_safe_float(row.get("close")),
                volume=_safe_float(row.get("volume")),
                source="financeBusiness_mcp_cached_csv",
                raw=dict(row),
                current_price=_safe_float(row.get("current_price")),
                amount=_safe_float(row.get("amount")),
                prev_close=_safe_float(row.get("prev_close")),
                pct_change=_safe_float(row.get("pct_change")),
                change_amount=_safe_float(row.get("change_amount")),
                amplitude=_safe_float(row.get("amplitude")),
                turnover_rate=_safe_float(row.get("turnover_rate")),
                volume_ratio=_safe_float(row.get("volume_ratio")),
            ))
    return bars


def cmd_indicators(args: argparse.Namespace) -> None:
    symbols = [s.upper() for s in args.symbols.split(",")]
    market_data_dir = Path(args.market_data_dir) if args.market_data_dir else None
    relative_benchmarks = ("SPY", "QQQ", "SMH", "SOXX")

    # Prefer pre-fetched CSV pack when available
    if market_data_dir and market_data_dir.exists():
        benchmark_bars = None
        if args.benchmark:
            bench_csv = market_data_dir / f"{args.benchmark.upper()}.csv"
            if bench_csv.exists():
                benchmark_bars = _load_bars_from_csv(bench_csv)
        relative_benchmark_bars = {
            benchmark: _load_bars_from_csv(market_data_dir / f"{benchmark}.csv")
            for benchmark in relative_benchmarks
            if (market_data_dir / f"{benchmark}.csv").exists()
        }
        output: list[dict] = []
        for symbol in symbols:
            csv_path = market_data_dir / f"{symbol}.csv"
            bars = _load_bars_from_csv(csv_path)
            # Find sector ETF bars for relative strength
            sector_bars = None
            if bars:
                sec = ticker_sector(symbol)
                if sec:
                    etfs = sector_etf_symbols(sec)
                    for etf in etfs:
                        etf_csv = market_data_dir / f"{etf}.csv"
                        if etf_csv.exists():
                            sector_bars = _load_bars_from_csv(etf_csv)
                            break
            summary = compute_indicator_summary(
                bars,
                benchmark_bars,
                sector_bars,
                relative_benchmark_bars,
                symbol,
            )
            summary["data_source"] = "prefetched_csv" if bars else "no_local_data"
            output.append(summary)
        print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
        return

    # financeBusiness-only policy: do not live-fetch from local adapters here.
    output: list[dict] = []
    for symbol in symbols:
        summary = compute_indicator_summary(
            [],
            None,
            None,
            {},
            symbol,
        )
        summary["data_source"] = "financeBusiness_mcp_required"
        summary["source_attempts"] = []
        summary["zeus_field_status"] = "ZEUS_FIELD_FAILURE"
        summary["missing_fields"] = ["financeBusiness_prefetched_history_or_direct_mcp"]
        output.append(summary)

    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))


def cmd_quality(args: argparse.Namespace) -> None:
    symbols = [s.upper() for s in args.symbols.split(",")]
    end_date = date.today()
    start_date = end_date - timedelta(days=args.days)
    market_data_dir = Path(args.market_data_dir) if args.market_data_dir else None

    output: list[dict] = []

    # Prefer pre-fetched CSV pack when available
    if market_data_dir and market_data_dir.exists():
        for symbol in symbols:
            csv_path = market_data_dir / f"{symbol}.csv"
            bars = _load_bars_from_csv(csv_path)
            report = validate_data_quality(bars, start_date, end_date, symbol)
            output.append({
                "symbol": report.symbol,
                "is_stale": report.is_stale,
                "staleness_days": report.staleness_days,
                "missing_bars": report.missing_bars,
                "outlier_count": len(report.outliers),
                "source_agreement": report.source_agreement,
                "issues": report.issues,
                "quality_score": report.quality_score,
                "data_source": "prefetched_csv" if bars else "no_local_data",
            })
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return

    for symbol in symbols:
        report = validate_data_quality([], start_date, end_date, symbol)
        output.append({
            "symbol": report.symbol,
            "is_stale": report.is_stale,
            "staleness_days": report.staleness_days,
            "missing_bars": report.missing_bars,
            "outlier_count": len(report.outliers),
            "source_agreement": report.source_agreement,
            "issues": report.issues,
            "quality_score": report.quality_score,
            "data_source": "financeBusiness_mcp_required",
            "source_attempts": [],
            "zeus_field_status": "ZEUS_FIELD_FAILURE",
        })

    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_sector_map(args: argparse.Namespace) -> None:
    symbols = [s.upper() for s in args.symbols.split(",")]
    result = {}
    for symbol in symbols:
        sector = ticker_sector(symbol)
        result[symbol] = {
            "sector": sector,
            "etfs": sector_etf_symbols(sector or ""),
            **ticker_instrument_metadata(symbol),
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_checkpoint_status(args: argparse.Namespace) -> None:
    from intelligence.checkpoint_report import checkpoint_status

    result = checkpoint_status(Path(args.run_dir), Path(args.parts_dir) if args.parts_dir else None)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_merge_checkpoints(args: argparse.Namespace) -> None:
    from intelligence.checkpoint_report import merge_checkpoints

    result = merge_checkpoints(
        Path(args.run_dir),
        subject=args.subject,
        output_path=Path(args.output) if args.output else None,
        parts_dir=Path(args.parts_dir) if args.parts_dir else None,
    )
    print(json.dumps({
        "output_path": str(result.output_path),
        "manifest_path": str(result.manifest_path),
        "part_count": result.part_count,
        "missing_sections": list(result.missing_sections),
        "complete": result.complete,
    }, ensure_ascii=False, indent=2))
    if not result.complete:
        raise SystemExit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Zeus Intelligence Division CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    # indicators
    ind = sub.add_parser("indicators", help="Compute technical indicators for symbols")
    ind.add_argument("--symbols", required=True, help="Comma-separated symbols (e.g., MU,AMD,NVDA)")
    ind.add_argument("--benchmark", default="SPY", help="Benchmark symbol for relative strength")
    ind.add_argument("--days", type=int, default=75, help="Lookback days for data fetch")
    ind.add_argument("--market-data-dir", help="Pre-fetched market data directory (reads CSV pack first)")
    ind.add_argument("--cache-dir", help=argparse.SUPPRESS)
    ind.add_argument("--timeout", type=float, default=8.0, help=argparse.SUPPRESS)
    ind.set_defaults(func=cmd_indicators)

    # quality
    qual = sub.add_parser("quality", help="Validate data quality for symbols")
    qual.add_argument("--symbols", required=True, help="Comma-separated symbols")
    qual.add_argument("--days", type=int, default=75, help="Lookback days")
    qual.add_argument("--market-data-dir", help="Pre-fetched market data directory (reads CSV pack first)")
    qual.add_argument("--cache-dir", help=argparse.SUPPRESS)
    qual.add_argument("--timeout", type=float, default=8.0, help=argparse.SUPPRESS)
    qual.set_defaults(func=cmd_quality)

    # sector-map
    sm = sub.add_parser("sector-map", help="Show sector classification for symbols")
    sm.add_argument("--symbols", required=True, help="Comma-separated symbols")
    sm.set_defaults(func=cmd_sector_map)

    status = sub.add_parser("checkpoint-status", help="List Zeus intelligence checkpoint parts")
    status.add_argument("--run-dir", required=True, help="Zeus report folder")
    status.add_argument("--parts-dir", help="Override checkpoint parts directory")
    status.set_defaults(func=cmd_checkpoint_status)

    merge = sub.add_parser("merge-checkpoints", help="Merge checkpoint parts into 03_zeus_intelligence.md")
    merge.add_argument("--run-dir", required=True, help="Zeus report folder")
    merge.add_argument("--subject", default="未命名主题", help="Report subject for the merged heading")
    merge.add_argument("--output", help="Override output markdown path")
    merge.add_argument("--parts-dir", help="Override checkpoint parts directory")
    merge.set_defaults(func=cmd_merge_checkpoints)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
