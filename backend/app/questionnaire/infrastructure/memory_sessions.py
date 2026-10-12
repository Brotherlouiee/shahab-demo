"""Process-local repository used only where no database is configured (tests/local development)."""

from __future__ import annotations

from datetime import datetime

from backend.app.questionnaire.domain.session import QuestionnaireAnswer, QuestionnaireSession


class InMemoryQuestionnaireSessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, QuestionnaireSession] = {}
        self._answers: dict[str, dict[str, QuestionnaireAnswer]] = {}

    def create(self, session: QuestionnaireSession) -> None:
        key = str(session.session_id)
        self._sessions[key] = session
        self._answers[key] = {}

    def get(self, session_id: str) -> QuestionnaireSession | None:
        return self._sessions.get(session_id)

    def upsert_answer(self, session_id: str, answer: QuestionnaireAnswer) -> None:
        self._answers[session_id][answer.question_id] = answer

    def list_answers(self, session_id: str) -> tuple[QuestionnaireAnswer, ...]:
        return tuple(self._answers[session_id].values())

    def delete_expired(self, now: datetime) -> tuple[str, ...]:
        expired = tuple(
            session_id
            for session_id, session in sorted(self._sessions.items(), key=lambda item: (item[1].expires_at, item[0]))
            if session.expires_at <= now
        )[:100]
        for session_id in expired:
            del self._sessions[session_id]
            del self._answers[session_id]
        return expired
