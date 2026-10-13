"""US-11.T05 bounded retention tick contracts; PostgreSQL behavior tested separately."""

import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from scripts.retention_tick import tick


class RetentionTickTests(unittest.TestCase):
    def invoke(self, cli_result, payload, argv=None):
        output = io.StringIO()

        def fake_main(args):
            print(json.dumps(payload))
            return cli_result

        with (
            patch("scripts.retention_tick.cleanup_main", side_effect=fake_main) as mocked,
            redirect_stdout(output),
        ):
            status = tick(argv if argv is not None else [])
        return status, json.loads(output.getvalue()), mocked

    def test_default_dry_run_never_passes_apply(self):
        code, out, mocked = self.invoke(
            0,
            {"mode": "dry-run", "completed_batches": 0, "pending_sessions": 2, "pending_answers": 3},
        )
        self.assertEqual(code, 0)
        self.assertEqual(out["event"], "retention_tick_complete")
        self.assertNotIn("--apply", mocked.call_args.args[0])
        self.assertEqual(out["pending_answers"], 3)

    def test_explicit_apply_and_pending_backlog_keep_exit_two(self):
        code, out, mocked = self.invoke(
            2,
            {"completed_batches": 10, "processed_sessions": 1000, "pending_sessions": 3},
            ["--apply", "--max-batches", "10"],
        )
        self.assertEqual(code, 2)
        self.assertEqual(out["event"], "retention_tick_backlog")
        self.assertIn("--apply", mocked.call_args.args[0])

    def test_failed_execution_never_prints_secret_or_traceback(self):
        code, out, _ = self.invoke(1, {"error": "private DSN password", "completed_batches": 1})
        self.assertEqual(code, 1)
        self.assertEqual(out, {"event": "retention_tick_failed", "completed_batches": 1})

    def test_no_raw_exception_or_payload_leak(self):
        output = io.StringIO()
        with (
            patch("scripts.retention_tick.cleanup_main", side_effect=ValueError("raw private answer")),
            redirect_stdout(output),
        ):
            status = tick([])
        self.assertEqual(status, 1)
        self.assertNotIn("raw private answer", output.getvalue())
        self.assertEqual(json.loads(output.getvalue())["event"], "retention_tick_failed")

    def test_max_batches_restricted_for_one_tick(self):
        with self.assertRaises(SystemExit):
            tick(["--max-batches", "11"])
