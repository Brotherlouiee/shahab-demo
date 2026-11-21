"""Persist the two required, non-scoring questionnaire entry steps.

Revision ID: a17d9c4e6b20
Revises: ff11b02f0001
"""

from alembic import op
import sqlalchemy as sa

revision = "a17d9c4e6b20"
down_revision = "ff11b02f0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "questionnaire_flow_answers",
        sa.Column("questionnaire_session_id", sa.Uuid(), nullable=False),
        sa.Column("step_id", sa.String(length=32), nullable=False),
        sa.Column("answer_id", sa.String(length=32), nullable=False),
        sa.PrimaryKeyConstraint("questionnaire_session_id", "step_id"),
        sa.ForeignKeyConstraint(
            ["questionnaire_session_id"],
            ["questionnaire_sessions.questionnaire_session_id"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint(
            "(step_id = 'loan_type' AND answer_id IN ('shahab', 'bank')) OR "
            "(step_id = 'entity_type' AND answer_id IN ('business', 'person'))",
            name="ck_questionnaire_flow_answer_value",
        ),
    )


def downgrade() -> None:
    # These are transient answers with the parent session's short expiry, like
    # questionnaire_answers; a schema rollback removes both owned answer sets.
    op.drop_table("questionnaire_flow_answers")
