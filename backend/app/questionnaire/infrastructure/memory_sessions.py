"""Process-local server-side adapter for development session wiring; never serializes answers into URLs."""

from __future__ import annotations

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
