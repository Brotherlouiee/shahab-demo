# ADR-0011: immutable, owner-scoped recommendation history

## Decision

US-09.T079 records one completed recommendation response only when the requester
has a verified account capability. recommendation_history_runs is unique on
questionnaire_session_id; recommendation_history_items and
recommendation_history_item_reasons retain the three ordered response partitions
and the facts displayed on each card. An item also references the existing immutable
loan-product version.

The write is a single request transaction. A nested transaction plus the database
unique constraint makes an HTTP retry idempotent and leaves no partial run if an item
write fails. API reads always constrain both run ID and owner phone; an entry belonging
to another account is indistinguishable from a missing entry.

## Consequences

Historic results do not rerun the recommender or reread mutable serving facts. The
history APIs contain no questionnaire answer, bearer token, phone number or database
URL. Anonymous recommendation output remains transient, and this change neither
extends nor changes the existing 30-minute questionnaire-session retention policy.

The migration is additive (e4c7b9a1d2f3) and is tested on CI's real PostgreSQL
service. Operational rollback must be planned against retained user history; do not
use the Alembic downgrade as a production data-deletion procedure.
