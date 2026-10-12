"""US-11.T02C: durable account credentials and shared OTP challenge/quota.

Revision ID: cc11b02c0001
Revises: bb11b02b0001
Only additive tables; no profile/history/answer/source backfill or copies.
"""

from alembic import op

revision = "cc11b02c0001"
down_revision = "bb11b02b0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE account_access_sessions (
      token_digest varchar(64) PRIMARY KEY CHECK(token_digest ~ '^[0-9a-f]{64}$'),
      account_id uuid NOT NULL REFERENCES accounts(account_id) ON DELETE RESTRICT,
      issued_at timestamptz NOT NULL,
      expires_at timestamptz NOT NULL,
      revoked_at timestamptz,
      CONSTRAINT ck_access_session_expiry CHECK(expires_at=issued_at+interval '1 hour'),
      CONSTRAINT ck_access_session_revocation CHECK(revoked_at IS NULL OR revoked_at>=issued_at)
    )""")
    op.execute("CREATE INDEX ix_access_session_account ON account_access_sessions(account_id)")
    op.execute("CREATE INDEX ix_access_session_expiry ON account_access_sessions(expires_at)")
    op.execute("""CREATE TABLE account_otp_challenges (
      challenge_digest varchar(64) PRIMARY KEY CHECK(challenge_digest ~ '^[0-9a-f]{64}$'),
      phone varchar(11) NOT NULL CHECK(phone ~ '^09[0-9]{9}$'),
      created_at timestamptz NOT NULL,
      expires_at timestamptz NOT NULL,
      attempts integer NOT NULL DEFAULT 0,
      consumed_at timestamptz,
      CONSTRAINT ck_otp_attempts CHECK(attempts>=0 AND attempts<=5),
      CONSTRAINT ck_otp_expiry CHECK(expires_at=created_at+interval '120 seconds')
    )""")
    op.execute("CREATE INDEX ix_otp_challenge_expiry ON account_otp_challenges(expires_at)")
    op.execute("""CREATE TABLE account_otp_quota_events (
      event_id uuid PRIMARY KEY,
      quota_key varchar(72) NOT NULL,
      occurred_at timestamptz NOT NULL
    )""")
    op.execute("CREATE INDEX ix_otp_quota_key_time ON account_otp_quota_events(quota_key,occurred_at)")
    op.execute("""CREATE FUNCTION protect_access_session() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.token_digest<>OLD.token_digest OR NEW.account_id<>OLD.account_id
         OR NEW.issued_at<>OLD.issued_at OR NEW.expires_at<>OLD.expires_at
         OR (OLD.revoked_at IS NOT NULL AND NEW.revoked_at IS DISTINCT FROM OLD.revoked_at) THEN
        RAISE EXCEPTION 'immutable access session';
      END IF;
      RETURN NEW;
    END $$""")
    op.execute("CREATE TRIGGER protect_access_session BEFORE UPDATE ON account_access_sessions "
               "FOR EACH ROW EXECUTE FUNCTION protect_access_session()")
    op.execute("""CREATE FUNCTION protect_otp_challenge() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF NEW.challenge_digest<>OLD.challenge_digest OR NEW.phone<>OLD.phone
         OR NEW.created_at<>OLD.created_at OR NEW.expires_at<>OLD.expires_at
         OR NEW.attempts<OLD.attempts
         OR (OLD.consumed_at IS NOT NULL AND NEW.consumed_at IS DISTINCT FROM OLD.consumed_at) THEN
        RAISE EXCEPTION 'immutable OTP lifecycle';
      END IF;
      RETURN NEW;
    END $$""")
    op.execute("CREATE TRIGGER protect_otp_challenge BEFORE UPDATE ON account_otp_challenges "
               "FOR EACH ROW EXECUTE FUNCTION protect_otp_challenge()")


def downgrade() -> None:
    # Credentials/challenges are intentionally invalidated, never rebound by phone.
    # All durable business data stays in its existing tables. Stop all workers
    # before reverting; old binaries must not reopen an incompatible schema.
    op.execute("DROP TRIGGER protect_otp_challenge ON account_otp_challenges")
    op.execute("DROP FUNCTION protect_otp_challenge()")
    op.execute("DROP TRIGGER protect_access_session ON account_access_sessions")
    op.execute("DROP FUNCTION protect_access_session()")
    op.drop_table("account_otp_quota_events")
    op.drop_table("account_otp_challenges")
    op.drop_table("account_access_sessions")
