from datetime import datetime
from typing import Protocol

from backend.app.questionnaire.domain.session import QuestionnaireAnswer, QuestionnaireSession


class QuestionnaireSessionRepository(Protocol):
    def create(self, session: QuestionnaireSession) -> None: ...

    def get(self, session_id: str) -> QuestionnaireSession | None: ...

    def upsert_answer(self, session_id: str, answer: QuestionnaireAnswer) -> None: ...

    def list_answers(self, session_id: str) -> tuple[QuestionnaireAnswer, ...]: ...

    def upsert_flow_answer(
        self,
        session_id: str,
        step_id: str,
        answer_id: str,
        *,
        supersede_proof_digests: tuple[str, ...] = (),
    ) -> tuple[str, ...]: ...

    def list_flow_answers(self, session_id: str) -> dict[str, str]: ...

    def delete_expired(self, now: datetime) -> tuple[str, ...]:
        """Purge one bounded batch of raw answers; preserve referenced result evidence."""
        ...


class QuestionnaireSessionCache(Protocol):
    def get(self, session_id: str) -> QuestionnaireSession | None: ...

    def set(self, session: QuestionnaireSession) -> None: ...

    def delete(self, session_id: str) -> None: ...
