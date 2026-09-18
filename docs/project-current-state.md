# Project current state

## Active task

- `activeTaskId`: `US-04.T01`
- Status: `completed — awaiting PR review`
- Base commit: `62744201db9a5f67d6193861990b9b3ae53f8f68`
- Working branch: `feature/us-04-conceptual-model`

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
- `US-03.T02` was merged in PR #6.
- Framework-free domain references and small application ports now define one-way dependencies; an AST validator blocks reverse imports and local cycles.
- `US-03.T03` was merged in PR #7.
- API v1 now has typed errors, server-generated correlation IDs, minimal public liveness and token-gated readiness without exposing dependency state.
- `US-03.T04` was merged in PR #8.
- A single local/CI quality command now runs formatting, linting, type checking, backend tests, architecture/data validators, secret scan and production build.
- `US-03.T05` was merged in PR #9; US-03 quality gate is complete.
- Conceptual bounded contexts, cardinalities, ownership/retention and physical-schema invariants are documented before ORM or migration work.

## Test record

| Command | Result |
| --- | --- |
| `npm run build` | Passed; Vite production build completed. |
| `npm run test:backend-core` | Passed; five settings, composition and redaction tests completed. |
| `python -m unittest discover -s backend/tests -p "test_*.py"` | Passed; 22 backend tests completed. |
| FastAPI composition boot with `SHAHAB_CORS_ALLOWED_ORIGINS` | Passed; comma-separated environment configuration was parsed safely. |
| `npm run validate:import-boundaries` | Passed; no prohibited reverse import or local circular dependency detected. |
| `python -m unittest backend.tests.test_application_ports` | Passed; four port and import-boundary tests completed. |
| `python -m unittest discover -s backend/tests -p "test_*.py"` | Passed; 26 backend tests completed after US-03.T03. |
| `npm run test:api-health` | Passed; liveness, readiness authorization and typed 404 behavior verified. |
| `python -m unittest discover -s backend/tests -p "test_*.py"` | Passed; 29 backend tests completed after US-03.T04. |
| `npm run quality` | Passed; Ruff format/lint, Mypy (22 source files), 31 backend tests, all validators, secret scan and production build completed. |
| `npm run quality` | Passed; conceptual data-model validator and 32 backend tests completed with all existing quality gates. |

## Blockers and next task

- Docker/Compose is unavailable in this environment; Docker-dependent verification belongs to its assigned future task.
- The prototype has no automated lint/typecheck/test suite yet; this remains recorded baseline risk.
- `US-01` was merged in PR #3.
- `US-02` was merged in PR #4.
- Next task: `US-04.T02` — 3NF physical schema design, constraints and database operation documentation.

## Compatibility pointer

This is the canonical current-state checkpoint required by the guide. `docs/progress/current-state.md` is retained only as historical context for earlier commits.
