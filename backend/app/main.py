"""FastAPI composition root; transport routes are intentionally added in US-03.T04."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis import Redis
from starlette.exceptions import HTTPException as StarletteHTTPException

from .accounts.access import AccountAccess, MockOtpProvider
from .api.errors import ApiError, ErrorCode, api_error_handler, error_payload
from .api.middleware import correlation_id_middleware
from .api.timing import development_timing_middleware
from .api.v1.router import router as api_v1_router
from .core.config import AppEnvironment, Settings, get_settings
from .core.dependencies import get_questionnaire_configuration
from .core.logging import configure_logging
from .infrastructure.db.session import create_database_engine, create_session_factory
from .questionnaire.infrastructure.redis_cache import RedisQuestionnaireSessionCache
from .questionnaire.infrastructure.sqlalchemy_sessions import SqlAlchemyQuestionnaireSessionRepository


@asynccontextmanager
async def database_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Own the process-wide engine while request dependencies own sessions."""
    engine = None
    cache = None
    if app.state.settings.database_url_value:
        engine = create_database_engine(app.state.settings)
        app.state.database_engine = engine
        app.state.database_session_factory = create_session_factory(engine)
        bootstrap_session = app.state.database_session_factory()
        try:
            repository = SqlAlchemyQuestionnaireSessionRepository(
                bootstrap_session,
                get_questionnaire_configuration(),
            )
            app.state.questionnaire_reference_catalogue = repository.reference_catalogue
        finally:
            bootstrap_session.close()
    else:
        app.state.database_engine = None
        app.state.database_session_factory = None
        app.state.questionnaire_reference_catalogue = None
    if app.state.settings.redis_url_value:
        cache = RedisQuestionnaireSessionCache(
            Redis.from_url(app.state.settings.redis_url_value, decode_responses=True)
        )
    app.state.questionnaire_session_cache = cache
    try:
        yield
    finally:
        if cache is not None:
            cache.close()
        if engine is not None:
            engine.dispose()


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
        lifespan=database_lifespan,
    )
    app.middleware("http")(correlation_id_middleware)
    app.middleware("http")(development_timing_middleware)
    app.add_exception_handler(ApiError, api_error_handler)

    @app.exception_handler(StarletteHTTPException)
    async def http_error_handler(request: Request, error: StarletteHTTPException) -> JSONResponse:
        code = (
            ErrorCode.NOT_FOUND
            if error.status_code == 404
            else ErrorCode.FORBIDDEN
            if error.status_code == 403
            else ErrorCode.INVALID_REQUEST
        )
        message = "Resource not found." if error.status_code == 404 else "Request could not be completed."
        return JSONResponse(status_code=error.status_code, content=error_payload(request, code=code, message=message))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, _: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_payload(request, code=ErrorCode.INVALID_REQUEST, message="Request validation failed."),
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, _: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=error_payload(request, code=ErrorCode.INTERNAL_ERROR, message="An unexpected error occurred."),
        )

    app.include_router(api_v1_router, prefix=active_settings.api_v1_prefix)
    app.dependency_overrides[get_settings] = lambda: active_settings
    app.state.settings = active_settings
    # Even an accidentally enabled flag cannot turn demo OTP into production authentication.
    mock_allowed = active_settings.profile_mock_otp_enabled and active_settings.environment in (
        AppEnvironment.LOCAL,
        AppEnvironment.TEST,
    )
    app.state.account_access = AccountAccess(MockOtpProvider() if mock_allowed else None)
    app.state.logger = logger
    app.state.database_engine = None
    app.state.database_session_factory = None
    app.state.questionnaire_reference_catalogue = None
    app.state.questionnaire_session_cache = None
    return app


app = create_app()
