# ADR 0006 — Durable internal workflow and append-only audit

Status: accepted for US-10.T03 (owner authorized).

T02 has repository ports but no durable review/version implementation. Keep its
pure normalizer and publication service. Persist reviewed preparation once as a
versioned immutable JSONB evidence document: its heterogeneous accepted/rejected
rows retain exact decimals, raw values, provenance and quality issues. Operational
identities, source hash/parser, import/version links, event order, state transitions,
actor, reason, time and correlation are relational fields. No JSON predicates or
parallel algorithm; JSONB is historical evidence, not the live catalogue schema.

Four tables: operations_imports, operations_versions, audit_events and singleton
operations_workflow_head. Versions reference imports instead of copying rows.
Approval is an approval_records view over the single immutable approve event;
there is no second copy of decision facts. Version state derives from events and
the current head. Each mutation locks the singleton row, validates current state,
and writes evidence plus state in one PostgreSQL transaction. The lock serializes
low-volume administration across processes; rollback compares expected current
version while holding the lock. Prepare rejects a diff calculated against a stale
head. A transaction failure cannot leave a history fragment.

Database triggers forbid UPDATE/DELETE/TRUNCATE of imports, versions and events.
This protects ordinary SQL writes, including writes through the approval view.
The database owner/superuser can alter DDL: this is not a cryptographically
immutable external ledger. T04 must use a non-owner role without DDL privileges.
A controlled downgrade is an explicit destructive backup-first operation.

The workflow head implements the T02 internal version contract; it does not
replace serving_catalogue_versions or publish into the public recommendation
projection. Existing approved live data stays intact. T04 must explicitly bridge
the protected operational tool to the existing materializer rather than exposing
this storage primitive or inventing another import/scoring pipeline. Until then,
no transport is installed and production operations remain deny-all.
