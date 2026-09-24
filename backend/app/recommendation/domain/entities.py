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


class RecommendationInputError(ValueError):
    """Raised when a score cannot be computed from a complete valid input."""
