# Runbook: prepared canonical import

## Scope and safety boundary

US-05.T05 adds a non-publishing preparation command. It converts an operator
reviewed JSON manifest to a canonical import plan and reports every rejection or
issue. It does not connect to PostgreSQL, approve a version, change the active
serving pointer, or accept uploads from a browser/API.

The source bytes first follow the existing raw-ingest and staging-validation
steps. The manifest is a controlled hand-off from that validated data; do not
manually invent values, alter source hashes or use it to bypass approval.

## Preconditions

1. Check out the reviewed commit and install the locked project dependencies.
2. Reread the canonical development guide and run the current data audit against
   byte-verified unitext sources.
3. Confirm the source SHA-256 and parser version in the manifest.
4. Store the input manifest outside Git when it contains operationally sensitive
   fields; no secret or user data belongs in it.

## Manifest shape

The UTF-8 JSON object contains sourceFileSha256, parserVersion and rows. Each row
contains sourceRowNumber, lenderName, loanName, all eight variableValues and
optional displayFields. The exact variable identifiers are defined by the
canonical identifier contract. A minimal example is maintained in the unit tests,
not as mutable production data.

## Dry preparation

Run from the repository root:

    python scripts/prepare_canonical_import.py --manifest /secure/path/import.json --output /secure/path/import-plan.json

Exit code zero means the plan has rows and no manifest/rejection evidence. Exit
code two means the plan is not eligible for review/publish; fix source data or
record a data decision before retrying. The output contains counts and typed
reasons, not raw financial values.

## Review and publication hand-off

1. Review rejectedRows and issues alongside the original source row.
2. Review core-field needs-review rows separately; they are not a license to
   force a score or replace a value.
3. Review the catalogue diff against the active published version.
4. Record a named approval with reason and UTC time through the internal
   operations workflow once US-10 authorization is implemented.
5. Publish atomically, run serving smoke tests, and retain the prior version for
   rollback. For the implemented official source, use the protected T04 tool and the T05 operations runbook; source/config changes require a separate reviewed version.

## Failure and recovery

Do not retry by editing raw source bytes. Keep the rejected plan as evidence,
correct the upstream source or approved parser/config, then create a new hash
and plan. If a later durable publish fails, leave the active serving pointer
unchanged and use the retained version; never repair tables by hand.

## Re-run guarantee

Re-running an unchanged manifest with the same source hash and parser version
must produce the same plan and source-row fingerprints. It is not permission to
create a duplicate serving version: the later durable import adapter must reject
the duplicate version/source identity atomically. If input is ambiguous, review
its typed evidence; never replace it with a guessed scalar merely to make the
command exit successfully.

## Internal use-case integration — US-10.T02

For future guarded tools, use `InternalDataOperations`, not a direct low-level publication call. Review stored import IDs and retain every issue; correct input in a new import. Require exact hash/parser/rows linkage before approval. Rollback must specify the expected active version, verified actor, reason and UTC decision, and preserve prior approval. T03 adds PostgreSQL review/version adapters and append-only decisions; verified internal tooling and the existing materializer bridge (T04) remain required before exposure. See audit-runbook.md. Existing CLI remains OS-trusted.

## مسیر عملیاتی فعلی — T04/T05

فرمان preparation بالا فقط plan است. برای mutation عملیاتی از
[راهنمای عملیات T05](operations-runbook.md) و `scripts.operations_tool` با
هویت معتبر، role محدود و audit استفاده کنید. actor-reference متن آزاد در
فرمان legacy تأیید هویت نیست؛ آن را جای authority یا برای bypass استفاده نکنید.
