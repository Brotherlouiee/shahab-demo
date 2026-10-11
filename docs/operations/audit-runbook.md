# Durable internal audit — US-10.T03

Apply with the established migration job: `python -m alembic upgrade head`.
Revision `b4d8e1f2a3c5` follows `a3b7c9d1e2f4`. New tables/view only, no live
catalogue or user backfill. Restart does not erase preparation or decisions.
No new environment variable/package/port; app remains deny-all until T04.

Import retry returns first evidence when ID, preparation, actor and reason match;
new time/correlation does not replace the originals. Conflicts require a new
import ID, not an edit. Other already-completed/stale transitions are rejected;
inspect history before retrying. Correlation UUID is server-generated, never a
client role/permission. Sequence gaps after rollback are normal; event_order is
stable ordering, not an assertion that there were no failed transactions.

## Read evidence safely

Use a trusted read-only database connection; never put these queries in the public
API. Select only required fields. This stable keyset pattern supports later tools:

```sql
SELECT event_order, event_type, actor_reference, reason, occurred_at,
       correlation_id, import_id, version_id, before_state, after_state,
       before_version_id, after_version_id
FROM audit_events
WHERE event_order > :last_order
ORDER BY event_order
LIMIT :page_size;
```

Bound page_size to 1–100 in a future transport. Actor lookup uses
`ix_audit_actor_order`; import/version lookup has FK indexes. `approval_records`
reads the same approve event, not duplicated approval facts. Import preparation
and version diff are versioned immutable JSONB evidence. Do not query them for
operational list predicates or store credentials/customer questionnaire answers.

## Failure and rollback

A database exception aborts the whole mutation. Check by import/version/correlation
and read current head before retry. No manual repair UPDATE/DELETE is permitted.
Rollback of an internal version takes expected_current_version_id and creates a
new decision; it preserves target rows and original approval.

The workflow head is not serving_catalogue_versions.active. T04 must explicitly
compose verified tooling with the existing materializer/public projection; this
task alone does not publish new loans into customer recommendations.

Code rollback can stop use of these adapters and leave additive storage intact.
Schema rollback is destructive to T03 evidence: export/backup all four tables and
approval view definition, verify restoration in a disposable database, stop all
operations writers, then migrate to `a3b7c9d1e2f4`. It drops only T03 objects,
not existing serving/user data. Keep backups access-controlled. Never execute
integration tests/downgrade against a shared, staging or production database.

## Verification

From repository root, set SHAHAB_TEST_DATABASE_URL to a **disposable PostgreSQL**
and run `python -m unittest backend.tests.test_operations_postgresql`. This suite
upgrades from the previous head, retains an existing lender fixture, exercises
transactions/concurrency/append-only constraints and downgrades afterward.
The existing PostgreSQL CI job runs it. No SQLite substitute; local skips are
reported as skips and do not qualify for readiness.
