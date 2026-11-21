"""Deterministic weighted-category scoring with no I/O or framework dependency."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

from backend.app.recommendation.domain.entities import (
    AnswerPreference,
    ClassificationState,
    LoanCandidate,
    NeedsReviewLoan,
    RecommendationInputError,
    RecommendationPartition,
    ScoredLoan,
)

CORE_VARIABLE_IDS = frozenset({"maxAmount", "monthlyInstallment", "maxRepaymentMonths", "interestRate"})
NEUTRAL_VARIABLE_IDS = frozenset({"depositRequired", "depositHoldingMonths", "loanToDepositRatio"})
_SCORE_SCALE = Decimal("0.000001")


def score_loan(candidate: LoanCandidate, preferences: tuple[AnswerPreference, ...]) -> ScoredLoan:
    """Return an exact weighted match ratio, excluding approved neutral attributes."""
    if not candidate.loan_id:
        raise RecommendationInputError("loan_id is required")
    if not preferences:
        raise RecommendationInputError("at least one preference is required")

    total_weight = Decimal("0")
    matched_weight = Decimal("0")
    seen_variables: set[str] = set()

    for preference in preferences:
        _validate_preference(preference, seen_variables)
        state = candidate.state_for(preference.variable_id)
        if preference.variable_id in CORE_VARIABLE_IDS and state is not ClassificationState.CLASSIFIED:
            raise RecommendationInputError("candidate core variable is not rankable")
        if preference.variable_id in NEUTRAL_VARIABLE_IDS and state is not ClassificationState.CLASSIFIED:
            continue
        if preference.variable_id not in candidate.categories:
            raise RecommendationInputError("candidate is missing a required variable")

        total_weight += preference.weight
        if candidate.categories[preference.variable_id] == preference.category_id:
            matched_weight += preference.weight

    if total_weight <= 0:
        raise RecommendationInputError("at least one non-neutral preference is required")
    score = (matched_weight / total_weight).quantize(_SCORE_SCALE, rounding=ROUND_HALF_UP)
    return ScoredLoan(loan_id=candidate.loan_id, score=score)


def partition_loans(
    candidates: tuple[LoanCandidate, ...],
    preferences: tuple[AnswerPreference, ...],
) -> RecommendationPartition:
    """Separate non-rankable core-unknown loans before deterministic ranking."""
    ranked: list[ScoredLoan] = []
    needs_review: list[NeedsReviewLoan] = []

    for candidate in candidates:
        reasons = tuple(
            f"{preference.variable_id}:{candidate.state_for(preference.variable_id)}"
            for preference in preferences
            if preference.variable_id in CORE_VARIABLE_IDS
            and candidate.state_for(preference.variable_id) is not ClassificationState.CLASSIFIED
        )
        if reasons:
            needs_review.append(NeedsReviewLoan(candidate.loan_id, reasons))
        else:
            ranked.append(score_loan(candidate, preferences))

    return RecommendationPartition(
        ranked=tuple(sorted(ranked, key=lambda item: (-item.score, item.loan_id))),
        needs_review=tuple(sorted(needs_review, key=lambda item: item.loan_id)),
    )


def rank_loans(
    candidates: tuple[LoanCandidate, ...],
    preferences: tuple[AnswerPreference, ...],
) -> tuple[ScoredLoan, ...]:
    """Compatibility helper that rejects candidates outside the rankable partition."""
    partition = partition_loans(candidates, preferences)
    if partition.needs_review:
        raise RecommendationInputError("non-rankable loans must be handled as needs_review")
    return partition.ranked


def _validate_preference(preference: AnswerPreference, seen_variables: set[str]) -> None:
    if not preference.variable_id or not preference.category_id:
        raise RecommendationInputError("preference identifiers are required")
    if preference.variable_id in seen_variables:
        raise RecommendationInputError("each variable may appear once")
    if preference.weight <= 0:
        raise RecommendationInputError("weights must be positive")
    seen_variables.add(preference.variable_id)
