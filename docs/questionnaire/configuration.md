# Questionnaire configuration — US-07.T01

`data/contracts/questionnaire-configuration.v1.json` is the approved,
source-derived configuration for the behavioural-preference questionnaire. It
contains exactly ten required canonical questions (`Q1`–`Q6`, `S7`, `S8`,
`S10`, `S13`) and fifty stable `answerId` values. The human-facing prompt and
answer labels are copied from the verified UTF-16LE questionnaire source; a
configuration answer is never identified by its display position.

## Contract and provenance

| Field | Rule |
| --- | --- |
| `schemaVersion` | `1.0.0`; incompatible changes create a new artifact/version. |
| `questionnaireVersion` | `behavioral-preference.v1`; identifies this approved wording/answer set. |
| `source.path` / `source.sha256` | The immutable verified source path and SHA-256. |
| `questionId` | Must follow `canonical-identifiers.v1.json` in its approved order. |
| `sourceQuestionNumber` | Provenance only; it is not a browser route or persistent UI index. |
| `answerId` | `<questionId>.<semantic-answer-key>`; no positional/index identifier is allowed. |
| `required` | All ten canonical questions are required before a recommendation can be requested. |

`python scripts/validate_questionnaire_configuration.py` validates the artifact
against canonical IDs, the six-source inventory hash, and the source prompt/
option order. The command is read-only and part of `npm run quality`.

## Explicitly deferred

No route mapping, session, persistence, API, UI flow, scoring or recommendation
output is introduced in this task. `US-07.T02` owns the `/question/3..12`
adapter; `US-07.T03` owns session retention and response validation; `US-07.T04`
owns UI integration.
