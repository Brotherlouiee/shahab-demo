"""Framework dependency providers; composition stays outside the loan use cases."""

from __future__ import annotations

import json
import logging
from collections.abc import Generator
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.orm import Session, sessionmaker

from backend.app.api.errors import ApiError, ErrorCode
from backend.app.loans.application.use_cases import GetLoanDetails
from backend.app.loans.infrastructure.sqlalchemy_catalogue import SqlAlchemyServingLoanCatalogueRepository
from backend.app.questionnaire.application.use_cases import QuestionnaireSessionService
from backend.app.questionnaire.domain.configuration import QuestionnaireConfiguration, load_questionnaire_configuration
from backend.app.questionnaire.domain.session import QuestionnaireRetentionPolicy
from backend.app.questionnaire.infrastructure.memory_sessions import InMemoryQuestionnaireSessionRepository
from backend.app.questionnaire.infrastructure.sqlalchemy_sessions import SqlAlchemyQuestionnaireSessionRepository

from .config import Settings, get_settings
from .logging import configure_logging


def get_app_logger(settings: Annotated[Settings, Depends(get_settings)]) -> logging.Logger:
    """Expose the configured, redacting application logger to HTTP adapters."""
    return configure_logging(settings.log_level)


@lru_cache
def _questionnaire_configuration() -> QuestionnaireConfiguration:
    root = Path(__file__).resolve().parents[3]
    return load_questionnaire_configuration(
        root / "data/contracts/questionnaire-configuration.v1.json",
        json.loads((root / "data/contracts/canonical-identifiers.v1.json").read_text(encoding="utf-8")),
    )


def get_questionnaire_configuration() -> QuestionnaireConfiguration:
    """Expose the cached canonical questionnaire configuration to app lifecycle wiring."""
    return _questionnaire_configuration()


_questionnaire_repository = InMemoryQuestionnaireSessionRepository()


def get_local_questionnaire_repository() -> InMemoryQuestionnaireSessionRepository:
    """Local/test authority for session creation proof; Redis never grants access."""
    return _questionnaire_repository


def get_request_database_session(request: Request) -> Generator[Session | None, None, None]:
    """Create and close one request-local session from the app-lifecycle factory."""
    session_factory: sessionmaker[Session] | None = request.app.state.database_session_factory
    if session_factory is None:
        yield None
        return
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


def get_questionnaire_session_service(
    request: Request,
    session: Annotated[Session | None, Depends(get_request_database_session)],
) -> Generator[QuestionnaireSessionService, None, None]:
    """Use PostgreSQL when configured; Redis is a best-effort cache, never the authority."""
    configuration = get_questionnaire_configuration()
    cache = request.app.state.questionnaire_session_cache
    if session is None:
        yield QuestionnaireSessionService(
            _questionnaire_repository, configuration, QuestionnaireRetentionPolicy(timedelta(minutes=30)), cache
        )
        return
    repository = SqlAlchemyQuestionnaireSessionRepository(
        session,
        configuration,
        reference_catalogue=request.app.state.questionnaire_reference_catalogue,
    )
    yield QuestionnaireSessionService(
        repository, configuration, QuestionnaireRetentionPolicy(timedelta(minutes=30)), cache
    )


def get_loan_details_use_case(
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[Session | None, Depends(get_request_database_session)],
) -> Generator[GetLoanDetails, None, None]:
    """Compose one request-scoped approved-serving loan-detail use case.

    A missing local database is an expected operational state, not an invitation
    to fall back to prototype data.  The endpoint therefore returns a typed
    unavailable response until an approved catalogue database is configured.
    """
    if session is None:
        raise ApiError(
            status_code=503,
            code=ErrorCode.SERVICE_UNAVAILABLE,
            message="Loan catalogue is temporarily unavailable.",
        )
    yield GetLoanDetails(SqlAlchemyServingLoanCatalogueRepository(session))
