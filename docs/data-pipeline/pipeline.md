# Pipeline, approval and serving-version contract

## US-05.T04 checkpoint

- Guide reviewed: SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md on 2026-09-19.
- Official inputs reread: all six UTF-16 LE unitext files in .agents/documents.
- Canonical source blobs reviewed: questionnaire 26c702…faf, category matrix
  f2121e…915, question-variable map 272194…fcd, answer weights f14d0d…10b,
  compatibility matrix 7eeed3…7c, loan database 0854a5…3fc.
- Decision contract: recommendation-data-decisions.v1.json version 1.0.0,
  approved.

## State flow

raw immutable bytes → staging validation → normalized canonical rows → draft
version → approved version → published serving version

Only an approved version can become the active serving version. Publication is an
atomic active-pointer change: the prior published version becomes superseded;
its rows, diff and approval evidence remain immutable. A failed publication must
leave the active pointer untouched. Rollback command and durable PostgreSQL
adapter are intentionally deferred to US-05.T05/T06.

## Canonical-row acceptance

Each row must have a positive source row number, lender name, loan name and
exactly the eight canonical loan variables. Rejected construction attempts return
typed CanonicalRowRejection evidence; no source text is rewritten.

Core ranking fields with unknown, variable, unparseable or unmapped states create
a valid needs-review row and record the exact variable IDs. They are not silently
neutralized. The three deposit attributes retain the approved neutral semantics
for US-08; their uncertainty does not make the row unrankable here. Display-only
fields are whitelisted and kept outside variables.

## Diff and approval evidence

The draft stores an identity-level diff (added, changed, removed) against the
prior published catalogue. Identity is lender name plus loan name only for this
staging boundary; immutable database IDs are assigned by the later durable import
adapter. Approval requires a non-empty actor reference, reason and UTC timestamp.
No HTTP route, user-controlled publication path or production credential was
added in this task.

## US-05.T05 preparation command

The internal command at scripts/prepare_canonical_import.py accepts a reviewed
UTF-8 JSON manifest and creates a non-publishing plan. It validates the manifest
shape, source SHA-256, duplicate source rows and duplicate catalogue identities;
then it preserves every typed rejection or issue in its output. Exit code zero
means a candidate is clean enough for review, not that it was approved or
published. The operations runbook documents source verification, review,
approval hand-off and failure recovery.

## US-05.T06 failure and idempotency evidence

The same source hash, parser version and manifest rows deterministically produce
the same canonical plan and source-row fingerprints. Ambiguous text remains
without a category; an ambiguous core field retains its needs-review exclusion
reason while an ambiguous deposit field stays explicit for later neutral
handling. A simulated publish failure occurs before the in-memory atomic
pointer commit, proving that the previous published version remains active and
the candidate remains approved rather than partially published.

## US-10.T02 authorized application boundary

`InternalDataOperations` guards import/review/prepare/approve/publish/rollback and checks exact stored clean-import linkage. Rollback targets an approved superseded version and compares the expected current pointer inside the atomic repository method; original rows/approval remain immutable. Preparation/publication decisions and rollback decisions retain verified actor/reason/UTC through port arguments. Existing memory adapters model this only for local/test; durable audit/approval and PostgreSQL transaction implementation/proof are T03. Existing OS-trusted CLI is not exposed as an operations route. See `../operations/data-use-cases.md`.

## US-10.T03 review evidence persistence

The existing manifest preparation and publication domain now have PostgreSQL
ports retaining immutable reviewed plans, diffs and decisions. This is internal
workflow evidence, not a second raw/core/serving pipeline. Normalization and
scoring are never rerun when historical evidence is read. The public serving
materializer remains unchanged; protected composition/projection is T04 scope.
