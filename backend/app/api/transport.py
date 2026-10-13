"""Bounded API transport checks; no change to authentication or ownership rules."""

from __future__ import annotations

from urllib.parse import urlsplit

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from backend.app.api.errors import ErrorCode, error_payload

MAX_API_BODY_BYTES = 1024 * 1024
UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def _origin_tuple(value: str) -> tuple[str, str, int] | None:
    try:
        parsed = urlsplit(value)
        if (
            parsed.scheme not in {"http", "https"}
            or not parsed.hostname
            or parsed.username is not None
            or parsed.password is not None
            or parsed.path not in {"", "/"}
            or parsed.query
            or parsed.fragment
        ):
            return None
        return parsed.scheme, parsed.hostname.lower(), parsed.port or (443 if parsed.scheme == "https" else 80)
    except ValueError:
        return None


def _same_origin(request: Request, origin: str) -> bool:
    return _origin_tuple(origin) == _origin_tuple(str(request.base_url).rstrip("/"))


async def transport_hardening_middleware(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
    """Protect API cookie writes and enforce bounded JSON/request response transport.

    Origin/Fetch-Metadata are browser protections; existing opaque bearer tokens
    still require server-owned account/proof authorization. Reverse proxies must
    set trusted scheme/host and enforce ingress/body and upstream timeouts.
    """
    api_request = request.url.path.startswith("/api/v1/")
    settings = request.app.state.settings

    def reject(status: int, code: ErrorCode, message: str) -> Response:
        return JSONResponse(status_code=status, content=error_payload(request, code=code, message=message))

    response: Response
    if api_request and request.method in UNSAFE_METHODS:
        origin = request.headers.get("origin")
        site = request.headers.get("sec-fetch-site")
        allowed = {_origin_tuple(value) for value in settings.cors_allowed_origins}
        bearer = request.headers.get("authorization", "").startswith("Bearer ")
        # CORS permission alone is not CSRF consent: a cookie-authenticated
        # mutation requires the same origin; an explicit bearer may use a
        # separately approved origin.
        origin_ok = origin is None or _same_origin(request, origin) or (
            bearer and _origin_tuple(origin) in allowed
        )
        if (not origin_ok) or (site == "cross-site" and origin is None and not bearer):
            response = reject(403, ErrorCode.FORBIDDEN, "Request origin is not allowed.")
        else:
            length = request.headers.get("content-length")
            try:
                declared = int(length) if length is not None else 0
            except ValueError:
                declared = -1
            if declared < 0:
                response = reject(400, ErrorCode.INVALID_REQUEST, "Invalid request length.")
            elif declared > MAX_API_BODY_BYTES:
                response = reject(413, ErrorCode.INVALID_REQUEST, "Request body is too large.")
            elif len(await request.body()) > MAX_API_BODY_BYTES:
                response = reject(413, ErrorCode.INVALID_REQUEST, "Request body is too large.")
            else:
                response = await call_next(request)
    else:
        response = await call_next(request)

    if api_request:
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    if request.url.scheme == "https":
        response.headers["Strict-Transport-Security"] = "max-age=31536000"
    return response
