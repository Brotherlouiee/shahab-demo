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

3. Open `http://localhost:5173/`. Browser requests to `/api/v1` stay
   same-origin and Vite proxies them to FastAPI inside the Compose network.

The Compose development stack mounts the repository into both Vite and FastAPI.
Frontend changes use Vite hot reload; backend changes under `backend/` restart
Uvicorn automatically. A full image rebuild is only needed after changing
Python dependencies, the Dockerfile, or the database/runtime configuration.

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
curl http://127.0.0.1:5173/api/v1/health/live
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


## Profile development access — US-09.T072

Development Compose passes SHAHAB_PROFILE_MOCK_OTP_ENABLED (default true for the local stack). Direct API execution requires explicit SHAHAB_PROFILE_MOCK_OTP_ENABLED=true with local/test environment. The existing demo code is ۱۲۳۴۵۶; no SMS is sent. Staging/production always reject this mock. Never configure a public production deployment as local.

After code update, recreate API with `docker compose up -d --build api`. Existing migration d1a9e71b4c3f supplies user_profiles; no new migration or publication command. Refresh/API restart requires development login before protected profile operations; DB records survive restart. Personal-info now persists before analysis, and failures remain visible/retryable. See ADR 0010.

## ابزار داخلی US-10.T04

python -m scripts.operations_tool --command /private/command.json؛ نیازمند
authority HTTPS معتبر مستقل و PostgreSQL account غیرمالک است. OTP فیک کاربر
جای آن نیست. secrets از محیط خصوصی، نه argument/command.json. راهنمای کامل
در operations/protected-tool.md؛ هیچ سرویس/port/dependency جدیدی ندارد.
