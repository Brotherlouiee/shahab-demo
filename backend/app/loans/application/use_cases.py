"""Read-only catalogue use cases with no FastAPI, ORM or source-document dependency."""

from __future__ import annotations

from backend.app.loans.application.ports import ServingLoanCatalogueRepository
from backend.app.loans.domain.models import LoanDetail, LoanSummary


class ListLoans:
    """List the current approved serving catalogue in deterministic display order."""

    def __init__(self, repository: ServingLoanCatalogueRepository) -> None:
        self._repository = repository

    def execute(self) -> tuple[LoanSummary, ...]:
        """Return safe summaries sorted by lender, loan name and opaque identifier."""
        records = self._repository.list_current_serving_loans()
        return tuple(
            record.summary
            for record in sorted(
                records,
                key=lambda record: (
                    record.summary.lender_name.casefold(),
                    record.summary.loan_name.casefold(),
                    record.summary.loan_id,
                ),
            )
        )


class GetLoanDetails:
    """Return one approved serving loan detail without interpreting its conditions."""

    def __init__(self, repository: ServingLoanCatalogueRepository) -> None:
        self._repository = repository

    def execute(self, loan_id: str) -> LoanDetail | None:
        """Look up an opaque loan ID; blank IDs are rejected before adapter access."""
        if not loan_id.strip():
            raise ValueError("loan id is required")
        record = self._repository.get_current_serving_loan(loan_id)
        return None if record is None else record.detail
