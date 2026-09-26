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

## Recommendation integration prerequisite

The API currently has questionnaire sessions and published-loan detail routes, but no live recommendation route. A usable local or preview result requires an approved configuration, a published serving catalogue with normalized categories and conditions, and a durable read adapter. Starting FastAPI alone cannot provide real matches. Keep the anonymous session ID in active-tab memory and the recommendation request body; configure the API origin explicitly for any later preview. This checkpoint performs no deployment.
