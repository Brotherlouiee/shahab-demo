"""Framework dependency providers; composition stays outside the loan use cases."""

from __future__ import annotations

import json
import logging
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.app.api.errors import ApiError, ErrorCode
from backend.app.infrastructure.db.session import create_database_engine, create_session_factory
from backend.app.loans.application.use_cases import GetLoanDetails
from backend.app.questionnaire.application.use_cases import QuestionnaireSessionService
from backend.app.questionnaire.domain.configuration import load_questionnaire_configuration
from backend.app.questionnaire.domain.session import QuestionnaireRetentionPolicy
from backend.app.questionnaire.infrastructure.memory_sessions import InMemoryQuestionnaireSessionRepository
from backend.app.loans.infrastructure.sqlalchemy_catalogue import SqlAlchemyServingLoanCatalogueRepository

from .config import Settings, get_settings
from .logging import configure_logging


def get_app_logger(settings: Annotated[Settings, Depends(get_settings)]) -> logging.Logger:
    """Expose the configured, redacting application logger to HTTP adapters."""
    return configure_logging(settings.log_level)


@lru_cache
def _questionnaire_configuration() -> object:
    root = Path(__file__).resolve().parents[3]
    return load_questionnaire_configuration(
        root / "data/contracts/questionnaire-configuration.v1.json",
        json.loads((root / "data/contracts/canonical-identifiers.v1.json").read_text(encoding="utf-8")),
    )

_questionnaire_repository = InMemoryQuestionnaireSessionRepository()


def get_questionnaire_session_service() -> QuestionnaireSessionService:
    """Compose temporary anonymous server-side sessions; answers are never URL data."""
    return QuestionnaireSessionService(
        _questionnaire_repository,
        _questionnaire_configuration(),
        QuestionnaireRetentionPolicy(timedelta(minutes=30)),
    )


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
