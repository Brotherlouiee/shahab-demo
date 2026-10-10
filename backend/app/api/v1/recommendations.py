"""Session-only recommendation endpoint; all scores originate in approved PostgreSQL."""

from __future__ import annotations

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from backend.app.api.errors import ApiError, ErrorCode
from backend.app.api.v1.account_access import optional_authenticated_phone
from backend.app.core.config import Settings, get_settings
from backend.app.core.dependencies import _questionnaire_configuration, get_request_database_session
from backend.app.loans.domain.models import ServingCatalogueUnavailableError
from backend.app.loans.infrastructure.sqlalchemy_catalogue import SqlAlchemyServingLoanCatalogueRepository
from backend.app.questionnaire.application.use_cases import QuestionnaireSessionService
from backend.app.questionnaire.domain.session import QuestionnaireRetentionPolicy, QuestionnaireSessionExpiredError
from backend.app.questionnaire.infrastructure.sqlalchemy_sessions import SqlAlchemyQuestionnaireSessionRepository
from backend.app.recommendation.application.use_cases import RecommendCanonicalLoans
from backend.app.recommendation.domain.entities import RecommendationInputError
from backend.app.recommendation.infrastructure.history import RecommendationHistoryRepository
from backend.app.recommendation.infrastructure.sqlalchemy_impacts import SqlAlchemyCanonicalImpactRepository
from backend.app.recommendation.infrastructure.sqlalchemy_snapshot import (
    SnapshotIntegrityError,
    SnapshotUnavailableError,
    SqlAlchemyRecommendationSnapshotRepository,
)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

_VARIABLE_LABELS = {
    "maxAmount": "حداکثر مبلغ وام",
    "monthlyInstallment": "مبلغ قسط ماهانه",
    "maxRepaymentMonths": "مدت بازپرداخت",
    "interestRate": "نرخ بهره",
}
_STATE_LABELS = {
    "unknown": "در دادهٔ منتشرشده اعلام نشده است",
    "variable": "در دادهٔ منتشرشده متغیر است",
    "neutral": "برای رتبه‌بندی مقدار خنثی دارد",
}


class RecommendationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: str = Field(alias="sessionId", min_length=1)


class LoanResultSummaryResponse(BaseModel):
    """Safe card facts from the same PUBLISHED serving record."""

    max_amount_tomans: float | None = Field(alias="maxAmountTomans")
    monthly_installment_tomans: float | None = Field(alias="monthlyInstallmentTomans")
    max_repayment_months: int | None = Field(alias="maxRepaymentMonths")
    interest_rate_percent: float | None = Field(alias="interestRatePercent")


class RankedRecommendationResponse(BaseModel):
    loan_id: str = Field(alias="loanId")
    lender_name: str = Field(alias="lenderName")
    loan_name: str = Field(alias="loanName")
    bank_logo_reference: str | None = Field(default=None, alias="bankLogoReference")
    compatibility_score: float = Field(alias="compatibilityScore", ge=0, le=1)
    compatibility_reason: str = Field(alias="compatibilityReason")
    loan_summary: LoanResultSummaryResponse = Field(alias="loanSummary")


class NeedsReviewResponse(BaseModel):
    loan_id: str = Field(alias="loanId")
    lender_name: str = Field(alias="lenderName")
    loan_name: str = Field(alias="loanName")
    bank_logo_reference: str | None = Field(default=None, alias="bankLogoReference")
    ranking_excluded_reasons: tuple[str, ...] = Field(alias="rankingExcludedReasons")
    loan_summary: LoanResultSummaryResponse = Field(alias="loanSummary")


class RecommendationResponse(BaseModel):
    data_version: str = Field(alias="dataVersion")
    config_version: str = Field(alias="configVersion")
    ranked_recommendations: tuple[RankedRecommendationResponse, ...] = Field(alias="rankedRecommendations")
    low_compatibility_recommendations: tuple[RankedRecommendationResponse, ...] = Field(
        alias="lowCompatibilityRecommendations"
    )
    needs_review: tuple[NeedsReviewResponse, ...] = Field(alias="needsReview")


@router.post("", response_model=RecommendationResponse, response_model_by_alias=True)
def recommend(
    payload: Annotated[RecommendationRequest, Body()],
    settings: Annotated[Settings, Depends(get_settings)],
    db: Annotated[Session | None, Depends(get_request_database_session)],
    actor: Annotated[str | None, Depends(optional_authenticated_phone)],
) -> RecommendationResponse:
    if db is None:
        raise ApiError(
            status_code=503, code=ErrorCode.SERVICE_UNAVAILABLE, message="Recommendation catalogue is unavailable."
        )
    result = _recommend_from_session(db, payload.session_id)
    if actor is not None:
        try:
            RecommendationHistoryRepository(db).save(actor, payload.session_id, result)
            db.commit()
        except PermissionError as error:
            db.rollback()
            raise ApiError(
                status_code=403, code=ErrorCode.FORBIDDEN, message="Recommendation history access is not allowed."
            ) from error
        except Exception:
            db.rollback()
            raise
    return result


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
    # The questionnaire reads may start a READ COMMITTED transaction. Finish it
    # before the published catalogue/weights/details are read at one PostgreSQL
    # repeatable-read snapshot, so a concurrent publication cannot mix versions.
    db.commit()
    if db.bind is not None and db.bind.dialect.name == "postgresql":
        db.connection(execution_options={"isolation_level": "REPEATABLE READ"})
    try:
        snapshot_repository = SqlAlchemyRecommendationSnapshotRepository(db)
        snapshot = snapshot_repository.read_approved_snapshot()
        impacts = SqlAlchemyCanonicalImpactRepository(db).read_approved_impacts(answers, snapshot.config_version)
        partition = RecommendCanonicalLoans.execute_for_snapshot(snapshot, impacts)
        records = SqlAlchemyServingLoanCatalogueRepository(db).list_current_serving_loans()
        catalogue = {record.summary.loan_id: record for record in records}
        if set(catalogue) != {candidate.loan_id for candidate in snapshot.candidates}:
            raise SnapshotIntegrityError("serving details and recommendation snapshot disagree")
        ranked = tuple(
            RankedRecommendationResponse(
                loanId=item.loan_id,
                lenderName=catalogue[item.loan_id].summary.lender_name,
                loanName=catalogue[item.loan_id].summary.loan_name,
                bankLogoReference=catalogue[item.loan_id].summary.bank_logo_reference,
                compatibilityScore=float(item.score),
                compatibilityReason="سازگاری دسته‌بندی شرایط وام با پاسخ‌های ثبت‌شدهٔ شما",
                loanSummary=_loan_result_summary(catalogue[item.loan_id].detail),
            )
            for item in partition.ranked
        )
        low_compatibility = tuple(
            RankedRecommendationResponse(
                loanId=item.loan_id,
                lenderName=catalogue[item.loan_id].summary.lender_name,
                loanName=catalogue[item.loan_id].summary.loan_name,
                bankLogoReference=catalogue[item.loan_id].summary.bank_logo_reference,
                compatibilityScore=float(item.score),
                compatibilityReason="تطابق پایین؛ پیشنهاد اصلی نیست",
                loanSummary=_loan_result_summary(catalogue[item.loan_id].detail),
            )
            for item in partition.below_threshold
        )
        needs_review = tuple(
            NeedsReviewResponse(
                loanId=item.loan_id,
                lenderName=catalogue[item.loan_id].summary.lender_name,
                loanName=catalogue[item.loan_id].summary.loan_name,
                bankLogoReference=catalogue[item.loan_id].summary.bank_logo_reference,
                rankingExcludedReasons=tuple(_public_review_reason(reason) for reason in item.excluded_reasons),
                loanSummary=_loan_result_summary(catalogue[item.loan_id].detail),
            )
            for item in partition.needs_review
        )
        return RecommendationResponse(
            dataVersion=snapshot.data_version,
            configVersion=snapshot.config_version,
            rankedRecommendations=ranked,
            lowCompatibilityRecommendations=low_compatibility,
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


def _loan_result_summary(detail) -> LoanResultSummaryResponse:
    """Expose only the four already-public card facts; conditions stay on details."""

    return LoanResultSummaryResponse(
        maxAmountTomans=detail.max_amount_tomans,
        monthlyInstallmentTomans=detail.monthly_installment_tomans,
        maxRepaymentMonths=detail.max_repayment_months,
        interestRatePercent=detail.interest_rate_percent,
    )


def _public_review_reason(reason: str) -> str:
    variable_id, separator, state = reason.partition(":")
    if not separator:
        return "اطلاعات لازم برای رتبه‌بندی در دادهٔ منتشرشده کامل نیست"
    variable = _VARIABLE_LABELS.get(variable_id, "یکی از شرایط اصلی وام")
    state_text = _STATE_LABELS.get(state, "برای رتبه‌بندی قطعی نیست")
    return f"{variable} {state_text}"
