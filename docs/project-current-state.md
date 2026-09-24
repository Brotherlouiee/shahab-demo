# Project current state

## Active task

- activeTaskId: US-07.T04
- Status: completed — PR #30 is ready for merge after all required CI checks passed.
- Base branch: main after merge of US-07.T03 / PR #29 (fcc12bd4e2eec4dbffeb6b6a1bae3a6432d6ad99).
- Working branch: feature/us-07-questionnaire-ui-session
- estimatedWorkScope: canonical behavioural-question UI, anonymous session transport, validation/error states, focused API/client tests and documentation.
- actualScope: behavioural pages render their source-traceable canonical prompt/answer IDs; selection is required before forward navigation; each selected canonical answer is written only in an HTTP request body to an anonymous server-side session. Back navigation keeps answers only in the active React instance.
- Session decision: confirmed by product owner on 2026-09-24 — 30-minute retention, same browser tab only. The opaque session ID remains in React memory; it is absent from URLs, localStorage, sessionStorage, logs and recommendation input.
- Explicit exclusions: no identity, OTP integration, cross-device resume, recommendation score/result, production deployment or source-data mutation.
- Source/guide attestation: the complete canonical guide, data decisions and all six verified UTF-16LE official sources were reread before implementation.
- Test plan: canonical configuration/client contract tests, API session lifecycle/ownership validation, full quality gate, PostgreSQL migration verification and Chromium E2E CI gates.

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
- Framework-free ListLoans and GetLoanDetails now depend on a serving-only port; source/draft/superseded data and provenance fields are blocked from their output.
- Typed loan response schemas now allowlist public catalogue facts and forbid raw conditions, provenance, serving-version and internal asset data.
- Approved conditions source text now has a pure plain-text bullet parser; nested list markers and blank lines are normalized without emitting HTML.
- The serving-only use cases now have a PostgreSQL/SQLAlchemy read adapter with an explicit `PUBLISHED` predicate; draft, raw, staging and superseded records cannot cross into the public-catalogue boundary.
- `US-06.T04` now composes a request-scoped `GetLoanDetails` endpoint at `GET /api/v1/loans/{loanId}`. It never accepts a source/version selector and returns typed unavailable/not-found errors without database details.
- The endpoint exposes approved terms and parsed plain-text `conditions` only; it omits raw conditions, provenance, approval metadata, serving-version IDs and internal logo references.
- The active Vite prototype's `src/features/loan-details/` fetches that contract and renders RTL loading, absent-detail, safe-error/retry and detail states. It has no hard-coded detail fallback and React renders every condition as text.
- `US-06.T05` adds four browser scenarios for RTL rendering, loading, typed absent detail, typed failure/retry, escaped hostile conditions and ignored invalid logo/link fields. The browser gate is isolated in CI and installs the pinned Chromium revision before execution.
- `US-07.T01` adds an approved questionnaire configuration artifact with the verified questionnaire source hash, all ten canonical required questions and fifty semantic answer IDs. Its pure loader rejects missing, reordered, duplicate or non-canonical answers before route/session/UI work begins.
- `US-07.T02` introduces the sole route adapter for `/question/3..12`. It translates public paths to canonical question IDs and back, while a documented compatibility bridge translates only those IDs to the prototype's existing screen indexes. Browser paths and indexes are never answer identifiers.

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
| loan catalogue use-case test | Passed; serving-only filtering, deterministic list ordering, missing detail and blank ID handling are covered. |
| loan response-schema test | Passed; camel-case allowlist, prohibited internal fields and validation errors are covered. |
| conditions parser test | Passed; bullets, line breaks, nested markers, empty text and HTML-as-text behavior are covered. |
| `npm run quality` | Passed; 70 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-06.T03. |
| `python -m unittest backend.tests.test_sqlalchemy_catalogue_adapter` | Passed; the durable adapter returns only published versions and rejects draft lookups. |
| `npm run quality` | Passed; 71 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after corrective US-06.R01. |
| `python -m unittest backend.tests.test_loan_detail_api backend.tests.test_loan_response_schemas` | Passed; approved detail allowlist, text bullets, typed not-found/unavailable errors and omitted internals are covered. |
| `npm run quality` | Passed; 74 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-06.T04. |
| `npx playwright test --list` | Passed; all four US-06.T05 browser scenarios were discovered and parsed. |
| `npm run build` | Passed; the active Vite frontend compiles with the new browser-test dependencies/configuration. |
| `npm run test:e2e` | Blocked locally only: the sandbox could not download the Playwright Chromium binary (network 502). CI has a dedicated browser-install-and-run job; this is not a test assertion failure. |
| GitHub Actions run #37 | Passed: quality gates, PostgreSQL migration verification and all four Chromium loan-details E2E scenarios. |
| `python -m unittest backend.tests.test_questionnaire_configuration` | Passed; ten canonical required questions, fifty canonical answer IDs and malformed/reordered answer rejection are covered. |
| Exact source/config comparison | Passed against the verified GitHub source blob; all ten prompts and fifty options match in source order. |
| `npm run quality` | Passed through format, lint, Mypy, 76 backend tests and prior validators locally; the final source-file validator cannot run in this scratch checkout because its already-versioned `.agents/documents` raw files are absent locally. |
| GitHub Actions run #41 | Passed: the complete checkout executed the source-file questionnaire validator, repository quality gate, PostgreSQL migration verification and Chromium E2E verification. |
| `npm run test:questionnaire-route-map` | Passed; all ten canonical forward/reverse route mappings, legacy index bridge, and unmapped-path rejection are covered. |
| `npm run quality` | Passed; 76 backend tests (2 PostgreSQL integration tests skipped locally), 3 route-adapter tests, source integrity validation, formatting, lint, typecheck, validators, secret scan and production build completed after US-07.T02. |
| `npm run test:e2e` | Browser binary unavailable locally; CI run #46 installed the pinned Chromium revision and passed all five scenarios, including the US-07.T02 all-routes browser case. |
| GitHub Actions run #46 | Passed: Quality gates, PostgreSQL migration verification, and Chromium browser verification on the final `US-07.T02` commit. |
| `npm run quality` | Passed; 67 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-06.T02. |
| `npm run quality` | Passed; 64 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-06.T01. |
| `npm run quality` | Passed; 59 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-05.T05. |
| GitHub Actions run #78 | Passed: quality gate (format/lint/Mypy, backend and client contracts, validators, secret scan, production build), PostgreSQL migration verification, and Chromium browser E2E on the final US-07.T04 commit. |

## Blockers and next task

- Docker/Compose is unavailable in this environment; real PostgreSQL migration integration is enforced in GitHub Actions.
- The prototype has no automated lint/typecheck/test suite yet; this remains recorded baseline risk.
- `US-01` was merged in PR #3.
- `US-02` was merged in PR #4.
- `US-05.T02` was merged in PR #16.
- `US-05.T03` was merged in PR #17.
- `US-05.T04` was merged in PR #18.
- `US-05.T05` was merged in PR #19.
- `US-05.T06` was merged in PR #20.
- `US-06.T01` was merged in PR #21.
- `US-06.T02` was merged in PR #22.
- Corrective `US-06.R01` was merged in PR #24.
- The current physical catalogue adapter has no persisted display-conditions column yet; until the approved import/persistence mapping supplies `LoanDetail.conditions_source_text`, the deployed endpoint correctly returns an empty `conditions` list rather than inventing terms. This is a data-hydration limitation, not a fallback to prototype data.
- Local Python dependencies are temporarily unavailable in this sandbox after runtime reset; CI reinstalled from the locked project configuration and passed quality/migration checks. The browser gate passed in CI run #37 and is the authoritative E2E execution.
- The local scratch checkout lacks the already-versioned `.agents/documents/*.unitext` raw files; no fallback or source alteration was introduced. GitHub Actions run #41 executed the authoritative exact-source gate against the complete repository successfully.
- `US-07.T03` is merged in PR #29 and `US-07.T04` is merged in PR #30. The next ordered task is `US-07.T05`; after it, the new mandatory `US-07.T06` persists anonymous questionnaire sessions/answers in normalized PostgreSQL tables with Redis cache, 30-minute expiry/cleanup, restart/cache-failure tests and synchronized ERD/schema documentation before `US-08` may start.

## Compatibility pointer

This is the canonical current-state checkpoint required by the guide. `docs/progress/current-state.md` is retained only as historical context for earlier commits.
