"""add anonymous questionnaire sessions
Revision ID: 7b3f2f4a9c10
Revises: 4376ef397102
"""
from alembic import op
import sqlalchemy as sa
revision = "7b3f2f4a9c10"
down_revision = "4376ef397102"
branch_labels = None
depends_on = None
def upgrade() -> None:
    state = sa.Enum("ACTIVE", "EXPIRED", name="questionnairesessionstate")
    op.create_table("questionnaire_sessions", sa.Column("questionnaire_session_id", sa.Uuid(), nullable=False), sa.Column("questionnaire_version_id", sa.Uuid(), nullable=False), sa.Column("state", state, nullable=False), sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.CheckConstraint("expires_at > created_at", name="ck_questionnaire_session_expiry"), sa.ForeignKeyConstraint(["questionnaire_version_id"], ["questionnaire_versions.questionnaire_version_id"]), sa.PrimaryKeyConstraint("questionnaire_session_id"))
    op.create_unique_constraint("uq_answer_option_question_id", "answer_options", ["question_id", "answer_option_id"])
    op.create_table("questionnaire_answers", sa.Column("questionnaire_answer_id", sa.Uuid(), nullable=False), sa.Column("questionnaire_session_id", sa.Uuid(), nullable=False), sa.Column("question_id", sa.Uuid(), nullable=False), sa.Column("answer_option_id", sa.Uuid(), nullable=False), sa.ForeignKeyConstraint(["questionnaire_session_id"], ["questionnaire_sessions.questionnaire_session_id"]), sa.ForeignKeyConstraint(["question_id"], ["questions.question_id"]), sa.ForeignKeyConstraint(["answer_option_id"], ["answer_options.answer_option_id"]), sa.ForeignKeyConstraint(["question_id", "answer_option_id"], ["answer_options.question_id", "answer_options.answer_option_id"], name="fk_questionnaire_answer_option_belongs_to_question"), sa.PrimaryKeyConstraint("questionnaire_answer_id"), sa.UniqueConstraint("questionnaire_session_id", "question_id", name="uq_questionnaire_answer_session_question"))
    op.create_index("ix_questionnaire_sessions_expiry", "questionnaire_sessions", ["expires_at"])
def downgrade() -> None:
    op.drop_index("ix_questionnaire_sessions_expiry", table_name="questionnaire_sessions")
    op.drop_table("questionnaire_answers")
    op.drop_table("questionnaire_sessions")
    op.drop_constraint("uq_answer_option_question_id", "answer_options", type_="unique")
    sa.Enum(name="questionnairesessionstate").drop(op.get_bind(), checkfirst=True)
