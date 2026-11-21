"""Explicit one-time upgrade for an already published T05A official catalogue."""

from __future__ import annotations

import argparse
import json
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.loans.infrastructure.backfill_serving_facts import backfill_official_serving_facts
from scripts.build_t05a_import_manifest import build_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--actor-reference", required=True)
    parser.add_argument("--approval-reason", required=True)
    args = parser.parse_args()
    if not args.actor_reference.strip() or not args.approval_reason.strip():
        raise SystemExit("operator reference and approval reason are required")
    url = os.environ.get("SHAHAB_DATABASE_URL")
    if not url:
        raise SystemExit("SHAHAB_DATABASE_URL is required")
    engine = create_engine(url, pool_pre_ping=True)
    try:
        with Session(engine) as session, session.begin():
            created = backfill_official_serving_facts(session, build_manifest())
        print(json.dumps({"created": created, "reused": 102 - created, "actorReference": args.actor_reference}))
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
