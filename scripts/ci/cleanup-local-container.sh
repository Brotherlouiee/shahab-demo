#!/usr/bin/env bash
# Recovery step after cooperative cancellation; never clean another job's resources.
set -euo pipefail
: "${GITHUB_RUN_ID:?Missing workflow run identity}"
: "${GITHUB_RUN_ATTEMPT:?Missing workflow attempt identity}"
: "${GITHUB_JOB:?Missing job identity}"
owner_label="shahab.ci.owner=$GITHUB_RUN_ID-$GITHUB_RUN_ATTEMPT-$GITHUB_JOB"
ids=$(docker ps --all --quiet --filter "label=$owner_label")
if [[ -n "$ids" ]]; then
  mapfile -t containers <<< "$ids"
  docker rm -f -v "${containers[@]}"
fi
ids=$(docker network ls --quiet --filter "label=$owner_label")
if [[ -n "$ids" ]]; then
  mapfile -t networks <<< "$ids"
  docker network rm "${networks[@]}"
fi
