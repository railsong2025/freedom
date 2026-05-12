"""Tests for stress_test module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from interface.models import Position

from verification.stress_test import (
    earnings_miss_scenario,
    geopolitical_event_scenario,
    portfolio_shock,
    rate_hike_scenario,
    run_all_stress_tests,
    sector_shock,
    vix_spike_scenario,
)

POSITIONS = (
    Position("NVDA", 7, 184.23),
    Position("MSFT", 18, 506.96),
    Position("KO", 30, 77.52),
    Position("AMD", 1, 413.23),
)

PRICES = {
    "NVDA": 215.20,
    "MSFT": 415.12,
    "KO": 78.42,
    "AMD": 400.00,
}


class TestPortfolioShock(unittest.TestCase):
    def test_mild_shock(self):
        result = portfolio_shock(POSITIONS, -0.10, PRICES)
        self.assertIn("Portfolio Shock", result.name)
        self.assertIsNotNone(result.portfolio_impact_usd)
        self.assertIsNotNone(result.portfolio_impact_pct)
        self.assertLess(result.portfolio_impact_usd, 0)

    def test_severe_shock(self):
        result = portfolio_shock(POSITIONS, -0.30, PRICES)
        self.assertLess(result.portfolio_impact_usd, 0)
        # Severe should be worse than mild
        mild = portfolio_shock(POSITIONS, -0.10, PRICES)
        self.assertLess(result.portfolio_impact_usd, mild.portfolio_impact_usd)

    def test_no_prices_uses_avg_cost(self):
        result = portfolio_shock(POSITIONS, -0.10)
        self.assertIsNotNone(result.portfolio_impact_usd)
        self.assertLess(result.portfolio_impact_usd, 0)

    def test_empty_positions(self):
        result = portfolio_shock((), -0.10)
        self.assertEqual(result.portfolio_impact_usd, 0.0)
        self.assertIsNone(result.portfolio_impact_pct)

    def test_mixed_currency_and_missing_prices_are_excluded_when_prices_supplied(self):
        positions = (
            Position("MSFT", 1, 100.0),
            Position("0700.HK", 100, 50.0, currency="HKD"),
            Position("NVDA", 1, 200.0),
        )
        result = portfolio_shock(positions, -0.10, {"MSFT": 110.0})
        self.assertAlmostEqual(result.portfolio_impact_usd, -11.0)
        self.assertEqual(2, len(result.excluded_positions))


class TestSectorShock(unittest.TestCase):
    def test_semiconductor_shock(self):
        result = sector_shock(POSITIONS, "semiconductor", -0.15, PRICES)
        self.assertIn("semiconductor", result.name)
        self.assertLess(result.portfolio_impact_usd, 0)
        # NVDA and AMD are semiconductors
        self.assertEqual(result.assumptions["affected_positions"], 2)

    def test_unaffected_sector(self):
        result = sector_shock(POSITIONS, "energy", -0.15, PRICES)
        self.assertEqual(result.portfolio_impact_usd, 0.0)

    def test_custom_sector_map(self):
        custom_map = {"NVDA": "ai_chips", "MSFT": "ai_chips"}
        result = sector_shock(POSITIONS, "ai_chips", -0.20, PRICES, custom_map)
        self.assertLess(result.portfolio_impact_usd, 0)
        self.assertEqual(result.assumptions["affected_positions"], 2)


class TestRateHikeScenario(unittest.TestCase):
    def test_100bps(self):
        result = rate_hike_scenario(POSITIONS, 100, PRICES)
        self.assertIn("Rate Hike", result.name)
        self.assertLess(result.portfolio_impact_usd, 0)

    def test_higher_rate_worse(self):
        r100 = rate_hike_scenario(POSITIONS, 100, PRICES)
        r200 = rate_hike_scenario(POSITIONS, 200, PRICES)
        self.assertLess(r200.portfolio_impact_usd, r100.portfolio_impact_usd)

    def test_custom_beta(self):
        beta_map = {"NVDA": 3.0, "MSFT": 1.0, "KO": 0.5, "AMD": 2.5}
        result = rate_hike_scenario(POSITIONS, 100, PRICES, beta_map)
        self.assertLess(result.portfolio_impact_usd, 0)


class TestVixSpikeScenario(unittest.TestCase):
    def test_vix_35(self):
        result = vix_spike_scenario(POSITIONS, 35.0, PRICES)
        self.assertIn("VIX", result.name)
        self.assertLess(result.portfolio_impact_usd, 0)

    def test_higher_vix_worse(self):
        r35 = vix_spike_scenario(POSITIONS, 35.0, PRICES)
        r45 = vix_spike_scenario(POSITIONS, 45.0, PRICES)
        self.assertLess(r45.portfolio_impact_usd, r35.portfolio_impact_usd)

    def test_low_vix_minimal_impact(self):
        result = vix_spike_scenario(POSITIONS, 20.0, PRICES)
        self.assertEqual(result.portfolio_impact_usd, 0.0)


class TestEarningsMissScenario(unittest.TestCase):
    def test_nvda_miss(self):
        result = earnings_miss_scenario(POSITIONS, "NVDA", -0.15, PRICES)
        self.assertIn("NVDA", result.name)
        self.assertLess(result.portfolio_impact_usd, 0)
        self.assertEqual(result.worst_position, "NVDA")
        self.assertAlmostEqual(result.worst_position_impact_pct, -15.0)

    def test_unknown_symbol(self):
        result = earnings_miss_scenario(POSITIONS, "UNKNOWN", -0.15, PRICES)
        self.assertEqual(result.portfolio_impact_usd, 0.0)
        self.assertIsNone(result.worst_position)


class TestGeopoliticalEventScenario(unittest.TestCase):
    def test_tech_geopolitical(self):
        result = geopolitical_event_scenario(
            POSITIONS, ["semiconductor", "technology"], -0.20, PRICES,
        )
        self.assertIn("semiconductor", result.name)
        self.assertLess(result.portfolio_impact_usd, 0)

    def test_unaffected_sector(self):
        result = geopolitical_event_scenario(
            POSITIONS, ["energy"], -0.20, PRICES,
        )
        self.assertEqual(result.portfolio_impact_usd, 0.0)


class TestRunAllStressTests(unittest.TestCase):
    def test_full_suite(self):
        scenarios = run_all_stress_tests(POSITIONS, PRICES)
        self.assertGreater(len(scenarios), 10)
        # Should have portfolio shocks, sector shocks, rate hikes, VIX, earnings, geopolitical
        names = [s.name for s in scenarios]
        self.assertTrue(any("Portfolio Shock" in n for n in names))
        self.assertTrue(any("Sector Shock" in n for n in names))
        self.assertTrue(any("Rate Hike" in n for n in names))
        self.assertTrue(any("VIX" in n for n in names))
        self.assertTrue(any("Earnings" in n for n in names))

    def test_no_prices(self):
        scenarios = run_all_stress_tests(POSITIONS)
        self.assertGreater(len(scenarios), 0)
        # All should still have impact values (using avg_cost as proxy)
        for s in scenarios:
            self.assertIsNotNone(s.portfolio_impact_usd)

    def test_empty_portfolio(self):
        scenarios = run_all_stress_tests(())
        # 3 portfolio shocks + 2 rate hikes + 2 VIX spikes = 7 (no sector/earnings/geopolitical)
        self.assertEqual(len(scenarios), 7)


if __name__ == "__main__":
    unittest.main()
