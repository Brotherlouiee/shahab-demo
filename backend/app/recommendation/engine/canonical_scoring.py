"""Official weighted answer/category scoring for a completed canonical questionnaire."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from backend.app.recommendation.domain.entities import (
    ClassificationState,
    LoanCandidate,
    NeedsReviewLoan,
    RecommendationInputError,
    ScoredLoan,
)
from backend.app.recommendation.engine.scoring import CORE_VARIABLE_IDS, NEUTRAL_VARIABLE_IDS


@dataclass(frozen=True)
class CategoryImpact:
    variable_id: str
    category_id: str
    answer_id: str
    normalized_question_weight: Decimal
    impact_factor: Decimal
    source_row: int
    source_column: int


@dataclass(frozen=True)
class CanonicalPartition:
    ranked: tuple[ScoredLoan, ...]
    needs_review: tuple[NeedsReviewLoan, ...]
    below_threshold: tuple[ScoredLoan, ...]
    # No answer IDs or session ID: per-loan redacted computation evidence.
    evidence: dict[str, tuple[Decimal, Decimal, tuple[str, ...]]]


def score_official_categories(
    candidates: tuple[LoanCandidate, ...],
    impacts: tuple[CategoryImpact, ...],
    *,
    minimum_match_score: Decimal = Decimal("0.5"),
) -> CanonicalPartition:
    """Sum source conversion weights × one-to-one factors, then score paths.

    A loan has exactly one category per classified variable, so the product of
    its eight category scores is its one valid tree path. Unknown deposit nodes
    are excluded from the product and effective weight. The maximum candidate
    raw score normalizes results; the documented 50% threshold applies after it.
    """
    if not candidates or not impacts:
        if impacts:
            return CanonicalPartition((), (), (), {})
        raise RecommendationInputError("approved category impacts are required")
    if not Decimal("0") <= minimum_match_score <= Decimal("1"):
        raise RecommendationInputError("minimum match score is invalid")
    categories: dict[tuple[str, str], Decimal] = {}
    seen_cells: set[tuple[str, str, str]] = set()
    for item in impacts:
        key = (item.variable_id, item.category_id)
        cell = (*key, item.answer_id)
        if cell in seen_cells or not 0 <= item.normalized_question_weight <= 1 or not 0 <= item.impact_factor <= 1:
            raise RecommendationInputError("approved category impact is invalid or duplicated")
        seen_cells.add(cell)
        categories[key] = categories.get(key, Decimal("0")) + item.normalized_question_weight * item.impact_factor
    raw: dict[str, Decimal] = {}
    review: list[NeedsReviewLoan] = []
    evidence: dict[str, tuple[Decimal, Decimal, tuple[str, ...]]] = {}
    for candidate in candidates:
        reasons = tuple(
            sorted(
                f"{variable_id}:{candidate.state_for(variable_id).value}"
                for variable_id in CORE_VARIABLE_IDS
                if candidate.state_for(variable_id) is not ClassificationState.CLASSIFIED
            )
        )
        if reasons:
            review.append(NeedsReviewLoan(candidate.loan_id, reasons))
            continue
        product = Decimal("1")
        effective = Decimal("0")
        neutral: list[str] = []
        for variable_id, category_id in candidate.categories.items():
            state = candidate.state_for(variable_id)
            if state is not ClassificationState.CLASSIFIED and variable_id in NEUTRAL_VARIABLE_IDS:
                neutral.append(variable_id)
                continue
            if state is not ClassificationState.CLASSIFIED or category_id is None:
                raise RecommendationInputError("unclassified non-neutral loan variable")
            key = (variable_id, category_id)
            if key not in categories:
                raise RecommendationInputError("approved category score is missing")
            product *= categories[key]
            effective += Decimal("1")
        raw[candidate.loan_id] = product
        evidence[candidate.loan_id] = (product, effective, tuple(sorted(neutral)))
    highest = max(raw.values(), default=Decimal("0"))
    ranked: list[ScoredLoan] = []
    below: list[ScoredLoan] = []
    for loan_id, value in raw.items():
        score = value / highest if highest else Decimal("0")
        if score >= minimum_match_score:
            ranked.append(ScoredLoan(loan_id, score))
        else:
            below.append(ScoredLoan(loan_id, score))
    return CanonicalPartition(
        tuple(sorted(ranked, key=lambda item: (-item.score, item.loan_id))),
        tuple(sorted(review, key=lambda item: item.loan_id)),
        tuple(sorted(below, key=lambda item: (item.score, item.loan_id))),
        evidence,
    )
