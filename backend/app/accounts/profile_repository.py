"""Profile persistence: one owned record, atomic writes and explicit storage failure."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.api.errors import ApiError, ErrorCode
from backend.app.infrastructure.db.models import UserProfile

from .profile_schema import ProfilePayload


def _response(profile: UserProfile) -> ProfilePayload:
    return ProfilePayload(
        phone=profile.phone,
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


def read_profile(phone: str, session: Session | None) -> ProfilePayload:
    record = _database_session(session).get(UserProfile, phone)
    if record is None:
        raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="Profile was not found.")
    return _response(record)


def ensure_profile(phone: str, session: Session | None) -> None:
    """Create the verified actor once; subsequent logins never overwrite their data."""
    active_session = _database_session(session)
    try:
        if active_session.get(UserProfile, phone) is not None:
            return
        active_session.add(
            UserProfile(phone=phone, first_name="", last_name="", income="", job="", gender="", avatar_data_url=None)
        )
        active_session.commit()
    except IntegrityError:
        # Another verification may have created the same primary-key record concurrently.
        active_session.rollback()
        if active_session.get(UserProfile, phone) is None:
            raise ApiError(
                status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Profile could not be created."
            ) from None
    except Exception:
        active_session.rollback()
        raise ApiError(
            status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Profile could not be created."
        ) from None


def upsert_profile(payload: ProfilePayload, session: Session | None) -> ProfilePayload:
    active_session = _database_session(session)
    record = active_session.get(UserProfile, payload.phone)
    if record is None:
        record = UserProfile(phone=payload.phone)
        active_session.add(record)
    record.first_name, record.last_name = payload.firstName, payload.lastName
    record.income, record.job, record.gender = payload.income, payload.job, payload.gender
    record.avatar_data_url = payload.avatar
    try:
        active_session.commit()
    except Exception:
        active_session.rollback()
        raise ApiError(
            status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Profile could not be saved."
        ) from None
    active_session.refresh(record)
    return _response(record)
