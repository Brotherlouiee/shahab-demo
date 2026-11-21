"""Development-only HTTP timing with redacted endpoint labels."""

from __future__ import annotations

from time import perf_counter

from fastapi import Request, Response

from backend.app.core.config import AppEnvironment


def _timed_endpoint(request: Request) -> str | None:
    """Return a fixed label; never log path parameters, request bodies, or URLs."""
    if request.method == "POST" and request.url.path == "/api/v1/questionnaire/sessions":
        return "questionnaire_session_create"
    if request.method == "POST" and request.url.path == "/api/v1/recommendations":
        return "recommendation"
    if request.method != "PUT":
        return None
    segments = request.url.path.split("/")
    if (
        len(segments) == 8
        and segments[:5] == ["", "api", "v1", "questionnaire", "sessions"]
        and segments[6] == "answers"
    ):
        return "questionnaire_answer_write"
    return None


async def development_timing_middleware(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
    """Log only safe local/test endpoint timing; production emits nothing."""
    endpoint = _timed_endpoint(request)
    if endpoint is None or request.app.state.settings.environment is AppEnvironment.PRODUCTION:
        return await call_next(request)

    started_at = perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        request.app.state.logger.info(
            "development_api_timing endpoint=%s status_code=%s duration_ms=%.1f",
            endpoint,
            500,
            (perf_counter() - started_at) * 1000,
        )
        raise
    request.app.state.logger.info(
        "development_api_timing endpoint=%s status_code=%s duration_ms=%.1f",
        endpoint,
        response.status_code,
        (perf_counter() - started_at) * 1000,
    )
    return response
