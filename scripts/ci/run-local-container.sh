#!/usr/bin/env bash
# Run trusted repository checks without pulling or modifying the host application.
set -euo pipefail

: "${GITHUB_WORKSPACE:?Run from a checked-out Actions workspace}"
: "${RUNNER_TEMP:?Missing runner temporary directory}"
: "${RUNNER_TOOL_CACHE:?Missing runner cache directory}"
: "${SHAHAB_CI_COMMANDS:?Missing verification commands}"

image=shahab-ci:local-v1
database=${SHAHAB_CI_DATABASE:-}
case "$database" in
  ''|shahab_test|shahab_profile_test) ;;
  *) echo 'Unsupported disposable database name' >&2; exit 2 ;;
esac
docker image inspect "$image" >/dev/null
if [[ -n "$database" ]]; then
  docker image inspect postgres:16-alpine >/dev/null
fi

task_dir=$(mktemp -d "$RUNNER_TEMP/shahab-ci.XXXXXXXXXX")
token=${task_dir##*/}
network="${token}-network"
job_container="${token}-checks"
db_container="${token}-postgres"
network_created=false
cleanup() {
  local result=$?
  trap - EXIT INT TERM
  docker rm -f -v "$job_container" >/dev/null 2>&1 || true
  if [[ -n "$database" ]]; then
    docker rm -f -v "$db_container" >/dev/null 2>&1 || true
  fi
  if [[ "$network_created" == true ]]; then
    docker network rm "$network" >/dev/null 2>&1 || true
  fi
  rm -f "$task_dir/commands.sh"
  rmdir "$task_dir"
  exit "$result"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

cache_dir="$RUNNER_TOOL_CACHE/shahab-ci-v1"
mkdir -p "$cache_dir/npm" "$cache_dir/pip"
docker network create "$network" >/dev/null
network_created=true
if [[ -n "$database" ]]; then
  docker run --detach --rm --pull=never --name "$db_container" \
    --network "$network" --network-alias postgres \
    --env "POSTGRES_DB=$database" --env POSTGRES_USER=shahab_test \
    --env POSTGRES_PASSWORD=test-password-not-a-secret \
    --health-cmd "pg_isready -U shahab_test -d $database" \
    --health-interval 5s --health-timeout 3s --health-retries 20 \
    postgres:16-alpine >/dev/null
  healthy=false
  for ((attempt=0; attempt<60; attempt++)); do
    status=$(docker inspect --format '{{.State.Health.Status}}' "$db_container")
    if [[ "$status" == healthy ]]; then healthy=true; break; fi
    if [[ "$status" == unhealthy ]]; then break; fi
    sleep 2
  done
  if [[ "$healthy" != true ]]; then
    docker logs "$db_container" >&2
    echo 'Disposable PostgreSQL did not become ready' >&2
    exit 1
  fi
fi

cat > "$task_dir/commands.sh" <<'BOOTSTRAP'
set -euo pipefail
mkdir -p "$HOME"
git config --global --add safe.directory "$GITHUB_WORKSPACE"
git worktree prune
python3 -m venv /tmp/shahab-job-python
export PATH="/tmp/shahab-job-python/bin:$PATH"
python -c 'import sys; assert sys.version_info[:2] == (3, 12), sys.version'
node -e 'if (process.version !== "v22.23.3") process.exit(1); if (require("/usr/local/lib/node_modules/playwright/package.json").version !== "1.63.0") process.exit(1);'
node --version
python --version
BOOTSTRAP
printf '\n%s\n' "$SHAHAB_CI_COMMANDS" >> "$task_dir/commands.sh"
env_args=()
for key in SHAHAB_TEST_DATABASE_URL SHAHAB_DATABASE_URL SHAHAB_ENVIRONMENT \
  SHAHAB_API_DOCS_INCLUDE_OPERATIONS SHAHAB_BOOKMARK_BASELINE_DIR \
  SHAHAB_BOOKMARK_BASELINE_URL SHAHAB_US13_BASELINE_DIR SHAHAB_US13_BASELINE_URL; do
  if [[ -v "$key" ]]; then env_args+=(--env "$key"); fi
done

docker run --rm --pull=never --init --name "$job_container" \
  --user "$(id -u):$(id -g)" --network "$network" --shm-size=1g \
  --mount "type=bind,source=$GITHUB_WORKSPACE,target=/workspace" \
  --mount "type=bind,source=$task_dir/commands.sh,target=/ci-commands.sh,readonly" \
  --mount "type=bind,source=$cache_dir,target=/ci-cache" \
  --workdir /workspace --env CI=true --env GITHUB_WORKSPACE=/workspace \
  --env HOME=/tmp/shahab-ci-home --env npm_config_cache=/ci-cache/npm \
  --env PIP_CACHE_DIR=/ci-cache/pip --env PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 \
  --env SHAHAB_E2E_BROWSER_PATH=/opt/chrome/chrome-linux64/chrome \
  "${env_args[@]}" "$image" bash /ci-commands.sh
