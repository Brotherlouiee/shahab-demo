"""Anonymous questionnaire-session rules independent of HTTP and persistence."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from .configuration import QuestionnaireConfiguration


class QuestionnaireSessionError(ValueError):
    pass


class QuestionnaireSessionExpiredError(QuestionnaireSessionError):
    pass


class CanonicalAnswerValidationError(QuestionnaireSessionError):
    pass


@dataclass(frozen=True)
class QuestionnaireRetentionPolicy:
    session_lifetime: timedelta

    def expires_at(self, created_at: datetime) -> datetime:
        if created_at.tzinfo is None or self.session_lifetime <= timedelta():
            raise ValueError("expiry requires aware creation time and positive lifetime")
        return created_at + self.session_lifetime


@dataclass(frozen=True)
class QuestionnaireSession:
    session_id: uuid.UUID
    questionnaire_version: str
    created_at: datetime
    expires_at: datetime
    creator_proof_digest: str | None = None

    def ensure_active(self, now: datetime) -> None:
        if now.tzinfo is None:
            raise ValueError("now must be timezone-aware")
        if now >= self.expires_at:
            raise QuestionnaireSessionExpiredError("questionnaire session has expired")


@dataclass(frozen=True)
class QuestionnaireAnswer:
    question_id: str
    answer_id: str


def new_anonymous_session(
    questionnaire_version: str, retention_policy: QuestionnaireRetentionPolicy, now: datetime | None = None
) -> QuestionnaireSession:
    created_at = now or datetime.now(UTC)
    if created_at.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    return QuestionnaireSession(
        uuid.uuid4(), questionnaire_version, created_at, retention_policy.expires_at(created_at)
    )


def validate_canonical_answer(
    configuration: QuestionnaireConfiguration, answer: QuestionnaireAnswer
) -> QuestionnaireAnswer:
    for question in configuration.questions:
        if question.question_id == answer.question_id and answer.answer_id in {
            option.answer_id for option in question.answer_options
        }:
            return answer
    raise CanonicalAnswerValidationError("answer does not belong to its approved question")
