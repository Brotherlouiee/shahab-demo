"""US-11.T02F: normalized bookmarks, owner-consistent optional historical context.

No browser backfill: legacy localStorage has no provable account provenance.
Revision ID: ff11b02f0001
Revises: cc11b02c0001
"""

import sqlalchemy as sa
from alembic import op

revision = "ff11b02f0001"
down_revision = "cc11b02c0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint("uq_history_run_owner", "recommendation_history_runs",
                                ["recommendation_history_run_id", "owner_account_id"])
    op.create_table(
        "account_bookmarks",
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("loan_product_version_id", sa.Uuid(), nullable=False),
        sa.Column("source_history_run_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("account_id", "loan_product_version_id"),
        sa.ForeignKeyConstraint(["account_id"], ["accounts.account_id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["loan_product_version_id"], ["loan_product_versions.loan_product_version_id"],
                                ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["source_history_run_id", "account_id"],
                                ["recommendation_history_runs.recommendation_history_run_id",
                                 "recommendation_history_runs.owner_account_id"],
                                name="fk_bookmark_history_owner", ondelete="RESTRICT"),
        sa.CheckConstraint("removed_at IS NULL OR removed_at >= created_at", name="ck_bookmark_removal_time"),
    )
    op.create_index("ix_bookmark_owner_visible_created", "account_bookmarks",
                    ["account_id", "removed_at", "created_at", "loan_product_version_id"])
    op.execute("""CREATE FUNCTION protect_bookmark_identity() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.account_id IS DISTINCT FROM OLD.account_id OR
         NEW.loan_product_version_id IS DISTINCT FROM OLD.loan_product_version_id THEN
        RAISE EXCEPTION 'immutable bookmark identity';
      END IF;
      RETURN NEW;
    END $$""")
    op.execute("CREATE TRIGGER protect_bookmark_identity BEFORE UPDATE ON account_bookmarks "
               "FOR EACH ROW EXECUTE FUNCTION protect_bookmark_identity()")


def downgrade() -> None:
    # A schema rollback cannot silently discard durable user associations.
    if op.get_bind().scalar(sa.text("SELECT count(*) FROM account_bookmarks")):
        raise RuntimeError("Retained bookmarks prevent destructive downgrade; use compatible roll-forward.")
    op.execute("DROP TRIGGER protect_bookmark_identity ON account_bookmarks")
    op.execute("DROP FUNCTION protect_bookmark_identity()")
    op.drop_index("ix_bookmark_owner_visible_created", table_name="account_bookmarks")
    op.drop_table("account_bookmarks")
    op.drop_constraint("uq_history_run_owner", "recommendation_history_runs", type_="unique")
