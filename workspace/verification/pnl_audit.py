"""P&L audit calculator for the Hades Verification Division.

Validates P&L calculations, fee application, integer shares, and
average-cost method consistency.
"""

from __future__ import annotations

from interface.constants import FEE_PER_TRADE_USD
from interface.models import (
    Portfolio,
    PortfolioPnL,
    Position,
    PositionPnL,
    PostTradePnL,
    Trade,
    ValidationResult,
)


def audit_position_pnl(
    position: Position,
    current_price: float | None,
    reported_pnl: PositionPnL | None = None,
) -> ValidationResult:
    """Verify a single position's P&L calculation."""
    errors: list[str] = []
    warnings: list[str] = []

    # Integer shares check
    if position.shares != int(position.shares) or position.shares <= 0:
        errors.append(f"{position.symbol}: shares must be positive integer, got {position.shares}")

    # Cost basis check
    expected_cost_basis = position.shares * position.avg_cost
    if position.avg_cost <= 0:
        errors.append(f"{position.symbol}: avg_cost must be positive, got {position.avg_cost}")

    # P&L computation check
    if current_price is not None and current_price > 0:
        expected_mv = position.shares * current_price
        expected_pnl = expected_mv - expected_cost_basis
        expected_pct = (expected_pnl / expected_cost_basis * 100) if expected_cost_basis > 0 else None

        if reported_pnl is not None:
            if reported_pnl.market_value is not None:
                if abs(reported_pnl.market_value - expected_mv) > 0.02:
                    errors.append(
                        f"{position.symbol}: market_value mismatch: reported {reported_pnl.market_value}, "
                        f"expected {expected_mv:.2f}"
                    )
            if reported_pnl.unrealized_pnl is not None:
                if abs(reported_pnl.unrealized_pnl - expected_pnl) > 0.02:
                    errors.append(
                        f"{position.symbol}: unrealized_pnl mismatch: reported {reported_pnl.unrealized_pnl}, "
                        f"expected {expected_pnl:.2f}"
                    )
            if reported_pnl.cost_basis is not None:
                if abs(reported_pnl.cost_basis - expected_cost_basis) > 0.02:
                    errors.append(
                        f"{position.symbol}: cost_basis mismatch: reported {reported_pnl.cost_basis}, "
                        f"expected {expected_cost_basis:.2f}"
                    )

    return ValidationResult(
        passed=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
        details={"symbol": position.symbol, "shares": position.shares, "avg_cost": position.avg_cost},
    )


def audit_portfolio_pnl(
    portfolio: Portfolio,
    prices: dict[str, float | None],
    reported_pnl: PortfolioPnL | None = None,
) -> ValidationResult:
    """Verify total P&L = sum of position P&Ls and equity = market_value + cash."""
    errors: list[str] = []
    warnings: list[str] = []

    computed_positions: list[PositionPnL] = []
    total_mv = 0.0
    total_cost = 0.0
    has_any_price = False

    for pos in portfolio.positions:
        pnl = PositionPnL(
            symbol=pos.symbol, shares=pos.shares, avg_cost=pos.avg_cost,
            current_price=prices.get(pos.symbol),
            market_value=None, cost_basis=pos.shares * pos.avg_cost,
            unrealized_pnl=None, unrealized_pnl_pct=None,
            currency=pos.currency,
        )
        if prices.get(pos.symbol) is not None and prices[pos.symbol] > 0:
            price = prices[pos.symbol]
            mv = pos.shares * price
            pnl = PositionPnL(
                symbol=pos.symbol, shares=pos.shares, avg_cost=pos.avg_cost,
                current_price=price, market_value=round(mv, 2),
                cost_basis=round(pos.shares * pos.avg_cost, 2),
                unrealized_pnl=round(mv - pos.shares * pos.avg_cost, 2),
                unrealized_pnl_pct=round((mv - pos.shares * pos.avg_cost) / (pos.shares * pos.avg_cost) * 100, 2) if pos.avg_cost > 0 else None,
                currency=pos.currency,
            )
            if pos.currency == "USD":
                total_mv += mv
                total_cost += pos.shares * pos.avg_cost
                has_any_price = True
        computed_positions.append(pnl)

    if reported_pnl is not None:
        if reported_pnl.total_cost_basis is not None:
            if abs(reported_pnl.total_cost_basis - total_cost) > 0.02:
                errors.append(f"total_cost_basis mismatch: reported {reported_pnl.total_cost_basis}, expected {total_cost:.2f}")
        if has_any_price and reported_pnl.total_market_value is not None:
            if abs(reported_pnl.total_market_value - total_mv) > 0.02:
                errors.append(f"total_market_value mismatch: reported {reported_pnl.total_market_value}, expected {total_mv:.2f}")

    return ValidationResult(
        passed=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
        details={
            "position_count": len(portfolio.positions),
            "total_cost_basis": round(total_cost, 2),
            "total_market_value": round(total_mv, 2) if has_any_price else None,
        },
    )


def audit_post_trade_pnl(
    portfolio: Portfolio,
    trades: list[Trade],
    prices: dict[str, float | None],
    reported: PostTradePnL | None = None,
    fee: float = FEE_PER_TRADE_USD,
) -> ValidationResult:
    """Verify post-trade P&L: fee application, cash, shares, realized P&L."""
    errors: list[str] = []
    warnings: list[str] = []
    expected = _simulate_post_trade_independently(portfolio, trades, fee)
    if expected["skipped_trades"]:
        errors.extend(str(item) for item in expected["skipped_trades"])

    if reported is not None:
        if tuple(reported.skipped_trades) != tuple(expected["skipped_trades"]):
            errors.append(
                f"skipped_trades mismatch: reported {tuple(reported.skipped_trades)}, expected {tuple(expected['skipped_trades'])}"
            )
        if abs(reported.total_fees - expected["total_fees"]) > 0.01:
            errors.append(f"total_fees mismatch: reported {reported.total_fees}, expected {expected['total_fees']}")
        if abs(reported.realized_pnl - expected["realized_pnl"]) > 0.01:
            errors.append(f"realized_pnl mismatch: reported {reported.realized_pnl}, expected {expected['realized_pnl']}")
        if abs(reported.remaining_cash - expected["remaining_cash"]) > 0.01:
            errors.append(f"remaining_cash mismatch: reported {reported.remaining_cash}, expected {expected['remaining_cash']}")
        reported_positions = {p.symbol: p for p in reported.remaining_positions}
        for expected_position in expected["remaining_positions"]:
            reported_position = reported_positions.get(expected_position.symbol)
            if reported_position is None:
                errors.append(f"{expected_position.symbol}: missing remaining position")
                continue
            if reported_position.shares != expected_position.shares:
                errors.append(
                    f"{expected_position.symbol}: remaining shares mismatch: "
                    f"reported {reported_position.shares}, expected {expected_position.shares}"
                )
            if abs(reported_position.avg_cost - expected_position.avg_cost) > 0.01:
                errors.append(
                    f"{expected_position.symbol}: avg_cost mismatch: "
                    f"reported {reported_position.avg_cost:.4f}, expected {expected_position.avg_cost:.4f}"
                )
            if reported_position.currency != expected_position.currency:
                errors.append(
                    f"{expected_position.symbol}: currency mismatch: "
                    f"reported {reported_position.currency}, expected {expected_position.currency}"
                )

    # Check each trade for integer shares and fee
    for trade in trades:
        if trade.shares != int(trade.shares) or trade.shares <= 0:
            errors.append(f"{trade.action} {trade.symbol}: shares must be positive integer, got {trade.shares}")
        if trade.limit_price <= 0:
            errors.append(f"{trade.action} {trade.symbol}: limit_price must be positive, got {trade.limit_price}")

    return ValidationResult(
        passed=len(errors) == 0,
        errors=tuple(errors),
        warnings=tuple(warnings),
        details={
            "trade_count": len(trades),
            "executed_trades": expected["executed_trades"],
            "total_fees": expected["total_fees"],
            "realized_pnl": expected["realized_pnl"],
            "remaining_cash": expected["remaining_cash"],
            "skipped_trades": expected["skipped_trades"],
        },
    )


def _simulate_post_trade_independently(
    portfolio: Portfolio,
    trades: list[Trade],
    fee: float,
) -> dict[str, object]:
    pos_map: dict[str, list[float | str]] = {
        p.symbol: [float(p.shares), p.avg_cost, p.currency]
        for p in portfolio.positions
    }
    cash = portfolio.cash
    realized_pnl = 0.0
    total_fees = 0.0
    executed_trades = 0
    skipped_trades: list[str] = []

    for trade in trades:
        if portfolio.cash_currency != "USD":
            skipped_trades.append(
                f"{trade.action} {trade.symbol} x{trade.shares}: cash currency {portfolio.cash_currency} cannot be used for USD trade projection without FX conversion"
            )
            continue
        if trade.action == "BUY":
            cash_required = trade.shares * trade.limit_price + fee
            if cash < cash_required:
                skipped_trades.append(f"BUY {trade.symbol} x{trade.shares}: insufficient cash ({cash:.2f} < {cash_required:.2f})")
                continue
            cash -= cash_required
            total_fees += fee
            executed_trades += 1
            if trade.symbol in pos_map:
                old_shares, old_avg_cost, currency = pos_map[trade.symbol]
                new_shares = float(old_shares) + trade.shares
                new_avg_cost = (
                    float(old_shares) * float(old_avg_cost)
                    + trade.shares * trade.limit_price
                    + fee
                ) / new_shares
                pos_map[trade.symbol] = [new_shares, new_avg_cost, currency]
            else:
                pos_map[trade.symbol] = [
                    float(trade.shares),
                    (trade.shares * trade.limit_price + fee) / trade.shares,
                    "USD",
                ]
        elif trade.action == "SELL":
            if trade.symbol not in pos_map:
                skipped_trades.append(f"SELL {trade.symbol} x{trade.shares}: position not found")
                continue
            current_shares, avg_cost, currency = pos_map[trade.symbol]
            if currency != "USD":
                skipped_trades.append(f"SELL {trade.symbol} x{trade.shares}: non-USD position currency {currency} requires FX-aware projection")
                continue
            if trade.shares > int(current_shares):
                skipped_trades.append(f"SELL {trade.symbol} x{trade.shares}: exceeds held {int(current_shares)}")
                continue
            cash += trade.shares * trade.limit_price - fee
            total_fees += fee
            realized_pnl += (trade.limit_price - float(avg_cost)) * trade.shares - fee
            executed_trades += 1
            remaining = float(current_shares) - trade.shares
            if remaining <= 0:
                del pos_map[trade.symbol]
            else:
                pos_map[trade.symbol] = [remaining, avg_cost, currency]

    remaining_positions = tuple(
        Position(symbol=symbol, shares=int(shares), avg_cost=float(avg_cost), currency=str(currency))
        for symbol, (shares, avg_cost, currency) in sorted(pos_map.items())
    )
    return {
        "executed_trades": executed_trades,
        "total_fees": round(total_fees, 2),
        "realized_pnl": round(realized_pnl, 2),
        "remaining_cash": round(cash, 2),
        "remaining_positions": remaining_positions,
        "skipped_trades": tuple(skipped_trades),
    }


def audit_fee_application(
    trades: list[Trade],
    expected_fee: float = FEE_PER_TRADE_USD,
    reported_total_fees: float | None = None,
) -> ValidationResult:
    """Verify total fees = number of trades * fee per side."""
    errors: list[str] = []
    expected_total = len(trades) * expected_fee

    if reported_total_fees is not None:
        if abs(reported_total_fees - expected_total) > 0.01:
            errors.append(f"fee mismatch: reported {reported_total_fees}, expected {expected_total}")

    return ValidationResult(
        passed=len(errors) == 0,
        errors=tuple(errors),
        warnings=(),
        details={"trade_count": len(trades), "fee_per_side": expected_fee, "expected_total": expected_total},
    )
