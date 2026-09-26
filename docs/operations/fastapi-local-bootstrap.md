# FastAPI local bootstrap — US-03.T02

Install the locked project dependencies in an isolated environment:

```bash
python -m pip install -e ".[test]"
uvicorn backend.app.main:app --reload
```

Configuration uses `SHAHAB_` variables. Example non-secret local settings:

```bash
export SHAHAB_ENVIRONMENT=local
export SHAHAB_LOG_LEVEL=INFO
```

To enable the restricted readiness endpoint locally, provide its value only through the process environment:

```bash
export SHAHAB_READINESS_TOKEN='replace-with-a-local-secret'
curl -H "X-Shahab-Readiness-Token: $SHAHAB_READINESS_TOKEN" http://127.0.0.1:8000/api/v1/health/ready
```

Do not place credentials, OTPs, tokens, authorization headers or API keys in source, `.env.example`, logs, test fixtures or command history. Production disables interactive OpenAPI documentation by default. `/api/v1/health/live` exposes only process liveness; `/api/v1/health/ready` is unavailable unless its environment secret is configured.

## Local recommendation integration after US-09.T06

The live `POST /api/v1/recommendations` route accepts only the opaque `sessionId`
from an active, complete questionnaire session. It resolves the session answers on
the server and calculates results from the approved recommendation configuration
and the active `PUBLISHED` serving catalogue in PostgreSQL. The browser does not
send raw answers, weights, scores, or catalogue selectors to this route.

A usable local result therefore requires more than starting Uvicorn: configure
`SHAHAB_DATABASE_URL`, apply all Alembic migrations, and make sure the database
contains the approved canonical impacts plus one active published catalogue with
its normalized categories and loan details. Questionnaire session persistence
also uses PostgreSQL; configure `SHAHAB_REDIS_URL` when exercising the supported
Redis cache path. If the session is missing, expired, or incomplete, the route
returns its typed client error. If the approved snapshot or serving catalogue is
missing or inconsistent, it fails closed with `503` rather than inventing a
recommendation.

Keep `.env` local and ignored, retain the anonymous session ID only in active-tab
memory, and send it only in the recommendation request body. Configure the
frontend to reach the local `/api/v1` origin; never put database credentials or a
service secret in the Vite client bundle. This local setup is not evidence of a
deployed staging or production service.
