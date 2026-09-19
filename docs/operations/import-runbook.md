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
   rollback. These durable operations are still staged for later US-05 tasks.

## Failure and recovery

Do not retry by editing raw source bytes. Keep the rejected plan as evidence,
correct the upstream source or approved parser/config, then create a new hash
and plan. If a later durable publish fails, leave the active serving pointer
unchanged and use the retained version; never repair tables by hand.
