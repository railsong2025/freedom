"""Tests for sector_scoring module."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from analysis.sector_scoring import (
    check_veto,
    decide_swing_trade_verdict,
    score_sector,
    score_short_term,
    score_stock,
    sector_rating,
    short_term_action,
    stock_tier,
)
from interface.constants import SECTOR_WEIGHTS, SHORT_TERM_WEIGHTS, STOCK_WEIGHTS


class TestScoreSector(unittest.TestCase):
    def test_high_score(self):
        factors = {k: 90.0 for k in SECTOR_WEIGHTS}
        result = score_sector(factors, sector="semiconductor")
        self.assertAlmostEqual(result.weighted_score, 90.0, places=1)
        self.assertEqual(result.rating, "overweight")

    def test_mixed_score(self):
        factors = {
            "market_regime_fit": 70,
            "relative_strength_breadth": 80,
            "earnings_revision": 75,
            "supply_demand_pricing": 85,
            "catalyst_quality": 70,
            "valuation_expectations": 60,
            "capital_flow_crowding": 65,
            "policy_geopolitical_risk": 50,
        }
        result = score_sector(factors, sector="technology")
        self.assertGreater(result.weighted_score, 60)
        self.assertLess(result.weighted_score, 80)

    def test_missing_factors(self):
        factors = {"market_regime_fit": 80, "catalyst_quality": 70}
        result = score_sector(factors, sector="energy")
        # Only 2 of 8 factors, so the score is marked insufficient evidence.
        self.assertIsNotNone(result.weighted_score)
        self.assertEqual(result.rating, "insufficient_evidence")
        self.assertLess(result.coverage_pct, 80.0)
        self.assertIn("earnings_revision", result.missing_factors)

    def test_invalid_factor_range_downgrades(self):
        factors = {k: 90.0 for k in SECTOR_WEIGHTS}
        factors["earnings_revision"] = 120.0
        result = score_sector(factors, sector="semiconductor")
        self.assertEqual(result.rating, "insufficient_evidence")
        self.assertIn("earnings_revision", result.invalid_factors)

    def test_avoid(self):
        factors = {k: 30.0 for k in SECTOR_WEIGHTS}
        result = score_sector(factors, sector="energy")
        self.assertEqual(result.rating, "avoid")


class TestScoreStock(unittest.TestCase):
    def test_core_candidate(self):
        factors = {k: 85.0 for k in STOCK_WEIGHTS}
        result = score_stock(factors, sector="semiconductor")
        self.assertEqual(result.tier, "core")

    def test_watch(self):
        factors = {k: 65.0 for k in STOCK_WEIGHTS}
        result = score_stock(factors, sector="technology")
        self.assertEqual(result.tier, "watch")

    def test_missing_stock_factors_downgrades(self):
        result = score_stock({"direct_beneficiary": 95.0}, sector="semiconductor")
        self.assertEqual(result.tier, "insufficient_evidence")


class TestScoreShortTerm(unittest.TestCase):
    def test_actionable(self):
        factors = {k: 85.0 for k in SHORT_TERM_WEIGHTS}
        result = score_short_term(factors, symbol="MU")
        self.assertEqual(result.action_bias, "actionable")

    def test_avoid(self):
        factors = {k: 40.0 for k in SHORT_TERM_WEIGHTS}
        result = score_short_term(factors, symbol="INTC")
        self.assertEqual(result.action_bias, "avoid")


class TestSectorRating(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(sector_rating(80), "overweight")
        self.assertEqual(sector_rating(79.9), "tactical_overweight")
        self.assertEqual(sector_rating(70), "tactical_overweight")
        self.assertEqual(sector_rating(69.9), "neutral")
        self.assertEqual(sector_rating(60), "neutral")
        self.assertEqual(sector_rating(59.9), "underweight")
        self.assertEqual(sector_rating(45), "underweight")
        self.assertEqual(sector_rating(44.9), "avoid")
        self.assertEqual(sector_rating(0), "avoid")


class TestStockTier(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(stock_tier(80), "core")
        self.assertEqual(stock_tier(79.9), "tactical")
        self.assertEqual(stock_tier(70), "tactical")
        self.assertEqual(stock_tier(69.9), "watch")
        self.assertEqual(stock_tier(60), "watch")
        self.assertEqual(stock_tier(59.9), "avoid")


class TestShortTermAction(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(short_term_action(80), "actionable")
        self.assertEqual(short_term_action(79.9), "tactical_only")
        self.assertEqual(short_term_action(70), "tactical_only")
        self.assertEqual(short_term_action(69.9), "watch")
        self.assertEqual(short_term_action(60), "watch")
        self.assertEqual(short_term_action(59.9), "avoid")


class TestSwingTradeVerdict(unittest.TestCase):
    def test_actionable_positive_rr_becomes_current_trade(self):
        score = score_short_term({k: 85.0 for k in SHORT_TERM_WEIGHTS}, symbol="AMD")
        verdict = decide_swing_trade_verdict(score, rr_verdict="positive_expectancy")
        self.assertEqual(verdict.verdict, "current_trade")
        self.assertFalse(verdict.hard_vetoes)

    def test_tactical_marginal_rr_becomes_small_starter(self):
        factors = {k: 75.0 for k in SHORT_TERM_WEIGHTS}
        score = score_short_term(factors, symbol="MU")
        verdict = decide_swing_trade_verdict(score, rr_verdict="marginal")
        self.assertEqual(verdict.verdict, "small_starter")

    def test_price_strength_alone_is_not_fomo_veto(self):
        score = score_short_term({k: 86.0 for k in SHORT_TERM_WEIGHTS}, symbol="FLEX")
        verdict = decide_swing_trade_verdict(
            score,
            rr_verdict="positive_expectancy",
            checks={"fomo_justified": True},
            has_defined_stop=True,
            has_volume_confirmation=True,
            price_extended_without_rr=False,
        )
        self.assertEqual(verdict.verdict, "current_trade")
        self.assertIn("fomo_justified", verdict.triggered_vetoes)
        self.assertNotIn("fomo_justified", verdict.hard_vetoes)

    def test_data_failure_requires_etf_fallback_review(self):
        score = score_short_term({k: 82.0 for k in SHORT_TERM_WEIGHTS}, symbol="WDC")
        verdict = decide_swing_trade_verdict(
            score,
            rr_verdict="positive_expectancy",
            checks={"single_source_critical_data": True},
            fallback_symbols=("SMH", "SOXX"),
        )
        self.assertEqual(verdict.verdict, "hard_veto")
        self.assertTrue(verdict.requires_fallback_review)
        self.assertEqual(verdict.fallback_symbols, ("SMH", "SOXX"))


class TestCheckVeto(unittest.TestCase):
    def test_no_vetoes(self):
        from interface.models import StockScoreResult
        result = StockScoreResult(symbol="MU", sector="semiconductor", scores={}, weighted_score=85.0, tier="core")
        vetoes = check_veto(result, {})
        self.assertEqual(len(vetoes), 0)

    def test_single_veto(self):
        from interface.models import StockScoreResult
        result = StockScoreResult(symbol="MU", sector="semiconductor", scores={}, weighted_score=85.0, tier="core")
        vetoes = check_veto(result, {"stale_data": True, "fomo_justified": False})
        self.assertEqual(len(vetoes), 1)
        self.assertIn("stale_data", vetoes)

    def test_multiple_vetoes(self):
        from interface.models import StockScoreResult
        result = StockScoreResult(symbol="MU", sector="semiconductor", scores={}, weighted_score=85.0, tier="core")
        vetoes = check_veto(result, {
            "stale_data": True,
            "narrative_only_beneficiary": True,
            "fomo_justified": True,
        })
        self.assertEqual(len(vetoes), 3)


if __name__ == "__main__":
    unittest.main()
