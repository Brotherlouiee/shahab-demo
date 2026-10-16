#!/usr/bin/env bash
set -euo pipefail
mkdir -p test-results
python -u scripts/ci/record-ci-resources.py &
metrics_pid=$!
trap 'kill "$metrics_pid" 2>/dev/null || true; wait "$metrics_pid" || true' EXIT
npm ci
result=0
printf '%s\n' reload > /tmp/shahab-diagnostic-phase
DEBUG=pw:browser npx playwright test tests/e2e/us-09-t06n-detail-performance.spec.mjs --grep 'refresh never renders' --reporter=line --output=test-results/reload || result=1
export SHAHAB_US13_BASELINE_DIR=/tmp/shahab-us13-original
export SHAHAB_US13_BASELINE_URL=http://127.0.0.1:4177
git fetch --no-tags --depth=1 origin f5e50da0ea29b7d933a813736a2616169ee9b8f3
git worktree add --detach "$SHAHAB_US13_BASELINE_DIR" f5e50da0ea29b7d933a813736a2616169ee9b8f3
ln -s "$GITHUB_WORKSPACE/node_modules" "$SHAHAB_US13_BASELINE_DIR/node_modules"
printf '%s\n' baseline > /tmp/shahab-diagnostic-phase
DEBUG=pw:browser npx playwright test tests/e2e/us13-baseline-inventory.spec.mjs --reporter=line --output=test-results/baseline || result=1
exit "$result"
