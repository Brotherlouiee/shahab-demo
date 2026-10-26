"""HTTP boundary for temporary anonymous questionnaire progress."""

from __future__ import annotations

import secrets
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Request, Response
from sqlalchemy.orm import Session

from backend.app.accounts.identity import AccountActor
from backend.app.api.errors import ApiError, ErrorCode
from backend.app.api.v1.account_access import optional_authenticated_account
from backend.app.core.config import AppEnvironment
from backend.app.core.dependencies import (
    get_local_questionnaire_repository,
    get_questionnaire_session_service,
    get_request_database_session,
)
from backend.app.questionnaire.application.use_cases import QuestionnaireSessionService
from backend.app.questionnaire.domain.configuration import QuestionnaireConfiguration
from backend.app.questionnaire.domain.session import (
    CanonicalAnswerValidationError,
    QuestionnaireAnswer,
    QuestionnaireSessionExpiredError,
)
from backend.app.questionnaire.infrastructure.proof import (
    PROOF_COOKIE_PREFIX,
    proof_digest,
    require_questionnaire_access,
)

from .questionnaire_schemas import (
    AnswerWriteRequest,
    QuestionnaireAnswerOptionResponse,
    QuestionnaireConfigurationResponse,
    QuestionnaireQuestionResponse,
    SessionResponse,
)

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])
QUESTIONNAIRE_PROOF_COOKIE_PREFIX = PROOF_COOKIE_PREFIX


def authorize_questionnaire(
    session_id: str,
    request: Request,
    db: Annotated[Session | None, Depends(get_request_database_session)],
    actor: Annotated[AccountActor | None, Depends(optional_authenticated_account)],
) -> None:
    try:
        cookie_id = str(UUID(session_id))
    except ValueError:
        cookie_id = session_id
    require_questionnaire_access(
        session_id,
        request.cookies.get(PROOF_COOKIE_PREFIX + cookie_id),
        actor,
        db,
        get_local_questionnaire_repository(),
    )


def _session_response(service: QuestionnaireSessionService, session_id: str) -> SessionResponse:
    session = service.get(session_id)
    return SessionResponse(
        sessionId=str(session.session_id),
        expiresAt=session.expires_at.isoformat(),
        answers={answer.question_id: answer.answer_id for answer in service.answers(session_id)},
    )


@router.post("/sessions", response_model=SessionResponse, status_code=201)
def start_session(
    service: Annotated[QuestionnaireSessionService, Depends(get_questionnaire_session_service)],
    response: Response,
    request: Request,
) -> SessionResponse:
    response.headers["Cache-Control"] = "no-store"
    secret = secrets.token_urlsafe(32)
    session = service.start(proof_digest=proof_digest(secret))
    # The opaque session id is not sufficient to attach it to an account.  The
    # browser that created it alone receives this HttpOnly proof cookie.
    response.set_cookie(
        f"{QUESTIONNAIRE_PROOF_COOKIE_PREFIX}{session.session_id}",
        secret,
        max_age=60 * 60,
        secure=request.url.scheme == "https"
        or request.app.state.settings.environment in {AppEnvironment.STAGING, AppEnvironment.PRODUCTION},
        httponly=True,
        samesite="lax",
        path="/api/v1",
    )
    return _session_response(service, str(session.session_id))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def resume_session(
    session_id: str,
    authorization: Annotated[None, Depends(authorize_questionnaire)],
    service: Annotated[QuestionnaireSessionService, Depends(get_questionnaire_session_service)],
    response: Response,
) -> SessionResponse:
    response.headers["Cache-Control"] = "no-store"
    try:
        return _session_response(service, session_id)
    except LookupError as error:
        raise ApiError(
            status_code=404, code=ErrorCode.NOT_FOUND, message="Questionnaire session was not found."
        ) from error
    except QuestionnaireSessionExpiredError as error:
        raise ApiError(
            status_code=410, code=ErrorCode.NOT_FOUND, message="Questionnaire session has expired."
        ) from error


@router.put("/sessions/{session_id}/answers/{question_id}", response_model=SessionResponse)
def write_answer(
    session_id: str,
    question_id: str,
    authorization: Annotated[None, Depends(authorize_questionnaire)],
    request: Request,
    db: Annotated[Session | None, Depends(get_request_database_session)],
    actor: Annotated[AccountActor | None, Depends(optional_authenticated_account)],
    payload: Annotated[AnswerWriteRequest, Body()],
    service: Annotated[QuestionnaireSessionService, Depends(get_questionnaire_session_service)],
    response: Response,
) -> SessionResponse:
    response.headers["Cache-Control"] = "no-store"
    try:
        service.record_answer(session_id, QuestionnaireAnswer(question_id, payload.answer_id))
        authorize_questionnaire(session_id, request, db, actor)
        return _session_response(service, session_id)
    except LookupError as error:
        raise ApiError(
            status_code=404, code=ErrorCode.NOT_FOUND, message="Questionnaire session was not found."
        ) from error
    except QuestionnaireSessionExpiredError as error:
        raise ApiError(
            status_code=410, code=ErrorCode.NOT_FOUND, message="Questionnaire session has expired."
        ) from error
    except CanonicalAnswerValidationError as error:
        raise ApiError(
            status_code=422, code=ErrorCode.INVALID_REQUEST, message="Answer is not valid for this question."
        ) from error


def configuration_response(configuration: QuestionnaireConfiguration) -> QuestionnaireConfigurationResponse:
    return QuestionnaireConfigurationResponse(
        questionnaireVersion=configuration.questionnaire_version,
        questions=[
            QuestionnaireQuestionResponse(
                questionId=question.question_id,
                prompt=question.prompt,
                required=question.required,
                answerOptions=[
                    QuestionnaireAnswerOptionResponse(answerId=option.answer_id, label=option.label)
                    for option in question.answer_options
                ],
            )
            for question in configuration.questions
        ],
    )
