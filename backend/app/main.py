"""FastAPI composition root; transport routes are intentionally added in US-03.T04."""

from __future__ import annotations

from fastapi import FastAPI

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
    app.state.settings = active_settings
    app.state.logger = logger
    return app


app = create_app()
