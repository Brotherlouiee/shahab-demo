"""Repeatable legacy ownership backfill, run only with customer writers stopped.

The accounts partial unique index persists the phone-to-ID mapping. This bridge
exists only between expand and contract; it must never authenticate credentials.
Errors contain invariant names/counts, never phone values or profile facts.
"""

from sqlalchemy import Connection, text


def backfill_accounts(connection: Connection) -> dict[str, int]:
    """Lock legacy tables, reject drift, and map every existing owner in one transaction."""
    connection.execute(
        text(
            "LOCK TABLE user_profiles, questionnaire_sessions, recommendation_history_runs IN SHARE ROW EXCLUSIVE MODE"
        )
    )
    bad = connection.scalar(text("SELECT count(*) FROM user_profiles WHERE phone !~ '^09[0-9]{9}$'"))
    mismatch = connection.scalar(
        text(
            "SELECT count(*) FROM recommendation_history_runs h "
            "JOIN questionnaire_sessions s USING (questionnaire_session_id) "
            "WHERE s.owner_phone IS NOT NULL AND s.owner_phone <> h.owner_phone"
        )
    )
    orphan = connection.scalar(
        text(
            "SELECT count(*) FROM recommendation_history_runs h "
            "LEFT JOIN user_profiles p ON p.phone=h.owner_phone "
            "LEFT JOIN questionnaire_sessions s USING (questionnaire_session_id) "
            "WHERE p.phone IS NULL OR s.questionnaire_session_id IS NULL"
        )
    )
    session_orphan = connection.scalar(
        text(
            "SELECT count(*) FROM questionnaire_sessions s "
            "LEFT JOIN user_profiles p ON p.phone=s.owner_phone "
            "WHERE s.owner_phone IS NOT NULL AND p.phone IS NULL"
        )
    )
    if bad or mismatch or orphan or session_orphan:
        raise RuntimeError("Legacy account audit failed; no data was normalized or reassigned.")
    # Same transaction, stable mapping on retry: never generate a new ID for an
    # already mapped phone. Profiles preserve all facts and original timestamps.
    connection.execute(
        text(
            "INSERT INTO accounts (account_id, phone, status, created_at) "
            "SELECT gen_random_uuid(), p.phone, 'active', p.created_at FROM user_profiles p "
            "WHERE NOT EXISTS (SELECT 1 FROM accounts a WHERE a.phone=p.phone AND a.status='active')"
        )
    )
    drift = connection.scalar(
        text(
            "SELECT count(*) FROM user_profiles p JOIN accounts a "
            "ON a.phone=p.phone AND a.status='active' "
            "WHERE p.account_id IS NOT NULL AND p.account_id <> a.account_id"
        )
    )
    if drift:
        raise RuntimeError("Persisted account mapping changed; backfill refused.")
    connection.execute(
        text(
            "UPDATE user_profiles p SET account_id=a.account_id FROM accounts a "
            "WHERE a.phone=p.phone AND a.status='active' AND p.account_id IS NULL"
        )
    )
    # Pre-f1 history can legitimately reference a session without owner_phone.
    # Only the already stored unique history owner supplies that legacy mapping;
    # a non-null conflicting owner was rejected above, never silently overwritten.
    connection.execute(
        text(
            "UPDATE questionnaire_sessions s SET owner_phone=h.owner_phone "
            "FROM recommendation_history_runs h WHERE h.questionnaire_session_id=s.questionnaire_session_id "
            "AND s.owner_phone IS NULL"
        )
    )
    for table in ("questionnaire_sessions", "recommendation_history_runs"):
        drift = connection.scalar(
            text(
                f"SELECT count(*) FROM {table} s JOIN user_profiles p ON p.phone=s.owner_phone "
                "WHERE s.owner_account_id IS NOT NULL AND s.owner_account_id <> p.account_id"
            )
        )
        if drift:
            raise RuntimeError("Persisted ownership mapping changed; backfill refused.")
        connection.execute(
            text(
                f"UPDATE {table} s SET owner_account_id=p.account_id FROM user_profiles p "
                "WHERE p.phone=s.owner_phone AND s.owner_account_id IS NULL"
            )
        )
    missing = connection.scalar(text("SELECT count(*) FROM user_profiles WHERE account_id IS NULL"))
    missing_history = connection.scalar(
        text("SELECT count(*) FROM recommendation_history_runs WHERE owner_account_id IS NULL")
    )
    missing_owned_session = connection.scalar(
        text("SELECT count(*) FROM questionnaire_sessions WHERE owner_phone IS NOT NULL AND owner_account_id IS NULL")
    )
    extra_account = connection.scalar(
        text(
            "SELECT count(*) FROM accounts a LEFT JOIN user_profiles p ON p.account_id=a.account_id "
            "WHERE p.account_id IS NULL OR p.phone <> a.phone OR a.status <> 'active'"
        )
    )
    if missing or missing_history or missing_owned_session or extra_account:
        raise RuntimeError("Account backfill incomplete; contract refused.")
    return {
        table: int(connection.scalar(text(f"SELECT count(*) FROM {table}")) or 0)
        for table in ("accounts", "user_profiles", "questionnaire_sessions", "recommendation_history_runs")
    }
