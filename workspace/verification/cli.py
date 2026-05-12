"""CLI for the Hades Verification Division.

Subcommands:
  audit-pnl    — Audit P&L calculations
  compliance   — Run compliance checks on proposed trades
  stress-test  — Run stress test scenarios on portfolio
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from interface.constants import FEE_PER_TRADE_USD, TICKER_SECTOR_MAP
from interface.cli_parsers import (
    parse_position_items,
    parse_price_items,
    parse_stop_items,
    parse_trade_items,
)
from interface.models import Portfolio, Position, RiskBudget, Trade

from verification.compliance import run_full_compliance
from verification.pnl_audit import audit_fee_application, audit_portfolio_pnl
from verification.stress_test import run_all_stress_tests


def _parse_positions(pos_args: list[str] | None) -> tuple[Position, ...]:
    """Parse position strings like 'NVDA:7:184.23' or 'KO:30:77.52'."""
    return parse_position_items(pos_args)


def _parse_prices(price_args: list[str] | None) -> dict[str, float]:
    """Parse price strings like 'NVDA:215.20' or 'KO=78.42'."""
    return parse_price_items(price_args)


def _portfolio_file(args: argparse.Namespace) -> str:
    path = getattr(args, "portfolio_file", None) or getattr(args, "base_short", None)
    if not path:
        raise SystemExit("audit-post-trade requires --portfolio-file (or legacy --base-short)")
    return path


def _portfolio_file_optional(args: argparse.Namespace) -> str | None:
    return getattr(args, "portfolio_file", None) or getattr(args, "base_short", None)


def _load_portfolio(args: argparse.Namespace) -> Portfolio:
    from analysis.portfolio_tracker import parse_base_short_positions

    path = _portfolio_file_optional(args)
    if path:
        portfolio = parse_base_short_positions(Path(path).read_text(encoding="utf-8"))
        positions = portfolio.positions if not getattr(args, "positions", None) else _parse_positions(args.positions)
        cash = portfolio.cash if getattr(args, "cash", None) is None else args.cash
        cash_currency = portfolio.cash_currency
        return Portfolio(positions=positions, cash=cash, cash_currency=cash_currency)

    positions = _parse_positions(getattr(args, "positions", None))
    cash = 10000.0 if getattr(args, "cash", None) is None else args.cash
    return Portfolio(positions=positions, cash=cash)


def cmd_audit_pnl(args: argparse.Namespace) -> None:
    """Audit P&L calculations for a portfolio."""
    prices = _parse_prices(args.prices)
    portfolio = _load_portfolio(args)

    result = audit_portfolio_pnl(portfolio, prices)
    output = {
        "passed": result.passed,
        "errors": list(result.errors),
        "warnings": list(result.warnings),
        "details": result.details,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_compliance(args: argparse.Namespace) -> None:
    """Run compliance checks on proposed trades."""
    prices = _parse_prices(args.prices)
    portfolio = _load_portfolio(args)

    trades = parse_trade_items(args.trades)
    stops = parse_stop_items(args.stops)

    risk_budget = RiskBudget(equity=args.equity) if args.equity is not None and args.equity > 0 else None
    results = run_full_compliance(portfolio, trades, prices, stops, risk_budget)

    output = {
        "total_checks": len(results),
        "passed": sum(1 for r in results if r.passed),
        "failed": sum(1 for r in results if not r.passed),
        "results": [
            {"passed": r.passed, "errors": list(r.errors), "warnings": list(r.warnings), "details": r.details}
            for r in results
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_stress_test(args: argparse.Namespace) -> None:
    """Run stress test scenarios on the portfolio."""
    portfolio = _load_portfolio(args)
    prices = _parse_prices(args.prices)

    scenarios = run_all_stress_tests(
        portfolio.positions, prices if prices else None,
        ticker_sector_map=TICKER_SECTOR_MAP,
    )

    output = {
        "scenario_count": len(scenarios),
        "scenarios": [
            {
                "name": s.name,
                "description": s.description,
                "assumptions": s.assumptions,
                "portfolio_impact_usd": s.portfolio_impact_usd,
                "portfolio_impact_pct": s.portfolio_impact_pct,
                "worst_position": s.worst_position,
                "worst_position_impact_pct": s.worst_position_impact_pct,
                "excluded_positions": list(s.excluded_positions),
            }
            for s in scenarios
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def cmd_audit_post_trade(args: argparse.Namespace) -> None:
    """Audit post-trade P&L: verify fee application, integer shares, cash, and P&L consistency."""
    from analysis.portfolio_tracker import compute_post_trade_pnl
    from verification.pnl_audit import audit_post_trade_pnl

    portfolio = _load_portfolio(args)
    prices = _parse_prices(args.prices)
    trades = parse_trade_items(args.trades)

    # Compute post-trade P&L
    computed = compute_post_trade_pnl(portfolio, trades, prices)

    # Audit fee application
    fee_result = audit_fee_application(list(computed.trades), FEE_PER_TRADE_USD, computed.total_fees)

    # Audit post-trade P&L
    pnl_result = audit_post_trade_pnl(portfolio, trades, prices, computed)

    output = {
        "fee_audit": {"passed": fee_result.passed, "errors": list(fee_result.errors)},
        "pnl_audit": {"passed": pnl_result.passed, "errors": list(pnl_result.errors), "warnings": list(pnl_result.warnings)},
        "computed": {
            "realized_pnl": computed.realized_pnl,
            "total_fees": computed.total_fees,
            "remaining_cash": computed.remaining_cash,
            "post_trade_equity": computed.post_trade_equity,
            "skipped_trades": list(computed.skipped_trades),
        },
        "overall_passed": fee_result.passed and pnl_result.passed,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Hades Verification Division CLI")
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # audit-pnl
    p_audit = subparsers.add_parser("audit-pnl", help="Audit P&L calculations")
    p_audit.add_argument("--portfolio-file", help="Path to portfolio file in base_short-compatible format")
    p_audit.add_argument("--base-short", help="Legacy alias for --portfolio-file")
    p_audit.add_argument("--positions", nargs="+", help="Positions as SYMBOL:SHARES:AVG_COST")
    p_audit.add_argument("--prices", nargs="+", help="Current prices as SYMBOL:PRICE or SYMBOL=PRICE")
    p_audit.add_argument("--cash", type=float, default=None, help="Available cash override")

    # compliance
    p_comp = subparsers.add_parser("compliance", help="Run compliance checks")
    p_comp.add_argument("--portfolio-file", help="Path to portfolio file in base_short-compatible format")
    p_comp.add_argument("--base-short", help="Legacy alias for --portfolio-file")
    p_comp.add_argument("--positions", nargs="+", help="Positions as SYMBOL:SHARES:AVG_COST")
    p_comp.add_argument("--prices", nargs="+", help="Current prices as SYMBOL:PRICE or SYMBOL=PRICE")
    p_comp.add_argument("--cash", type=float, default=None, help="Available cash override")
    p_comp.add_argument("--trades", nargs="+", help="Trades as SYMBOL:ACTION:SHARES:PRICE")
    p_comp.add_argument("--stops", nargs="+", help="Stop losses as SYMBOL:STOP_PRICE or SYMBOL=STOP_PRICE")
    p_comp.add_argument("--equity", type=float, default=None, help="Override equity for risk budget")

    # stress-test
    p_stress = subparsers.add_parser("stress-test", help="Run stress test scenarios")
    p_stress.add_argument("--portfolio-file", help="Path to portfolio file in base_short-compatible format")
    p_stress.add_argument("--base-short", help="Legacy alias for --portfolio-file")
    p_stress.add_argument("--positions", nargs="+", help="Positions as SYMBOL:SHARES:AVG_COST")
    p_stress.add_argument("--prices", nargs="+", help="Current prices as SYMBOL:PRICE or SYMBOL=PRICE")

    # audit-post-trade
    p_apt = subparsers.add_parser("audit-post-trade", help="Audit post-trade P&L calculations")
    p_apt.add_argument("--portfolio-file", help="Path to portfolio file in base_short-compatible format")
    p_apt.add_argument("--base-short", help="Legacy alias for --portfolio-file")
    p_apt.add_argument("--positions", nargs="+", help="Positions as SYMBOL:SHARES:AVG_COST")
    p_apt.add_argument("--cash", type=float, default=None, help="Available cash override")
    p_apt.add_argument("--prices", nargs="+", help="Current prices as SYMBOL:PRICE or SYMBOL=PRICE")
    p_apt.add_argument("--trades", nargs="+", help="Trades as SYMBOL:ACTION:SHARES:PRICE")

    args = parser.parse_args()
    if args.command == "audit-pnl":
        cmd_audit_pnl(args)
    elif args.command == "compliance":
        cmd_compliance(args)
    elif args.command == "stress-test":
        cmd_stress_test(args)
    elif args.command == "audit-post-trade":
        cmd_audit_post_trade(args)


if __name__ == "__main__":
    main()
