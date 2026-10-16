"""Measure one existing migration test against the wrapper's disposable database."""

import os
import time
import unittest

started = time.perf_counter()
from sqlalchemy import create_engine, text
from backend.tests.test_postgresql_migrations import PostgreSqlMigrationTests

print(f"DIAGNOSTIC imports_seconds={time.perf_counter() - started:.3f}", flush=True)
engine = create_engine(os.environ["SHAHAB_TEST_DATABASE_URL"])
with engine.connect() as connection:
    for setting in ("fsync", "synchronous_commit", "full_page_writes"):
        print(f"DIAGNOSTIC {setting}={connection.execute(text('SHOW ' + setting)).scalar_one()}", flush=True)
started = time.perf_counter()
for _ in range(20):
    with engine.begin() as connection:
        connection.execute(text("CREATE TEMP TABLE diagnostic_probe (value integer) ON COMMIT DROP"))
        connection.execute(text("INSERT INTO diagnostic_probe VALUES (1)"))
print(f"DIAGNOSTIC twenty_transactions_seconds={time.perf_counter() - started:.3f}", flush=True)
engine.dispose()
original = PostgreSqlMigrationTests._alembic


def measured(self, *arguments, **kwargs):
    started = time.perf_counter()
    try:
        return original(self, *arguments, **kwargs)
    finally:
        print(f"DIAGNOSTIC alembic={arguments!r} seconds={time.perf_counter() - started:.3f}", flush=True)


PostgreSqlMigrationTests._alembic = measured
suite = unittest.TestSuite([PostgreSqlMigrationTests("test_upgrade_fixture_and_downgrade")])
result = unittest.TextTestRunner(verbosity=2).run(suite)
raise SystemExit(0 if result.wasSuccessful() and not result.skipped else 1)
