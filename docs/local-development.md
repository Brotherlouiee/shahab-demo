# Local full-stack development

The supported local stack is Vite, FastAPI, PostgreSQL, and Redis under Docker
Compose. Docker Desktop (with Compose v2), Node.js 22+, and Git are required.

## Start

1. Copy `.env.example` to the ignored `.env` file and replace the local-only
   placeholder password and readiness token. Never commit `.env`.
2. Start the stack from the repository root:

   ```bash
   docker compose up --build
   ```

3. Open `http://localhost:4173/`. Browser requests to `/api/v1` stay
   same-origin and Vite proxies them to FastAPI inside the Compose network.

## Publish the verified local catalogue

On a new local PostgreSQL volume, first inspect the migrated database without
writing serving data:

```bash
docker compose --profile tools run --rm operator python -m scripts.materialize_t05a
```

Confirm the inventory is empty and matches the reviewed official-source audit,
then explicitly publish the verified local catalogue:

```bash
docker compose --profile tools run --rm operator python -m scripts.materialize_t05a \
  --publish \
  --actor-reference local-developer \
  --approval-reason "Reviewed empty local database and official source audit"
```

This operator profile mounts only the required source/config/script directories
read-only. It is not started by ordinary `docker compose up`, and it does not
expose PostgreSQL outside the Compose network.

## Verify

The public liveness endpoint is available both directly and through Vite:

```bash
curl http://127.0.0.1:8000/api/v1/health/live
curl http://127.0.0.1:4173/api/v1/health/live
```

Both must return JSON containing `{"status":"ok"}`. Opening
`http://localhost:8000/` is expected to return 404 because FastAPI intentionally
has no root route.

Run focused local checks with:

```bash
npm run test:vite-proxy
npm run build
```

After the catalogue is published, the opt-in browser check exercises the real
questionnaire, proxied API, recommendation result, and loan-detail route. Playwright
uses its managed Chromium by default:

```powershell
$env:SHAHAB_LIVE_E2E = "1"
npx playwright test tests/e2e/local-fullstack-live.spec.mjs
```

If the Playwright browser CDN is unavailable, point the check at an already
installed Chromium-compatible browser without committing that machine-specific
path:

```powershell
$env:SHAHAB_E2E_BROWSER_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
npx playwright test tests/e2e/local-fullstack-live.spec.mjs
```

On Windows, set `PYTHONUTF8=1` for host-run Python checks so canonical UTF-8
contracts are not decoded with the legacy system code page:

```powershell
$env:PYTHONUTF8 = "1"
npm run quality
```

## Host-run Vite

When FastAPI is already reachable at `127.0.0.1:8000`, `npm run dev` uses that
address by default. To use another local API, set `VITE_DEV_API_PROXY_TARGET` in
the process environment. This value is development-only and must never contain
credentials.

## Stop safely

Use `docker compose down` to stop the stack while preserving PostgreSQL data.
See [the Docker runbook](operations/docker-runbook.md) before any reset.
