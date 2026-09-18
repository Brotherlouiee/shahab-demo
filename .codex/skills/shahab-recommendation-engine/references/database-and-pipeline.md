# Database and pipeline guidance

Use FastAPI + PostgreSQL. Keep router, application, domain and infrastructure separate. Pydantic validates request/response/settings, SQLAlchemy 2.x implements repository adapters and Alembic is the only schema-migration path.

Model to at least 3NF: stable loans and versioned loan terms, normalized lender/category/question/config relationships, canonical numeric values and explicit unknown/variable states. Use JSONB only for genuinely flexible data. Add constraints first; indexes come from real query plans. Use `timestamptz` UTC, documented key policy, deterministic pagination and short transactions.

Import Excel through a versioned idempotent pipeline: immutable raw file + hash → provenance-preserving staging → canonical core → audit/approval → serving version. Ambiguous data becomes a quality issue, not an inferred correction. Imports must be atomic and rollback-safe.

Commit and maintain ERD (with cardinalities), data dictionary, index/query strategy, migration/rollback runbook, pipeline runbook, API/OpenAPI documentation and backend module map. Test empty DB migrations, upgrade fixtures, duplicate imports, malformed data, integrity constraints, atomic rollback, representative performance, concurrency, authorization and backup restore against PostgreSQL—not SQLite alone.

Write detailed meaningful comments/docstrings for modules, use cases, parsers, complex queries, migrations and security/transaction decisions. Keep comments current and never expose secrets or real user data.
