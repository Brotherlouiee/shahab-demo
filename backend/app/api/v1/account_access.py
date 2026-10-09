"""HTTP adapter for local/test OTP and profile ownership; no public phone lookup authorization."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from backend.app.accounts.access import AccessFailure, AccountAccess
from backend.app.accounts.phone import normalize_phone
from backend.app.accounts.profile_repository import ensure_profile
from backend.app.api.errors import ApiError, ErrorCode
from backend.app.core.dependencies import get_request_database_session

router = APIRouter(prefix="/account-access", tags=["account-access"])


class CodeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    phone: str = Field(max_length=11)

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, value: str) -> str:
        return normalize_phone(value)


class CodeVerification(BaseModel):
    model_config = ConfigDict(extra="forbid")
    challengeId: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=6, max_length=6)


def access_service(request: Request, response: Response) -> AccountAccess:
    response.headers["Cache-Control"] = "no-store"
    return request.app.state.account_access  # type: ignore[no-any-return]


def safe_failure(error: AccessFailure) -> ApiError:
    code = (
        ErrorCode.SERVICE_UNAVAILABLE
        if error.status == 503
        else ErrorCode.INVALID_REQUEST
        if error.status == 429
        else ErrorCode.UNAUTHORIZED
    )
    return ApiError(status_code=error.status, code=code, message="Account access could not be completed.")


def bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer ") or len(authorization) > 128:
        raise safe_failure(AccessFailure(401))
    return authorization[7:]


def authenticated_phone(
    service: Annotated[AccountAccess, Depends(access_service)], token: Annotated[str, Depends(bearer_token)]
) -> str:
    try:
        return service.actor(token)
    except AccessFailure as error:
        raise safe_failure(error) from None


@router.post("/request")
def request_code(
    payload: CodeRequest, request: Request, service: Annotated[AccountAccess, Depends(access_service)]
) -> dict[str, str | int]:
    try:
        # Ignore forwarded headers: callers cannot create arbitrary rate-limit identities.
        challenge_id = service.request_code(payload.phone, request.client.host if request.client else "unknown")
    except AccessFailure as error:
        raise safe_failure(error) from None
    return {"challengeId": challenge_id, "expiresIn": 120}


@router.post("/verify")
def verify_code(
    payload: CodeVerification,
    service: Annotated[AccountAccess, Depends(access_service)],
    session: Annotated[Session | None, Depends(get_request_database_session)],
) -> dict[str, str | int]:
    try:
        token = service.verify_code(payload.challengeId, payload.code)
    except AccessFailure as error:
        raise safe_failure(error) from None
    phone = service.actor(token)
    try:
        ensure_profile(phone, session)
    except Exception:
        service.revoke(token)
        raise
    return {"accessToken": token, "phone": phone, "expiresIn": 1800}


@router.post("/logout", status_code=204)
def logout(
    service: Annotated[AccountAccess, Depends(access_service)], token: Annotated[str, Depends(bearer_token)]
) -> None:
    service.revoke(token)
