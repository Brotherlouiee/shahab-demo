#!/usr/bin/env bash
set -euo pipefail
mkdir -p test-results
python -u scripts/ci/record-ci-resources.py &
metrics_pid=$!
trap 'kill "$metrics_pid" 2>/dev/null || true; wait "$metrics_pid" || true' EXIT
phase() { printf '%s\n' "$1" > /tmp/shahab-diagnostic-phase; echo "DIAGNOSTIC_PHASE $1"; }
phase setup
npm ci
export SHAHAB_BOOKMARK_BASELINE_DIR=/tmp/shahab-bookmark-baseline
export SHAHAB_BOOKMARK_BASELINE_URL=http://127.0.0.1:4175
git fetch --no-tags --depth=1 origin d4197e94b24da8cb91e277a7cb1d82be936bbd07
git worktree add --detach "$SHAHAB_BOOKMARK_BASELINE_DIR" d4197e94b24da8cb91e277a7cb1d82be936bbd07
ln -s "$GITHUB_WORKSPACE/node_modules" "$SHAHAB_BOOKMARK_BASELINE_DIR/node_modules"
npm run build
npm --prefix "$SHAHAB_BOOKMARK_BASELINE_DIR" run build
phase discovery
npx playwright test --list --reporter=json > test-results/e2e-original-list.json
SHAHAB_E2E_BUILT=1 npx playwright test --list --reporter=json > test-results/e2e-built-list.json
npx playwright test tests/e2e/initial-and-questionnaire-loading.spec.mjs tests/e2e/recommendation-result-journey.spec.mjs --list --reporter=json > test-results/e2e-development-list.json
node scripts/ci/verify_e2e_partition.mjs test-results/e2e-original-list.json test-results/e2e-built-list.json test-results/e2e-development-list.json
phase built
SHAHAB_E2E_BUILT=1 npx playwright test --reporter=line --output=test-results/built
phase development
env -u SHAHAB_BOOKMARK_BASELINE_DIR -u SHAHAB_BOOKMARK_BASELINE_URL npx playwright test tests/e2e/initial-and-questionnaire-loading.spec.mjs tests/e2e/recommendation-result-journey.spec.mjs --reporter=line --output=test-results/development
phase complete
