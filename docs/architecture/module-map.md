# Module map — US-03.T01

## Current transition state

The root `src/` Vite application is the active prototype and remains operational. The new `frontend/src/` is a migration target, not a second active application. `src/features/loan-details/` is the first active feature extraction and owns only the UI/API client for loan details. `backend/app/recommendation/domain/` already contains framework-independent data contracts from US-02; no FastAPI runtime is introduced yet.

| Boundary | Owns | Must not own |
| --- | --- | --- |
| `frontend/src/app` | composition, routing, providers, environment bootstrap | scoring, source parsing, persistence |
| `frontend/src/shared` | generic UI and utility code | feature/domain rules |
| `frontend/src/features/questionnaire` | questionnaire presentation and canonical-answer interaction | raw source documents, scoring |
| `src/features/questionnaire` | active prototype's route-to-canonical-ID adapter | answer persistence, raw source documents, scoring |
| `src/features/recommendation/presentation` | validated server-result view models, API client, display states, local filter/sort controls, RTL/a11y screen contracts and safe details routes | scoring, direct database/session access |
| `frontend/src/features/loan-details` | loan-detail presentation | HTML rendering of raw conditions, scoring |
| `src/features/loan-details` | active prototype's loan-detail API client and RTL presentation states | raw source parsing, scoring, persistence, `innerHTML` rendering |
| `backend/app/recommendation/domain` | entities/value contracts/pure parsing | FastAPI, ORM, React imports |
| `backend/app/recommendation/application` | RecommendLoans use case and approved read-snapshot port | FastAPI, ORM, session resolution, UI rendering |
| `backend/app/domain` | framework-free shared domain value types | FastAPI, ORM, transport, infrastructure |
| `backend/app/application` | use cases and dependency ports | FastAPI, ORM, direct adapter imports |
| `backend/app/infrastructure` | outbound adapter implementations | domain/application dependency reversal |
| `backend/app/infrastructure/db` | SQLAlchemy metadata, bounded engine/session factory and future repository adapters | API import, business scoring, migration execution at import time |
| `backend/app/data_pipeline` | immutable raw source capture, staged transformation boundaries and adapters | scoring, serving publication, UI/API ownership before its task |
| `backend/app/questionnaire/domain` | approved configuration, canonical answer validation and anonymous-session invariants | route indexes, HTTP, ORM, raw-source mutation, scoring |\n| `backend/app/questionnaire/application` | session use cases and persistence port | FastAPI, direct ORM/adapter imports, scoring |
| backend/app/loans/domain | approved-catalogue value types and safe loan detail facts | FastAPI, ORM, source parsing, conditions HTML |
| backend/app/loans/application | ListLoans/GetLoanDetails use cases and serving-only repository port | raw/staging/draft version access, HTTP concerns |
| backend/app/loans/infrastructure | replaceable serving-catalogue adapters | business interpretation or source parsing |
| `backend/app/api/v1` | versioned transport adapters and restricted operational endpoints | domain logic, direct database decisions |
| `backend/app/core` | typed settings, dependency wiring, redacted logging, security hooks | product use cases |
| `backend/app/shared` | truly cross-feature backend helpers | recommendation-specific rules |

## Dependency direction

`frontend presentation → application/API contract → backend application → backend domain`.

Infrastructure implementations may depend on application ports and domain types, never the reverse. `backend/app/main.py` is the FastAPI composition root and must not import feature/domain implementations directly. `scripts/validate_import_boundaries.py` enforces prohibited reverse imports and local import cycles. The active root prototype has not yet been migrated to this graph; each later move requires tests and a focused commit.

All HTTP routes are mounted below the versioned API prefix. Transport errors use the typed `ErrorResponse` envelope; liveness is minimal and readiness is token-gated without returning dependency status.

Repository-wide quality boundaries are enforced by Ruff, Mypy, backend tests, data/architecture validators and secret scan in `npm run quality`; `.github/workflows/quality.yml` runs the same gate in CI.

Alembic is the sole schema-DDL owner under `alembic/`; its PostgreSQL 16 CI job verifies an empty-database upgrade, representative fixture write and full downgrade. Docker Compose is local-only composition and has no production secret or deployment authority.

## US-09.T06 readiness boundary

The future transport adapter resolves the anonymous session and creates an allowlisted read model. A separate answer mapper must consume approved versioned coefficients; a serving repository must return an immutable `PUBLISHED` snapshot with categories for all eight loan variables, display names and approved conditions. The current SQLAlchemy catalogue adapter does not populate conditions text or category assignments, and the in-memory publication adapter is test/local only. None of these gaps may be filled with prototype cards or raw spreadsheet rows at request time.
