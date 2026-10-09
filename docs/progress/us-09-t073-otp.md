# US-09.T073 — Local OTP routing and configuration repair

Start: 2026-10-09. Codex-owned branch from merged main 377f746aab318c1b2703fa7404e48a7ec7059797; API Git transport used because the local tree is a partial test snapshot. Full canonical guide retained/read in the previous task; current main incorporates only the known reviewed additions. Three golden rules: bounded repair, canonical source, evidence before Done.

Reproduction: default local Settings without the newly introduced environment flag returns 503 at POST /api/v1/account-access/request. Old Compose containers retain their environment even after mounted Python files reload. Both UI forms use that route. Separate defect: the profile client ignored the configured API base used by questionnaire/recommendations. User confirmed local Docker; public Netlify read-only checks are not evidence of their local runtime.

Implementation: local/test fake OTP defaults on, explicit false disables it, staging/production denied. All account requests use the configured API base. No user Docker commands executed, no DB deletion, no migration/catalogue/design changes. Existing six official source hashes remain unchanged remotely.

Validation: local backend suite ran 141 tests with 6 real-DB-dependent skips; mypy, build and Ruff passed. 13 targeted API tests and 3 client tests passed, including Vite-transformed configured-base requests. CI adds real browser → Vite → FastAPI → PostgreSQL coverage for both login and personal-info, without route fixtures. Latest head CI must pass before readiness. The user's Docker instance remains separately unverified until updated/recreated.
