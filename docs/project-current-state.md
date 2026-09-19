# Project current state

## Active task

- `activeTaskId`: `US-05.T06`
- Status: `completed locally — idempotency/failure-test PR pending`
- Base commit: `95793289af48aa56b9086230bf5af1b89439f5ae`
- Working branch: `feature/us-05-pipeline-failure-tests`

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
- `US-04.T01` was merged in PR #10.
- PostgreSQL 3NF physical tables, type/state semantics, constraint catalog and migration/rollback operations are specified before ORM/migration implementation.
- `US-04.T02` was merged in PR #11.
- SQLAlchemy 2.x metadata declares the core 3NF catalog/config/import constraints without creating a session, engine or schema.
- `US-04.T03` was merged in PR #12.
- Alembic owns versioned DDL; a bounded SQLAlchemy engine/session factory is isolated in the database infrastructure adapter.
- Docker Compose defines local-only API/PostgreSQL startup without committing operational credentials; GitHub Actions provisions PostgreSQL 16 for migration verification.
- Query contracts now own a small, reversible index set; a representative selective catalogue query must use the lender FK index according to PostgreSQL `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`.
- `US-04.T05` was merged in PR #14 after PostgreSQL 16 migration and plan-verification CI passed.
- Raw source capture is now isolated from parsers and serving data: source bytes have an immutable SHA-256 identity and traceable capture metadata.
- Raw evidence now has strict, non-destructive staging checks for encoding, headers, row shape and duplicate source hashes.
- All eight approved loan variables now have a pure, conservative category-normalization boundary. Matrix gaps, capped-out amounts, free text, ranges, unknown and variable values remain typed evidence rather than inferred categories.
- Canonical rows now retain source-row fingerprints, typed construction rejections and rankability evidence; reviewable drafts require explicit approval before an atomic serving-version pointer can move.
- The internal import command now produces a typed, reviewable canonical plan and cannot connect to a database or publish data; the operations runbook fixes the safe hand-off and recovery sequence.
- Repeated manifest preparation is deterministic; ambiguous fields remain typed evidence, and a publish failure leaves the previous serving version active.

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
| `npm run quality` | Passed; physical-schema specification validator and 33 backend tests completed with all existing quality gates. |
| `npm run quality` | Passed; SQLAlchemy metadata tests and 35 backend tests completed with all existing quality gates. |
| `SHAHAB_DATABASE_URL=sqlite:///… alembic upgrade head → downgrade base → upgrade head` | Passed; clean structural lifecycle check completed. |
| GitHub Actions PostgreSQL 16 migration job | Pending PR execution; it enforces empty-db upgrade, fixture write and downgrade on real PostgreSQL. |
| `npm run quality` | Passed; 38 backend tests (two PostgreSQL integration tests skipped locally), all quality gates and production build completed. |
| Alembic index lifecycle | Passed locally: initial migration + index migration upgrade, downgrade to base and repeated upgrade. |
| `python -m unittest backend.tests.test_normalization` | Passed; approved categories, Persian digits, boundary ownership, gaps, unknowns and text-only categories are covered. |
| `npm run quality` | Passed; 50 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-05.T03. |
| `python -m unittest backend.tests.test_serving_publication` | Passed; canonical-row rejection/eligibility, approval gate, diff and atomic-pointer failure behavior are covered. |
| `npm run quality` | Passed; 55 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-05.T04. |
| `python -m unittest backend.tests.test_import_preparation` | Passed; clean plan, typed issues/rejections, core needs-review preservation and non-publishing CLI behavior are covered. |
| `python -m unittest backend.tests.test_import_preparation backend.tests.test_serving_publication` | Passed; repeated import determinism, ambiguous input and previous-pointer preservation on publication failure are covered. |
| `npm run quality` | Passed; 61 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-05.T06. |
| `npm run quality` | Passed; 59 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-05.T05. |

## Blockers and next task

- Docker/Compose is unavailable in this environment; real PostgreSQL migration integration is enforced in GitHub Actions.
- The prototype has no automated lint/typecheck/test suite yet; this remains recorded baseline risk.
- `US-01` was merged in PR #3.
- `US-02` was merged in PR #4.
- `US-05.T02` was merged in PR #16.
- `US-05.T03` was merged in PR #17.
- `US-05.T04` was merged in PR #18.
- `US-05.T05` was merged in PR #19.
- Next task after this PR is merged: `US-06.T01` — ListLoans and GetLoanDetails use cases on approved serving data.

## Compatibility pointer

This is the canonical current-state checkpoint required by the guide. `docs/progress/current-state.md` is retained only as historical context for earlier commits.
