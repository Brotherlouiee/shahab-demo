"""Operator-only raw retention command; dry-run by default, no HTTP authority."""

import argparse
import json
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.core.config import Settings
from backend.app.questionnaire.infrastructure.retention import (
    DEFAULT_BATCH_SIZE,
    PurgeBatch,
    pending_counts,
    purge_expired_batch,
    validate_batch_size,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="commit bounded purge batches; default is read-only")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max-batches", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        validate_batch_size(args.batch_size)
        if not 1 <= args.max_batches <= 10000:
            raise ValueError("invalid max-batches")
    except ValueError:
        parser.error("batch-size must be 1..1000 and max-batches 1..10000")
    counts = PurgeBatch().counts()
    completed_batches = 0
    engine = None
    try:
        url = Settings().database_url_value
        if not url:
            raise ValueError("database is not configured")
        engine = create_engine(url, connect_args={"connect_timeout": 5})
        if engine.dialect.name != "postgresql":
            raise ValueError("operator command requires PostgreSQL")
        if args.apply:
            for _ in range(args.max_batches):
                with Session(engine) as db:
                    result = purge_expired_batch(db, batch_size=args.batch_size)
                if result.processed_sessions == 0:
                    break
                completed_batches += 1
                for name, count in result.counts().items():
                    counts[name] += count
        with Session(engine) as db:
            pending = pending_counts(db)
        print(
            json.dumps(
                {
                    "mode": "apply" if args.apply else "dry-run",
                    "completed_batches": completed_batches,
                    **counts,
                    **pending,
                },
                sort_keys=True,
            )
        )
        # Locked rows/batch limit are remaining work, never silently claim drained.
        return 2 if args.apply and pending["pending_sessions"] else 0
    except Exception:
        # Driver/Pydantic exceptions may contain DSNs or bind values. No traceback,
        # personal data or credentials; counts reflect only already committed work.
        print(
            json.dumps({"error": "raw_retention_failed", "completed_batches": completed_batches, **counts}),
            file=sys.stderr,
        )
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
