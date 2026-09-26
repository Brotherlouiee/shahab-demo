# US-09.T05B — approved serving read readiness

This task reads only the active approved PostgreSQL catalogue. It does not provision a database, publish production data, add the recommendation endpoint or connect the frontend. The separate `US-09.T07` gate requires a persistent staging database, Netlify/API wiring and evidence on a real URL.

## Schema and existing T05A catalogue

Run migration `a62c0b5b005b` after reviewing the database and backup. A fresh T05A import under this schema writes `loan_serving_facts` with the source row. If the verified 102-row T05A catalogue was already published before this schema change, inspect it with `python -m scripts.materialize_t05a`, then run the explicit, reviewed backfill:

```sh
python -m scripts.backfill_t05b_serving_facts --actor-reference OPERATOR_REFERENCE --approval-reason 'Reviewed official serving detail projection'
```

Set `SHAHAB_DATABASE_URL` through the selected environment's secret store. The backfill validates the exact official manifest digest, source hash, 102 active members, loan identities and exact conditions before inserting any missing detail facts in one transaction. Existing matching facts are reused; mismatches raise and roll back. It cannot repair a conflicting source or invent an unknown value. Keep the command log and operator approval with the deployment record. The CLI is an operational job, never a public API.

## Read semantics

`SqlAlchemyRecommendationSnapshotRepository` fetches active catalogue, approved config counts, member versions and eight category states in one SQL statement for a consistent snapshot under PostgreSQL's default read isolation. Missing active data, incomplete config/category coverage and nonpublished members fail closed. The pure engine still takes canonical preferences supplied by its caller; session-to-preference mapping belongs to T06. An active catalogue with zero members yields a legitimate no-candidate snapshot.

Loan details use the same active membership and published/source checks. Missing details are not replaced by prototype content; stored empty conditions produce an empty bullet list, while the absent loan returns 404. Database read failures produce a typed unavailable response. Safe public response schemas omit source hash, source row, approval, trace, config and session internals. `prepare_canonical_import.py` remains a nonpublishing plan; the reviewed T05A materializer and the explicit backfill are the durable write paths for this official source. No generic in-memory repository is wired into production.

## Verification and rollback

PostgreSQL CI upgrades/downgrades the schema, materializes official data, reads a reproducible recommendation and loan conditions, then deletes/rebuilds the facts projection to prove backfill idempotency. The SQLite test also checks fail-closed cases and transaction rollback. A failed backfill leaves the prior active version and facts unchanged. Schema downgrade removes `loan_serving_facts` only after a controlled backup; it is not a publication rollback. Passing CI does not establish a persistent deployed database or a working Netlify URL.
