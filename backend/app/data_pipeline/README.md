# Data pipeline boundary

This bounded context turns approved source bytes into traceable recommendation data in explicit stages:

- `domain/`: immutable records and invariants without filesystem, ORM or FastAPI dependencies.
- `application/`: ingest use cases and ports; it never parses a loan row or publishes serving data.
- `infrastructure/`: replaceable storage adapters. The filesystem adapter is safe for local/test use only.

`US-05.T01` owns raw byte capture, SHA-256 identity, source metadata and immutable deduplication. Staging validation begins only in `US-05.T02`.
