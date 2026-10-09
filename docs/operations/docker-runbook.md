# Local Docker operations runbook

## Routine commands

Start or rebuild the local stack:

```bash
docker compose up --build
```

Inspect service state and recent logs:

```bash
docker compose ps
docker compose logs --tail 100 api frontend postgres redis
```

Stop containers without deleting PostgreSQL data:

```bash
docker compose down
```

## Health troubleshooting

- PostgreSQL must become healthy before migrations and FastAPI start.
- FastAPI must answer `/api/v1/health/live` before Vite starts.
- Compose publishes Vite on host and container port `5173`. This avoids the
  `4173` range that Windows/Hyper-V can reserve dynamically.
- The API mounts the repository and Uvicorn reloads when a file under
  `backend/` changes. Rebuild the API only after dependency, Dockerfile, or
  runtime-configuration changes.
- A 404 at FastAPI `/` is expected; use the liveness path instead.
- If the browser receives HTML for an API request, confirm it was started through
  the repository Vite config and inspect the `api` and `frontend` logs.
- The `operator` service is an explicit tools profile for reviewed local audit and
  publication commands. It never runs during ordinary stack startup.

## Data safety

The named `postgres_data` volume persists local database state. Do not run
`docker compose down -v`, remove the volume, or reset migrations unless the exact
local target and data-loss impact have been reviewed and explicitly approved.
Never put production exports, database URLs, passwords, or tokens in the repo or
Compose logs.


## Profile access repair — US-09.T072

After update run `docker compose up -d --build api` to apply routes and the development mock flag. No new migration or data publication command; normal startup applies the existing profile migration. Staging/production profile access remains fail-closed pending real authentication.

401 after refresh/restart requires development login again. For 503, check DB readiness/migration and explicit local/test flag; never bypass ownership or treat browser storage as successful DB persistence. Disable flag/restart to invalidate access without deleting profiles. Do not roll back to PR #85's unprotected endpoints.
