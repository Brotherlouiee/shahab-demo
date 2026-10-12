# Security documentation

## Current system review — US-11.T01

- [System threat model and release findings](threat-model.md): current assets,
  trust boundaries, evidence, owners and unresolved F01–F07.
- [Privacy, retention and deletion review](privacy-retention-review.md): actual
  storage/expiry/hide behavior and pending P01–P06 decisions.
- [Review/test checkpoint](../progress/us-11-t01.md): isolated evidence and task boundary.

This is a completed review, not completed hardening, a production audit or a
claim that release blockers are fixed. US-11.T02–T05 and real hosting gates
must resolve and prove the required controls. No real secrets or personal data
belong in documentation, logs or evidence.

## Existing domain reviews

- [Profile access](profile-threat-model.md).
- [Internal roles](../operations/authorization.md#threat-review).
- [Durable operations audit](operations-audit-threat-model.md).

The system review adds cross-domain findings; older domain-only controls do not
establish full questionnaire proof or physical retention/erasure guarantees.
