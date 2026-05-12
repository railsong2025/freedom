"""Position sizing calculator for the Poseidon Research Division.

Computes risk-based position sizes, ATR-based stops, Kelly criterion,
and position cap checks based on Buffett workflow parameters.
"""

from __future__ import annotations

import math

from interface.constants import (
    DEFAULT_INITIAL_POSITION_PCT_MAX,
    DEFAULT_INITIAL_POSITION_PCT_MIN,
    DEFAULT_RISK_PER_TRADE_PCT,
    DEFAULT_SLIPPAGE_USD,
    DEFAULT_STOP_LOSS_PCT_MAX,
    DEFAULT_STOP_LOSS_PCT_MIN,
    FEE_PER_TRADE_USD,
    SINGLE_STOCK_CAP_PCT,
)
from interface.models import RiskBudget


def risk_based_shares(
    equity: float,
    risk_per_trade_pct: float = DEFAULT_RISK_PER_TRADE_PCT,
    entry: float = 0.0,
    stop: float = 0.0,
    fee_per_trade: float = FEE_PER_TRADE_USD,
    slippage: float = DEFAULT_SLIPPAGE_USD,
    cash: float | None = None,
) -> int:
    """Compute max shares such that risk per trade <= equity * risk_pct/100.

    Risk per share = entry - stop plus round-trip slippage. Total risk includes
    both entry and exit fees. If cash is supplied, the result is also capped by
    fee-inclusive BUY affordability.
    """
    if equity <= 0 or entry <= 0 or stop <= 0 or entry <= stop:
        return 0
    max_risk_usd = equity * risk_per_trade_pct / 100.0
    risk_per_share = entry - stop + 2 * slippage
    if risk_per_share <= 0:
        return 0
    # max_risk_usd >= shares * risk_per_share + two fees
    shares = int((max_risk_usd - 2 * fee_per_trade) / risk_per_share)
    if cash is not None:
        affordable = int((cash - fee_per_trade) / entry) if cash > fee_per_trade else 0
        shares = min(shares, affordable)
    return max(0, shares)


def atr_based_stop(entry: float, atr_value: float, multiplier: float = 1.5) -> float:
    """Stop price = entry - multiplier * ATR(14)."""
    if entry <= 0 or atr_value <= 0 or multiplier <= 0:
        return 0.0
    stop = entry - multiplier * atr_value
    return round(max(0.01, stop), 4)


def position_size_check(
    shares: int,
    entry: float,
    equity: float,
    max_position_pct: float = SINGLE_STOCK_CAP_PCT,
) -> bool:
    """Return True if shares * entry / equity <= max_position_pct/100."""
    if equity <= 0:
        return False
    return (shares * entry) / equity <= max_position_pct / 100.0


def position_pct(
    shares: int,
    entry: float,
    equity: float,
) -> float:
    """Position as percentage of equity."""
    if equity <= 0:
        return 0.0
    return (shares * entry) / equity * 100.0


def kelly_fraction(win_prob: float, avg_win: float, avg_loss: float) -> float:
    """Kelly criterion: f* = p - (1-p) / (avg_win / avg_loss).

    Capped at [0, 1]. Returns 0 if avg_loss is 0 or inputs are invalid.
    """
    if avg_loss <= 0 or win_prob < 0 or win_prob > 1:
        return 0.0
    if avg_win <= 0:
        return 0.0
    ratio = avg_win / avg_loss
    f = win_prob - (1 - win_prob) / ratio
    return max(0.0, min(1.0, f))


def fee_adjusted_entry_cost(
    shares: int,
    price: float,
    fee: float = FEE_PER_TRADE_USD,
) -> float:
    """Total cash outlay for a BUY: shares * price + fee."""
    return shares * price + fee


def fee_adjusted_sell_proceeds(
    shares: int,
    price: float,
    fee: float = FEE_PER_TRADE_USD,
) -> float:
    """Net cash from a SELL: shares * price - fee."""
    return shares * price - fee


def compute_sizing_summary(
    equity: float,
    entry: float,
    stop: float,
    current_position_value: float | None = None,
    fee_per_trade: float = FEE_PER_TRADE_USD,
    risk_per_trade_pct: float = DEFAULT_RISK_PER_TRADE_PCT,
    position_pct_min: float = DEFAULT_INITIAL_POSITION_PCT_MIN,
    position_pct_max: float = DEFAULT_INITIAL_POSITION_PCT_MAX,
    slippage: float = DEFAULT_SLIPPAGE_USD,
    cash: float | None = None,
) -> dict[str, object]:
    """Compute full sizing summary for a proposed trade."""
    risk_only_shares = risk_based_shares(
        equity, risk_per_trade_pct, entry, stop, fee_per_trade, slippage,
    )
    max_risk_shares = risk_based_shares(
        equity, risk_per_trade_pct, entry, stop, fee_per_trade, slippage, cash,
    )
    stop_distance_pct = ((entry - stop) / entry * 100) if entry > 0 else 0.0
    risk_per_share = entry - stop + 2 * slippage if entry > stop else 0.0
    total_risk = risk_per_share * max_risk_shares + 2 * fee_per_trade if max_risk_shares > 0 else 0.0
    entry_cost = fee_adjusted_entry_cost(max_risk_shares, entry, fee_per_trade) if max_risk_shares > 0 else 0.0
    risk_only_entry_cost = fee_adjusted_entry_cost(risk_only_shares, entry, fee_per_trade) if risk_only_shares > 0 else 0.0

    # Position size as % of equity
    if max_risk_shares > 0 and equity > 0:
        proposed_pct = position_pct(max_risk_shares, entry, equity)
    else:
        proposed_pct = 0.0

    # Check against position range
    in_range = position_pct_min <= proposed_pct <= position_pct_max
    below_min = proposed_pct < position_pct_min
    above_max = proposed_pct > position_pct_max

    # Cap check
    cap_ok = position_size_check(max_risk_shares, entry, equity, SINGLE_STOCK_CAP_PCT)

    # If current position exists, check total exposure
    total_position_value = current_position_value or 0.0
    new_total = total_position_value + max_risk_shares * entry if max_risk_shares > 0 else total_position_value
    total_pct = (new_total / equity * 100) if equity > 0 else 0.0

    return {
        "equity": equity,
        "entry": entry,
        "stop": stop,
        "stop_distance_pct": round(stop_distance_pct, 2),
        "risk_per_share": round(risk_per_share, 4),
        "risk_only_shares": risk_only_shares,
        "max_risk_shares": max_risk_shares,
        "total_risk_usd": round(total_risk, 2),
        "entry_cost_with_fee": round(entry_cost, 2),
        "cash": cash,
        "cash_sufficient": None if cash is None else cash >= risk_only_entry_cost,
        "cash_limited": False if cash is None else max_risk_shares < risk_only_shares,
        "position_pct": round(proposed_pct, 2),
        "in_initial_range": in_range,
        "below_min": below_min,
        "above_max": above_max,
        "single_stock_cap_ok": cap_ok,
        "total_position_pct_after": round(total_pct, 2),
    }
