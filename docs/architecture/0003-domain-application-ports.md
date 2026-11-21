# ADR-0003: Domain/application ports and one-way imports

- Status: Accepted
- Date: 2026-09-18
- Task: `US-03.T03`

## Decision

Domain value types are framework-free. Application declares small `Protocol` ports for loan/config access and only cross-cutting needs that are genuinely required later (`Clock`, `IdGenerator`). Infrastructure adapters may implement those ports; neither domain nor application may import infrastructure or HTTP transport.

An AST validator runs without importing the app. It rejects reverse-layer imports and detects local circular import graphs. The composition root remains the only future location for adapter construction.

## Consequences

These are contracts, not speculative repository implementations. No ORM model, database adapter, scoring logic or HTTP endpoint is added. New ports require a named use case and a matching contract test.

## Validation and rollback

`validate_import_boundaries.py` and unit tests verify the current graph, deliberately forbidden edges and a synthetic cycle. Rollback removes only these unused contracts and does not affect the active Vite prototype.
