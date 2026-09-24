from typing import Protocol

from backend.app.questionnaire.domain.session import QuestionnaireAnswer, QuestionnaireSession


class QuestionnaireSessionRepository(Protocol):
    def create(self, session: QuestionnaireSession) -> None: ...

    def get(self, session_id: str) -> QuestionnaireSession | None: ...

    def upsert_answer(self, session_id: str, answer: QuestionnaireAnswer) -> None: ...
