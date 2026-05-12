"""Stress testing for the Hades Verification Division.

Scenario analysis: portfolio shock, sector shock, rate hike,
VIX spike, earnings miss, geopolitical event.
"""

from __future__ import annotations

from interface.constants import (
    DEFAULT_BETA_MAP,
    STRESS_SHOCKS,
    TICKER_SECTOR_MAP,
)
from interface.models import Position, StressScenario


def _priced_positions(
    positions: tuple[Position, ...] | list[Position],
    prices: dict[str, float] | None,
) -> tuple[list[tuple[Position, float]], tuple[str, ...]]:
    priced: list[tuple[Position, float]] = []
    excluded: list[str] = []
    for pos in positions:
        if pos.currency != "USD":
            excluded.append(f"{pos.symbol}: currency {pos.currency} excluded without FX conversion")
            continue
        if prices is not None:
            price = prices.get(pos.symbol)
            if price is None or price <= 0:
                excluded.append(f"{pos.symbol}: missing current USD price")
                continue
        else:
            price = pos.avg_cost
        priced.append((pos, pos.shares * price))
    return priced, tuple(excluded)


def portfolio_shock(
    positions: tuple[Position, ...] | list[Position],
    shock_pct: float,
    prices: dict[str, float] | None = None,
) -> StressScenario:
    """Apply a uniform shock across all positions.

    Args:
        positions: Current holdings.
        shock_pct: Shock as decimal (e.g. -0.10 for -10%).
        prices: Current prices per symbol. If None, uses avg_cost as proxy.
    """
    total_impact = 0.0
    total_value = 0.0
    worst_symbol = None
    worst_impact_pct = 0.0

    priced, excluded = _priced_positions(positions, prices)
    worst_impact_usd = 0.0
    for pos, value in priced:
        impact = value * shock_pct
        total_value += value
        total_impact += impact
        if abs(impact) > abs(worst_impact_usd):
            worst_impact_usd = impact
            worst_impact_pct = shock_pct
            worst_symbol = pos.symbol

    impact_pct = (total_impact / total_value * 100) if total_value > 0 else None

    return StressScenario(
        name=f"Portfolio Shock {shock_pct:.0%}",
        description=f"Uniform {shock_pct:.0%} shock across all positions",
        assumptions={"shock_pct": shock_pct, "position_count": len(positions)},
        portfolio_impact_usd=round(total_impact, 2),
        portfolio_impact_pct=round(impact_pct, 2) if impact_pct is not None else None,
        worst_position=worst_symbol,
        worst_position_impact_pct=round(worst_impact_pct * 100, 2) if worst_impact_pct else None,
        excluded_positions=excluded,
    )


def sector_shock(
    positions: tuple[Position, ...] | list[Position],
    sector: str,
    shock_pct: float,
    prices: dict[str, float] | None = None,
    ticker_sector_map: dict[str, str] | None = None,
) -> StressScenario:
    """Apply a shock to positions in a specific sector only."""
    if ticker_sector_map is None:
        ticker_sector_map = TICKER_SECTOR_MAP

    total_impact = 0.0
    total_value = 0.0
    sector_impact = 0.0
    sector_value = 0.0
    worst_symbol = None
    worst_impact_pct = 0.0

    priced, excluded = _priced_positions(positions, prices)
    worst_impact_usd = 0.0
    for pos, value in priced:
        total_value += value

        pos_sector = ticker_sector_map.get(pos.symbol, "unknown")
        if pos_sector == sector:
            impact = value * shock_pct
            sector_impact += impact
            sector_value += value
            if abs(impact) > abs(worst_impact_usd):
                worst_impact_usd = impact
                worst_impact_pct = shock_pct
                worst_symbol = pos.symbol

    impact_pct = (sector_impact / total_value * 100) if total_value > 0 else None

    return StressScenario(
        name=f"Sector Shock: {sector} {shock_pct:.0%}",
        description=f"{shock_pct:.0%} shock to {sector} sector positions",
        assumptions={"sector": sector, "shock_pct": shock_pct, "affected_positions": len([p for p, _ in priced if ticker_sector_map.get(p.symbol) == sector])},
        portfolio_impact_usd=round(sector_impact, 2),
        portfolio_impact_pct=round(impact_pct, 2) if impact_pct is not None else None,
        worst_position=worst_symbol,
        worst_position_impact_pct=round(worst_impact_pct * 100, 2) if worst_impact_pct else None,
        excluded_positions=excluded,
    )


def rate_hike_scenario(
    positions: tuple[Position, ...] | list[Position],
    rate_hike_bps: int = 100,
    prices: dict[str, float] | None = None,
    beta_map: dict[str, float] | None = None,
) -> StressScenario:
    """Simulate rate hike impact: growth/high-beta stocks hit harder.

    Simplified model: each position's shock = rate_hike_bps / 100 * beta * -1%.
    E.g., 100bps hike, beta 2.0 → -2% shock.
    """
    if beta_map is None:
        beta_map = DEFAULT_BETA_MAP

    total_impact = 0.0
    total_value = 0.0
    worst_symbol = None
    worst_impact_pct = 0.0

    priced, excluded = _priced_positions(positions, prices)
    worst_impact_usd = 0.0
    for pos, value in priced:
        total_value += value

        beta = beta_map.get(pos.symbol, 1.0)
        shock = rate_hike_bps / 100 * beta * -0.01  # bps -> pct
        impact = value * shock
        total_impact += impact

        if abs(impact) > abs(worst_impact_usd):
            worst_impact_usd = impact
            worst_impact_pct = shock
            worst_symbol = pos.symbol

    impact_pct = (total_impact / total_value * 100) if total_value > 0 else None

    return StressScenario(
        name=f"Rate Hike +{rate_hike_bps}bps",
        description=f"Interest rate hike of {rate_hike_bps}bps, high-beta stocks hit harder",
        assumptions={"rate_hike_bps": rate_hike_bps, "model": "shock = bps/100 * beta * -1%"},
        portfolio_impact_usd=round(total_impact, 2),
        portfolio_impact_pct=round(impact_pct, 2) if impact_pct is not None else None,
        worst_position=worst_symbol,
        worst_position_impact_pct=round(worst_impact_pct * 100, 2) if worst_impact_pct else None,
        excluded_positions=excluded,
    )


def vix_spike_scenario(
    positions: tuple[Position, ...] | list[Position],
    vix_level: float = 35.0,
    prices: dict[str, float] | None = None,
    beta_map: dict[str, float] | None = None,
) -> StressScenario:
    """Simulate VIX spike: higher beta = larger drawdown.

    Model: shock = -(vix_level - 20) / 20 * beta * 5%.
    At VIX 35, beta 2.0 → shock = -15/20 * 2.0 * 5% = -7.5%.
    """
    if beta_map is None:
        beta_map = DEFAULT_BETA_MAP

    total_impact = 0.0
    total_value = 0.0
    worst_symbol = None
    worst_impact_pct = 0.0

    priced, excluded = _priced_positions(positions, prices)
    worst_impact_usd = 0.0
    for pos, value in priced:
        total_value += value

        beta = beta_map.get(pos.symbol, 1.0)
        shock = -(vix_level - 20) / 20 * beta * 0.05
        impact = value * shock
        total_impact += impact

        if abs(impact) > abs(worst_impact_usd):
            worst_impact_usd = impact
            worst_impact_pct = shock
            worst_symbol = pos.symbol

    impact_pct = (total_impact / total_value * 100) if total_value > 0 else None

    return StressScenario(
        name=f"VIX Spike to {vix_level:.0f}",
        description=f"VIX spike to {vix_level:.0f}, high-beta drawdown model",
        assumptions={"vix_level": vix_level, "model": "shock = -(VIX-20)/20 * beta * 5%"},
        portfolio_impact_usd=round(total_impact, 2),
        portfolio_impact_pct=round(impact_pct, 2) if impact_pct is not None else None,
        worst_position=worst_symbol,
        worst_position_impact_pct=round(worst_impact_pct * 100, 2) if worst_impact_pct else None,
        excluded_positions=excluded,
    )


def earnings_miss_scenario(
    positions: tuple[Position, ...] | list[Position],
    symbol: str,
    miss_pct: float = -0.15,
    prices: dict[str, float] | None = None,
) -> StressScenario:
    """Simulate an earnings miss on a single stock.

    Args:
        miss_pct: Negative shock to the stock (e.g. -0.15 for -15%).
    """
    total_impact = 0.0
    total_value = 0.0
    target_value = 0.0

    priced, excluded = _priced_positions(positions, prices)
    worst_symbol = None
    worst_pct = None
    for pos, value in priced:
        total_value += value

        if pos.symbol == symbol:
            target_value = value
            total_impact += value * miss_pct
            worst_symbol = symbol
            worst_pct = miss_pct

    impact_pct = (total_impact / total_value * 100) if total_value > 0 else None

    return StressScenario(
        name=f"Earnings Miss: {symbol} {miss_pct:.0%}",
        description=f"Earnings miss shock of {miss_pct:.0%} on {symbol}",
        assumptions={"symbol": symbol, "miss_pct": miss_pct},
        portfolio_impact_usd=round(total_impact, 2),
        portfolio_impact_pct=round(impact_pct, 2) if impact_pct is not None else None,
        worst_position=worst_symbol,
        worst_position_impact_pct=round(worst_pct * 100, 2) if worst_pct is not None else None,
        excluded_positions=excluded,
    )


def geopolitical_event_scenario(
    positions: tuple[Position, ...] | list[Position],
    affected_sectors: list[str],
    shock_pct: float = -0.15,
    prices: dict[str, float] | None = None,
    ticker_sector_map: dict[str, str] | None = None,
) -> StressScenario:
    """Simulate a geopolitical event affecting specific sectors."""
    if ticker_sector_map is None:
        ticker_sector_map = TICKER_SECTOR_MAP

    total_impact = 0.0
    total_value = 0.0
    affected_count = 0
    worst_symbol = None
    worst_impact_pct = 0.0

    priced, excluded = _priced_positions(positions, prices)
    worst_impact_usd = 0.0
    for pos, value in priced:
        total_value += value

        pos_sector = ticker_sector_map.get(pos.symbol, "unknown")
        if pos_sector in affected_sectors:
            impact = value * shock_pct
            total_impact += impact
            affected_count += 1
            if abs(impact) > abs(worst_impact_usd):
                worst_impact_usd = impact
                worst_impact_pct = shock_pct
                worst_symbol = pos.symbol

    impact_pct = (total_impact / total_value * 100) if total_value > 0 else None

    return StressScenario(
        name=f"Geopolitical: {', '.join(affected_sectors)} {shock_pct:.0%}",
        description=f"Geopolitical event: {shock_pct:.0%} shock to {', '.join(affected_sectors)}",
        assumptions={"affected_sectors": affected_sectors, "shock_pct": shock_pct, "affected_positions": affected_count},
        portfolio_impact_usd=round(total_impact, 2),
        portfolio_impact_pct=round(impact_pct, 2) if impact_pct is not None else None,
        worst_position=worst_symbol,
        worst_position_impact_pct=round(worst_impact_pct * 100, 2) if worst_impact_pct else None,
        excluded_positions=excluded,
    )


def run_all_stress_tests(
    positions: tuple[Position, ...] | list[Position],
    prices: dict[str, float] | None = None,
    ticker_sector_map: dict[str, str] | None = None,
    beta_map: dict[str, float] | None = None,
) -> list[StressScenario]:
    """Run the full stress test suite."""
    scenarios: list[StressScenario] = []

    # Portfolio shocks (mild, moderate, severe)
    for label, shock in STRESS_SHOCKS.items():
        scenarios.append(portfolio_shock(positions, shock, prices))

    # Sector shocks for each represented sector
    if ticker_sector_map is None:
        ticker_sector_map = TICKER_SECTOR_MAP
    represented_sectors = set()
    for pos in positions:
        sec = ticker_sector_map.get(pos.symbol)
        if sec and sec != "broad_market":
            represented_sectors.add(sec)
    for sector in sorted(represented_sectors):
        scenarios.append(sector_shock(positions, sector, -0.15, prices, ticker_sector_map))

    # Rate hike
    scenarios.append(rate_hike_scenario(positions, 100, prices, beta_map))
    scenarios.append(rate_hike_scenario(positions, 200, prices, beta_map))

    # VIX spike
    scenarios.append(vix_spike_scenario(positions, 35.0, prices, beta_map))
    scenarios.append(vix_spike_scenario(positions, 45.0, prices, beta_map))

    # Earnings miss for each position
    for pos in positions:
        scenarios.append(earnings_miss_scenario(positions, pos.symbol, -0.15, prices))

    # Geopolitical: semiconductor and technology sectors
    tech_sectors = [s for s in ("semiconductor", "technology") if s in represented_sectors]
    if tech_sectors:
        scenarios.append(geopolitical_event_scenario(positions, tech_sectors, -0.20, prices, ticker_sector_map))

    return scenarios
