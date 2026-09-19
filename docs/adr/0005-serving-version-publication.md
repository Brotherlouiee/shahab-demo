# ADR 0005: immutable approved serving versions

## Status

Accepted for US-05.T04.

## Context

Raw source imports need reviewable publication without allowing a partially
imported or unapproved catalogue to affect recommendations.

## Decision

Canonical rows are immutable value objects with source-row fingerprints. A draft
version stores its diff; a named operator approves it with a reason; only the
repository atomic-publication operation can change the active serving pointer.
The previous version is superseded, never overwritten.

## Consequences

The current in-memory adapter is test/local evidence only. A PostgreSQL adapter,
real transaction and rollback operation will be added in later US-05 work.
No public endpoint is exposed before US-10 authorization and audit controls.
