#!/usr/bin/env python3
"""Batch fetch daily market data through the local Buffett data adapter."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from market_data import batch_summary, default_client


def _parse_date(value: str) -> dt.date:
    return dt.date.fromisoformat(value)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--symbols", nargs="+", required=True)
    parser.add_argument("--start", required=True, type=_parse_date)
    parser.add_argument("--end", required=True, type=_parse_date)
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--aktools-api-url")
    parser.add_argument("--http-api-url")
    parser.add_argument("--timeout-seconds", type=float, default=8.0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    client = default_client(
        cache_dir=args.cache_dir,
        aktools_api_url=args.aktools_api_url,
        http_api_url=args.http_api_url,
        timeout_seconds=args.timeout_seconds,
    )
    results = client.daily_bars_batch(
        [symbol.upper() for symbol in args.symbols],
        args.start,
        args.end,
    )
    print(json.dumps(batch_summary(results), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
