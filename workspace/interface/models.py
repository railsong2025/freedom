"""Shared data models for project-local investment workflows.

All models use frozen dataclasses for immutability and hashability,
consistent with the DailyBar/SourceAttempt/MarketDataResult pattern
in workspace/interface/market_data.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Position:
    symbol: str
    shares: int
    avg_cost: float
    currency: str = "USD"


@dataclass(frozen=True)
class Portfolio:
    positions: tuple[Position, ...]
    cash: float
    cash_currency: str = "USD"


@dataclass(frozen=True)
class Trade:
    symbol: str
    action: str  # "BUY" or "SELL"
    shares: int
    limit_price: float


@dataclass(frozen=True)
class PositionPnL:
    symbol: str
    shares: int
    avg_cost: float
    current_price: float | None
    market_value: float | None
    cost_basis: float
    unrealized_pnl: float | None
    unrealized_pnl_pct: float | None
    currency: str = "USD"
    aggregation_status: str = "included"
    exclusion_reason: str | None = None


@dataclass(frozen=True)
class PortfolioPnL:
    positions: tuple[PositionPnL, ...]
    total_market_value: float | None
    total_cost_basis: float
    total_unrealized_pnl: float | None
    total_unrealized_pnl_pct: float | None
    total_equity: float | None
    cash: float
    valuation_notes: str
    cash_currency: str = "USD"
    priced_usd_market_value: float | None = None
    priced_usd_cost_basis: float | None = None
    priced_usd_unrealized_pnl: float | None = None
    priced_usd_unrealized_pnl_pct: float | None = None
    unpriced_usd_cost_basis: float = 0.0
    excluded_positions: tuple[str, ...] = ()


@dataclass(frozen=True)
class PostTradePnL:
    trades: tuple[Trade, ...]
    realized_pnl: float
    total_fees: float
    remaining_positions: tuple[Position, ...]
    remaining_cash: float
    remaining_portfolio_pnl: PortfolioPnL | None
    post_trade_equity: float | None
    skipped_trades: tuple[str, ...] = ()


@dataclass(frozen=True)
class RiskBudget:
    equity: float
    max_risk_per_trade_pct: float = 2.0
    max_position_pct: float = 25.0
    min_position_pct: float = 5.0
    max_position_pct_range: float = 8.0
    stop_loss_min_pct: float = 3.0
    stop_loss_max_pct: float = 5.0


@dataclass(frozen=True)
class FeeAdjustedRR:
    symbol: str
    entry: float
    stop: float
    target_1: float | None
    target_2: float | None
    fee_per_side: float
    slippage: float
    rr_target_1: float | None
    rr_target_2: float | None
    break_even_price: float
    verdict: str  # "positive_expectancy" / "marginal" / "insufficient" / "invalid"
    shares: int = 1


@dataclass(frozen=True)
class TradeVerdict:
    symbol: str
    action: str
    approved: bool
    reasons: tuple[str, ...]
    risk_usd: float | None
    fee_adjusted_rr: FeeAdjustedRR | None
    compliance_issues: tuple[str, ...]


@dataclass(frozen=True)
class SectorScoreResult:
    sector: str
    scores: dict[str, float]
    weighted_score: float
    rating: str  # overweight / tactical_overweight / neutral / underweight / avoid
    coverage_pct: float = 0.0
    missing_factors: tuple[str, ...] = ()
    invalid_factors: tuple[str, ...] = ()


@dataclass(frozen=True)
class StockScoreResult:
    symbol: str
    sector: str
    scores: dict[str, float]
    weighted_score: float
    tier: str  # core / tactical / watch / avoid
    coverage_pct: float = 0.0
    missing_factors: tuple[str, ...] = ()
    invalid_factors: tuple[str, ...] = ()


@dataclass(frozen=True)
class ShortTermScoreResult:
    symbol: str
    scores: dict[str, float]
    weighted_score: float
    action_bias: str  # actionable / tactical_only / watch / avoid
    coverage_pct: float = 0.0
    missing_factors: tuple[str, ...] = ()
    invalid_factors: tuple[str, ...] = ()


@dataclass(frozen=True)
class SwingTradeVerdict:
    symbol: str
    weighted_score: float
    action_bias: str
    rr_verdict: str
    verdict: str  # current_trade / small_starter / wait / hard_veto
    reasons: tuple[str, ...]
    triggered_vetoes: tuple[str, ...] = ()
    hard_vetoes: tuple[str, ...] = ()
    fallback_symbols: tuple[str, ...] = ()
    requires_fallback_review: bool = False


@dataclass(frozen=True)
class StressScenario:
    name: str
    description: str
    assumptions: dict[str, Any]
    portfolio_impact_usd: float | None
    portfolio_impact_pct: float | None
    worst_position: str | None
    worst_position_impact_pct: float | None
    excluded_positions: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    details: dict[str, Any]
