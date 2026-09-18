# ADR-0004: Versioned API, typed errors and restricted readiness

- Status: Accepted
- Date: 2026-09-18
- Task: `US-03.T04`

## Decision

All current transport routes are mounted below the configurable `/api/v1` prefix. Application-generated errors use a stable envelope containing an error code, a safe message and a server-generated correlation ID. User-supplied correlation headers are not trusted.

`/health/live` returns only process liveness. `/health/ready` is hidden from API documentation and responds only after constant-time comparison with a `SHAHAB_READINESS_TOKEN` environment secret; otherwise it returns the same typed 404 response. It deliberately reports no environment, package, database, provider or configuration state.

## Consequences

No business endpoint, persistence check or external dependency is included. Adapter-specific readiness checks are added only with their own implementation and tests. Public clients must not rely on health routes as product APIs.

## Validation and rollback

API tests cover liveness, readiness denial/authorization, correlation headers and safe unknown-route behavior. Rollback removes only this API shell and does not affect the active Vite prototype.
