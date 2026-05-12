"""Shared parsers for project-local investment CLI tools."""

from __future__ import annotations

from interface.models import Position, Trade


def _flatten_items(items: str | list[str] | None, *, separators: tuple[str, ...]) -> list[str]:
    if not items:
        return []
    raw_items = [items] if isinstance(items, str) else items
    tokens: list[str] = []
    for item in raw_items:
        fragments = [item]
        for sep in separators:
            next_fragments: list[str] = []
            for fragment in fragments:
                next_fragments.extend(fragment.split(sep))
            fragments = next_fragments
        tokens.extend(fragment.strip() for fragment in fragments if fragment.strip())
    return tokens


def parse_price_items(items: str | list[str] | None) -> dict[str, float]:
    """Parse prices in SYMBOL=PRICE or SYMBOL:PRICE form.

    Accepts either comma-separated strings or argparse ``nargs`` lists.
    Invalid tokens are skipped.
    """
    prices: dict[str, float] = {}
    for token in _flatten_items(items, separators=(",", ";")):
        if "=" in token:
            symbol, price = token.split("=", 1)
        elif ":" in token:
            symbol, price = token.split(":", 1)
        else:
            continue
        try:
            parsed_price = float(price.strip())
            if parsed_price <= 0:
                continue
            prices[symbol.strip().upper()] = parsed_price
        except ValueError:
            continue
    return prices


def parse_trade_items(items: str | list[str] | None) -> list[Trade]:
    """Parse trades in SYMBOL:ACTION:SHARES:PRICE or SYMBOL=ACTION:SHARES:PRICE form."""
    trades: list[Trade] = []
    for token in _flatten_items(items, separators=(";",)):
        normalized = token.replace("=", ":", 1)
        parts = [part.strip() for part in normalized.split(":")]
        if len(parts) != 4:
            continue
        symbol, action, shares, price = parts
        try:
            normalized_action = action.upper()
            parsed_shares = int(shares)
            parsed_price = float(price)
            if normalized_action not in {"BUY", "SELL"} or parsed_shares <= 0 or parsed_price <= 0:
                continue
            trades.append(
                Trade(
                    symbol=symbol.upper(),
                    action=normalized_action,
                    shares=parsed_shares,
                    limit_price=parsed_price,
                )
            )
        except ValueError:
            continue
    return trades


def parse_stop_items(items: str | list[str] | None) -> dict[str, float]:
    """Parse stops in SYMBOL:STOP_PRICE or SYMBOL=STOP_PRICE form."""
    return parse_price_items(items)


def parse_position_items(items: str | list[str] | None) -> tuple[Position, ...]:
    """Parse positions in SYMBOL:SHARES:AVG_COST or SYMBOL=SHARES:AVG_COST form."""
    positions: list[Position] = []
    for token in _flatten_items(items, separators=(",", ";")):
        normalized = token.replace("=", ":", 1)
        parts = [part.strip() for part in normalized.split(":")]
        if len(parts) != 3:
            continue
        symbol, shares, avg_cost = parts
        try:
            parsed_shares = int(shares)
            parsed_cost = float(avg_cost)
            if parsed_shares <= 0 or parsed_cost <= 0:
                continue
            positions.append(Position(symbol=symbol.upper(), shares=parsed_shares, avg_cost=parsed_cost))
        except ValueError:
            continue
    return tuple(positions)
