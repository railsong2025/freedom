"""Sector and stock scoring engine for the Poseidon Research Division.

Implements the exact scoring rubrics from
.codex/skills/buffett/references/sector-stock-playbook.md.
"""

from __future__ import annotations

from interface.constants import (
    SECTOR_RATING_THRESHOLDS,
    SECTOR_WEIGHTS,
    SHORT_TERM_THRESHOLDS,
    SHORT_TERM_WEIGHTS,
    STOCK_TIER_THRESHOLDS,
    STOCK_WEIGHTS,
    VETO_CONDITIONS,
)
from interface.models import SectorScoreResult, ShortTermScoreResult, StockScoreResult, SwingTradeVerdict


MIN_SCORE_COVERAGE_PCT = 80.0

POSITIVE_RR_VERDICTS = {"positive_expectancy", "marginal"}
DATA_QUALITY_VETOES = {"single_source_critical_data", "stale_data"}


def _validated_scores(
    factors: dict[str, float],
    weights: dict[str, float],
) -> tuple[dict[str, float], tuple[str, ...], tuple[str, ...], float]:
    scores: dict[str, float] = {}
    invalid: list[str] = []
    for factor, value in factors.items():
        if factor not in weights:
            continue
        if not isinstance(value, (int, float)) or value < 0 or value > 100:
            invalid.append(factor)
            continue
        scores[factor] = float(value)
    missing = tuple(factor for factor in weights if factor not in scores)
    covered_weight = sum(weight for factor, weight in weights.items() if factor in scores)
    coverage_pct = covered_weight / sum(weights.values()) * 100 if weights else 0.0
    return scores, missing, tuple(invalid), round(coverage_pct, 2)


def _weighted_score(factors: dict[str, float], weights: dict[str, float]) -> float:
    """Compute weighted score from 0-100 factor scores and weights."""
    total_weight = 0.0
    total_score = 0.0
    for factor, weight in weights.items():
        score = factors.get(factor)
        if score is not None:
            total_weight += weight
            total_score += score * weight
    if total_weight == 0:
        return 0.0
    return round(total_score / total_weight, 2)


def score_sector(factors: dict[str, float], sector: str = "") -> SectorScoreResult:
    """Compute sector score 0-100 using SECTOR_WEIGHTS.

    ``factors`` maps factor name to 0-100 score. Missing or invalid factors are
    reported in the result; if weighted evidence coverage is below 80%, the
    rating is downgraded to ``insufficient_evidence`` to prevent false
    confidence from renormalized partial scores.
    """
    scores, missing, invalid, coverage_pct = _validated_scores(factors, SECTOR_WEIGHTS)
    weighted = _weighted_score(scores, SECTOR_WEIGHTS)
    rating = "insufficient_evidence" if coverage_pct < MIN_SCORE_COVERAGE_PCT or invalid else sector_rating(weighted)
    return SectorScoreResult(
        sector=sector,
        scores=scores,
        weighted_score=weighted,
        rating=rating,
        coverage_pct=coverage_pct,
        missing_factors=missing,
        invalid_factors=invalid,
    )


def score_stock(factors: dict[str, float], sector: str = "", symbol: str = "") -> StockScoreResult:
    """Compute stock score 0-100 using STOCK_WEIGHTS."""
    scores, missing, invalid, coverage_pct = _validated_scores(factors, STOCK_WEIGHTS)
    weighted = _weighted_score(scores, STOCK_WEIGHTS)
    tier = "insufficient_evidence" if coverage_pct < MIN_SCORE_COVERAGE_PCT or invalid else stock_tier(weighted)
    return StockScoreResult(
        symbol=symbol,
        sector=sector,
        scores=scores,
        weighted_score=weighted,
        tier=tier,
        coverage_pct=coverage_pct,
        missing_factors=missing,
        invalid_factors=invalid,
    )


def score_short_term(factors: dict[str, float], symbol: str = "") -> ShortTermScoreResult:
    """Compute short-term score 0-100 using SHORT_TERM_WEIGHTS."""
    scores, missing, invalid, coverage_pct = _validated_scores(factors, SHORT_TERM_WEIGHTS)
    weighted = _weighted_score(scores, SHORT_TERM_WEIGHTS)
    action = "insufficient_evidence" if coverage_pct < MIN_SCORE_COVERAGE_PCT or invalid else short_term_action(weighted)
    return ShortTermScoreResult(
        symbol=symbol,
        scores=scores,
        weighted_score=weighted,
        action_bias=action,
        coverage_pct=coverage_pct,
        missing_factors=missing,
        invalid_factors=invalid,
    )


def sector_rating(score: float) -> str:
    """Map sector score to rating: overweight/tactical_overweight/neutral/underweight/avoid."""
    for threshold, label in SECTOR_RATING_THRESHOLDS:
        if score >= threshold:
            return label
    return "avoid"


def stock_tier(score: float) -> str:
    """Map stock score to tier: core/tactical/watch/avoid."""
    for threshold, label in STOCK_TIER_THRESHOLDS:
        if score >= threshold:
            return label
    return "avoid"


def short_term_action(score: float) -> str:
    """Map short-term score to action: actionable/tactical_only/watch/avoid."""
    for threshold, label in SHORT_TERM_THRESHOLDS:
        if score >= threshold:
            return label
    return "avoid"


def check_veto(stock_score: StockScoreResult, checks: dict[str, bool]) -> list[str]:
    """Return list of triggered veto conditions.

    ``checks`` maps veto condition name to True if triggered.
    Only conditions in VETO_CONDITIONS are recognized.
    """
    triggered: list[str] = []
    for condition in VETO_CONDITIONS:
        if checks.get(condition, False):
            triggered.append(condition)
    return triggered


def decide_swing_trade_verdict(
    short_term_score: ShortTermScoreResult,
    *,
    rr_verdict: str,
    checks: dict[str, bool] | None = None,
    has_defined_stop: bool = True,
    has_volume_confirmation: bool = True,
    within_risk_budget: bool = True,
    data_quality_ok: bool = True,
    price_extended_without_rr: bool = False,
    fallback_symbols: tuple[str, ...] = (),
) -> SwingTradeVerdict:
    """Convert a swing score into an auditable current-trade verdict.

    The workflow uses this as the hard boundary between "strong trend" and
    "FOMO". A stock being up is not by itself a hard veto. The FOMO veto only
    becomes hard when price extension breaks R/R, stop definition, volume
    confirmation, or risk-budget discipline.
    """
    checks = checks or {}
    raw_vetoes = tuple(condition for condition in VETO_CONDITIONS if checks.get(condition, False))
    hard_vetoes: list[str] = []
    reasons: list[str] = []

    rr_is_valid = rr_verdict in POSITIVE_RR_VERDICTS

    for veto in raw_vetoes:
        if veto == "fomo_justified":
            if price_extended_without_rr or not has_defined_stop or not has_volume_confirmation or not rr_is_valid:
                hard_vetoes.append(veto)
            else:
                reasons.append("price strength alone is not a FOMO veto when stop, volume, and fee-adjusted R/R pass")
            continue
        hard_vetoes.append(veto)

    if not data_quality_ok:
        hard_vetoes.append("data_quality_insufficient")
    if not has_defined_stop:
        hard_vetoes.append("missing_hard_stop")
    if not has_volume_confirmation:
        hard_vetoes.append("volume_relative_strength_unverified")
    if not within_risk_budget:
        hard_vetoes.append("risk_budget_or_position_limit_conflict")
    if rr_verdict in {"insufficient", "invalid"}:
        hard_vetoes.append(f"fee_adjusted_rr_{rr_verdict}")
    elif rr_verdict not in POSITIVE_RR_VERDICTS:
        hard_vetoes.append("fee_adjusted_rr_unknown")

    deduped_hard_vetoes = tuple(dict.fromkeys(hard_vetoes))
    data_only_failure = bool(deduped_hard_vetoes) and all(
        veto in DATA_QUALITY_VETOES or veto == "data_quality_insufficient"
        for veto in deduped_hard_vetoes
    )
    requires_fallback_review = data_only_failure and bool(fallback_symbols)

    if deduped_hard_vetoes:
        if requires_fallback_review:
            reasons.append("single-stock data failed; review ETF/basket fallback before declaring no-trade")
        else:
            reasons.append("hard veto condition blocks the current swing trade")
        verdict = "hard_veto"
    elif short_term_score.action_bias == "actionable" and rr_verdict == "positive_expectancy":
        verdict = "current_trade"
        reasons.append("score is actionable and fee-adjusted R/R is positive")
    elif short_term_score.action_bias in {"actionable", "tactical_only"} and rr_verdict in POSITIVE_RR_VERDICTS:
        verdict = "small_starter"
        reasons.append("setup supports a starter but not a full current trade")
    elif short_term_score.action_bias in {"watch", "insufficient_evidence"}:
        verdict = "wait"
        reasons.append("setup is plausible but not executable yet")
    else:
        verdict = "hard_veto"
        reasons.append("short-term score is avoid or insufficient for a swing trade")

    return SwingTradeVerdict(
        symbol=short_term_score.symbol,
        weighted_score=short_term_score.weighted_score,
        action_bias=short_term_score.action_bias,
        rr_verdict=rr_verdict,
        verdict=verdict,
        reasons=tuple(reasons),
        triggered_vetoes=raw_vetoes,
        hard_vetoes=deduped_hard_vetoes,
        fallback_symbols=fallback_symbols,
        requires_fallback_review=requires_fallback_review,
    )
