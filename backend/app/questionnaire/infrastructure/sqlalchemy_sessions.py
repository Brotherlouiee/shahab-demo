"""Normalized PostgreSQL repository for anonymous questionnaire progress."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import (
    AnswerOption,
    Question,
    QuestionnaireSessionState,
    QuestionnaireVersion,
)
from backend.app.infrastructure.db.models import QuestionnaireAnswer as QuestionnaireAnswerRow
from backend.app.infrastructure.db.models import QuestionnaireSession as QuestionnaireSessionRow
from backend.app.questionnaire.domain.configuration import QuestionnaireConfiguration
from backend.app.questionnaire.domain.session import QuestionnaireAnswer, QuestionnaireSession


class SqlAlchemyQuestionnaireSessionRepository:
    def __init__(
        self,
        session: Session,
        configuration: QuestionnaireConfiguration,
        *,
        reference_catalogue: tuple[uuid.UUID, dict[str, uuid.UUID], dict[str, uuid.UUID]] | None = None,
    ) -> None:
        self._session = session
        self._configuration = configuration
        self._version_id, self._question_ids, self._answer_ids = (
            reference_catalogue if reference_catalogue is not None else self._ensure_reference_catalogue()
        )

    @property
    def reference_catalogue(self) -> tuple[uuid.UUID, dict[str, uuid.UUID], dict[str, uuid.UUID]]:
        """Return the identifiers prepared once during application startup."""
        return self._version_id, self._question_ids, self._answer_ids

    def create(self, session: QuestionnaireSession) -> None:
        self._session.add(
            QuestionnaireSessionRow(
                questionnaire_session_id=session.session_id,
                questionnaire_version_id=self._version_id,
                state=QuestionnaireSessionState.ACTIVE,
                created_at=session.created_at,
                expires_at=session.expires_at,
            )
        )
        self._session.commit()

    def get(self, session_id: str) -> QuestionnaireSession | None:
        try:
            identifier = uuid.UUID(session_id)
        except ValueError:
            return None
        row = self._session.get(QuestionnaireSessionRow, identifier)
        if row is None:
            return None
        return QuestionnaireSession(
            row.questionnaire_session_id,
            self._configuration.questionnaire_version,
            row.created_at if row.created_at.tzinfo else row.created_at.replace(tzinfo=UTC),
            row.expires_at if row.expires_at.tzinfo else row.expires_at.replace(tzinfo=UTC),
        )

    def upsert_answer(self, session_id: str, answer: QuestionnaireAnswer) -> None:
        session_uuid = uuid.UUID(session_id)
        question_id = self._question_ids[answer.question_id]
        answer_id = self._answer_ids[answer.answer_id]
        row = self._session.scalar(
            select(QuestionnaireAnswerRow).where(
                QuestionnaireAnswerRow.questionnaire_session_id == session_uuid,
                QuestionnaireAnswerRow.question_id == question_id,
            )
        )
        if row is None:
            self._session.add(
                QuestionnaireAnswerRow(
                    questionnaire_session_id=session_uuid,
                    question_id=question_id,
                    answer_option_id=answer_id,
                )
            )
        else:
            row.answer_option_id = answer_id
        self._session.commit()

    def list_answers(self, session_id: str) -> tuple[QuestionnaireAnswer, ...]:
        rows = self._session.execute(
            select(Question.canonical_id, AnswerOption.canonical_id)
            .join(QuestionnaireAnswerRow, QuestionnaireAnswerRow.question_id == Question.question_id)
            .join(AnswerOption, AnswerOption.answer_option_id == QuestionnaireAnswerRow.answer_option_id)
            .where(QuestionnaireAnswerRow.questionnaire_session_id == uuid.UUID(session_id))
            .order_by(Question.display_order)
        ).all()
        return tuple(QuestionnaireAnswer(question_id, answer_id) for question_id, answer_id in rows)

    def delete_expired(self, now: datetime) -> tuple[str, ...]:
        rows = self._session.scalars(
            select(QuestionnaireSessionRow).where(QuestionnaireSessionRow.expires_at <= now)
        ).all()
        identifiers = [row.questionnaire_session_id for row in rows]
        if not identifiers:
            return ()
        self._session.execute(
            delete(QuestionnaireAnswerRow).where(QuestionnaireAnswerRow.questionnaire_session_id.in_(identifiers))
        )
        self._session.execute(
            delete(QuestionnaireSessionRow).where(QuestionnaireSessionRow.questionnaire_session_id.in_(identifiers))
        )
        self._session.commit()
        return tuple(str(identifier) for identifier in identifiers)

    def _ensure_reference_catalogue(self) -> tuple[uuid.UUID, dict[str, uuid.UUID], dict[str, uuid.UUID]]:
        version = self._session.scalar(
            select(QuestionnaireVersion).where(
                QuestionnaireVersion.version_code == self._configuration.questionnaire_version
            )
        )
        if version is None:
            version = QuestionnaireVersion(
                version_code=self._configuration.questionnaire_version,
                source_hash=self._configuration.source_sha256,
            )
            self._session.add(version)
            self._session.flush()
        questions: dict[str, uuid.UUID] = {}
        answers: dict[str, uuid.UUID] = {}
        for order, configured_question in enumerate(self._configuration.questions, start=1):
            question = self._session.scalar(
                select(Question).where(
                    Question.questionnaire_version_id == version.questionnaire_version_id,
                    Question.canonical_id == configured_question.question_id,
                )
            )
            if question is None:
                question = Question(
                    questionnaire_version_id=version.questionnaire_version_id,
                    canonical_id=configured_question.question_id,
                    display_order=order,
                )
                self._session.add(question)
                self._session.flush()
            questions[configured_question.question_id] = question.question_id
            for configured_answer in configured_question.answer_options:
                option = self._session.scalar(
                    select(AnswerOption).where(
                        AnswerOption.question_id == question.question_id,
                        AnswerOption.canonical_id == configured_answer.answer_id,
                    )
                )
                if option is None:
                    option = AnswerOption(question_id=question.question_id, canonical_id=configured_answer.answer_id)
                    self._session.add(option)
                    self._session.flush()
                answers[configured_answer.answer_id] = option.answer_option_id
        self._session.commit()
        return version.questionnaire_version_id, questions, answers
