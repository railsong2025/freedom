"""Shared constants for project-local investment workflows.

Numeric parameters are sourced from AGENTS.md and shared skill contracts.
Some symbol and sector mappings are project aliases used by multiple public
modules; they are not private to any single runner.
"""

from __future__ import annotations

# ── Trade fees ──────────────────────────────────────────────────────────────

FEE_PER_TRADE_USD: float = 5.0
DEFAULT_SLIPPAGE_USD: float = 0.05

# ── Risk budget defaults ────────────────────────────────────────────────────

DEFAULT_RISK_PER_TRADE_PCT: float = 2.0
DEFAULT_INITIAL_POSITION_PCT_MIN: float = 5.0
DEFAULT_INITIAL_POSITION_PCT_MAX: float = 8.0
DEFAULT_STOP_LOSS_PCT_MIN: float = 3.0
DEFAULT_STOP_LOSS_PCT_MAX: float = 5.0
SINGLE_STOCK_CAP_PCT: float = 25.0

# ── Sector scorecard weights (from sector-stock-playbook.md) ───────────────

SECTOR_WEIGHTS: dict[str, float] = {
    "market_regime_fit": 10,
    "relative_strength_breadth": 15,
    "earnings_revision": 15,
    "supply_demand_pricing": 15,
    "catalyst_quality": 15,
    "valuation_expectations": 10,
    "capital_flow_crowding": 10,
    "policy_geopolitical_risk": 10,
}

# ── Stock scorecard weights (from sector-stock-playbook.md) ─────────────────

STOCK_WEIGHTS: dict[str, float] = {
    "direct_beneficiary": 15,
    "moat_profit_pool": 15,
    "earnings_visibility": 15,
    "valuation_margin_safety": 15,
    "balance_sheet_cash_conversion": 10,
    "catalyst_timing": 10,
    "liquidity_technical_quality": 10,
    "risk_concentration": 10,
}

# ── Short-term scorecard weights (from sector-stock-playbook.md) ────────────

SHORT_TERM_WEIGHTS: dict[str, float] = {
    "sector_theme_heat": 15,
    "relative_strength": 15,
    "volume_liquidity": 15,
    "technical_setup_quality": 20,
    "catalyst_freshness": 10,
    "fee_adjusted_risk_reward": 15,
    "crowding_reversal_risk": 10,
}

# ── Sector rating thresholds ───────────────────────────────────────────────

SECTOR_RATING_THRESHOLDS: list[tuple[float, str]] = [
    (80.0, "overweight"),
    (70.0, "tactical_overweight"),
    (60.0, "neutral"),
    (45.0, "underweight"),
    (0.0, "avoid"),
]

# ── Stock tier thresholds ──────────────────────────────────────────────────

STOCK_TIER_THRESHOLDS: list[tuple[float, str]] = [
    (80.0, "core"),
    (70.0, "tactical"),
    (60.0, "watch"),
    (0.0, "avoid"),
]

# ── Short-term action thresholds ───────────────────────────────────────────

SHORT_TERM_THRESHOLDS: list[tuple[float, str]] = [
    (80.0, "actionable"),
    (70.0, "tactical_only"),
    (60.0, "watch"),
    (0.0, "avoid"),
]

# ── Benchmark and sector ETF symbols ───────────────────────────────────────

BENCHMARK_SYMBOLS: tuple[str, ...] = ("SPY", "QQQ")

NON_TRADABLE_INDEX_SYMBOLS: tuple[str, ...] = (
    "IXIC",
    "SPX",
    "GSPC",
    "INX",
    "SP500",
)

INDEX_PROXY_ETF_TO_BENCHMARK: dict[str, str] = {
    "SPY": "S&P 500",
    "QQQ": "Nasdaq 100 / Nasdaq growth proxy",
}

MARKET_INDEX_BENCHMARKS: dict[str, dict[str, object]] = {
    "NASDAQ_COMPOSITE": {
        "name": "Nasdaq Composite",
        "index_code": "IXIC",
        "index_code_candidates": ("IXIC",),
        "tradable_proxy": "QQQ",
        "aliases": ("纳斯达克", "纳指", "纳斯达克综合指数", "NASDAQ", "IXIC"),
    },
    "SP500": {
        "name": "S&P 500",
        "index_code": None,
        "index_code_candidates": ("SPX", "GSPC", "INX", "SP500"),
        "tradable_proxy": "SPY",
        "aliases": ("标普", "标普500", "标普 500", "S&P 500", "SP500", "SPX", "GSPC"),
    },
}

SECTOR_ETF_SYMBOLS: dict[str, tuple[str, ...]] = {
    "semiconductor": ("SMH", "SOXX"),
    "technology": ("XLK",),
    "communication": ("XLC",),
    "consumer_discretionary": ("XLY",),
    "industrial": ("XLI",),
    "utility": ("XLU",),
    "financial": ("XLF",),
    "healthcare": ("XLV",),
    "consumer_staples": ("XLP",),
    "energy": ("XLE",),
    "materials": ("XLB",),
    "real_estate": ("XLRE",),
}

# ── Ticker-to-sector mapping ───────────────────────────────────────────────

TICKER_SECTOR_MAP: dict[str, str] = {
    # Semiconductors
    "MU": "semiconductor",
    "WDC": "semiconductor",
    "STX": "semiconductor",
    "AMD": "semiconductor",
    "NVDA": "semiconductor",
    "TSM": "semiconductor",
    "ANET": "semiconductor",
    "INTC": "semiconductor",
    "PLAB": "semiconductor",
    "MRVL": "semiconductor",
    # Technology
    "MSFT": "technology",
    "FLEX": "technology",
    "JBL": "technology",
    "CLS": "technology",
    # Communication services
    "TSLA": "consumer_discretionary",
    # Consumer staples
    "KO": "consumer_staples",
    # Broad market ETFs (not a real sector)
    "SPY": "broad_market",
    "QQQ": "broad_market",
    "DIA": "broad_market",
    "IXIC": "broad_market_index",
    "SPX": "broad_market_index",
    "GSPC": "broad_market_index",
    "INX": "broad_market_index",
    "SP500": "broad_market_index",
    "SMH": "semiconductor",
    "SOXX": "semiconductor",
    "XLK": "technology",
    "XLC": "communication",
    "XLY": "consumer_discretionary",
    "XLI": "industrial",
    "XLU": "utility",
    "XLF": "financial",
    "XLV": "healthcare",
    "XLP": "consumer_staples",
    "XLE": "energy",
    "XLB": "materials",
    "XLRE": "real_estate",
}

# ── Stress test default shocks ─────────────────────────────────────────────

STRESS_SHOCKS: dict[str, float] = {
    "portfolio_mild": -0.10,
    "portfolio_moderate": -0.20,
    "portfolio_severe": -0.30,
}

# ── Veto conditions (from sector-stock-playbook.md) ────────────────────────

VETO_CONDITIONS: tuple[str, ...] = (
    "single_source_critical_data",
    "stale_data",
    "narrative_only_beneficiary",
    "valuation_assumes_best_case",
    "fomo_justified",
    "guaranteed_profit_language",
    "inadequate_liquidity",
    "accounting_governance_risk",
    "sanctions_export_risk",
    "customer_concentration",
    "stress_loss_exceeds_risk_budget",
)

# ── Chinese stock name to ticker mapping (for base_short.md parsing) ───────

CHINESE_NAME_TO_TICKER: dict[str, str] = {
    "腾讯控股": "0700.HK",
    "可口可乐": "KO",
    "微软": "MSFT",
    "英伟达": "NVDA",
    "标普500": "SPY",
    "标普 500": "SPY",
    "标普": "SPY",
    "纳斯达克": "QQQ",
    "纳指": "QQQ",
    "纳指100": "QQQ",
    "纳斯达克100": "QQQ",
    "特斯拉": "TSLA",
    "超威半导体": "AMD",
    "台积电": "TSM",
    "迈威尔科技": "MRVL",
    "迈威尔": "MRVL",
}

# ── Beta approximations for stress testing ─────────────────────────────────

DEFAULT_BETA_MAP: dict[str, float] = {
    "MU": 1.6,
    "WDC": 1.5,
    "STX": 1.4,
    "AMD": 1.8,
    "NVDA": 2.0,
    "TSM": 1.3,
    "ANET": 1.4,
    "INTC": 1.2,
    "VRT": 1.6,
    "FLEX": 1.2,
    "PLAB": 1.5,
    "JBL": 1.1,
    "CLS": 1.3,
    "MRVL": 1.7,
    "TSLA": 2.0,
    "KO": 0.6,
    "MSFT": 0.9,
    "SPY": 1.0,
    "QQQ": 1.1,
    "SMH": 1.7,
    "SOXX": 1.6,
}
