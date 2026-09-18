"""FastAPI composition root; transport routes are intentionally added in US-03.T04."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api.errors import ApiError, ErrorCode, api_error_handler, error_payload
from .api.middleware import correlation_id_middleware
from .api.v1.router import router as api_v1_router
from .core.config import Settings, get_settings
from .core.logging import configure_logging


def create_app(settings: Settings | None = None) -> FastAPI:
    """Compose the API without importing domain, ORM, or feature implementation code."""
    active_settings = settings or get_settings()
    logger = configure_logging(active_settings.log_level)
    app = FastAPI(
        title=active_settings.app_name,
        debug=active_settings.debug,
        docs_url="/docs" if active_settings.docs_enabled else None,
        redoc_url="/redoc" if active_settings.docs_enabled else None,
        openapi_url=f"{active_settings.api_v1_prefix}/openapi.json" if active_settings.docs_enabled else None,
    )
    app.middleware("http")(correlation_id_middleware)
    app.add_exception_handler(ApiError, api_error_handler)

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, error: StarletteHTTPException) -> JSONResponse:
        code = ErrorCode.NOT_FOUND if error.status_code == 404 else ErrorCode.FORBIDDEN if error.status_code == 403 else ErrorCode.INVALID_REQUEST
        message = "Resource not found." if error.status_code == 404 else "Request could not be completed."
        return JSONResponse(status_code=error.status_code, content=error_payload(request, code=code, message=message))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, _: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content=error_payload(request, code=ErrorCode.INVALID_REQUEST, message="Request validation failed."))

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, _: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content=error_payload(request, code=ErrorCode.INTERNAL_ERROR, message="An unexpected error occurred."))
    app.include_router(api_v1_router, prefix=active_settings.api_v1_prefix)
    app.dependency_overrides[get_settings] = lambda: active_settings
    app.state.settings = active_settings
    app.state.logger = logger
    return app


app = create_app()
