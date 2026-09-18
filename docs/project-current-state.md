# Project current state

## Active task

- `activeTaskId`: `US-03.T02`
- Status: `completed — awaiting PR review`
- Base commit: `1ab386b783f33875336c2118a2c7a2691ec24529`
- Working branch: `feature/us-03-fastapi-core`

## Evidence

- The full canonical guide and its three golden rules were reread before this task.
- The baseline, repository, and canonical-source inventories are complete.
- All six `.unitext` files are byte-verified UTF-16 LE sources.
- Documentation skeletons and an ADR template now establish stable locations for future architecture, API, database, pipeline, security, operations, and test evidence.
- The initial risk and ambiguity register is recorded in `docs/project-risk-register.md`; no risk is silently accepted.
- Canonical IDs for questionnaire questions/answers, loan variables, categories, routes, and future loan identity are versioned in `data/contracts/canonical-identifiers.v1.json` and statically validated.
- Pure, framework-independent schema and Persian scalar parser contracts are versioned and unit tested; ambiguous ranges/prose remain typed unknowns.
- A read-only source audit and provenance report record source hashes, structural coverage, numeric coefficient ranges, loan-row evidence, and blocking core-value issues.
- Versioned data decisions define the Q5 interest weight, neutral deposit-feature behavior, core-value ranking exclusion, and display-only source columns.
- Versioned golden contract fixtures cover every canonical question and the complete, neutral, and core-unknown loan-policy boundaries without asserting an engine score prematurely.
- A staged frontend/backend architecture scaffold and module map are created without moving the active Vite prototype.
- `US-03.T01` was merged in PR #5.
- Typed FastAPI application composition, environment settings, redacting logging and dependency providers are implemented without any product endpoint, database or deploy change.

## Test record

| Command | Result |
| --- | --- |
| `npm run build` | Passed; Vite production build completed. |
| `npm run test:backend-core` | Passed; five settings, composition and redaction tests completed. |
| `python -m unittest discover -s backend/tests -p "test_*.py"` | Passed; 22 backend tests completed. |
| FastAPI composition boot with `SHAHAB_CORS_ALLOWED_ORIGINS` | Passed; comma-separated environment configuration was parsed safely. |

## Blockers and next task

- Docker/Compose is unavailable in this environment; Docker-dependent verification belongs to its assigned future task.
- The prototype has no automated lint/typecheck/test suite yet; this remains recorded baseline risk.
- `US-01` was merged in PR #3.
- `US-02` was merged in PR #4.
- Next task: `US-03.T03` — domain/application ports and import-boundary enforcement.

## Compatibility pointer

This is the canonical current-state checkpoint required by the guide. `docs/progress/current-state.md` is retained only as historical context for earlier commits.
