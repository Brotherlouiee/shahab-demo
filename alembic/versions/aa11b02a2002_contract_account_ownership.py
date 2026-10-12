"""US-11.T02A.2: guarded ownership cutover after stopped-writer backfill.

Revision ID: aa11b02a2002
Revises: aa11b02a2001

Runbook requires writer shutdown and new backend deployment before reopening.
The backfill is also callable independently after expand, for repeatability and
preflight verification; this invocation catches last legacy writes under locks.
"""

import sqlalchemy as sa
from alembic import op

from backend.app.infrastructure.db.account_backfill import backfill_accounts

revision = "aa11b02a2002"
down_revision = "aa11b02a2001"
branch_labels = None
depends_on = None


def _phone_fk(table: str) -> str:
    matches = [fk['name'] for fk in sa.inspect(op.get_bind()).get_foreign_keys(table)
               if fk['constrained_columns'] == ['owner_phone'] and fk['referred_table'] == 'user_profiles']
    if len(matches) != 1 or not matches[0]:
        raise RuntimeError("Legacy foreign-key audit failed.")
    return matches[0]


def upgrade() -> None:
    backfill_accounts(op.get_bind())
    for table in ("recommendation_history_runs", "questionnaire_sessions"):
        op.drop_constraint(_phone_fk(table), table, type_="foreignkey")
    op.drop_index("ix_recommendation_history_owner_created", table_name="recommendation_history_runs")
    op.drop_index("ix_questionnaire_sessions_owner_phone", table_name="questionnaire_sessions")
    op.alter_column("user_profiles", "account_id", nullable=False)
    op.drop_constraint("user_profiles_pkey", "user_profiles", type_="primary")
    op.drop_constraint("uq_profile_account", "user_profiles", type_="unique")
    op.create_primary_key("user_profiles_pkey", "user_profiles", ["account_id"])
    op.alter_column("recommendation_history_runs", "owner_account_id", nullable=False)
    op.create_unique_constraint("uq_questionnaire_session_owner", "questionnaire_sessions", ["questionnaire_session_id", "owner_account_id"])
    op.create_foreign_key("fk_history_session_owner", "recommendation_history_runs", "questionnaire_sessions",
                          ["questionnaire_session_id", "owner_account_id"], ["questionnaire_session_id", "owner_account_id"], ondelete="RESTRICT")
    op.create_index("ix_questionnaire_sessions_owner_account_id", "questionnaire_sessions", ["owner_account_id"])
    op.create_index("ix_recommendation_history_owner_created", "recommendation_history_runs",
                    ["owner_account_id", "created_at", "recommendation_history_run_id"])
    for table in ("recommendation_history_runs", "questionnaire_sessions"):
        op.drop_column(table, "owner_phone")
    op.drop_column("user_profiles", "phone")
    # SQL writes cannot retarget an identity or rebound session; status archive is
    # terminal. No public archive feature is introduced here.
    op.execute("""CREATE FUNCTION protect_account_identity() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.account_id <> OLD.account_id OR NEW.phone <> OLD.phone OR NEW.created_at <> OLD.created_at
         OR (OLD.status='archived' AND (NEW.status <> OLD.status OR NEW.archived_at IS DISTINCT FROM OLD.archived_at)) THEN
        RAISE EXCEPTION 'immutable account identity';
      END IF;
      RETURN NEW;
    END $$""")
    op.execute("CREATE TRIGGER protect_account_identity BEFORE UPDATE ON accounts FOR EACH ROW EXECUTE FUNCTION protect_account_identity()")
    op.execute("""CREATE FUNCTION protect_questionnaire_owner() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF OLD.owner_account_id IS NOT NULL AND NEW.owner_account_id IS DISTINCT FROM OLD.owner_account_id THEN
        RAISE EXCEPTION 'immutable questionnaire owner';
      END IF;
      RETURN NEW;
    END $$""")
    op.execute("CREATE TRIGGER protect_questionnaire_owner BEFORE UPDATE ON questionnaire_sessions FOR EACH ROW EXECUTE FUNCTION protect_questionnaire_owner()")


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(sa.text("LOCK TABLE accounts, user_profiles, questionnaire_sessions, recommendation_history_runs IN ACCESS EXCLUSIVE MODE"))
    # Refuse before any DDL: phone-PK cannot represent multiple retained generations.
    if connection.scalar(sa.text("SELECT count(*) FROM (SELECT phone FROM accounts GROUP BY phone HAVING count(*)>1) x")):
        raise RuntimeError("Account downgrade refused: multiple retained generations; roll forward.")
    if connection.scalar(sa.text("SELECT count(*) FROM accounts WHERE status <> 'active'")):
        raise RuntimeError("Account downgrade refused: archive state cannot be represented by legacy schema.")
    if connection.scalar(sa.text("SELECT count(*) FROM accounts a LEFT JOIN user_profiles p USING(account_id) WHERE p.account_id IS NULL")):
        raise RuntimeError("Account downgrade refused: missing profile.")
    op.execute("DROP TRIGGER protect_questionnaire_owner ON questionnaire_sessions")
    op.execute("DROP FUNCTION protect_questionnaire_owner()")
    op.execute("DROP TRIGGER protect_account_identity ON accounts")
    op.execute("DROP FUNCTION protect_account_identity()")
    op.add_column("user_profiles", sa.Column("phone", sa.String(11), nullable=True))
    op.execute("UPDATE user_profiles p SET phone=a.phone FROM accounts a WHERE p.account_id=a.account_id")
    op.alter_column("user_profiles", "phone", nullable=False)
    op.drop_constraint("fk_history_session_owner", "recommendation_history_runs", type_="foreignkey")
    op.drop_constraint("uq_questionnaire_session_owner", "questionnaire_sessions", type_="unique")
    op.drop_index("ix_questionnaire_sessions_owner_account_id", table_name="questionnaire_sessions")
    op.drop_index("ix_recommendation_history_owner_created", table_name="recommendation_history_runs")
    op.drop_constraint("user_profiles_pkey", "user_profiles", type_="primary")
    op.create_primary_key("user_profiles_pkey", "user_profiles", ["phone"])
    op.create_unique_constraint("uq_profile_account", "user_profiles", ["account_id"])
    op.alter_column("user_profiles", "account_id", nullable=True)
    op.alter_column("recommendation_history_runs", "owner_account_id", nullable=True)
    for table in ("questionnaire_sessions", "recommendation_history_runs"):
        op.add_column(table, sa.Column("owner_phone", sa.String(11), nullable=True))
        op.execute(f"UPDATE {table} s SET owner_phone=a.phone FROM accounts a WHERE s.owner_account_id=a.account_id")
        op.create_foreign_key("fk_" + table + "_owner_phone", table, "user_profiles", ["owner_phone"], ["phone"])
    op.alter_column("recommendation_history_runs", "owner_phone", nullable=False)
    op.create_index("ix_questionnaire_sessions_owner_phone", "questionnaire_sessions", ["owner_phone"])
    op.create_index("ix_recommendation_history_owner_created", "recommendation_history_runs", ["owner_phone", "created_at", "recommendation_history_run_id"])
