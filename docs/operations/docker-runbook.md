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
