#!/usr/bin/env bash
# A/B the same real-API assertion with and without diagnostic tracing.
set -euo pipefail
mkdir -p test-results
python -u scripts/ci/record-ci-resources.py &
metrics_pid=$!
phase() {
  printf '%s\n' "$1" > /tmp/shahab-diagnostic-phase
  echo "DIAGNOSTIC_PHASE $1"
}
phase setup
npm ci
python -m alembic upgrade head
result=0
for trace in off retain-on-failure; do
  phase "swagger-trace-$trace"
  DEBUG=pw:browser npx playwright test tests/profile-live/api-documentation.spec.mjs \
    --config playwright.profile-live.config.mjs --trace="$trace" \
    --reporter=line --output="test-results/swagger-trace-$trace" || result=1
done
phase complete
kill "$metrics_pid"
wait "$metrics_pid" || true
exit "$result"
