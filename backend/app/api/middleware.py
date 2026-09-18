"""Small transport middleware that avoids accepting user-provided correlation identifiers."""

from __future__ import annotations

from uuid import uuid4

from fastapi import Request, Response


async def correlation_id_middleware(request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
    """Generate a fresh opaque request identifier and expose it in the response header."""
    request.state.correlation_id = str(uuid4())
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = request.state.correlation_id
    return response
