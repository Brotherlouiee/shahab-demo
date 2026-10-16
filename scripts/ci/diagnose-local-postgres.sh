#!/usr/bin/env bash
# Run from an isolated worktree; no GitHub workflow is dispatched.
set -euo pipefail
root=$(git rev-parse --show-toplevel)
cd "$root"
command -v timeout >/dev/null
if [[ -n "$(docker ps -q --filter name=shahab-ci.)" ]]; then
  echo 'An existing CI container is running. Stop here to avoid overlapping checks.' >&2
  exit 2
fi
scratch=$(mktemp -d)
export GITHUB_WORKSPACE="$root" RUNNER_TEMP="$scratch"
export RUNNER_TOOL_CACHE="${SHAHAB_DIAGNOSTIC_CACHE:-$HOME/actions-runner/_work/_tool}"
export GITHUB_RUN_ID="diagnostic-$(date +%s)-$$" GITHUB_RUN_ATTEMPT=1 GITHUB_JOB=cancel-probe
export SHAHAB_CI_DATABASE=''
cleanup() {
  local result=$?
  trap - EXIT INT TERM
  bash scripts/ci/cleanup-local-container.sh || result=1
  rm -rf -- "$scratch"
  exit "$result"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
export SHAHAB_CI_COMMANDS='echo DIAGNOSTIC_CANCEL_READY; sleep 90'
set +e
timeout --signal=TERM --kill-after=10s 20s bash scripts/ci/run-local-container.sh > "$scratch/cancel.log" 2>&1
cancel_status=$?
set -e
cat "$scratch/cancel.log"
[[ "$cancel_status" == 124 ]]
grep -q DIAGNOSTIC_CANCEL_READY "$scratch/cancel.log"
owner="label=shahab.ci.owner=$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT-$GITHUB_JOB"
[[ -z "$(docker ps -aq --filter "$owner")" ]]
[[ -z "$(docker network ls -q --filter "$owner")" ]]
echo 'DIAGNOSTIC cancellation passed: no owned containers or network remain'
export GITHUB_JOB=postgres-probe SHAHAB_CI_DATABASE=shahab_test
export SHAHAB_TEST_DATABASE_URL='postgresql+psycopg://shahab_test:test-password-not-a-secret@postgres:5432/shahab_test'
export SHAHAB_CI_COMMANDS='
started=$SECONDS
python -m pip install -e ".[test,quality]"
echo "DIAGNOSTIC install_seconds=$((SECONDS-started))"
PYTHONPATH=. python -u scripts/ci/profile-postgres-test.py
'
timeout --signal=TERM --kill-after=10s 240s bash scripts/ci/run-local-container.sh
