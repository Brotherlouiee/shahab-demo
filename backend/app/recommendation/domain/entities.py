"""Immutable, framework-free inputs and outputs for the recommendation engine."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class LoanCandidate:
    loan_id: str
    categories: dict[str, str]


@dataclass(frozen=True)
class AnswerPreference:
    variable_id: str
    category_id: str
    weight: Decimal


@dataclass(frozen=True)
class ScoredLoan:
    loan_id: str
    score: Decimal


class RecommendationInputError(ValueError):
    """Raised when a score cannot be computed from a complete valid input."""
