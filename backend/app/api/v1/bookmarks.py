"""Authenticated desired-state bookmark API; client facts/owner/score are forbidden."""

import base64
import json
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.accounts.bookmarks import AccountBookmarkRepository
from backend.app.accounts.identity import AccountActor
from backend.app.api.errors import ApiError, ErrorCode
from backend.app.core.dependencies import get_request_database_session

from .account_access import authenticated_account
from .recommendation_history import HistoryRankedItem, LoanSummary

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


class BookmarkContext(BaseModel):
    model_config = ConfigDict(extra="forbid", json_schema_extra={"example": {}})
    historyId: UUID | None = None


class BookmarkPage(BaseModel):
    items: list[HistoryRankedItem]
    nextCursor: str | None


def repository(db: Session | None) -> AccountBookmarkRepository:
    if db is None:
        raise unavailable()
    return AccountBookmarkRepository(db)


def unavailable() -> ApiError:
    return ApiError(status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Bookmarks are unavailable.")


@router.get("", response_model=BookmarkPage, response_model_by_alias=True)
def list_bookmarks(
    actor: Annotated[AccountActor, Depends(authenticated_account)],
    db: Annotated[Session | None, Depends(get_request_database_session)],
    response: Response,
    limit: int = Query(50, ge=1, le=50),
    cursor: str | None = Query(None, max_length=256),
) -> BookmarkPage:
    response.headers["Cache-Control"] = "no-store"
    decoded = None
    if cursor is not None:
        try:
            value = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
            if not isinstance(value, list) or len(value) != 2 or not all(isinstance(item, str) for item in value):
                raise ValueError
            timestamp = datetime.fromisoformat(value[0])
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError
            decoded = timestamp, UUID(value[1])
        except (ValueError, TypeError, UnicodeDecodeError, json.JSONDecodeError):
            raise ApiError(
                status_code=422, code=ErrorCode.INVALID_REQUEST, message="Bookmark cursor is invalid."
            ) from None
    try:
        rows = repository(db).list_for_owner(actor, limit, decoded)
    except SQLAlchemyError:
        raise unavailable() from None
    next_cursor = None
    if len(rows) > limit:
        bookmark = rows[limit - 1][0]
        next_cursor = base64.urlsafe_b64encode(
            json.dumps(
                [
                    (
                        bookmark.created_at if bookmark.created_at.tzinfo else bookmark.created_at.replace(tzinfo=UTC)
                    ).isoformat(),
                    str(bookmark.loan_product_version_id),
                ]
            ).encode()
        ).decode()
    items = []
    for bookmark, product, lender, terms, facts, snapshot in rows[:limit]:
        summary = LoanSummary(
            maxAmountTomans=snapshot.max_amount_tomans if snapshot is not None else terms.max_amount if terms else None,
            monthlyInstallmentTomans=snapshot.monthly_installment_tomans
            if snapshot is not None
            else terms.monthly_installment
            if terms
            else None,
            maxRepaymentMonths=snapshot.max_repayment_months
            if snapshot is not None
            else terms.max_repayment_months
            if terms
            else None,
            interestRatePercent=snapshot.interest_rate_percent
            if snapshot is not None
            else terms.interest_rate
            if terms
            else None,
        )
        items.append(
            HistoryRankedItem(
                loanId=str(bookmark.loan_product_version_id),
                lenderName=snapshot.lender_name if snapshot is not None else lender.canonical_name,
                loanName=snapshot.loan_name if snapshot is not None else product.canonical_name,
                bankLogoReference=snapshot.bank_logo_reference
                if snapshot is not None
                else facts.bank_logo_reference
                if facts
                else None,
                loanSummary=summary,
                compatibilityScore=snapshot.compatibility_score if snapshot is not None else None,
                compatibilityReason=snapshot.compatibility_reason if snapshot is not None else None,
            )
        )
    return BookmarkPage(items=items, nextCursor=next_cursor)


@router.put("/{loan_id}", status_code=204)
def save_bookmark(
    loan_id: UUID,
    payload: BookmarkContext,
    actor: Annotated[AccountActor, Depends(authenticated_account)],
    db: Annotated[Session | None, Depends(get_request_database_session)],
) -> Response:
    try:
        repository(db).save(actor, loan_id, payload.historyId)
        assert db is not None
        db.commit()
    except LookupError:
        raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="Bookmark target was not found.") from None
    except SQLAlchemyError:
        if db is not None:
            db.rollback()
        raise unavailable() from None
    return Response(status_code=204, headers={"Cache-Control": "no-store"})


@router.delete("/{loan_id}", status_code=204)
def remove_bookmark(
    loan_id: UUID,
    actor: Annotated[AccountActor, Depends(authenticated_account)],
    db: Annotated[Session | None, Depends(get_request_database_session)],
) -> Response:
    try:
        repository(db).remove(actor, loan_id)
        assert db is not None
        db.commit()
    except SQLAlchemyError:
        if db is not None:
            db.rollback()
        raise unavailable() from None
    return Response(status_code=204, headers={"Cache-Control": "no-store"})
