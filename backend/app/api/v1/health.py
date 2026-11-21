"""Minimal non-product health endpoints; readiness is deliberately token-gated."""

from __future__ import annotations

from secrets import compare_digest

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel

from backend.app.api.errors import ApiError, ErrorCode
from backend.app.core.config import Settings, get_settings

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Intentionally minimal response that exposes no dependency or environment detail."""

    status: str


@router.get("/live", response_model=HealthResponse, include_in_schema=False)
def live() -> HealthResponse:
    """Public liveness: the running process can answer HTTP requests."""
    return HealthResponse(status="ok")


def require_readiness_token(
    settings: Settings = Depends(get_settings),  # noqa: B008 - FastAPI declares dependencies in the signature.
    supplied_token: str | None = Header(default=None, alias="X-Shahab-Readiness-Token"),
) -> None:
    """Keep readiness unavailable unless an environment-provided token matches exactly."""
    configured_token = settings.readiness_token.get_secret_value() if settings.readiness_token else None
    if not configured_token or not supplied_token or not compare_digest(configured_token, supplied_token):
        raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="Resource not found.")


@router.get("/ready", response_model=HealthResponse, include_in_schema=False)
def ready(_: None = Depends(require_readiness_token)) -> HealthResponse:
    """Restricted application readiness; dependency readiness is added with each adapter."""
    return HealthResponse(status="ready")
