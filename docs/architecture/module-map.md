# Module map — US-03.T01

## Current transition state

The root `src/` Vite application is the active prototype and remains operational. The new `frontend/src/` is a migration target, not a second active application. `backend/app/recommendation/domain/` already contains framework-independent data contracts from US-02; no FastAPI runtime is introduced yet.

| Boundary | Owns | Must not own |
| --- | --- | --- |
| `frontend/src/app` | composition, routing, providers, environment bootstrap | scoring, source parsing, persistence |
| `frontend/src/shared` | generic UI and utility code | feature/domain rules |
| `frontend/src/features/questionnaire` | questionnaire presentation and canonical-answer interaction | raw source documents, scoring |
| `frontend/src/features/recommendation` | result presentation and API view models | scoring formulas, database access |
| `frontend/src/features/loan-details` | loan-detail presentation | HTML rendering of raw conditions, scoring |
| `backend/app/recommendation/domain` | entities/value contracts/pure parsing | FastAPI, ORM, React imports |
| `backend/app/domain` | framework-free shared domain value types | FastAPI, ORM, transport, infrastructure |
| `backend/app/application` | use cases and dependency ports | FastAPI, ORM, direct adapter imports |
| `backend/app/infrastructure` | outbound adapter implementations | domain/application dependency reversal |
| `backend/app/infrastructure/db` | SQLAlchemy metadata, bounded engine/session factory and future repository adapters | API import, business scoring, migration execution at import time |
| `backend/app/data_pipeline` | immutable raw source capture, staged transformation boundaries and adapters | scoring, serving publication, UI/API ownership before its task |
| `backend/app/api/v1` | versioned transport adapters and restricted operational endpoints | domain logic, direct database decisions |
| `backend/app/core` | typed settings, dependency wiring, redacted logging, security hooks | product use cases |
| `backend/app/shared` | truly cross-feature backend helpers | recommendation-specific rules |

## Dependency direction

`frontend presentation → application/API contract → backend application → backend domain`.

Infrastructure implementations may depend on application ports and domain types, never the reverse. `backend/app/main.py` is the FastAPI composition root and must not import feature/domain implementations directly. `scripts/validate_import_boundaries.py` enforces prohibited reverse imports and local import cycles. The active root prototype has not yet been migrated to this graph; each later move requires tests and a focused commit.

All HTTP routes are mounted below the versioned API prefix. Transport errors use the typed `ErrorResponse` envelope; liveness is minimal and readiness is token-gated without returning dependency status.

Repository-wide quality boundaries are enforced by Ruff, Mypy, backend tests, data/architecture validators and secret scan in `npm run quality`; `.github/workflows/quality.yml` runs the same gate in CI.

Alembic is the sole schema-DDL owner under `alembic/`; its PostgreSQL 16 CI job verifies an empty-database upgrade, representative fixture write and full downgrade. Docker Compose is local-only composition and has no production secret or deployment authority.
