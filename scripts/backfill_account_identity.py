"""Stopped-writer bridge after expand; default is read-only count/revision audit.

Use only the explicitly selected SHAHAB_DATABASE_URL. --apply is an operational
write, not a reset. The product UI/API never invokes this legacy phone bridge.
"""

import argparse
import json

from sqlalchemy import create_engine, text

from backend.app.core.config import get_settings
from backend.app.infrastructure.db.account_backfill import backfill_accounts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply the atomic backfill with writers stopped")
    args = parser.parse_args()
    url = get_settings().database_url_value
    if not url:
        raise SystemExit("SHAHAB_DATABASE_URL is required.")
    engine = create_engine(url)
    try:
        with engine.begin() as connection:
            revision = connection.scalar(text("SELECT version_num FROM alembic_version"))
            if revision != "aa11b02a2001":
                raise SystemExit("Requires exactly the account expand revision; no changes applied.")
            if args.apply:
                counts = backfill_accounts(connection)
            else:
                counts = {
                    table: int(connection.scalar(text(f"SELECT count(*) FROM {table}")) or 0)
                    for table in ("accounts", "user_profiles", "questionnaire_sessions", "recommendation_history_runs")
                }
            print(json.dumps({"revision": revision, "applied": args.apply, "counts": counts}))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
