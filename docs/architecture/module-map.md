# Module map — US-03.T01

## Current transition state

The root `src/` Vite application is the active prototype and remains operational. The new `frontend/src/` is a migration target, not a second active application. `src/features/loan-details/` is the first active feature extraction and owns only the UI/API client for loan details. `backend/app/recommendation/domain/` already contains framework-independent data contracts from US-02; no FastAPI runtime is introduced yet.

| Boundary | Owns | Must not own |
| --- | --- | --- |
| `frontend/src/app` | composition, routing, providers, environment bootstrap | scoring, source parsing, persistence |
| `frontend/src/shared` | generic UI and utility code | feature/domain rules |
| `frontend/src/features/questionnaire` | questionnaire presentation and canonical-answer interaction | raw source documents, scoring |
| `src/features/questionnaire` | active prototype's route-to-canonical-ID adapter | answer persistence, raw source documents, scoring |
| `src/features/recommendation/presentation` | validated three-part server-result view model, API client, display states, RTL/a11y controls and safe detail/explanation navigation | scoring, threshold classification, result reordering, direct database/session access |
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

`backend/app/operations/` owns the pure role/permission policy and current-grant
authorization port. It imports no HTTP, ORM, customer account or pipeline code.
`main.py` composes a deny-all authorizer until T02/T04 connect reviewed internal
use cases and credentials. The boundary validator rejects reversed dependencies
to API/core/infrastructure/accounts/data_pipeline. See
[operations authorization](../operations/authorization.md).

`frontend presentation → application/API contract → backend application → backend domain`.

Infrastructure implementations may depend on application ports and domain types, never the reverse. `backend/app/main.py` is the FastAPI composition root and must not import feature/domain implementations directly. `scripts/validate_import_boundaries.py` enforces prohibited reverse imports and local import cycles. The active root prototype has not yet been migrated to this graph; each later move requires tests and a focused commit.

All HTTP routes are mounted below the versioned API prefix. Transport errors use the typed `ErrorResponse` envelope; liveness is minimal and readiness is token-gated without returning dependency status.

Repository-wide quality boundaries are enforced by Ruff, Mypy, backend tests, data/architecture validators and secret scan in `npm run quality`; `.github/workflows/quality.yml` runs the same gate in CI.

Alembic is the sole schema-DDL owner under `alembic/`; its PostgreSQL 16 CI job verifies an empty-database upgrade, representative fixture write and full downgrade. Docker Compose is local-only composition and has no production secret or deployment authority.

## US-09.T06 readiness boundary

The future transport adapter resolves the anonymous session and creates an allowlisted read model. A separate answer mapper must consume approved versioned coefficients; a serving repository must return an immutable `PUBLISHED` snapshot with categories for all eight loan variables, display names and approved conditions. T05B supplies active-only SQLAlchemy reads of approved conditions and all eight categories; the in-memory publication adapter remains test/local only. T06 still owns the session mapper and public recommendation endpoint. None of these boundaries may use prototype cards or raw spreadsheet rows at request time.

## US-09.T06A loan-route integrity boundary

`backend/app/api/v1/recommendations.py` owns the public high/low/review read
model; `canonical_scoring.py` owns threshold partitioning and stable ordering.
The active Vite result screen selects one returned array and performs no score,
weight, category or threshold calculation. Loan details and comparisons read
allowlisted facts through `GET /api/v1/loans/{loanId}`. The action route remains
fail-closed because no approved provider contract exists, and the explanation
route renders only engine explanations, exclusion reasons and published
conditions. See `docs/ui/loan-route-inventory.md` for the complete route map.

## US-09.T05A materialization boundary

`scripts/build_t05a_*.py` فقط بایت منبع و قراردادها را به manifest قطعی تبدیل می‌کنند. `backend/app/data_pipeline/infrastructure/materialize_official_sources.py` تنها adapter نوشتن PostgreSQL است و به session پرسشنامه، موتور pure یا HTTP متصل نیست. آداپتورهای خواندن active snapshot و جزئیات در T05B باقی می‌مانند.

## US-09.T05B serving boundaries

`backend/app/recommendation/infrastructure/sqlalchemy_snapshot.py` پورت read snapshot را پیاده می‌کند؛ engine/application ORM نمی‌خوانند. `backend/app/loans/infrastructure/sqlalchemy_catalogue.py` تنها active published members و detail facts همان version را می‌خواند. `backend/app/loans/infrastructure/backfill_serving_facts.py` projection رسمی T05A را با manifest قفل‌شده تکمیل می‌کند. اتصال session و endpoint در T06 و استقرار پایدار در T07 است.


## Account/profile repair — US-09.T072

backend/app/accounts/phone.py normalizes full phone identities; profile_schema.py validates allowlisted fields; profile_repository.py owns DB persistence; access.py provides bounded local/test OTP sessions. api/v1/account_access.py resolves actors and maps safe errors; api/v1/profiles.py checks ownership before persistence. main.py disables mock outside explicit local/test. No account dependency on recommendation scoring.

## US-09.T081 documentation boundary

`backend/app/api/documentation.py` enriches FastAPI's generated schema with the existing transport error/auth contracts; `DocumentedFastAPI` changes descriptions only. `main.py` serves pinned, cookie-preserving Swagger and respects the proxy root for schema loading. `api_docs_include_operations` controls health visibility in non-production docs, never runtime authorization. `scripts/export_api_docs.py` emits deterministic OpenAPI, Postman and route inventory without DB startup or user data; CI rejects drift. No ORM, migration, data, scoring, application UI or authentication implementation changed. [Online test runbook](../runbook/api-testing.md) records the hosting blocker and existing publication reuse.

