"""Profile endpoints authorize the server-owned actor before touching storage."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.accounts import profile_repository
from backend.app.accounts.profile_schema import ProfilePayload
from backend.app.api.errors import ApiError, ErrorCode
from backend.app.core.dependencies import get_request_database_session

from .account_access import authenticated_phone

router = APIRouter(prefix="/profiles", tags=["profiles"])
Actor = Annotated[str, Depends(authenticated_phone)]
Database = Annotated[Session | None, Depends(get_request_database_session)]


@router.get("/me", response_model=ProfilePayload)
def read_own_profile(actor: Actor, session: Database) -> ProfilePayload:
    return profile_repository.read_profile(actor, session)


@router.put("", response_model=ProfilePayload)
def upsert_profile(payload: ProfilePayload, actor: Actor, session: Database) -> ProfilePayload:
    if payload.phone != actor:
        raise ApiError(status_code=403, code=ErrorCode.FORBIDDEN, message="Profile access is not allowed.")
    return profile_repository.upsert_profile(payload, session)
