"""Run one bounded retention tick; an external authorized scheduler owns cadence.

Default dry-run. All emitted records are count-only. No database, log, or
backup target is selected implicitly beyond the existing SHAHAB_DATABASE_URL.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from contextlib import redirect_stderr, redirect_stdout

from scripts.cleanup_questionnaire_sessions import main as cleanup_main

MAX_BATCHES_PER_TICK = 10
DEFAULT_BATCH_SIZE = 100


def tick(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="explicitly authorize deletion of expired raw answers")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--max-batches", type=int, default=MAX_BATCHES_PER_TICK)
    args = parser.parse_args(argv)
    if isinstance(args.batch_size, bool) or not 1 <= args.batch_size <= 1000:
        parser.error("batch-size must be 1..1000")
    if not 1 <= args.max_batches <= MAX_BATCHES_PER_TICK:
        parser.error("max-batches must be 1..10")

    output = io.StringIO()
    errors = io.StringIO()
    command = ["--batch-size", str(args.batch_size), "--max-batches", str(args.max_batches)]
    if args.apply:
        command.insert(0, "--apply")

    try:
        with redirect_stdout(output), redirect_stderr(errors):
            result = cleanup_main(command)
        source = output.getvalue() if result in (0, 2) else errors.getvalue()
        payload = json.loads(source)
        permitted = (
            "completed_batches",
            "processed_sessions",
            "deleted_answers",
            "deleted_sessions",
            "retained_sessions",
            "pending_sessions",
            "pending_answers",
        )
        metrics = {name: value for name in permitted if isinstance((value := payload.get(name)), int)}
        if result not in (0, 2):
            print(
                json.dumps({"event": "retention_tick_failed", "completed_batches": metrics.get("completed_batches", 0)})
            )
            return 1
        event = "retention_tick_backlog" if result == 2 else "retention_tick_complete"
        print(json.dumps({"event": event, "mode": "apply" if args.apply else "dry-run", **metrics}, sort_keys=True))
        return result
    except Exception:  # Driver/runtime messages may embed credentials; never relay them.
        print(json.dumps({"event": "retention_tick_failed"}))
        return 1


if __name__ == "__main__":
    sys.exit(tick())
