"""Test/local serving-catalogue adapter with an explicit active-version boundary."""

from __future__ import annotations

from backend.app.loans.application.ports import ServingLoanCatalogueRepository
from backend.app.loans.domain.models import PublishedLoanRecord


class InMemoryServingLoanCatalogueRepository(ServingLoanCatalogueRepository):
    """Expose only records whose version equals the declared approved serving ID."""

    def __init__(self, *, active_serving_version_id: str, records: tuple[PublishedLoanRecord, ...]) -> None:
        if not active_serving_version_id.strip():
            raise ValueError("active serving version id is required")
        self._active_serving_version_id = active_serving_version_id
        self._records = tuple(
            record for record in records if record.serving_version_id == self._active_serving_version_id
        )

    def list_current_serving_loans(self) -> tuple[PublishedLoanRecord, ...]:
        return self._records

    def get_current_serving_loan(self, loan_id: str) -> PublishedLoanRecord | None:
        return next((record for record in self._records if record.summary.loan_id == loan_id), None)
