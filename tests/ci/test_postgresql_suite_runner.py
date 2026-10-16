"""Safety and failure propagation for the isolated PostgreSQL CI scheduler."""

import contextlib
import io
import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from scripts.ci import run_postgresql_suites as runner


class PostgreSqlSuiteRunnerTests(unittest.TestCase):
    def environment(self):
        return {
            "CI": "true",
            "SHAHAB_CI_DATABASE": "shahab_test",
            "SHAHAB_TEST_DATABASE_URL": "postgresql+psycopg://runner@postgres/shahab_test",
        }

    def test_refuses_non_ci_remote_and_mismatched_database_targets(self):
        for update in (
            {"CI": "false"},
            {"SHAHAB_CI_DATABASE": ""},
            {"SHAHAB_TEST_DATABASE_URL": "postgresql+psycopg://runner@example.com/shahab_test"},
            {"SHAHAB_TEST_DATABASE_URL": "postgresql+psycopg://runner@postgres/another_database"},
        ):
            with self.subTest(update=update), self.assertRaises(ValueError):
                runner.validate_database({**self.environment(), **update})

    def test_only_generated_worker_names_can_replace_the_database(self):
        url = runner.validate_database(self.environment())
        with self.assertRaises(ValueError):
            runner.database_url(url, "shahab_test")
        with self.assertRaises(ValueError):
            runner.database_url(url, 'shahab_ci_pg_bad;DROP DATABASE postgres')
        self.assertEqual(
            runner.database_url(url, "shahab_ci_pg_012345abcdef_0"),
            "postgresql+psycopg://runner@postgres/shahab_ci_pg_012345abcdef_0",
        )

    def test_success_requires_real_tests_without_skips_or_process_failure(self):
        for status, output in (
            (1, "Ran 3 tests in 1s\nFAILED"),
            (0, "Ran 0 tests in 1s\nOK"),
            (0, "Ran 3 tests in 1s\nOK (skipped=1)"),
            (0, "no tests ran"),
        ):
            with self.subTest(status=status, output=output):
                self.assertFalse(runner.verify_output(status, output)[0])
        self.assertEqual(runner.verify_output(0, "Ran 3 tests in 1s\nOK"), (True, 3))

    def test_scheduler_runs_every_suite_once_with_two_workers_and_propagates_failure(self):
        lock = threading.Lock()
        active = peak = 0
        seen = []

        def task(module, name, environment):
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
                seen.append((module, name))
            time.sleep(0.01)
            with lock:
                active -= 1
            return runner.Outcome(module, module != runner.MODULES[2], 1, 0.01, "fixture")

        with (
            patch.dict(runner.os.environ, self.environment(), clear=True),
            patch.object(runner, "run_suite", task),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(runner.main(), 1)
        self.assertEqual(sorted(module for module, _ in seen), sorted(runner.MODULES))
        self.assertEqual(len({name for _, name in seen}), len(runner.MODULES))
        self.assertEqual(peak, 2)

    def test_worker_cleanup_survives_failed_or_crashed_child_and_preserves_parent_database(self):
        for crashes in (False, True):
            connection = MagicMock()
            connection.__enter__.return_value = connection
            sql = SimpleNamespace(
                SQL=lambda text: SimpleNamespace(format=lambda name: text.format(name)),
                Identifier=lambda name: name,
            )
            driver = SimpleNamespace(connect=MagicMock(return_value=connection), sql=sql)
            parent = self.environment()
            name = "shahab_ci_pg_012345abcdef_0"
            result = SimpleNamespace(returncode=1, stdout="Ran 3 tests in 1s\nFAILED")
            with (
                self.subTest(crashes=crashes),
                patch.dict(runner.sys.modules, {"psycopg": driver}),
                patch.object(runner.subprocess, "run", return_value=result) as child,
            ):
                if crashes:
                    child.side_effect = RuntimeError("child could not start")
                    with self.assertRaises(RuntimeError):
                        runner.run_suite(runner.MODULES[0], name, parent)
                else:
                    outcome = runner.run_suite(runner.MODULES[0], name, parent)
                    self.assertFalse(outcome.succeeded)
                    self.assertEqual(outcome.count, 3)
                self.assertEqual(
                    [call.args[0] for call in connection.execute.call_args_list],
                    [f"CREATE DATABASE {name}", f"DROP DATABASE {name}"],
                )
                self.assertTrue(child.call_args.kwargs["env"]["SHAHAB_TEST_DATABASE_URL"].endswith("/" + name))
                self.assertTrue(parent["SHAHAB_TEST_DATABASE_URL"].endswith("/shahab_test"))


if __name__ == "__main__":
    unittest.main()
