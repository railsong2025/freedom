#!/usr/bin/env python3
"""Compatibility wrapper for the public market data adapters.

The implementation lives in `workspace/interface/market_data.py`. This module
keeps older imports working for the manual research runner and its tests.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

_WORKSPACE_DIR = Path(__file__).resolve().parents[1]
_PROJECT_ROOT = _WORKSPACE_DIR.parent
for _path in (str(_PROJECT_ROOT), str(_WORKSPACE_DIR)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

try:
    from workspace.interface.market_data import (
        AkShareMarketDataProvider,
        AkToolsMarketDataProvider,
        CompositeMarketDataClient,
        CsvMarketDataProvider,
        DailyBar,
        HttpApiMarketDataProvider,
        MarketDataError,
        MarketDataTimeoutError,
        MarketDataProvider,
        MarketDataResult,
        SourceAttempt,
        StooqMarketDataProvider,
        YFinanceMarketDataProvider,
        batch_summary,
        default_client as _public_default_client,
        five_day_return,
        write_csv_cache,
    )
except ModuleNotFoundError:
    from interface.market_data import (
        AkShareMarketDataProvider,
        AkToolsMarketDataProvider,
        CompositeMarketDataClient,
        CsvMarketDataProvider,
        DailyBar,
        HttpApiMarketDataProvider,
        MarketDataError,
        MarketDataTimeoutError,
        MarketDataProvider,
        MarketDataResult,
        SourceAttempt,
        StooqMarketDataProvider,
        YFinanceMarketDataProvider,
        batch_summary,
        default_client as _public_default_client,
        five_day_return,
        write_csv_cache,
    )

# Backward-compatible alias: TimeoutError was renamed to MarketDataTimeoutError
TimeoutError = MarketDataTimeoutError


def default_client(
    *,
    cache_dir: Path | None = None,
    aktools_api_url: str | None = None,
    http_api_url: str | None = None,
    timeout_seconds: float = 8.0,
    disable_yfinance: bool | None = None,
) -> CompositeMarketDataClient:
    if aktools_api_url is None:
        aktools_api_url = os.getenv("BUFFETT_AKTOOLS_API_URL")
    if http_api_url is None:
        http_api_url = os.getenv("BUFFETT_MARKET_DATA_API_URL")
    if disable_yfinance is None:
        disable_yfinance = os.getenv("BUFFETT_DISABLE_YFINANCE", "").strip().lower() in {
            "1",
            "true",
            "yes",
        }
        if not disable_yfinance:
            disable_yfinance = None
    return _public_default_client(
        cache_dir=cache_dir,
        aktools_api_url=aktools_api_url,
        http_api_url=http_api_url,
        timeout_seconds=timeout_seconds,
        disable_yfinance=disable_yfinance,
    )


__all__ = [
    "AkShareMarketDataProvider",
    "AkToolsMarketDataProvider",
    "CompositeMarketDataClient",
    "CsvMarketDataProvider",
    "DailyBar",
    "HttpApiMarketDataProvider",
    "MarketDataError",
    "MarketDataProvider",
    "MarketDataResult",
    "SourceAttempt",
    "StooqMarketDataProvider",
    "TimeoutError",
    "YFinanceMarketDataProvider",
    "batch_summary",
    "default_client",
    "five_day_return",
    "write_csv_cache",
]
