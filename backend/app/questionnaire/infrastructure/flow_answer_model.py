"""Small ORM mapping for non-scoring questionnaire entry answers."""

from __future__ import annotations

import uuid

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.infrastructure.db.models import Base


class QuestionnaireFlowAnswer(Base):
    """Two required entry answers stored under the short-lived session."""

    __tablename__ = "questionnaire_flow_answers"
    __table_args__ = (
        CheckConstraint(
            "(step_id = 'loan_type' AND answer_id IN ('shahab', 'bank')) OR "
            "(step_id = 'entity_type' AND answer_id IN ('business', 'person'))",
            name="ck_questionnaire_flow_answer_value",
        ),
    )
    questionnaire_session_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questionnaire_sessions.questionnaire_session_id", ondelete="CASCADE"), primary_key=True
    )
    step_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    answer_id: Mapped[str] = mapped_column(String(32), nullable=False)
