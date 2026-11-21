"""Process-local repository used only where no database is configured (tests/local development)."""

from __future__ import annotations

from datetime import datetime

from backend.app.questionnaire.domain.session import QuestionnaireAnswer, QuestionnaireSession


class InMemoryQuestionnaireSessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, QuestionnaireSession] = {}
        self._answers: dict[str, dict[str, QuestionnaireAnswer]] = {}
        self._flow_answers: dict[str, dict[str, str]] = {}
        self._superseded: set[str] = set()

    def create(self, session: QuestionnaireSession) -> None:
        key = str(session.session_id)
        self._sessions[key] = session
        self._answers[key] = {}
        self._flow_answers[key] = {}

    def get(self, session_id: str) -> QuestionnaireSession | None:
        return self._sessions.get(session_id)

    def upsert_answer(self, session_id: str, answer: QuestionnaireAnswer) -> None:
        self._answers[session_id][answer.question_id] = answer

    def list_answers(self, session_id: str) -> tuple[QuestionnaireAnswer, ...]:
        return tuple(self._answers[session_id].values())

    def upsert_flow_answer(
        self,
        session_id: str,
        step_id: str,
        answer_id: str,
        *,
        supersede_proof_digests: tuple[str, ...] = (),
    ) -> tuple[str, ...]:
        self._flow_answers[session_id][step_id] = answer_id
        if not supersede_proof_digests:
            return ()
        current = self._sessions[session_id]
        superseded = tuple(
            candidate_id
            for candidate_id, candidate in self._sessions.items()
            if candidate_id != session_id
            and candidate_id not in self._superseded
            and candidate.created_at < current.created_at
            and candidate.expires_at > current.created_at
            and candidate.creator_proof_digest in supersede_proof_digests
        )
        self._superseded.update(superseded)
        return superseded

    def is_superseded(self, session_id: str) -> bool:
        return session_id in self._superseded

    def list_flow_answers(self, session_id: str) -> dict[str, str]:
        return dict(self._flow_answers[session_id])

    def delete_expired(self, now: datetime) -> tuple[str, ...]:
        expired = tuple(
            session_id
            for session_id, session in sorted(self._sessions.items(), key=lambda item: (item[1].expires_at, item[0]))
            if session.expires_at <= now
        )[:100]
        for session_id in expired:
            del self._sessions[session_id]
            del self._answers[session_id]
            del self._flow_answers[session_id]
        return expired
