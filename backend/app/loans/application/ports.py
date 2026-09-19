"""Outbound catalogue port; adapters must filter to the current approved serving version."""

from __future__ import annotations

from typing import Protocol

from backend.app.loans.domain.models import PublishedLoanRecord


class ServingLoanCatalogueRepository(Protocol):
    """Read only the single active approved serving catalogue.

    Draft, rejected, superseded and raw/staging records must never be returned.
    This is a security and product boundary: transport/UI code cannot choose a
    source version or bypass the approval state through this use case.
    """

    def list_current_serving_loans(self) -> tuple[PublishedLoanRecord, ...]:
        """Return records from one current approved serving version only."""

    def get_current_serving_loan(self, loan_id: str) -> PublishedLoanRecord | None:
        """Return one record from that same serving version, or no record."""
