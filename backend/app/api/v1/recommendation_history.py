"""Owner-scoped read API for immutable recommendation history."""

import base64
import json
from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.app.accounts.identity import AccountActor
from backend.app.api.errors import ApiError, ErrorCode
from backend.app.core.dependencies import get_request_database_session
from backend.app.recommendation.infrastructure.history import RecommendationHistoryRepository

from .account_access import authenticated_account

router = APIRouter(prefix="/recommendation-history", tags=["recommendation-history"])


class HistoryEntry(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    history_id: str = Field(alias="historyId")
    created_at: str = Field(alias="createdAt")
    ranked_count: int = Field(alias="rankedCount")


class HistoryPage(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    items: list[HistoryEntry]
    next_cursor: str | None = Field(alias="nextCursor")


class LoanSummary(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    max_amount_tomans: float | None = Field(alias="maxAmountTomans")
    monthly_installment_tomans: float | None = Field(alias="monthlyInstallmentTomans")
    max_repayment_months: int | None = Field(alias="maxRepaymentMonths")
    interest_rate_percent: float | None = Field(alias="interestRatePercent")


class HistoryItemBase(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    loan_id: str = Field(alias="loanId")
    lender_name: str = Field(alias="lenderName")
    loan_name: str = Field(alias="loanName")
    bank_logo_reference: str | None = Field(alias="bankLogoReference")
    loan_summary: LoanSummary = Field(alias="loanSummary")


class HistoryRankedItem(HistoryItemBase):
    compatibility_score: float | None = Field(default=None, alias="compatibilityScore")
    compatibility_reason: str | None = Field(default=None, alias="compatibilityReason")


class HistoryReviewItem(HistoryItemBase):
    ranking_excluded_reasons: tuple[str, ...] = Field(alias="rankingExcludedReasons")


class HistoryDetail(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    data_version: str = Field(alias="dataVersion")
    config_version: str = Field(alias="configVersion")
    ranked_recommendations: list[HistoryRankedItem] = Field(alias="rankedRecommendations")
    low_compatibility_recommendations: list[HistoryRankedItem] = Field(alias="lowCompatibilityRecommendations")
    needs_review: list[HistoryReviewItem] = Field(alias="needsReview")


@router.get("", response_model=HistoryPage, response_model_by_alias=True)
def list_history(
    actor: Annotated[AccountActor, Depends(authenticated_account)],
    db: Annotated[Session | None, Depends(get_request_database_session)],
    limit: int = Query(20, ge=1, le=50),
    cursor: str | None = Query(None, max_length=256),
) -> HistoryPage:
    if db is None:
        raise ApiError(status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="History is unavailable.")
    decoded = None
    if cursor:
        try:
            value = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
            decoded = (datetime.fromisoformat(value[0]), UUID(value[1]))
        except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
            raise ApiError(
                status_code=422, code=ErrorCode.INVALID_REQUEST, message="History cursor is invalid."
            ) from None
    runs = RecommendationHistoryRepository(db).list_for_owner(actor, limit, decoded)
    next_cursor = None
    if len(runs) == limit:
        run = runs[-1][0]
        next_cursor = base64.urlsafe_b64encode(
            json.dumps([run.created_at.isoformat(), str(run.recommendation_history_run_id)]).encode()
        ).decode()
    return HistoryPage(
        items=[
            HistoryEntry(
                historyId=str(run.recommendation_history_run_id),
                createdAt=run.created_at.isoformat(),
                rankedCount=ranked_count,
            )
            for run, ranked_count in runs
        ],
        nextCursor=next_cursor,
    )


@router.get(
    "/{history_id}",
    response_model=HistoryDetail,
    response_model_by_alias=True,
)
def read_history(
    history_id: str,
    actor: Annotated[AccountActor, Depends(authenticated_account)],
    db: Annotated[Session | None, Depends(get_request_database_session)],
) -> HistoryDetail:
    if db is None:
        raise ApiError(status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="History is unavailable.")
    try:
        run, items, reasons = RecommendationHistoryRepository(db).read_for_owner(actor, history_id)
    except (LookupError, ValueError):
        raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="History entry was not found.") from None
    ranked: list[HistoryRankedItem] = []
    low: list[HistoryRankedItem] = []
    review: list[HistoryReviewItem] = []
    for item in items:
        summary = LoanSummary(
            maxAmountTomans=item.max_amount_tomans,
            monthlyInstallmentTomans=item.monthly_installment_tomans,
            maxRepaymentMonths=item.max_repayment_months,
            interestRatePercent=item.interest_rate_percent,
        )
        if item.section == "review":
            review.append(
                HistoryReviewItem(
                    loanId=str(item.loan_product_version_id),
                    lenderName=item.lender_name,
                    loanName=item.loan_name,
                    bankLogoReference=item.bank_logo_reference,
                    loanSummary=summary,
                    rankingExcludedReasons=reasons.get(item.recommendation_history_item_id, ()),
                )
            )
        else:
            (ranked if item.section == "ranked" else low).append(
                HistoryRankedItem(
                    loanId=str(item.loan_product_version_id),
                    lenderName=item.lender_name,
                    loanName=item.loan_name,
                    bankLogoReference=item.bank_logo_reference,
                    loanSummary=summary,
                    compatibilityScore=item.compatibility_score,
                    compatibilityReason=item.compatibility_reason,
                )
            )
    return HistoryDetail(
        dataVersion=run.data_version,
        configVersion=run.config_version,
        rankedRecommendations=ranked,
        lowCompatibilityRecommendations=low,
        needsReview=review,
    )


@router.delete("/{history_id}", status_code=204)
def hide_history(
    history_id: str,
    actor: Annotated[AccountActor, Depends(authenticated_account)],
    db: Annotated[Session | None, Depends(get_request_database_session)],
) -> Response:
    if db is None:
        raise ApiError(status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="History is unavailable.")
    try:
        hidden = RecommendationHistoryRepository(db).hide_for_owner(actor, history_id)
    except ValueError:
        hidden = False
    if not hidden:
        raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="History entry was not found.")
    db.commit()
    return Response(status_code=204)
