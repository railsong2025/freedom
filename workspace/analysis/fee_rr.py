"""Fee-adjusted risk/reward calculator for the Poseidon Research Division.

Computes forward-looking risk/reward ratios incorporating the USD 5 per-trade
fee and configurable slippage, matching the Buffett workflow requirements.
"""

from __future__ import annotations

from interface.constants import DEFAULT_SLIPPAGE_USD, FEE_PER_TRADE_USD
from interface.models import FeeAdjustedRR


def fee_adjusted_rr(
    entry: float,
    stop: float,
    target: float,
    fee_per_side: float = FEE_PER_TRADE_USD,
    slippage: float = DEFAULT_SLIPPAGE_USD,
    shares: int = 1,
) -> float:
    """Compute fee-adjusted risk/reward ratio.

    R/R = ((target - entry) * shares - 2 fees - 2 slippage)
          / ((entry - stop) * shares + 2 fees + 2 slippage)

    Returns negative if inputs are invalid (e.g., stop >= entry for long, or
    target <= entry).
    """
    if entry <= 0 or stop <= 0 or target <= 0 or shares <= 0:
        return -1.0
    if stop >= entry:
        return -1.0  # Invalid stop for long position
    if target <= entry:
        return -1.0
    round_trip_fees = 2 * fee_per_side
    round_trip_slippage = 2 * slippage * shares
    reward = (target - entry) * shares - round_trip_fees - round_trip_slippage
    risk = (entry - stop) * shares + round_trip_fees + round_trip_slippage
    if risk <= 0:
        return -1.0
    return reward / risk


def break_even_price(
    entry: float,
    fee_per_side: float = FEE_PER_TRADE_USD,
    slippage: float = DEFAULT_SLIPPAGE_USD,
    shares: int = 1,
) -> float:
    """Minimum exit price for net-zero P&L including round-trip fees.

    break_even = entry + (2 * fee + 2 * slippage) / shares
    """
    if shares <= 0:
        return entry
    return entry + (2 * fee_per_side + 2 * slippage) / shares


def multi_target_rr(
    entry: float,
    stop: float,
    targets: list[float],
    fee_per_side: float = FEE_PER_TRADE_USD,
    slippage: float = DEFAULT_SLIPPAGE_USD,
    symbol: str = "",
    shares: int = 1,
) -> list[FeeAdjustedRR]:
    """Compute R/R for each target level, returning FeeAdjustedRR per target."""
    be = break_even_price(entry, fee_per_side, slippage, shares)
    results: list[FeeAdjustedRR] = []
    for i, target in enumerate(targets):
        rr = fee_adjusted_rr(entry, stop, target, fee_per_side, slippage, shares)
        verdict = rr_verdict(rr)
        results.append(FeeAdjustedRR(
            symbol=symbol,
            entry=entry,
            stop=stop,
            target_1=target,
            target_2=targets[i + 1] if i + 1 < len(targets) else None,
            fee_per_side=fee_per_side,
            slippage=slippage,
            rr_target_1=round(rr, 4) if rr is not None and rr >= 0 else None,
            rr_target_2=None,
            break_even_price=round(be, 4),
            verdict=verdict,
            shares=shares,
        ))
    return results


def rr_verdict(rr: float | None) -> str:
    """Classify R/R ratio.

    - "positive_expectancy" if rr >= 2.0
    - "marginal" if 1.0 <= rr < 2.0
    - "insufficient" if 0 < rr < 1.0
    - "invalid" if rr is None or negative
    """
    if rr is None or rr < 0:
        return "invalid"
    if rr >= 2.0:
        return "positive_expectancy"
    if rr >= 1.0:
        return "marginal"
    return "insufficient"
