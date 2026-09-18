# Project current state

## Active task

- `activeTaskId`: `US-02.T05`
- Status: `completed — awaiting PR review`
- Base commit: `f1dc2ec4a45ea6190a1d1b716b5ae03e01a51cf0`
- Working branch: `feature/us-02-canonical-identifiers`

## Evidence

- The full canonical guide and its three golden rules were reread before this task.
- The baseline, repository, and canonical-source inventories are complete.
- All six `.unitext` files are byte-verified UTF-16 LE sources.
- Documentation skeletons and an ADR template now establish stable locations for future architecture, API, database, pipeline, security, operations, and test evidence.
- The initial risk and ambiguity register is recorded in `docs/project-risk-register.md`; no risk is silently accepted.
- Canonical IDs for questionnaire questions/answers, loan variables, categories, routes, and future loan identity are versioned in `data/contracts/canonical-identifiers.v1.json` and statically validated.
- Pure, framework-independent schema and Persian scalar parser contracts are versioned and unit tested; ambiguous ranges/prose remain typed unknowns.
- A read-only source audit and provenance report record source hashes, structural coverage, numeric coefficient ranges, loan-row evidence, and blocking core-value issues.
- Versioned data decisions define the Q5 interest weight, neutral deposit-feature behavior, core-value ranking exclusion, and display-only source columns.
- Versioned golden contract fixtures cover every canonical question and the complete, neutral, and core-unknown loan-policy boundaries without asserting an engine score prematurely.
- No product behavior, data interpretation, backend, database, secret, or deploy configuration was changed.

## Test record

| Command | Result |
| --- | --- |
| `npm run build` | Passed; Vite production build completed. |

## Blockers and next task

- Docker/Compose is unavailable in this environment; Docker-dependent verification belongs to its assigned future task.
- The prototype has no automated lint/typecheck/test suite yet; this remains recorded baseline risk.
- `US-01` was merged in PR #3.
- `US-02` is complete and awaiting PR review/merge. Only then may `US-03.T01` begin.

## Compatibility pointer

This is the canonical current-state checkpoint required by the guide. `docs/progress/current-state.md` is retained only as historical context for earlier commits.
