# ADR-0001: Stage the architecture scaffold without moving the live prototype

- Status: Accepted
- Date: 2026-09-18
- Owner: Product/technical owner
- Task: `US-03.T01`

## Context

The current Vite prototype has a large active composition module and custom routing. Moving all frontend code while backend, tests and API contracts do not yet exist would combine multiple risks and violate the staged-development rule.

## Decision

Create the target `frontend/src` and `backend/app` boundaries now, retain the active root `src` application unchanged, and migrate features only in their assigned stories after relevant contracts and characterization tests exist.

## Consequences

The repository temporarily has a clear migration workspace. This is intentional and documented. No runtime duplication, data synchronization, router replacement or deploy configuration change is introduced by this ADR.

## Validation and rollback

The scaffold validator and existing production build must pass. Rollback is removal of unused scaffold-only files; it does not affect the active prototype.
