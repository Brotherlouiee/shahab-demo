"""Database authority for immutable customer identities, independent of operator grants."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.api.errors import ApiError, ErrorCode
from backend.app.infrastructure.db.models import Account


@dataclass(frozen=True)
class AccountActor:
    account_id: UUID
    phone: str


def require_active_account(account_id: UUID, session: Session | None) -> AccountActor:
    """Lock and freshly validate this exact generation until the request transaction ends.

    Shared locks permit concurrent reads and block archive/update; mutation callers
    use the same account lock before touching owned children. No phone lookup can
    retarget an issued credential to a newer generation.
    """
    if session is None:
        raise ApiError(
            status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Account service is temporarily unavailable."
        )
    account = session.scalar(
        select(Account)
        .where(Account.account_id == account_id, Account.status == "active")
        .with_for_update(read=True)
        .execution_options(populate_existing=True)
    )
    if account is None:
        raise ApiError(status_code=401, code=ErrorCode.UNAUTHORIZED, message="Account access could not be completed.")
    return AccountActor(account.account_id, account.phone)
