# RecommendLoans Use-Case Contract

## Scope

US-08.T04 composes the pure engine through one outbound read port. It does not
create an API endpoint, read questionnaire sessions, add an ORM adapter, write
a result, expose a trace to the client, or modify the database.

## Approved read snapshot

The repository returns exactly one immutable RecommendationSnapshot per
execution:

- dataVersion identifies the approved serving catalogue snapshot;
- configVersion identifies the approved scoring configuration;
- candidates are the complete, stable input set for that snapshot.

The future infrastructure adapter must make this a consistent transaction/read
snapshot and must not allow a caller to choose raw, draft or superseded data.

## Output

RecommendLoans.execute(preferences) returns one RecommendationRun with:

- ranked recommendations, deterministically ordered by the engine;
- needs-review loans with typed exclusion reasons;
- exactly one versioned, redacted trace per input candidate;
- the same data/config versions that were read in the snapshot.

Canonical preferences are passed in explicitly. Session lookup, answer-to-
preference conversion and HTTP input validation are not part of this contract
and remain later boundaries.

## Invariants

- empty or whitespace-only version identifiers are rejected;
- duplicate candidate IDs are rejected before scoring;
- no candidate is silently dropped: it is ranked or needs review and always has
  a trace;
- no FastAPI, SQLAlchemy, React, database or session import exists in this
  application layer.
