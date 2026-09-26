"""Versioned HTTP adapter for one approved serving-loan detail."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from backend.app.api.errors import ApiError, ErrorCode
from backend.app.core.dependencies import get_loan_details_use_case
from backend.app.loans.application.use_cases import GetLoanDetails
from backend.app.loans.domain.models import ServingCatalogueUnavailableError

from .loan_schemas import LoanDetailResponse

router = APIRouter(prefix="/loans", tags=["loans"])


@router.get("/{loan_id}", response_model=LoanDetailResponse)
def get_loan_detail(
    loan_id: str,
    use_case: Annotated[GetLoanDetails, Depends(get_loan_details_use_case)],
) -> LoanDetailResponse:
    """Return only approved serving facts; identifiers never select a source version."""
    try:
        loan = use_case.execute(loan_id)
    except ServingCatalogueUnavailableError as error:
        raise ApiError(
            status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Loan catalogue is temporarily unavailable."
        ) from error
    except ValueError as error:
        raise ApiError(status_code=422, code=ErrorCode.INVALID_REQUEST, message="Loan ID is invalid.") from error
    if loan is None:
        raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="Loan was not found.")
    return LoanDetailResponse.from_loan_detail(loan)
