"""Atomic account/profile creation and updates scoped to an immutable account ID."""

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.accounts.identity import AccountActor, require_active_account
from backend.app.accounts.phone import normalize_phone
from backend.app.api.errors import ApiError, ErrorCode
from backend.app.infrastructure.db.models import Account, UserProfile

from .profile_schema import ProfilePayload


def _response(profile: UserProfile, phone: str) -> ProfilePayload:
    return ProfilePayload(
        phone=phone,
        firstName=profile.first_name,
        lastName=profile.last_name,
        income=profile.income,
        job=profile.job,
        gender=profile.gender,
        avatar=profile.avatar_data_url,
    )


def _database_session(session: Session | None) -> Session:
    if session is None:
        raise ApiError(
            status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Profile service is temporarily unavailable."
        )
    return session


def read_profile(actor: AccountActor, session: Session | None) -> ProfilePayload:
    db = _database_session(session)
    current = require_active_account(actor.account_id, db)
    record = db.get(UserProfile, current.account_id)
    if record is None:
        raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="Profile was not found.")
    return _response(record, current.phone)


def ensure_profile(phone: str, session: Session | None) -> AccountActor:
    """Return the verified active generation, creating its empty profile atomically.

    The partial unique index is the race arbiter. A losing insert rolls back the
    whole account/profile transaction before re-reading the winner. Archived rows
    are never reused. A profile missing from an existing account is corruption,
    not permission to overwrite or invent its facts.
    """
    db = _database_session(session)
    phone = normalize_phone(phone)
    for attempt in range(2):
        try:
            # Serialize against archive before locking the active account row.
            # The partial unique index remains the final race arbiter.
            if db.get_bind().dialect.name == "postgresql":
                from sqlalchemy import func
                db.execute(select(func.pg_advisory_xact_lock(func.hashtextextended(phone, 110211))))
            account = db.scalar(
                select(Account)
                .where(Account.phone == phone, Account.status == "active")
                .with_for_update(read=True)
                .execution_options(populate_existing=True)
            )
            if account is not None:
                if db.get(UserProfile, account.account_id) is None:
                    raise RuntimeError("account profile invariant")
                return AccountActor(account.account_id, account.phone)
            account = Account(account_id=uuid.uuid4(), phone=phone, status="active")
            db.add(account)
            db.flush()
            db.add(
                UserProfile(account_id=account.account_id, first_name="", last_name="", income="", job="", gender="")
            )
            db.commit()
            # Reacquire status/lock: an archive between commit and issuance fails closed.
            return require_active_account(account.account_id, db)
        except IntegrityError:
            db.rollback()
            if attempt == 0:
                continue
        except Exception:
            db.rollback()
            break
        break
    raise ApiError(
        status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Profile could not be created."
    ) from None


def upsert_profile(payload: ProfilePayload, actor: AccountActor, session: Session | None) -> ProfilePayload:
    db = _database_session(session)
    current = require_active_account(actor.account_id, db)
    if payload.phone != current.phone:
        raise ApiError(status_code=403, code=ErrorCode.FORBIDDEN, message="Profile access is not allowed.")
    record = db.get(UserProfile, current.account_id)
    if record is None:
        raise ApiError(status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Profile could not be saved.")
    record.first_name, record.last_name = payload.firstName, payload.lastName
    record.income, record.job, record.gender = payload.income, payload.job, payload.gender
    record.avatar_data_url = payload.avatar
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise ApiError(
            status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Profile could not be saved."
        ) from None
    db.refresh(record)
    return _response(record, current.phone)
