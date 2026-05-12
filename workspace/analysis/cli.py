"""CLI entry point for Poseidon Research Division tools."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from interface.cli_parsers import parse_price_items, parse_trade_items


def _parse_factor_pairs(raw: str) -> dict[str, float]:
    """Parse 'key=value,key2=value2' into a dict, skipping malformed tokens."""
    result: dict[str, float] = {}
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        parts = token.split("=", 1)
        if len(parts) != 2:
            continue
        try:
            result[parts[0].strip()] = float(parts[1].strip())
        except ValueError:
            continue
    return result


def _parse_check_pairs(raw: str) -> dict[str, bool]:
    """Parse 'key=true,key2=false' into a dict, skipping malformed tokens."""
    result: dict[str, bool] = {}
    for token in raw.split(","):
        token = token.strip()
        if not token:
            continue
        parts = token.split("=", 1)
        if len(parts) != 2:
            continue
        result[parts[0].strip()] = parts[1].strip().lower() in ("true", "1", "yes", "y")
    return result


def _parse_base_short(path: str) -> dict:
    from analysis.portfolio_tracker import parse_base_short_positions, compute_portfolio_pnl
    text = Path(path).read_text(encoding="utf-8")
    portfolio = parse_base_short_positions(text)
    return {"positions": [{"symbol": p.symbol, "shares": p.shares, "avg_cost": p.avg_cost, "currency": p.currency} for p in portfolio.positions], "cash": portfolio.cash, "cash_currency": portfolio.cash_currency}


def _portfolio_file(args: argparse.Namespace) -> str:
    path = getattr(args, "portfolio_file", None) or getattr(args, "base_short", None)
    if not path:
        raise SystemExit("pnl/post-trade requires --portfolio-file (or legacy --base-short)")
    return path


def cmd_pnl(args: argparse.Namespace) -> None:
    from analysis.portfolio_tracker import parse_base_short_positions, compute_portfolio_pnl, portfolio_pnl_to_markdown
    text = Path(_portfolio_file(args)).read_text(encoding="utf-8")
    portfolio = parse_base_short_positions(text)
    # If prices provided, use them; otherwise output positions only
    prices = parse_price_items(args.prices)
    pnl = compute_portfolio_pnl(portfolio, prices)
    if args.markdown:
        print(portfolio_pnl_to_markdown(pnl))
        return
    result = {
        "positions": [
            {"symbol": p.symbol, "shares": p.shares, "avg_cost": p.avg_cost,
             "currency": p.currency, "aggregation_status": p.aggregation_status,
             "exclusion_reason": p.exclusion_reason,
             "current_price": p.current_price, "market_value": p.market_value,
             "cost_basis": p.cost_basis, "unrealized_pnl": p.unrealized_pnl,
             "unrealized_pnl_pct": p.unrealized_pnl_pct}
            for p in pnl.positions
        ],
        "total_market_value": pnl.total_market_value,
        "total_cost_basis": pnl.total_cost_basis,
        "total_unrealized_pnl": pnl.total_unrealized_pnl,
        "total_unrealized_pnl_pct": pnl.total_unrealized_pnl_pct,
        "total_equity": pnl.total_equity,
        "cash": pnl.cash,
        "cash_currency": pnl.cash_currency,
        "priced_usd_market_value": pnl.priced_usd_market_value,
        "priced_usd_cost_basis": pnl.priced_usd_cost_basis,
        "priced_usd_unrealized_pnl": pnl.priced_usd_unrealized_pnl,
        "priced_usd_unrealized_pnl_pct": pnl.priced_usd_unrealized_pnl_pct,
        "unpriced_usd_cost_basis": pnl.unpriced_usd_cost_basis,
        "excluded_positions": list(pnl.excluded_positions),
        "valuation_notes": pnl.valuation_notes,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_sizing(args: argparse.Namespace) -> None:
    from analysis.position_sizing import compute_sizing_summary
    result = compute_sizing_summary(
        equity=args.equity, entry=args.entry, stop=args.stop,
        risk_per_trade_pct=args.risk_pct, cash=args.cash,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_rr(args: argparse.Namespace) -> None:
    from analysis.fee_rr import fee_adjusted_rr, break_even_price, rr_verdict, multi_target_rr
    if args.target_2:
        targets = [args.target, args.target_2]
    else:
        targets = [args.target]
    results = multi_target_rr(
        entry=args.entry, stop=args.stop, targets=targets,
        symbol=args.symbol or "", shares=args.shares,
    )
    output = [
        {"target": r.target_1, "rr": r.rr_target_1, "verdict": r.verdict, "break_even": r.break_even_price, "shares": r.shares}
        for r in results
    ]
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_score_sector(args: argparse.Namespace) -> None:
    from analysis.sector_scoring import score_sector
    factors = _parse_factor_pairs(args.factors)
    result = score_sector(factors, sector=args.sector or "")
    print(json.dumps({"sector": result.sector, "scores": result.scores, "weighted_score": result.weighted_score, "rating": result.rating, "coverage_pct": result.coverage_pct, "missing_factors": list(result.missing_factors), "invalid_factors": list(result.invalid_factors)}, ensure_ascii=False, indent=2))


def cmd_score_stock(args: argparse.Namespace) -> None:
    from analysis.sector_scoring import score_stock
    factors = _parse_factor_pairs(args.factors)
    result = score_stock(factors, sector=args.sector or "", symbol=args.symbol or "")
    print(json.dumps({"scores": result.scores, "weighted_score": result.weighted_score, "tier": result.tier, "coverage_pct": result.coverage_pct, "missing_factors": list(result.missing_factors), "invalid_factors": list(result.invalid_factors)}, ensure_ascii=False, indent=2))


def cmd_score_short_term(args: argparse.Namespace) -> None:
    from analysis.sector_scoring import score_short_term
    factors = _parse_factor_pairs(args.factors)
    result = score_short_term(factors, symbol=args.symbol or "")
    print(json.dumps({"scores": result.scores, "weighted_score": result.weighted_score, "action_bias": result.action_bias, "coverage_pct": result.coverage_pct, "missing_factors": list(result.missing_factors), "invalid_factors": list(result.invalid_factors)}, ensure_ascii=False, indent=2))


def cmd_swing_verdict(args: argparse.Namespace) -> None:
    from analysis.sector_scoring import decide_swing_trade_verdict, score_short_term
    factors = _parse_factor_pairs(args.factors)
    checks = _parse_check_pairs(args.checks) if args.checks else {}
    score = score_short_term(factors, symbol=args.symbol or "")
    result = decide_swing_trade_verdict(
        score,
        rr_verdict=args.rr_verdict,
        checks=checks,
        has_defined_stop=args.has_defined_stop.strip().lower() in ("true", "1", "yes", "y"),
        has_volume_confirmation=args.has_volume_confirmation.strip().lower() in ("true", "1", "yes", "y"),
        within_risk_budget=args.within_risk_budget.strip().lower() in ("true", "1", "yes", "y"),
        data_quality_ok=args.data_quality_ok.strip().lower() in ("true", "1", "yes", "y"),
        price_extended_without_rr=args.price_extended_without_rr.strip().lower() in ("true", "1", "yes", "y"),
        fallback_symbols=tuple(symbol.strip().upper() for symbol in args.fallback_symbols.split(",") if symbol.strip()),
    )
    print(json.dumps({
        "symbol": result.symbol,
        "weighted_score": result.weighted_score,
        "action_bias": result.action_bias,
        "rr_verdict": result.rr_verdict,
        "verdict": result.verdict,
        "reasons": list(result.reasons),
        "triggered_vetoes": list(result.triggered_vetoes),
        "hard_vetoes": list(result.hard_vetoes),
        "fallback_symbols": list(result.fallback_symbols),
        "requires_fallback_review": result.requires_fallback_review,
    }, ensure_ascii=False, indent=2))


def cmd_post_trade(args: argparse.Namespace) -> None:
    from analysis.portfolio_tracker import parse_base_short_positions, compute_post_trade_pnl, post_trade_pnl_to_markdown
    text = Path(_portfolio_file(args)).read_text(encoding="utf-8")
    portfolio = parse_base_short_positions(text)
    prices = parse_price_items(args.prices)
    trades = parse_trade_items(args.trades)
    result = compute_post_trade_pnl(portfolio, trades, prices)
    output = {
        "realized_pnl": result.realized_pnl,
        "total_fees": result.total_fees,
        "remaining_cash": result.remaining_cash,
        "post_trade_equity": result.post_trade_equity,
        "executed_trades": [{"symbol": t.symbol, "action": t.action, "shares": t.shares, "limit_price": t.limit_price} for t in result.trades],
        "skipped_trades": list(result.skipped_trades),
        "remaining_positions": [{"symbol": p.symbol, "shares": p.shares, "avg_cost": p.avg_cost} for p in result.remaining_positions],
    }
    if result.remaining_portfolio_pnl:
        rp = result.remaining_portfolio_pnl
        output["remaining_unrealized_pnl"] = rp.total_unrealized_pnl
        output["remaining_market_value"] = rp.total_market_value
    if args.markdown:
        print(post_trade_pnl_to_markdown(result))
    else:
        print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_veto_check(args: argparse.Namespace) -> None:
    from analysis.sector_scoring import score_stock, check_veto
    factors = _parse_factor_pairs(args.factors)
    stock_result = score_stock(factors, sector=args.sector or "")
    checks = _parse_check_pairs(args.checks) if args.checks else {}
    triggered = check_veto(stock_result, checks)
    print(json.dumps({"weighted_score": stock_result.weighted_score, "tier": stock_result.tier, "triggered_vetoes": triggered, "veto_active": len(triggered) > 0}, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Poseidon Research Division CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    pnl_p = sub.add_parser("pnl", help="Compute portfolio P&L from a portfolio file")
    pnl_p.add_argument("--portfolio-file", help="Path to portfolio file in base_short-compatible format")
    pnl_p.add_argument("--base-short", help="Legacy alias for --portfolio-file")
    pnl_p.add_argument("--prices", nargs="+", help="SYMBOL=PRICE or SYMBOL:PRICE pairs; commas/semicolons also supported")
    pnl_p.add_argument("--markdown", action="store_true", help="Output Markdown table instead of JSON")
    pnl_p.set_defaults(func=cmd_pnl)

    sizing_p = sub.add_parser("sizing", help="Compute position sizing")
    sizing_p.add_argument("--equity", type=float, required=True)
    sizing_p.add_argument("--entry", type=float, required=True)
    sizing_p.add_argument("--stop", type=float, required=True)
    sizing_p.add_argument("--risk-pct", type=float, default=2.0)
    sizing_p.add_argument("--cash", type=float, default=None)
    sizing_p.set_defaults(func=cmd_sizing)

    rr_p = sub.add_parser("rr", help="Compute fee-adjusted risk/reward")
    rr_p.add_argument("--entry", type=float, required=True)
    rr_p.add_argument("--stop", type=float, required=True)
    rr_p.add_argument("--target", type=float, required=True)
    rr_p.add_argument("--target-2", type=float, default=None)
    rr_p.add_argument("--symbol", default="")
    rr_p.add_argument("--shares", type=int, default=1)
    rr_p.set_defaults(func=cmd_rr)

    score_s = sub.add_parser("score-sector", help="Score a sector")
    score_s.add_argument("--factors", required=True, help="Comma-separated factor=score pairs")
    score_s.add_argument("--sector", default="")
    score_s.set_defaults(func=cmd_score_sector)

    score_stk = sub.add_parser("score-stock", help="Score a stock")
    score_stk.add_argument("--factors", required=True, help="Comma-separated factor=score pairs")
    score_stk.add_argument("--sector", default="")
    score_stk.add_argument("--symbol", default="", help="Stock ticker symbol")
    score_stk.set_defaults(func=cmd_score_stock)

    score_st = sub.add_parser("score-short-term", help="Score short-term setup")
    score_st.add_argument("--factors", required=True, help="Comma-separated factor=score pairs")
    score_st.add_argument("--symbol", default="")
    score_st.set_defaults(func=cmd_score_short_term)

    swing = sub.add_parser("swing-verdict", help="Classify a swing candidate into current_trade/small_starter/wait/hard_veto")
    swing.add_argument("--factors", required=True, help="Comma-separated short-term factor=score pairs")
    swing.add_argument("--rr-verdict", required=True, choices=["positive_expectancy", "marginal", "insufficient", "invalid"])
    swing.add_argument("--checks", default="", help="Comma-separated veto_condition=true/false pairs")
    swing.add_argument("--symbol", default="", help="Stock ticker symbol")
    swing.add_argument("--has-defined-stop", default="true")
    swing.add_argument("--has-volume-confirmation", default="true")
    swing.add_argument("--within-risk-budget", default="true")
    swing.add_argument("--data-quality-ok", default="true")
    swing.add_argument("--price-extended-without-rr", default="false")
    swing.add_argument("--fallback-symbols", default="", help="Comma-separated ETF/basket fallback symbols to review")
    swing.set_defaults(func=cmd_swing_verdict)

    # post-trade
    pt = sub.add_parser("post-trade", help="Project post-trade P&L with fees")
    pt.add_argument("--portfolio-file", help="Path to portfolio file in base_short-compatible format")
    pt.add_argument("--base-short", help="Legacy alias for --portfolio-file")
    pt.add_argument("--prices", nargs="+", help="SYMBOL=PRICE or SYMBOL:PRICE pairs; commas/semicolons also supported")
    pt.add_argument("--trades", nargs="+", help="SYMBOL:ACTION:SHARES:PRICE trades; semicolons also supported")
    pt.add_argument("--markdown", action="store_true", help="Output Markdown table instead of JSON")
    pt.set_defaults(func=cmd_post_trade)

    # veto-check
    veto = sub.add_parser("veto-check", help="Check veto conditions for a stock")
    veto.add_argument("--factors", required=True, help="Comma-separated factor=score pairs")
    veto.add_argument("--checks", required=True, help="Comma-separated veto_condition=true/false pairs")
    veto.add_argument("--sector", default="")
    veto.set_defaults(func=cmd_veto_check)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
