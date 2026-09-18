"""Small dependency-inversion ports for future Shahab application use cases."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol

from backend.app.domain.loan import LoanReference, RecommendationConfigReference


class TransactionManager(Protocol):
    """Application transaction boundary; concrete sessions stay in infrastructure."""

    def commit(self) -> None: ...

    def rollback(self) -> None: ...


class LoanRepository(Protocol):
    """Read-only loan access split by rankability; implementations belong to infrastructure."""

    def list_rankable_loans(self) -> tuple[LoanReference, ...]:
        """Return only loans eligible for main ranking under approved data decisions."""

    def list_loans_needing_review(self) -> tuple[LoanReference, ...]:
        """Return loans excluded from ranking because core data are not classifiable."""

    def get_loan_by_id(self, loan_id: str) -> LoanReference | None:
        """Look up a single stable loan reference without transport concerns."""


class RecommendationConfigRepository(Protocol):
    """Reads exactly one approved configuration reference for a recommendation run."""

    def get_approved_config(self) -> RecommendationConfigReference:
        """Return the approved immutable configuration reference."""


class Clock(Protocol):
    """Time boundary for reproducible use cases and deterministic tests."""

    def now(self) -> datetime:
        """Return the current timezone-aware instant."""


class IdGenerator(Protocol):
    """Identifier boundary used only when a use case needs a new trace/session ID."""

    def new_id(self) -> str:
        """Return a collision-resistant opaque identifier."""
