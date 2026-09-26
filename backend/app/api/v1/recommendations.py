"""Session-only recommendation endpoint; all scores originate in approved PostgreSQL."""

from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.app.api.errors import ApiError, ErrorCode
from backend.app.core.config import Settings, get_settings
from backend.app.core.dependencies import _questionnaire_configuration
from backend.app.infrastructure.db.session import create_database_engine, create_session_factory
from backend.app.loans.domain.models import ServingCatalogueUnavailableError
from backend.app.loans.infrastructure.sqlalchemy_catalogue import SqlAlchemyServingLoanCatalogueRepository
from backend.app.questionnaire.application.use_cases import QuestionnaireSessionService
from backend.app.questionnaire.domain.session import QuestionnaireRetentionPolicy, QuestionnaireSessionExpiredError
from backend.app.questionnaire.infrastructure.sqlalchemy_sessions import SqlAlchemyQuestionnaireSessionRepository
from backend.app.recommendation.application.use_cases import RecommendCanonicalLoans
from backend.app.recommendation.domain.entities import RecommendationInputError
from backend.app.recommendation.infrastructure.sqlalchemy_impacts import SqlAlchemyCanonicalImpactRepository
from backend.app.recommendation.infrastructure.sqlalchemy_snapshot import (
    SnapshotIntegrityError,
    SnapshotUnavailableError,
    SqlAlchemyRecommendationSnapshotRepository,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: str = Field(alias="sessionId", min_length=1)


class RankedRecommendationResponse(BaseModel):
    loan_id: str = Field(alias="loanId")
    lender_name: str = Field(alias="lenderName")
    loan_name: str = Field(alias="loanName")
    compatibility_score: float = Field(alias="compatibilityScore", ge=0, le=1)
    compatibility_reason: str = Field(alias="compatibilityReason")


class NeedsReviewResponse(BaseModel):
    loan_id: str = Field(alias="loanId")
    lender_name: str = Field(alias="lenderName")
    loan_name: str = Field(alias="loanName")
    ranking_excluded_reasons: tuple[str, ...] = Field(alias="rankingExcludedReasons")


class RecommendationResponse(BaseModel):
    data_version: str = Field(alias="dataVersion")
    config_version: str = Field(alias="configVersion")
    ranked_recommendations: tuple[RankedRecommendationResponse, ...] = Field(alias="rankedRecommendations")
    needs_review: tuple[NeedsReviewResponse, ...] = Field(alias="needsReview")


@router.post("", response_model=RecommendationResponse, response_model_by_alias=True)
def recommend(
    payload: Annotated[RecommendationRequest, Body()],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RecommendationResponse:
    if not settings.database_url_value:
        raise ApiError(
            status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Recommendation catalogue is unavailable."
        )
    engine = create_database_engine(settings)
    try:
        with create_session_factory(engine)() as db:
            return _recommend_from_session(db, payload.session_id)
    finally:
        engine.dispose()


def _recommend_from_session(db: Session, session_id: str) -> RecommendationResponse:
    configuration = _questionnaire_configuration()
    service = QuestionnaireSessionService(
        SqlAlchemyQuestionnaireSessionRepository(db, configuration),
        configuration,
        QuestionnaireRetentionPolicy(timedelta(minutes=30)),
    )
    try:
        session = service.get(session_id)
        answers = {answer.question_id: answer.answer_id for answer in service.answers(session_id)}
    except LookupError as error:
        raise ApiError(
            status_code=404, code=ErrorCode.NOT_FOUND, message="Questionnaire session was not found."
        ) from error
    except QuestionnaireSessionExpiredError as error:
        raise ApiError(
            status_code=410, code=ErrorCode.NOT_FOUND, message="Questionnaire session has expired."
        ) from error
    if session.questionnaire_version != configuration.questionnaire_version or set(answers) != {
        question.question_id for question in configuration.questions if question.required
    }:
        raise ApiError(status_code=422, code=ErrorCode.INVALID_REQUEST, message="Questionnaire is incomplete.")
    try:
        snapshot_repository = SqlAlchemyRecommendationSnapshotRepository(db)
        snapshot = snapshot_repository.read_approved_snapshot()
        impacts = SqlAlchemyCanonicalImpactRepository(db).read_approved_impacts(answers, snapshot.config_version)
        _, partition = RecommendCanonicalLoans(snapshot_repository).execute(impacts)
        records = SqlAlchemyServingLoanCatalogueRepository(db).list_current_serving_loans()
        catalogue = {record.summary.loan_id: record.summary for record in records}
        if set(catalogue) != {candidate.loan_id for candidate in snapshot.candidates}:
            raise SnapshotIntegrityError("serving details and recommendation snapshot disagree")
        ranked = tuple(
            RankedRecommendationResponse(
                loanId=item.loan_id,
                lenderName=catalogue[item.loan_id].lender_name,
                loanName=catalogue[item.loan_id].loan_name,
                compatibilityScore=float(item.score),
                compatibilityReason="سازگاری دسته‌بندی شرایط وام با پاسخ‌های ثبت‌شدهٔ شما",
            )
            for item in partition.ranked
        )
        needs_review = tuple(
            NeedsReviewResponse(
                loanId=item.loan_id,
                lenderName=catalogue[item.loan_id].lender_name,
                loanName=catalogue[item.loan_id].loan_name,
                rankingExcludedReasons=item.excluded_reasons,
            )
            for item in partition.needs_review
        )
        return RecommendationResponse(
            dataVersion=snapshot.data_version,
            configVersion=snapshot.config_version,
            rankedRecommendations=ranked,
            needsReview=needs_review,
        )
    except (
        SnapshotUnavailableError,
        SnapshotIntegrityError,
        ServingCatalogueUnavailableError,
        RecommendationInputError,
    ) as error:
        raise ApiError(
            status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Recommendation catalogue is unavailable."
        ) from error
