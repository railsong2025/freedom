"""Portfolio tracker and P&L calculator for the Poseidon Research Division.

Parses base_short.md, computes per-position and total unrealized P&L,
and projects post-trade P&L with USD 5 fee logic.
"""

from __future__ import annotations

import re
from dataclasses import replace
from typing import Any

from interface.constants import CHINESE_NAME_TO_TICKER, FEE_PER_TRADE_USD
from interface.models import (
    Portfolio,
    PortfolioPnL,
    Position,
    PositionPnL,
    PostTradePnL,
    Trade,
)


def parse_base_short_positions(text: str) -> Portfolio:
    """Parse base_short.md text into a Portfolio model.

    Handles both USD and HKD positions. Looks for the latest position section
    (## record N操作后持仓 or ## 初始持仓) and the ## 可用资金 section.
    """
    positions: list[Position] = []
    cash = 0.0
    cash_currency = "USD"

    position_lines = _latest_position_lines(text)

    # Pattern: "- 名称：N 股，成本 X 单位" or "- Ticker：N shares，cost $X"
    position_patterns = [
        # Chinese format: "- 腾讯控股：400 股，成本 549 港元"
        re.compile(r"-\s*([^：]+?)\s*[：:]\s*(\d+)\s*股\s*[，,]\s*成本\s*([\d.]+)\s*(港元|美元|USD|HKD|\$)"),
        # English format: "- MSFT: 18 shares, cost $506.96"
        re.compile(r"-\s*([A-Z]{1,5}(?:\.[A-Z])?)\s*[：:]\s*(\d+)\s*股?\s*[，,]?\s*成本?\s*[\$￥]?\s*([\d.]+)\s*(港元|美元|USD|HKD|\$)?"),
        # Mixed format: "- 可口可乐：30 股，成本 77.52 美元"
        re.compile(r"-\s*([^\-：\n]+?)\s*[：:]\s*(\d+)\s*股\s*[，,]\s*成本\s*([\d.]+)\s*(港元|美元|USD|HKD)"),
    ]

    for line in position_lines:
        line = line.strip()
        for pattern in position_patterns:
            m = pattern.match(line)
            if m:
                name_or_ticker = m.group(1).strip()
                shares = int(m.group(2))
                cost = float(m.group(3))
                currency_raw = (m.group(4) or "").strip()

                # Determine currency
                if currency_raw in ("港元", "HKD"):
                    currency = "HKD"
                else:
                    currency = "USD"

                # Resolve ticker
                ticker = _resolve_ticker(name_or_ticker)
                if ticker:
                    positions.append(Position(
                        symbol=ticker, shares=shares, avg_cost=cost, currency=currency,
                    ))
                break

    # Parse cash section
    cash_patterns = [
        # "- 103754 港元，可投资港股或美股"
        re.compile(r"-\s*([\d,]+\.?\d*)\s*(港元|港币|HKD|美元|USD|\$)"),
        # "- 剩余可用资金103754 港元，可投资港股或美股"
        re.compile(r"-\s*.*?(?:可用资金|剩余资金|现金)\s*[:：]?\s*([\d,]+\.?\d*)\s*(港元|港币|HKD|美元|USD|\$)"),
        # "- 50,000 元人民币"
        re.compile(r"-\s*([\d,]+\.?\d*)\s*元人民币"),
    ]
    for line in text.split("\n"):
        line = line.strip()
        for pattern in cash_patterns:
            m = pattern.match(line)
            if m:
                amount = float(m.group(1).replace(",", ""))
                unit = m.group(2) if m.lastindex and m.lastindex >= 2 else ""
                if unit in ("港元", "港币", "HKD"):
                    cash = amount
                    cash_currency = "HKD"
                elif unit in ("美元", "USD", "$"):
                    cash = amount
                    cash_currency = "USD"
                else:
                    cash = amount
                    cash_currency = "CNY"
                break

    return Portfolio(positions=tuple(positions), cash=cash, cash_currency=cash_currency)


def _latest_position_lines(text: str) -> list[str]:
    """Return only the latest holding section from base_short.md.

    The user keeps both initial holdings and the latest "record N操作后持仓" in the
    same file. P&L must use the latest section only; otherwise sold shares are
    double-counted.
    """
    sections: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("##"):
            if current_title is not None:
                sections.append((current_title, current_lines))
            current_title = stripped.lstrip("#").strip()
            current_lines = []
        elif current_title is not None:
            current_lines.append(raw_line)
    if current_title is not None:
        sections.append((current_title, current_lines))

    if not sections:
        return text.splitlines()

    record_sections: list[tuple[int, list[str]]] = []
    fallback_sections: list[list[str]] = []
    initial_sections: list[list[str]] = []
    for title, lines in sections:
        if "持仓" not in title:
            continue
        record_match = re.search(r"record\s*(\d+)", title, flags=re.IGNORECASE)
        if record_match:
            record_sections.append((int(record_match.group(1)), lines))
        elif "当前" in title or "操作后" in title:
            fallback_sections.append(lines)
        elif "初始" in title:
            initial_sections.append(lines)

    if record_sections:
        return max(record_sections, key=lambda item: item[0])[1]
    if fallback_sections:
        return fallback_sections[-1]
    if initial_sections:
        return initial_sections[-1]
    return text.splitlines()


def _resolve_ticker(name_or_ticker: str) -> str | None:
    """Resolve a Chinese name or ticker to a canonical ticker symbol."""
    # Direct match in Chinese name map
    if name_or_ticker in CHINESE_NAME_TO_TICKER:
        return CHINESE_NAME_TO_TICKER[name_or_ticker]
    # Already a ticker-like string (e.g., "NVDA", "0700.HK")
    cleaned = name_or_ticker.strip().upper()
    if re.match(r"^[A-Z0-9]{1,5}(\.[A-Z]{1,2})?$", cleaned):
        return cleaned
    # Try partial match against Chinese names
    for cn_name, ticker in CHINESE_NAME_TO_TICKER.items():
        if cn_name in name_or_ticker or name_or_ticker in cn_name:
            return ticker
    # Return None instead of garbage for unrecognized names
    return None


def compute_position_pnl(position: Position, current_price: float | None) -> PositionPnL:
    """Compute P&L for a single position."""
    cost_basis = position.shares * position.avg_cost
    if current_price is not None and current_price > 0:
        market_value = position.shares * current_price
        unrealized_pnl = market_value - cost_basis
        unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else None
    else:
        market_value = None
        unrealized_pnl = None
        unrealized_pnl_pct = None
    return PositionPnL(
        symbol=position.symbol,
        shares=position.shares,
        avg_cost=position.avg_cost,
        current_price=current_price,
        market_value=round(market_value, 2) if market_value is not None else None,
        cost_basis=round(cost_basis, 2),
        unrealized_pnl=round(unrealized_pnl, 2) if unrealized_pnl is not None else None,
        unrealized_pnl_pct=round(unrealized_pnl_pct, 2) if unrealized_pnl_pct is not None else None,
        currency=position.currency,
    )


def compute_portfolio_pnl(
    portfolio: Portfolio,
    prices: dict[str, float | None],
) -> PortfolioPnL:
    """Compute USD P&L for all priced USD positions.

    Positions without prices still appear in the per-position table, but they
    are excluded from aggregate market value, cost basis, and unrealized P&L.
    Non-USD positions are not combined into USD totals without FX conversion.
    """
    position_pnls = []
    total_market_value = 0.0
    total_cost_basis = 0.0
    unpriced_usd_cost_basis = 0.0
    excluded_positions: list[str] = []
    has_any_price = False

    for pos in portfolio.positions:
        price = prices.get(pos.symbol)
        pnl = compute_position_pnl(pos, price)
        if pos.currency != "USD":
            reason = f"currency {pos.currency} excluded from USD aggregate without FX conversion"
            pnl = replace(pnl, aggregation_status="excluded", exclusion_reason=reason)
            excluded_positions.append(f"{pos.symbol}: {reason}")
        elif pnl.market_value is None:
            reason = "missing current price excluded from aggregate P&L"
            pnl = replace(pnl, aggregation_status="excluded", exclusion_reason=reason)
            unpriced_usd_cost_basis += pnl.cost_basis
            excluded_positions.append(f"{pos.symbol}: {reason}")
        else:
            pnl = replace(pnl, aggregation_status="included", exclusion_reason=None)
            total_market_value += pnl.market_value
            total_cost_basis += pnl.cost_basis
            has_any_price = True
        position_pnls.append(pnl)

    if has_any_price:
        total_unrealized = total_market_value - total_cost_basis
        total_pct = (total_unrealized / total_cost_basis * 100) if total_cost_basis > 0 else None
        # Estimate equity using USD positions only for now
        total_equity = total_market_value + portfolio.cash if portfolio.cash_currency == "USD" else total_market_value
    else:
        total_unrealized = None
        total_pct = None
        total_equity = None
        total_market_value = None

    notes = []
    hkd_positions = [p for p in portfolio.positions if p.currency == "HKD"]
    if hkd_positions:
        notes.append(f"{len(hkd_positions)} HKD position(s) not included in USD equity estimate")
    unpriced_usd_positions = [
        p.symbol for p, pnl in zip(portfolio.positions, position_pnls)
        if p.currency == "USD" and pnl.market_value is None
    ]
    if unpriced_usd_positions:
        notes.append(f"USD positions without current prices excluded from aggregate P&L: {', '.join(unpriced_usd_positions)}")
    if portfolio.cash_currency == "HKD":
        notes.append(f"Cash {portfolio.cash_currency} {portfolio.cash:.0f} not converted to USD")

    return PortfolioPnL(
        positions=tuple(position_pnls),
        total_market_value=round(total_market_value, 2) if total_market_value is not None else None,
        total_cost_basis=round(total_cost_basis, 2),
        total_unrealized_pnl=round(total_unrealized, 2) if total_unrealized is not None else None,
        total_unrealized_pnl_pct=round(total_pct, 2) if total_pct is not None else None,
        total_equity=round(total_equity, 2) if total_equity is not None else None,
        cash=portfolio.cash,
        valuation_notes="; ".join(notes) if notes else "average cost method",
        cash_currency=portfolio.cash_currency,
        priced_usd_market_value=round(total_market_value, 2) if total_market_value is not None else None,
        priced_usd_cost_basis=round(total_cost_basis, 2),
        priced_usd_unrealized_pnl=round(total_unrealized, 2) if total_unrealized is not None else None,
        priced_usd_unrealized_pnl_pct=round(total_pct, 2) if total_pct is not None else None,
        unpriced_usd_cost_basis=round(unpriced_usd_cost_basis, 2),
        excluded_positions=tuple(excluded_positions),
    )


def compute_post_trade_pnl(
    portfolio: Portfolio,
    trades: list[Trade],
    prices: dict[str, float | None],
    fee_per_trade: float = FEE_PER_TRADE_USD,
) -> PostTradePnL:
    """Project P&L after proposed trades execute.

    Rules (from AGENTS.md):
    - Each BUY or SELL incurs fee_per_trade per side.
    - BUY cash impact: limit_price * shares + fee_per_trade.
    - SELL cash recovery: limit_price * shares - fee_per_trade.
    - Shares must be integer (enforced by Trade model).
    - Average cost method for cost basis updates on partial SELL.
    - SELL realized P&L: (limit_price - avg_cost) * shares - fee_per_trade.
    - BUY adds new position or increases existing position with updated avg cost.
    - If cash insufficient for BUY + fee, that trade is skipped.
    """
    # Build mutable position map
    pos_map: dict[str, list[float | str]] = {}  # symbol -> [shares, avg_cost, currency]
    for p in portfolio.positions:
        pos_map[p.symbol] = [float(p.shares), p.avg_cost, p.currency]

    cash = portfolio.cash
    realized_pnl = 0.0
    total_fees = 0.0
    executed_trades: list[Trade] = []
    skipped: list[str] = []

    for trade in trades:
        if portfolio.cash_currency != "USD":
            skipped.append(
                f"{trade.action} {trade.symbol} x{trade.shares}: cash currency {portfolio.cash_currency} cannot be used for USD trade projection without FX conversion"
            )
            continue
        if trade.action == "BUY":
            cost = trade.limit_price * trade.shares + fee_per_trade
            if cash < cost:
                skipped.append(f"BUY {trade.symbol} x{trade.shares}: insufficient cash ({cash:.2f} < {cost:.2f})")
                continue
            cash -= cost
            total_fees += fee_per_trade
            if trade.symbol in pos_map:
                old_shares, old_cost, currency = pos_map[trade.symbol]
                new_shares = old_shares + trade.shares
                new_avg_cost = (old_shares * old_cost + trade.shares * trade.limit_price + fee_per_trade) / new_shares
                pos_map[trade.symbol] = [new_shares, new_avg_cost, currency]
            else:
                new_avg_cost = (trade.shares * trade.limit_price + fee_per_trade) / trade.shares
                pos_map[trade.symbol] = [float(trade.shares), new_avg_cost, "USD"]
            executed_trades.append(trade)

        elif trade.action == "SELL":
            if trade.symbol not in pos_map:
                skipped.append(f"SELL {trade.symbol} x{trade.shares}: position not found")
                continue
            current_shares, avg_cost, currency = pos_map[trade.symbol]
            if currency != "USD":
                skipped.append(f"SELL {trade.symbol} x{trade.shares}: non-USD position currency {currency} requires FX-aware projection")
                continue
            if trade.shares > int(current_shares):
                skipped.append(f"SELL {trade.symbol} x{trade.shares}: exceeds held {int(current_shares)}")
                continue
            proceeds = trade.limit_price * trade.shares - fee_per_trade
            cash += proceeds
            total_fees += fee_per_trade
            realized = (trade.limit_price - avg_cost) * trade.shares - fee_per_trade
            realized_pnl += realized
            remaining = current_shares - trade.shares
            if remaining <= 0:
                del pos_map[trade.symbol]
            else:
                pos_map[trade.symbol] = [remaining, avg_cost, currency]
            executed_trades.append(trade)

    # Build remaining positions
    remaining_positions = tuple(
        Position(symbol=sym, shares=int(shares), avg_cost=float(cost), currency=str(currency))
        for sym, (shares, cost, currency) in sorted(pos_map.items())
    )

    # Compute remaining portfolio P&L
    remaining_portfolio = Portfolio(positions=remaining_positions, cash=cash, cash_currency=portfolio.cash_currency)
    remaining_pnl = compute_portfolio_pnl(remaining_portfolio, prices)

    # Post-trade equity
    post_trade_equity = None
    if remaining_pnl.total_market_value is not None:
        post_trade_equity = (
            remaining_pnl.total_market_value + cash
            if portfolio.cash_currency == "USD"
            else remaining_pnl.total_market_value
        )

    return PostTradePnL(
        trades=tuple(executed_trades),
        realized_pnl=round(realized_pnl, 2),
        total_fees=round(total_fees, 2),
        remaining_positions=remaining_positions,
        remaining_cash=round(cash, 2),
        remaining_portfolio_pnl=remaining_pnl,
        post_trade_equity=round(post_trade_equity, 2) if post_trade_equity is not None else None,
        skipped_trades=tuple(skipped),
    )


def portfolio_pnl_to_markdown(pnl: PortfolioPnL) -> str:
    """Format P&L as a Markdown table suitable for report inclusion."""
    lines = [
        "| Ticker | Shares | Avg Cost | Current Price | Market Value | Cost Basis | Unrealized P&L | P&L % |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for p in pnl.positions:
        price_str = f"${p.current_price:.2f}" if p.current_price is not None else "N/A"
        mv_str = f"${p.market_value:,.2f}" if p.market_value is not None else "N/A"
        pnl_str = f"${p.unrealized_pnl:,.2f}" if p.unrealized_pnl is not None else "N/A"
        pct_str = f"{p.unrealized_pnl_pct:.2f}%" if p.unrealized_pnl_pct is not None else "N/A"
        symbol = p.symbol if p.aggregation_status == "included" else f"{p.symbol} ({p.currency}, excluded)"
        lines.append(f"| {symbol} | {p.shares} | ${p.avg_cost:.2f} | {price_str} | {mv_str} | ${p.cost_basis:,.2f} | {pnl_str} | {pct_str} |")

    total_mv = f"${pnl.total_market_value:,.2f}" if pnl.total_market_value is not None else "N/A"
    total_pnl = f"${pnl.total_unrealized_pnl:,.2f}" if pnl.total_unrealized_pnl is not None else "N/A"
    total_pct = f"{pnl.total_unrealized_pnl_pct:.2f}%" if pnl.total_unrealized_pnl_pct is not None else "N/A"
    lines.append(f"| **Total** | | | | {total_mv} | ${pnl.total_cost_basis:,.2f} | {total_pnl} | {total_pct} |")
    lines.append(f"\n*{pnl.valuation_notes}*")
    return "\n".join(lines)


def post_trade_pnl_to_markdown(post_trade: PostTradePnL) -> str:
    """Format post-trade P&L projection as a Markdown table."""
    lines = [
        "## 交易后预计盈亏",
        "",
        f"| 项目 | 金额/数量 | 说明 |",
        f"|---|---:|---|",
    ]
    lines.append(f"| 本次已实现盈亏 | ${post_trade.realized_pnl:,.2f} | 卖出后费用后盈亏 |")
    lines.append(f"| 本次交易费用 | ${post_trade.total_fees:,.2f} | {len(post_trade.trades)} 笔交易 × ${5:.0f}/笔 |")
    lines.append(f"| 交易后现金 | ${post_trade.remaining_cash:,.2f} | {post_trade.remaining_portfolio_pnl.cash_currency if post_trade.remaining_portfolio_pnl else ''} |")
    if post_trade.skipped_trades:
        lines.append(f"| 跳过交易 | {len(post_trade.skipped_trades)} | {'; '.join(post_trade.skipped_trades)} |")

    if post_trade.remaining_portfolio_pnl and post_trade.remaining_portfolio_pnl.total_market_value is not None:
        rp = post_trade.remaining_portfolio_pnl
        lines.append(f"| 交易后持仓市值 | ${rp.total_market_value:,.2f} | |")
        lines.append(f"| 交易后未实现盈亏 | ${rp.total_unrealized_pnl:,.2f} | |" if rp.total_unrealized_pnl is not None else "| 交易后未实现盈亏 | N/A | |")
        if post_trade.post_trade_equity is not None:
            lines.append(f"| 交易后组合权益 | ${post_trade.post_trade_equity:,.2f} | 持仓市值 + 现金 |")

    return "\n".join(lines)
