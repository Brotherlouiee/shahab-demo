"""Public questionnaire transport models; values are body-only and canonical."""
from __future__ import annotations

from pydantic import BaseModel, Field


class AnswerWriteRequest(BaseModel):
    answer_id: str = Field(alias="answerId", min_length=1, max_length=200)
    model_config = {"populate_by_name": True}


class SessionResponse(BaseModel):
    session_id: str = Field(alias="sessionId")
    expires_at: str = Field(alias="expiresAt")
    answers: dict[str, str]
    model_config = {"populate_by_name": True}


class QuestionnaireAnswerOptionResponse(BaseModel):
    answer_id: str = Field(alias="answerId")
    label: str
    model_config = {"populate_by_name": True}


class QuestionnaireQuestionResponse(BaseModel):
    question_id: str = Field(alias="questionId")
    prompt: str
    required: bool
    answer_options: list[QuestionnaireAnswerOptionResponse] = Field(alias="answerOptions")
    model_config = {"populate_by_name": True}


class QuestionnaireConfigurationResponse(BaseModel):
    questionnaire_version: str = Field(alias="questionnaireVersion")
    questions: list[QuestionnaireQuestionResponse]
    model_config = {"populate_by_name": True}
