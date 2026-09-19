"""Framework dependency providers; composition stays outside the loan use cases."""

from __future__ import annotations

import logging
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.api.errors import ApiError, ErrorCode
from backend.app.infrastructure.db.session import create_database_engine, create_session_factory
from backend.app.loans.application.use_cases import GetLoanDetails
from backend.app.loans.infrastructure.sqlalchemy_catalogue import SqlAlchemyServingLoanCatalogueRepository

from .config import Settings, get_settings
from .logging import configure_logging


def get_app_logger(settings: Annotated[Settings, Depends(get_settings)]) -> logging.Logger:
    """Expose the configured, redacting application logger to HTTP adapters."""
    return configure_logging(settings.log_level)


def get_loan_details_use_case(
    settings: Annotated[Settings, Depends(get_settings)],
) -> Generator[GetLoanDetails, None, None]:
    """Compose one request-scoped approved-serving loan-detail use case.

    A missing local database is an expected operational state, not an invitation
    to fall back to prototype data.  The endpoint therefore returns a typed
    unavailable response until an approved catalogue database is configured.
    """
    if not settings.database_url_value:
        raise ApiError(
            status_code=503,
            code=ErrorCode.SERVICE_UNAVAILABLE,
            message="Loan catalogue is temporarily unavailable.",
        )
    engine = create_database_engine(settings)
    session: Session = create_session_factory(engine)()
    try:
        yield GetLoanDetails(SqlAlchemyServingLoanCatalogueRepository(session))
    finally:
        session.close()
        engine.dispose()
