# Internal data operations — US-10.T02

`InternalDataOperations` is a transport-independent application coordinator in
`backend/app/data_pipeline/application/operations.py`. Pipeline coordination
imports the pure operations authority; authority imports no pipeline/ORM code.
Existing canonical preparation and serving publication remain the only parser
and transition implementation. No new management endpoint is registered.

## Contract

| Method | Permission | Resource / transition |
| --- | --- | --- |
| import_data | data.import | Store immutable preparation, including issues/rejections, under a unique import ID; never publish |
| review_import | data.review | Return server-stored plan for that ID; cannot clear issues or normalize ambiguous data |
| prepare_version | data.import | Only a clean stored import; create draft from its exact canonical rows, with verified actor/reason/UTC |
| approve_version | data.approve | Draft linked to clean matching import; verified actor, nonempty reason and UTC decision |
| publish_version | data.publish | Matching import and explicit existing approval, plus separate publisher actor/reason/UTC |
| rollback_version | data.rollback | Approved superseded target, exact expected active ID, verified actor/reason/UTC |

Every method calls `OperationsAuthorizer.require` before accessing any resource
port. Neither a missing resource nor its internal details are inspected for an
unauthorized caller. Roles are freshly read each time. Service can import but
cannot review or approve; ordinary customer/mock OTP cannot call these methods.
An admin has no implicit import/review grant. Canonical customer data is not
within this catalogue-wide authority; this flow never reads profiles/history.

Stored import ID, source hash, parser version and canonical rows must match the
selected version before approval/publication/rollback. Rejecting malformed rows
cannot create a publishable partial catalogue. Unknown core fields still retain
the existing approved needs-review exclusions; review never invents a score or
coerces an unknown. Corrections require new source evidence/import, not editing
the old plan or marking blocking issues resolved without correcting the input.

`ImportReviewRepository.save_if_absent` must atomically preserve first actor/time
on identical retry and reject changed content/reason/actor under the same ID.
`ServingVersionRepository.rollback_atomically` must recheck expected current
pointer and target state within its transaction. Preparation/publication ports also carry the actual verified actor/reason/UTC
decision; legacy trusted callers may omit it, while the guarded coordinator cannot.
Rows and original approval are immutable. A rollback decision is separate evidence; it must commit with the
pointer switch or neither may persist. A stale request must be reviewed again,
never automatically retried against a newer current version.

## Availability and remaining production gates

T02 delivers these internal use cases and test/local adapters. It **does not**
deliver durable review/audit storage, a PostgreSQL implementation of these
new contracts, an operator credential verifier or a protected transport.
The memory repositories model contracts only and are not wired into the app.
T03 implements durable append-only event/approval adapters, real transaction
and concurrency/rollback tests on PostgreSQL before operational exposure.
T04 supplies verified operator/service credentials and guarded endpoint/tool
composition. Creating an `OperationsIdentity` object is not authentication.

The app remains deny-all. Existing OS-trusted materialization/backfill jobs
retain their explicit reviewed operator workflow and must not be called directly
from a public route. T02 itself made no database change; T03 adds the durable adapters described below.

## Verification / code rollback

`python -m unittest backend.tests.test_internal_data_operations
backend.tests.test_operations_authorization backend.tests.test_serving_publication
backend.tests.test_import_preparation` exercises the authorized flow, role
denials before any persistence access, revocation, dirty/mismatched resources,
idempotent import, stale rollback and failure preservation. These use local/test
repositories; they are not PostgreSQL persistence evidence. Existing CI retains
all four full quality/migration/browser jobs.

Code rollback removes the coordinator/new ports and restores prior trusted
publication API. No migration, production pointer, source/config/scoring or UI
state is changed by deploying this code, because operations composition is not
enabled. Later data rollback is the guarded version operation, not a schema
downgrade or raw SQL edit. See `docs/progress/us-10-t02.md` for dependency/time
evidence. T07/online T081 and the story continuity gate remain open.

## Durable adapters — US-10.T03

`SqlAlchemyImportReviewRepository` and `SqlAlchemyServingVersionRepository` take
an existing trusted Session factory and implement the T02 ports. Compose them
behind `InternalDataOperations`, never as directly callable HTTP primitives.
No adapter is installed into the production app before T04 credential verification.
See [ADR 0006](../adr/0006-durable-operations-audit.md) and
[the audit runbook](audit-runbook.md). This internal workflow persists its own
review/preparation/approval decisions; it does not rewrite the existing public
serving catalogue. The public projection bridge is an explicit T04 requirement.
