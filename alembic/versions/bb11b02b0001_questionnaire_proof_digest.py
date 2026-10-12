"""US-11.T02B: persist creator capability digests; legacy sessions fail closed.

Existing sessions stay intact, with NULL proof: the former constant cookie is
not evidence of creation. No fabricated secret or raw-answer backfill is made.
Revision ID: bb11b02b0001
Revises: aa11b02a2002
"""

import sqlalchemy as sa
from alembic import op

revision = "bb11b02b0001"
down_revision = "aa11b02a2002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questionnaire_sessions", sa.Column("creator_proof_digest", sa.String(64), nullable=True))
    op.create_check_constraint("ck_questionnaire_proof_digest", "questionnaire_sessions",
                               "creator_proof_digest IS NULL OR creator_proof_digest ~ '^[0-9a-f]{64}$'")
    op.execute("""CREATE FUNCTION protect_questionnaire_proof() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.creator_proof_digest IS DISTINCT FROM OLD.creator_proof_digest THEN
        RAISE EXCEPTION 'immutable questionnaire proof';
      END IF;
      RETURN NEW;
    END $$""")
    op.execute("CREATE TRIGGER protect_questionnaire_proof BEFORE UPDATE ON questionnaire_sessions "
               "FOR EACH ROW EXECUTE FUNCTION protect_questionnaire_proof()")


def downgrade() -> None:
    op.execute("DROP TRIGGER protect_questionnaire_proof ON questionnaire_sessions")
    op.execute("DROP FUNCTION protect_questionnaire_proof()")
    op.drop_constraint("ck_questionnaire_proof_digest", "questionnaire_sessions", type_="check")
    op.drop_column("questionnaire_sessions", "creator_proof_digest")
