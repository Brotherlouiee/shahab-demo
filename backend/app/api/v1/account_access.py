"""HTTP adapter for OTP and profile ownership; no public phone lookup authorization."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request, Response
from pydantic import BaseModel, ConfigDict, Field, field_validator
from sqlalchemy.orm import Session

from backend.app.accounts.access import AccessFailure, AccountAccess
from backend.app.accounts.identity import AccountActor, require_active_account
from backend.app.accounts.phone import normalize_phone
from backend.app.accounts.profile_repository import ensure_profile
from backend.app.accounts.sqlalchemy_access import SqlAlchemyAccountAccess
from backend.app.api.errors import ApiError, ErrorCode
from backend.app.core.config import AppEnvironment
from backend.app.core.dependencies import get_request_database_session

router = APIRouter(prefix="/account-access", tags=["account-access"])
ACCESS_COOKIE = "shahab_account_access"


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


def access_service(
    request: Request, response: Response, session: Annotated[Session | None, Depends(get_request_database_session)]
) -> AccountAccess:
    response.headers["Cache-Control"] = "no-store"
    if isinstance(session, Session):
        return SqlAlchemyAccountAccess(request.app.state.account_access.provider, session)
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


def bearer_token(request: Request, authorization: Annotated[str | None, Header()] = None) -> str:
    token = (
        authorization.removeprefix("Bearer ")
        if authorization and authorization.startswith("Bearer ")
        else request.cookies.get(ACCESS_COOKIE)
    )
    if not token or len(token) > 128:
        raise safe_failure(AccessFailure(401))
    return token


def authenticated_account(
    service: Annotated[AccountAccess, Depends(access_service)],
    token: Annotated[str, Depends(bearer_token)],
    session: Annotated[Session | None, Depends(get_request_database_session)],
) -> AccountActor:
    try:
        return require_active_account(service.actor(token), session)
    except AccessFailure as error:
        raise safe_failure(error) from None


def optional_authenticated_account(
    service: Annotated[AccountAccess, Depends(access_service)],
    request: Request,
    session: Annotated[Session | None, Depends(get_request_database_session)],
    authorization: Annotated[str | None, Header()] = None,
) -> AccountActor | None:
    """Permit anonymous recommendation while never trusting a malformed token."""
    if authorization is None and not request.cookies.get(ACCESS_COOKIE):
        return None
    token = bearer_token(request, authorization)
    try:
        return require_active_account(service.actor(token), session)
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
    response: Response,
    request: Request,
) -> dict[str, str | int]:
    try:
        token = service.verify_code(payload.challengeId, payload.code)
    except AccessFailure as error:
        raise safe_failure(error) from None
    phone = service.verified_phone(token)
    try:
        actor = ensure_profile(phone, session)
        service.bind_account(token, actor.account_id)
    except AccessFailure as error:
        try:
            service.revoke(token)
        except AccessFailure as revoke_error:
            raise safe_failure(revoke_error) from None
        raise safe_failure(error) from None
    except Exception:
        try:
            service.revoke(token)
        except AccessFailure as error:
            raise safe_failure(error) from None
        raise
    response.set_cookie(
        ACCESS_COOKIE,
        token,
        max_age=3600,
        httponly=True,
        samesite="lax",
        secure=request.url.scheme == "https"
        or request.app.state.settings.environment in {AppEnvironment.STAGING, AppEnvironment.PRODUCTION},
        path="/api/v1",
    )
    return {"accessToken": token, "phone": phone, "accountId": str(actor.account_id), "expiresIn": 3600}


@router.get("/session")
def current_session(
    actor: Annotated[AccountActor, Depends(authenticated_account)],
    service: Annotated[AccountAccess, Depends(access_service)],
    token: Annotated[str, Depends(bearer_token)],
) -> dict[str, str | int]:
    try:
        remaining = service.remaining(token)
    except AccessFailure as error:
        raise safe_failure(error) from None
    return {"phone": actor.phone, "accountId": str(actor.account_id), "expiresIn": remaining}


@router.post("/logout", status_code=204)
def logout(
    service: Annotated[AccountAccess, Depends(access_service)],
    token: Annotated[str, Depends(bearer_token)],
    response: Response,
    request: Request,
) -> None:
    try:
        service.revoke(token)
    except AccessFailure as error:
        raise safe_failure(error) from None
    response.delete_cookie(ACCESS_COOKIE, path="/api/v1")
    # The browser cannot clear HttpOnly creator secrets itself. Logout removes
    # only Shahab questionnaire cookies; raw DB retention remains independent.
    for cookie in request.cookies:
        if cookie.startswith("shahab_questionnaire_proof_"):
            response.delete_cookie(cookie, path="/api/v1")

