from datetime import datetime, timezone

from backend.app.questionnaire.domain.configuration import QuestionnaireConfiguration
from backend.app.questionnaire.domain.session import (
    QuestionnaireAnswer,
    QuestionnaireRetentionPolicy,
    QuestionnaireSession,
    new_anonymous_session,
    validate_canonical_answer,
)

from .ports import QuestionnaireSessionRepository


class QuestionnaireSessionService:
    def __init__(
        self,
        repository: QuestionnaireSessionRepository,
        configuration: QuestionnaireConfiguration,
        retention_policy: QuestionnaireRetentionPolicy,
    ) -> None:
        self._repository = repository
        self._configuration = configuration
        self._retention_policy = retention_policy

    def start(self, now: datetime | None = None) -> QuestionnaireSession:
        session = new_anonymous_session(self._configuration.questionnaire_version, self._retention_policy, now)
        self._repository.create(session)
        return session

    def record_answer(self, session_id: str, answer: QuestionnaireAnswer, now: datetime | None = None) -> None:
        session = self._repository.get(session_id)
        if session is None:
            raise LookupError("questionnaire session was not found")
        session.ensure_active(now or datetime.now(timezone.utc))
        self._repository.upsert_answer(session_id, validate_canonical_answer(self._configuration, answer))
