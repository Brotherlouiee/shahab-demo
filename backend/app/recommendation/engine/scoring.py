"""Deterministic weighted-category scoring with no I/O or framework dependency."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from backend.app.recommendation.domain.entities import (
    AnswerPreference,
    LoanCandidate,
    RecommendationInputError,
    ScoredLoan,
)

_SCORE_SCALE = Decimal("0.000001")


def score_loan(candidate: LoanCandidate, preferences: tuple[AnswerPreference, ...]) -> ScoredLoan:
    """Return an exact weighted match ratio for one fully classified loan."""
    if not candidate.loan_id:
        raise RecommendationInputError("loan_id is required")
    if not preferences:
        raise RecommendationInputError("at least one preference is required")

    total_weight = Decimal("0")
    matched_weight = Decimal("0")
    seen_variables: set[str] = set()

    for preference in preferences:
        if not preference.variable_id or not preference.category_id:
            raise RecommendationInputError("preference identifiers are required")
        if preference.variable_id in seen_variables:
            raise RecommendationInputError("each variable may appear once")
        if preference.weight <= 0:
            raise RecommendationInputError("weights must be positive")
        if preference.variable_id not in candidate.categories:
            raise RecommendationInputError("candidate is missing a required variable")

        seen_variables.add(preference.variable_id)
        total_weight += preference.weight
        if candidate.categories[preference.variable_id] == preference.category_id:
            matched_weight += preference.weight

    score = (matched_weight / total_weight).quantize(_SCORE_SCALE, rounding=ROUND_HALF_UP)
    return ScoredLoan(loan_id=candidate.loan_id, score=score)


def rank_loans(
    candidates: tuple[LoanCandidate, ...],
    preferences: tuple[AnswerPreference, ...],
) -> tuple[ScoredLoan, ...]:
    """Score then order by score descending and stable loan identifier ascending."""
    return tuple(
        sorted(
            (score_loan(candidate, preferences) for candidate in candidates),
            key=lambda item: (-item.score, item.loan_id),
        )
    )
