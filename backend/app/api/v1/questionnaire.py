"""HTTP boundary for temporary anonymous questionnaire progress."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends

from backend.app.api.errors import ApiError, ErrorCode
from backend.app.core.dependencies import get_questionnaire_session_service
from backend.app.questionnaire.application.use_cases import QuestionnaireSessionService
from backend.app.questionnaire.domain.configuration import QuestionnaireConfiguration
from backend.app.questionnaire.domain.session import (
    CanonicalAnswerValidationError,
    QuestionnaireAnswer,
    QuestionnaireSessionExpiredError,
)

from .questionnaire_schemas import (
    AnswerWriteRequest,
    QuestionnaireAnswerOptionResponse,
    QuestionnaireConfigurationResponse,
    QuestionnaireQuestionResponse,
    SessionResponse,
)

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])


def _session_response(service: QuestionnaireSessionService, session_id: str) -> SessionResponse:
    session = service.get(session_id)
    return SessionResponse(
        sessionId=str(session.session_id),
        expiresAt=session.expires_at.isoformat(),
        answers={answer.question_id: answer.answer_id for answer in service.answers(session_id)},
    )


@router.post("/sessions", response_model=SessionResponse, status_code=201)
def start_session(service: Annotated[QuestionnaireSessionService, Depends(get_questionnaire_session_service)]) -> SessionResponse:
    session = service.start()
    return _session_response(service, str(session.session_id))


@router.get("/sessions/{session_id}", response_model=SessionResponse)
def resume_session(
    session_id: str, service: Annotated[QuestionnaireSessionService, Depends(get_questionnaire_session_service)]
) -> SessionResponse:
    try:
        return _session_response(service, session_id)
    except LookupError as error:
        raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="Questionnaire session was not found.") from error
    except QuestionnaireSessionExpiredError as error:
        raise ApiError(status_code=410, code=ErrorCode.NOT_FOUND, message="Questionnaire session has expired.") from error


@router.put("/sessions/{session_id}/answers/{question_id}", response_model=SessionResponse)
def write_answer(
    session_id: str,
    question_id: str,
    payload: Annotated[AnswerWriteRequest, Body()],
    service: Annotated[QuestionnaireSessionService, Depends(get_questionnaire_session_service)],
) -> SessionResponse:
    try:
        service.record_answer(session_id, QuestionnaireAnswer(question_id, payload.answer_id))
        return _session_response(service, session_id)
    except LookupError as error:
        raise ApiError(status_code=404, code=ErrorCode.NOT_FOUND, message="Questionnaire session was not found.") from error
    except QuestionnaireSessionExpiredError as error:
        raise ApiError(status_code=410, code=ErrorCode.NOT_FOUND, message="Questionnaire session has expired.") from error
    except CanonicalAnswerValidationError as error:
        raise ApiError(status_code=422, code=ErrorCode.INVALID_REQUEST, message="Answer is not valid for this question.") from error


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
