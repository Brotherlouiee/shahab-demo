#!/usr/bin/env bash
# Target the failures of 6117ebf9; this does not replace the six required gates.
set -euo pipefail
mkdir -p test-results
python -u scripts/ci/record-ci-resources.py &
metrics_pid=$!
phase() {
  printf '%s\n' "$1" > /tmp/shahab-diagnostic-phase
  echo "DIAGNOSTIC_PHASE $1"
}
phase setup
"$SHAHAB_E2E_BROWSER_PATH" --version
npm ci
python -m alembic upgrade head
result=0

phase profile
DEBUG=pw:browser npx playwright test \
  tests/profile-live/api-documentation.spec.mjs tests/profile-live/bookmarks-account.spec.mjs \
  --config playwright.profile-live.config.mjs \
  --grep 'Swagger lists every operation|two devices share database bookmarks' \
  --reporter=line --output=test-results/diagnostic-profile || result=1

phase frontend-fixtures
export SHAHAB_BOOKMARK_BASELINE_DIR=/tmp/shahab-bookmark-baseline
export SHAHAB_BOOKMARK_BASELINE_URL=http://127.0.0.1:4175
git fetch --no-tags --depth=1 origin d4197e94b24da8cb91e277a7cb1d82be936bbd07
git worktree add --detach "$SHAHAB_BOOKMARK_BASELINE_DIR" d4197e94b24da8cb91e277a7cb1d82be936bbd07
ln -s "$GITHUB_WORKSPACE/node_modules" "$SHAHAB_BOOKMARK_BASELINE_DIR/node_modules"
DEBUG=pw:browser npx playwright test \
  tests/e2e/bookmarks-visual-preservation.spec.mjs \
  tests/e2e/initial-and-questionnaire-loading.spec.mjs \
  tests/e2e/live-recommendation-route.spec.mjs tests/e2e/questionnaire-route-map.spec.mjs \
  --grep 'empty artwork|document fallback|detail-shaped|keeps card identity|preserves every approved behavioural path' \
  --workers=2 --reporter=line --output=test-results/diagnostic-frontend || result=1

phase frozen-baseline
unset SHAHAB_BOOKMARK_BASELINE_DIR SHAHAB_BOOKMARK_BASELINE_URL
export SHAHAB_US13_BASELINE_DIR=/tmp/shahab-us13-original
export SHAHAB_US13_BASELINE_URL=http://127.0.0.1:4177
git fetch --no-tags --depth=1 origin f5e50da0ea29b7d933a813736a2616169ee9b8f3
git worktree add --detach "$SHAHAB_US13_BASELINE_DIR" f5e50da0ea29b7d933a813736a2616169ee9b8f3
ln -s "$GITHUB_WORKSPACE/node_modules" "$SHAHAB_US13_BASELINE_DIR/node_modules"
DEBUG=pw:browser npx playwright test tests/e2e/us13-baseline-inventory.spec.mjs \
  --grep 'freeze initial user-visible routes' --workers=1 \
  --reporter=line --output=test-results/diagnostic-baseline || result=1
phase complete
kill "$metrics_pid"
wait "$metrics_pid" || true
exit "$result"
