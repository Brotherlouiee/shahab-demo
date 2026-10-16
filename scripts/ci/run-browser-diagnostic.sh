#!/usr/bin/env bash
set -euo pipefail
mkdir -p test-results
python -u scripts/ci/record-ci-resources.py &
metrics_pid=$!
trap 'kill "$metrics_pid" 2>/dev/null || true; wait "$metrics_pid" || true' EXIT
phase() { printf '%s\n' "$1" > /tmp/shahab-diagnostic-phase; echo "DIAGNOSTIC_PHASE $1"; }
phase setup
npm ci
python -m alembic upgrade head
result=0
phase swagger
npx playwright test tests/profile-live/api-documentation.spec.mjs --config playwright.profile-live.config.mjs --repeat-each=2 --reporter=line --output=test-results/swagger || result=1
phase reload
npx playwright test tests/e2e/us-09-t06n-detail-performance.spec.mjs --grep 'refresh never renders' --repeat-each=2 --reporter=line --output=test-results/reload || result=1
# All Python servers from the completed phase have exited; release only this job's venv.
rm -rf /tmp/shahab-job-python
phase build
export SHAHAB_US13_BASELINE_DIR=/tmp/shahab-us13-original
export SHAHAB_US13_BASELINE_URL=http://127.0.0.1:4177
git fetch --no-tags --depth=1 origin f5e50da0ea29b7d933a813736a2616169ee9b8f3
git worktree add --detach "$SHAHAB_US13_BASELINE_DIR" f5e50da0ea29b7d933a813736a2616169ee9b8f3
ln -s "$GITHUB_WORKSPACE/node_modules" "$SHAHAB_US13_BASELINE_DIR/node_modules"
npm run build
npm --prefix "$SHAHAB_US13_BASELINE_DIR" run build
phase built-baseline
SHAHAB_E2E_BUILT=1 npx playwright test tests/e2e/us13-baseline-inventory.spec.mjs --repeat-each=2 --reporter=line --output=test-results/baseline || result=1
phase complete
exit "$result"
