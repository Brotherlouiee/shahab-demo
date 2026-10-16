#!/usr/bin/env bash
set -euo pipefail
mkdir -p test-results
ruff format --check scripts/ci/run_postgresql_suites.py || { ruff format --diff scripts/ci/run_postgresql_suites.py; exit 1; }
ruff check scripts/ci/run_postgresql_suites.py tests/ci/test_postgresql_suite_runner.py
node --test tests/ci/local-container.test.mjs tests/ci/e2e-partition.test.mjs
python -m unittest discover -s tests/ci -p test_postgresql_suite_runner.py
python scripts/scan_repository_secrets.py
