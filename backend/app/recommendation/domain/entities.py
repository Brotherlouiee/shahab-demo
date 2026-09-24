"""Immutable, framework-free inputs and outputs for the recommendation engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum


class ClassificationState(StrEnum):
    CLASSIFIED = "classified"
    UNKNOWN = "unknown"
    VARIABLE = "variable"
    NEUTRAL = "neutral"


class RecommendationDecision(StrEnum):
    RANKED = "ranked"
    NEEDS_REVIEW = "needs_review"


@dataclass(frozen=True)
class LoanCandidate:
    loan_id: str
    categories: dict[str, str | None]
    category_states: dict[str, ClassificationState] = field(default_factory=dict)

    def state_for(self, variable_id: str) -> ClassificationState:
        if variable_id in self.category_states:
            return self.category_states[variable_id]
        return ClassificationState.CLASSIFIED if self.categories.get(variable_id) else ClassificationState.UNKNOWN


@dataclass(frozen=True)
class AnswerPreference:
    variable_id: str
    category_id: str
    weight: Decimal


@dataclass(frozen=True)
class ScoredLoan:
    loan_id: str
    score: Decimal


@dataclass(frozen=True)
class NeedsReviewLoan:
    loan_id: str
    excluded_reasons: tuple[str, ...]


@dataclass(frozen=True)
class RecommendationPartition:
    ranked: tuple[ScoredLoan, ...]
    needs_review: tuple[NeedsReviewLoan, ...]


@dataclass(frozen=True)
class TraceContribution:
    """A redacted per-variable explanation; it contains category IDs, never raw answers."""

    variable_id: str
    preferred_category_id: str
    candidate_category_id: str | None
    classification_state: ClassificationState
    preference_weight: Decimal
    included_in_effective_weight: bool
    matched: bool | None
    neutral: bool
    reason: str | None


@dataclass(frozen=True)
class RecommendationTrace:
    """Versioned, deterministic evidence for one loan decision without user/session data."""

    trace_version: str
    data_version: str
    config_version: str
    loan_id: str
    decision: RecommendationDecision
    raw_score: Decimal | None
    normalized_score: Decimal | None
    effective_weight: Decimal
    neutral_variables: tuple[str, ...]
    ranking_excluded_reasons: tuple[str, ...]
    contributions: tuple[TraceContribution, ...]
    stable_hash: str


class RecommendationInputError(ValueError):
    """Raised when a score cannot be computed from a complete valid input."""
