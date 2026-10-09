"""Typed, safe HTTP error contracts shared by versioned API routers."""

from __future__ import annotations

from enum import StrEnum

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ErrorCode(StrEnum):
    """Stable public error codes; messages remain safe, localized at the UI boundary later."""

    INVALID_REQUEST = "invalid_request"
    NOT_FOUND = "not_found"
    FORBIDDEN = "forbidden"
    UNAUTHORIZED = "unauthorized"
    SERVICE_UNAVAILABLE = "service_unavailable"
    INTERNAL_ERROR = "internal_error"


class ErrorDetail(BaseModel):
    """A safe error envelope with an opaque ID for support and log correlation."""

    code: ErrorCode
    message: str
    correlation_id: str = Field(alias="correlationId")
    model_config = {"populate_by_name": True}


class ErrorResponse(BaseModel):
    """Every application-generated error response uses this public shape."""

    error: ErrorDetail


class ApiError(Exception):
    """Expected, typed application/transport error without implementation details."""

    def __init__(self, *, status_code: int, code: ErrorCode, message: str) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


def correlation_id_for(request: Request) -> str:
    """Read the middleware-generated opaque correlation ID for an error response."""
    return str(getattr(request.state, "correlation_id", "unavailable"))


def error_payload(request: Request, *, code: ErrorCode, message: str) -> dict[str, object]:
    """Build the stable public error payload without including request input or tracebacks."""
    return ErrorResponse(
        error=ErrorDetail(code=code, message=message, correlationId=correlation_id_for(request))
    ).model_dump(by_alias=True)


async def api_error_handler(request: Request, error: Exception) -> JSONResponse:
    """Render known errors through the public schema."""
    if not isinstance(error, ApiError):
        raise TypeError("api_error_handler only supports ApiError instances")
    return JSONResponse(
        status_code=error.status_code,
        content=error_payload(request, code=error.code, message=error.message),
        headers={"Cache-Control": "no-store"},
    )
