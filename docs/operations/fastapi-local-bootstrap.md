# FastAPI local bootstrap — US-03.T02

Install the locked project dependencies in an isolated environment:

```bash
python -m pip install -e .
uvicorn backend.app.main:app --reload
```

Configuration uses `SHAHAB_` variables. Example non-secret local settings:

```bash
export SHAHAB_ENVIRONMENT=local
export SHAHAB_LOG_LEVEL=INFO
```

Do not place credentials, OTPs, tokens, authorization headers or API keys in source, `.env.example`, logs, test fixtures or command history. Production disables interactive OpenAPI documentation by default. Health/readiness routes are intentionally deferred to `US-03.T04`.
