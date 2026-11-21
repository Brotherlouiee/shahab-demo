# Project baseline — US-01.T01

## Scope

This checkpoint establishes a reproducible baseline for the existing React/Vite prototype. It intentionally makes no product, recommendation, database, authentication, or deployment change.

## Source state

- Repository: `Brotherlouiee/shahab-demo`
- Base branch/commit: `main` at `6f406146b9020bf20ea0ba786ee8f959400c307d`
- Working branch: `feature/us-01-project-baseline`
- Active task: `US-01.T01`

## Verified tooling

| Tool | Observed version | Baseline result |
| --- | --- | --- |
| Node.js | `v24.19.0` | Compatible with the prototype README requirement (`>=22.12`). |
| npm | `11.9.0` | `npm ci` completed from the committed lockfile. |
| Python | `3.12.14` | Available for later FastAPI work; no backend package was installed in this task. |
| uv | `0.12.15` | Available for later locked Python dependency management. |
| Docker / Compose | Not installed in this execution environment | Recorded as a local-development prerequisite; no Docker configuration is created in this task. |

## Dependency and build verification

1. Executed `npm ci` using the existing `package-lock.json`; 21 packages were installed.
2. Executed `npm run build` successfully with Vite `8.0.14`.
3. Build output is generated under `dist/`; the JavaScript bundle is approximately `291.25 kB` before gzip and the CSS bundle approximately `70.57 kB` before gzip.

## Existing test coverage and scripts

The current `package.json` provides only `dev`, `build`, and `preview` scripts. It contains no lint, typecheck, unit-test, integration-test, E2E, backend, migration, Docker, or CI script. This is an observed baseline, not an approval to skip those controls; they are introduced only in their assigned later tasks.

## Constraints and risks recorded

- The current workspace snapshot is not a Git checkout; GitHub is the authoritative repository state for commits and branches.
- `npm` reported a non-blocking `http-proxy` environment warning.
- The prototype currently uses `latest` ranges in `package.json`; the committed lockfile made this baseline reproducible today. Dependency pinning and security scanning are deferred to the architecture/CI task, where they can be reviewed as a deliberate change.
- Docker is unavailable in this execution environment. The future Docker requirement remains a blocker only for tasks that create or verify the containerized stack, not for this baseline build.

## Golden-rule attestation

1. This task is a single incremental baseline task; no deploy occurred.
2. The complete canonical guide was reread before execution.
3. The task is complete only with this record, the current-state checkpoint, a successful build, and a dedicated commit.
