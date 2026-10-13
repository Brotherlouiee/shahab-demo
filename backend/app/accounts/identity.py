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


def archive_account(account_id: UUID, session: Session | None) -> None:
    """Internal use case only: archive one generation and revoke every credential atomically.

    Acquire the account row before session rows, matching readers' lock order.
    Concurrent authenticated requests either finish before archival commits or
    revalidate the archived identity and fail closed. No customer HTTP route exists.
    Existing profile, history, bookmarks and evidence are retained untouched.
    """
    from datetime import UTC, datetime

    from sqlalchemy import func, update
    from sqlalchemy.exc import SQLAlchemyError

    from backend.app.infrastructure.db.models import AccountAccessSession

    if session is None:
        raise ApiError(status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Account service unavailable.")
    try:
        # The phone is immutable; acquire the same advisory lock as verified login
        # before the account row lock to serialize archival with new login.
        phone = session.scalar(select(Account.phone).where(Account.account_id == account_id))
        if phone is None:
            raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="Account not found.")
        if session.get_bind().dialect.name == "postgresql":
            session.execute(select(func.pg_advisory_xact_lock(func.hashtextextended(phone, 110211))))
        account = session.scalar(
            select(Account).where(Account.account_id == account_id)
            .with_for_update().execution_options(populate_existing=True)
        )
        if account is None or account.status != "active":
            raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="Account not found.")
        now = (
            session.scalar(select(func.clock_timestamp()))
            if session.get_bind().dialect.name == "postgresql" else datetime.now(UTC)
        )
        account.status = "archived"
        created = account.created_at.replace(tzinfo=UTC) if account.created_at.tzinfo is None else account.created_at
        account.archived_at = max(now, created)
        session.flush()
        session.execute(
            update(AccountAccessSession)
            .where(AccountAccessSession.account_id == account_id, AccountAccessSession.revoked_at.is_(None))
            .values(revoked_at=account.archived_at)
        )
        session.commit()
    except ApiError:
        session.rollback()
        raise
    except SQLAlchemyError:
        session.rollback()
        raise ApiError(status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Account archival failed.") from None
