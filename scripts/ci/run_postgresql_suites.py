"""Run the existing PostgreSQL suites in isolated disposable CI databases."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit
from uuid import uuid4

MODULES = (
    "backend.tests.test_postgresql_migrations",
    "backend.tests.test_account_identity_postgresql",
    "backend.tests.test_questionnaire_proof_postgresql",
    "backend.tests.test_account_access_postgresql",
    "backend.tests.test_questionnaire_retention_postgresql",
    "backend.tests.test_account_bookmarks_postgresql",
    "backend.tests.test_t06_postgresql",
    "backend.tests.test_operations_postgresql",
    "backend.tests.test_operations_tool_postgresql",
)


def validate_database(environment: dict[str, str]) -> str:
    """Refuse to provision databases outside the existing disposable CI service."""
    value = environment.get("SHAHAB_TEST_DATABASE_URL", "")
    parsed = urlsplit(value)
    owned = environment.get("SHAHAB_CI_DATABASE", "")
    if (
        environment.get("CI") != "true"
        or not owned.startswith("shahab_")
        or parsed.scheme != "postgresql+psycopg"
        or parsed.hostname != "postgres"
        or parsed.port not in (None, 5432)
        or parsed.path != "/" + owned
    ):
        raise ValueError("requires the owned disposable PostgreSQL CI service")
    return value


def database_url(value: str, name: str) -> str:
    if not re.fullmatch(r"shahab_ci_pg_[a-f0-9]{12}_[0-8]", name):
        raise ValueError("invalid owned worker database name")
    return urlunsplit(urlsplit(value)._replace(path="/" + name))


@dataclass(frozen=True)
class Outcome:
    module: str
    succeeded: bool
    count: int
    seconds: float
    output: str


def verify_output(returncode: int, output: str) -> tuple[bool, int]:
    count = re.search(r"Ran (\d+) tests? in", output)
    skipped = re.search(r"skipped=(\d+)", output)
    total = int(count.group(1)) if count else 0
    return returncode == 0 and total > 0 and not (skipped and int(skipped.group(1))), total


def run_suite(module: str, name: str, parent_environment: dict[str, str]) -> Outcome:
    import psycopg
    from psycopg import sql

    started = time.monotonic()
    admin_url = validate_database(parent_environment)
    target_url = database_url(admin_url, name)
    admin_dsn = admin_url.replace("postgresql+psycopg://", "postgresql://", 1)
    with psycopg.connect(admin_dsn, autocommit=True) as connection:
        connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(name)))
    try:
        environment = {
            **parent_environment,
            "SHAHAB_TEST_DATABASE_URL": target_url,
            "SHAHAB_DATABASE_URL": target_url,
        }
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "-v", module],
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        succeeded, count = verify_output(result.returncode, result.stdout)
        return Outcome(module, succeeded, count, time.monotonic() - started, result.stdout)
    finally:
        with psycopg.connect(admin_dsn, autocommit=True) as connection:
            connection.execute(sql.SQL("DROP DATABASE {}").format(sql.Identifier(name)))


def main() -> int:
    environment = dict(os.environ)
    validate_database(environment)
    started = time.monotonic()
    prefix = "shahab_ci_pg_" + uuid4().hex[:12]
    outcomes = []
    failed = False
    # Every module owns a different DB; each module's internal race tests remain unchanged.
    with ThreadPoolExecutor(max_workers=2) as executor:
        pending = {
            executor.submit(run_suite, module, f"{prefix}_{index}", environment): module
            for index, module in enumerate(MODULES)
        }
        for future in as_completed(pending):
            module = pending[future]
            try:
                outcome = future.result()
            except Exception:
                # Preserve the diagnostic traceback; provisioning/cleanup failure fails the gate.
                import traceback

                traceback.print_exc()
                failed = True
                continue
            outcomes.append(outcome)
            print(f"::group::{module}", flush=True)
            print(outcome.output, flush=True)
            print(
                f"PG_SUITE module={module} tests={outcome.count} "
                f"seconds={outcome.seconds:.3f} success={outcome.succeeded}",
                flush=True,
            )
            print("::endgroup::", flush=True)
            failed |= not outcome.succeeded
    total = sum(item.count for item in outcomes)
    print(
        f"PG_TOTAL suites={len(outcomes)}/{len(MODULES)} tests={total} "
        f"seconds={time.monotonic() - started:.3f}",
        flush=True,
    )
    return int(failed or len(outcomes) != len(MODULES))


if __name__ == "__main__":
    raise SystemExit(main())
