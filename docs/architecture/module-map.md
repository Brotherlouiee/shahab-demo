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
| `backend/app/api/v1` | versioned transport adapters | domain logic, direct database decisions |
| `backend/app/core` | typed settings, dependency wiring, redacted logging, security hooks | product use cases |
| `backend/app/shared` | truly cross-feature backend helpers | recommendation-specific rules |

## Dependency direction

`frontend presentation → application/API contract → backend application → backend domain`.

Infrastructure implementations may depend on domain ports, never the reverse. `backend/app/main.py` is the FastAPI composition root and must not import feature/domain implementations directly. The active root prototype has not yet been migrated to this graph; each later move requires tests and a focused commit.
