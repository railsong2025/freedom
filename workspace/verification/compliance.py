"""Compliance checks for the Hades Verification Division.

Enforces Buffett Investment Team risk rules:
- 25% single stock cap
- 2% risk budget per trade
- 3-5% stop loss distance
- 5-8% initial position range
- Cash sufficiency for proposed trades
- Integer shares requirement
"""

from __future__ import annotations

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
from interface.models import (
    Portfolio,
    Position,
    RiskBudget,
    Trade,
    ValidationResult,
)


def check_single_stock_cap(
    position_value: float,
    equity: float,
    max_pct: float = SINGLE_STOCK_CAP_PCT,
) -> ValidationResult:
    """Check if a single position exceeds the 25% cap."""
    errors: list[str] = []
    warnings: list[str] = []
    if equity <= 0:
        errors.append(f"equity must be positive, got {equity}")
        return ValidationResult(passed=False, errors=tuple(errors), warnings=tuple(warnings), details={})
    pct = position_value / equity * 100
    if pct > max_pct:
        errors.append(f"single stock cap exceeded: {pct:.1f}% > {max_pct:.0f}%")
    elif pct > max_pct * 0.8:
        warnings.append(f"single stock near cap: {pct:.1f}% (limit {max_pct:.0f}%)")
    return ValidationResult(
        passed=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
        details={"position_pct": round(pct, 2), "max_pct": max_pct},
    )


def check_risk_budget(
    shares: int,
    entry: float,
    stop: float,
    equity: float,
    risk_pct: float = DEFAULT_RISK_PER_TRADE_PCT,
    fee: float = FEE_PER_TRADE_USD,
    slippage: float = DEFAULT_SLIPPAGE_USD,
) -> ValidationResult:
    """Check if a trade's risk stays within the 2% risk budget."""
    errors: list[str] = []
    warnings: list[str] = []
    if equity <= 0:
        errors.append(f"equity must be positive, got {equity}")
        return ValidationResult(passed=False, errors=tuple(errors), warnings=tuple(warnings), details={})
    if entry <= 0:
        errors.append(f"entry price must be positive, got {entry}")
        return ValidationResult(passed=False, errors=tuple(errors), warnings=tuple(warnings), details={})
    if stop >= entry:
        errors.append(f"stop {stop} must be below entry {entry}")
        return ValidationResult(passed=False, errors=tuple(errors), warnings=tuple(warnings), details={})

    risk_per_share = entry - stop + 2 * slippage
    total_risk = shares * risk_per_share + 2 * fee
    max_risk = equity * risk_pct / 100
    actual_risk_pct = total_risk / equity * 100

    if total_risk > max_risk:
        errors.append(f"risk budget exceeded: ${total_risk:.2f} > ${max_risk:.2f} ({actual_risk_pct:.2f}% > {risk_pct:.0f}%)")
    elif total_risk > max_risk * 0.8:
        warnings.append(f"risk near budget: ${total_risk:.2f} ({actual_risk_pct:.2f}% of {risk_pct:.0f}%)")

    return ValidationResult(
        passed=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
        details={
            "total_risk_usd": round(total_risk, 2),
            "max_risk_usd": round(max_risk, 2),
            "actual_risk_pct": round(actual_risk_pct, 2),
            "risk_pct_limit": risk_pct,
            "fee_per_side_usd": fee,
            "round_trip_fee_usd": 2 * fee,
        },
    )


def check_stop_loss_distance(
    entry: float,
    stop: float,
    min_pct: float = DEFAULT_STOP_LOSS_PCT_MIN,
    max_pct: float = DEFAULT_STOP_LOSS_PCT_MAX,
) -> ValidationResult:
    """Check if stop loss is within the 3-5% distance range."""
    errors: list[str] = []
    warnings: list[str] = []
    if entry <= 0:
        errors.append(f"entry price must be positive, got {entry}")
        return ValidationResult(passed=False, errors=tuple(errors), warnings=tuple(warnings), details={})
    if stop >= entry:
        errors.append(f"stop {stop} must be below entry {entry}")
        return ValidationResult(passed=False, errors=tuple(errors), warnings=tuple(warnings), details={})

    stop_pct = (entry - stop) / entry * 100
    epsilon = 1e-9
    if stop_pct < min_pct - epsilon:
        errors.append(f"stop too tight: {stop_pct:.2f}% < {min_pct:.0f}% minimum")
    elif stop_pct > max_pct + epsilon:
        errors.append(f"stop too wide: {stop_pct:.2f}% > {max_pct:.0f}% maximum")

    return ValidationResult(
        passed=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
        details={"stop_distance_pct": round(stop_pct, 2), "min_pct": min_pct, "max_pct": max_pct},
    )


def check_position_range(
    pct: float,
    min_pct: float = DEFAULT_INITIAL_POSITION_PCT_MIN,
    max_pct: float = DEFAULT_INITIAL_POSITION_PCT_MAX,
) -> ValidationResult:
    """Check if initial position size is within the 5-8% range."""
    errors: list[str] = []
    warnings: list[str] = []
    if pct < min_pct:
        errors.append(f"position too small: {pct:.2f}% < {min_pct:.0f}% minimum")
    elif pct > max_pct:
        errors.append(f"position too large: {pct:.2f}% > {max_pct:.0f}% maximum")

    return ValidationResult(
        passed=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
        details={"position_pct": round(pct, 2), "min_pct": min_pct, "max_pct": max_pct},
    )


def check_cash_sufficiency(
    cash: float,
    trade: Trade,
    fee: float = FEE_PER_TRADE_USD,
    cash_currency: str = "USD",
) -> ValidationResult:
    """Check if there's enough cash for a BUY trade (shares * price + fee)."""
    errors: list[str] = []
    warnings: list[str] = []
    if trade.action != "BUY":
        return ValidationResult(
            passed=True, errors=(), warnings=(),
            details={"action": trade.action, "note": "cash check only applies to BUY"},
        )
    if cash_currency != "USD":
        errors.append(f"cash currency must be USD for US-equity BUY, got {cash_currency}")
        return ValidationResult(
            passed=False,
            errors=tuple(errors),
            warnings=tuple(warnings),
            details={"required_currency": "USD", "cash_currency": cash_currency},
        )
    required = trade.shares * trade.limit_price + fee
    if cash < required:
        errors.append(f"insufficient cash: ${cash:.2f} < ${required:.2f} ({trade.shares} x ${trade.limit_price:.2f} + ${fee:.2f})")
    elif cash < required * 1.1:
        warnings.append(f"cash near minimum: ${cash:.2f} barely covers ${required:.2f}")

    return ValidationResult(
        passed=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
        details={"required_cash": round(required, 2), "available_cash": round(cash, 2), "cash_currency": cash_currency},
    )


def check_integer_shares(shares: float) -> ValidationResult:
    """Check that shares are a positive integer (no fractional shares)."""
    errors: list[str] = []
    if shares != int(shares) or shares <= 0:
        errors.append(f"shares must be positive integer, got {shares}")
    return ValidationResult(
        passed=len(errors) == 0,
        errors=tuple(errors),
        warnings=(),
        details={"shares": shares, "is_integer": shares == int(shares)},
    )


def run_full_compliance(
    portfolio: Portfolio,
    trades: list[Trade],
    prices: dict[str, float | None],
    stops: dict[str, float],
    risk_budget: RiskBudget | None = None,
) -> list[ValidationResult]:
    """Run all compliance checks for proposed trades.

    Returns a list of ValidationResult objects, one per check category.
    """
    if risk_budget is None:
        risk_budget = RiskBudget(equity=0)

    # Estimate equity from portfolio
    total_mv = 0.0
    for pos in portfolio.positions:
        price = prices.get(pos.symbol)
        if price is not None and price > 0:
            total_mv += pos.shares * price
    equity = total_mv + portfolio.cash if portfolio.cash_currency == "USD" else total_mv
    if risk_budget.equity <= 0:
        risk_budget = RiskBudget(
            equity=equity,
            max_risk_per_trade_pct=risk_budget.max_risk_per_trade_pct,
            max_position_pct=risk_budget.max_position_pct,
            min_position_pct=risk_budget.min_position_pct,
            max_position_pct_range=risk_budget.max_position_pct_range,
            stop_loss_min_pct=risk_budget.stop_loss_min_pct,
            stop_loss_max_pct=risk_budget.stop_loss_max_pct,
        )
    equity = risk_budget.equity

    results: list[ValidationResult] = []

    # Integer shares check for all trades
    for trade in trades:
        results.append(check_integer_shares(trade.shares))

    running_cash = portfolio.cash if portfolio.cash_currency == "USD" else 0.0
    post_positions: dict[str, int] = {p.symbol: p.shares for p in portfolio.positions if p.currency == "USD"}

    # Per-trade checks
    for trade in trades:
        price = prices.get(trade.symbol, trade.limit_price) or trade.limit_price
        position_value = trade.shares * price

        # Single stock cap
        if equity > 0:
            results.append(check_single_stock_cap(position_value, equity, risk_budget.max_position_pct))

        # Risk budget (for BUY trades with stop)
        if trade.action == "BUY" and trade.symbol in stops:
            results.append(check_risk_budget(
                trade.shares, trade.limit_price, stops[trade.symbol],
                risk_budget.equity, risk_budget.max_risk_per_trade_pct,
            ))

        # Stop loss distance
        if trade.symbol in stops:
            results.append(check_stop_loss_distance(
                trade.limit_price, stops[trade.symbol],
                risk_budget.stop_loss_min_pct, risk_budget.stop_loss_max_pct,
            ))

        # Position range
        if equity > 0:
            pct = position_value / equity * 100
            results.append(check_position_range(
                pct, risk_budget.min_position_pct, risk_budget.max_position_pct_range,
            ))

        # Cash sufficiency
        if trade.action == "BUY":
            cash_result = check_cash_sufficiency(running_cash, trade, cash_currency=portfolio.cash_currency)
            results.append(cash_result)
            if cash_result.passed:
                running_cash -= trade.shares * trade.limit_price + FEE_PER_TRADE_USD
                post_positions[trade.symbol] = post_positions.get(trade.symbol, 0) + trade.shares
        elif trade.action == "SELL":
            held = post_positions.get(trade.symbol, 0)
            if trade.shares <= held:
                running_cash += trade.shares * trade.limit_price - FEE_PER_TRADE_USD
                remaining = held - trade.shares
                if remaining:
                    post_positions[trade.symbol] = remaining
                elif trade.symbol in post_positions:
                    del post_positions[trade.symbol]

    # Existing position cap checks
    for pos in portfolio.positions:
        price = prices.get(pos.symbol)
        if price is not None and price > 0 and equity > 0:
            pos_value = pos.shares * price
            results.append(check_single_stock_cap(pos_value, equity, risk_budget.max_position_pct))

    # Post-trade merged position cap checks. A BUY into an existing position must
    # be evaluated on the combined exposure, not only the proposed order slice.
    if equity > 0:
        for symbol, shares in sorted(post_positions.items()):
            price = prices.get(symbol)
            if price is None or price <= 0:
                matching_trade = next((t for t in trades if t.symbol == symbol), None)
                price = matching_trade.limit_price if matching_trade else None
            if price is None or price <= 0:
                continue
            result = check_single_stock_cap(shares * price, equity, risk_budget.max_position_pct)
            if not result.passed or result.warnings:
                results.append(
                    ValidationResult(
                        passed=result.passed,
                        errors=tuple(f"post-trade {symbol}: {e}" for e in result.errors),
                        warnings=tuple(f"post-trade {symbol}: {w}" for w in result.warnings),
                        details={**result.details, "symbol": symbol, "shares_after": shares},
                    )
                )

    return results
