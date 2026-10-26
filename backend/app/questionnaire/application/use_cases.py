from dataclasses import replace
from datetime import UTC, datetime

from backend.app.questionnaire.domain.configuration import QuestionnaireConfiguration
from backend.app.questionnaire.domain.session import (
    CanonicalAnswerValidationError,
    QuestionnaireAnswer,
    QuestionnaireRetentionPolicy,
    QuestionnaireSession,
    new_anonymous_session,
    validate_canonical_answer,
)

from .ports import QuestionnaireSessionCache, QuestionnaireSessionRepository


class QuestionnaireSessionService:
    def __init__(
        self,
        repository: QuestionnaireSessionRepository,
        configuration: QuestionnaireConfiguration,
        retention_policy: QuestionnaireRetentionPolicy,
        cache: QuestionnaireSessionCache | None = None,
    ) -> None:
        self._repository = repository
        self._configuration = configuration
        self._retention_policy = retention_policy
        self._cache = cache

    def start(self, now: datetime | None = None, *, proof_digest: str | None = None) -> QuestionnaireSession:
        session = new_anonymous_session(self._configuration.questionnaire_version, self._retention_policy, now)
        session = replace(session, creator_proof_digest=proof_digest)
        self._repository.create(session)
        self._cache_set(session)
        return session

    def record_answer(self, session_id: str, answer: QuestionnaireAnswer, now: datetime | None = None) -> None:
        session = self.get(session_id)
        session.ensure_active(now or datetime.now(UTC))
        validated_answer = validate_canonical_answer(self._configuration, answer)
        question_ids = [question.question_id for question in self._configuration.questions]
        question_index = question_ids.index(validated_answer.question_id)
        answered_question_ids = {saved.question_id for saved in self._repository.list_answers(session_id)}
        unanswered_required = [
            question.question_id
            for question in self._configuration.questions[:question_index]
            if question.required and question.question_id not in answered_question_ids
        ]
        if unanswered_required:
            raise CanonicalAnswerValidationError("required questions must be answered in order")

        self._repository.upsert_answer(session_id, validated_answer)
        self._cache_set(session)

    def get(self, session_id: str) -> QuestionnaireSession:
        session = self._cache_get(session_id) or self._repository.get(session_id)
        if session is None:
            raise LookupError("questionnaire session was not found")
        session.ensure_active(datetime.now(UTC))
        self._cache_set(session)
        return session

    def answers(self, session_id: str) -> tuple[QuestionnaireAnswer, ...]:
        self.get(session_id)
        return self._repository.list_answers(session_id)

    def cleanup_expired(self, now: datetime | None = None) -> int:
        session_ids = self._repository.delete_expired(now or datetime.now(UTC))
        for session_id in session_ids:
            self._cache_delete(session_id)
        return len(session_ids)

    def _cache_get(self, session_id: str) -> QuestionnaireSession | None:
        return self._cache.get(session_id) if self._cache else None

    def _cache_set(self, session: QuestionnaireSession) -> None:
        if self._cache:
            self._cache.set(session)

    def _cache_delete(self, session_id: str) -> None:
        if self._cache:
            self._cache.delete(session_id)
