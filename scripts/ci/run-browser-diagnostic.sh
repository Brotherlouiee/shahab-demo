#!/usr/bin/env bash
set -euo pipefail
mkdir -p test-results
python -u scripts/ci/record-ci-resources.py &
metrics_pid=$!
trap 'kill "$metrics_pid" 2>/dev/null || true; wait "$metrics_pid" || true' EXIT
printf '%s\n' postgresql > /tmp/shahab-diagnostic-phase
ruff check scripts/ci/run_postgresql_suites.py tests/ci/test_postgresql_suite_runner.py
python -m unittest discover -s tests/ci -p test_postgresql_suite_runner.py
python -m scripts.ci.run_postgresql_suites
printf '%s\n' swagger > /tmp/shahab-diagnostic-phase
python -m alembic upgrade head
npm ci
npx playwright test tests/profile-live/api-documentation.spec.mjs --config playwright.profile-live.config.mjs --repeat-each=2 --reporter=line --output=test-results/swagger
