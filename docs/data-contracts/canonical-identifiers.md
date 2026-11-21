# Canonical identifiers — US-02.T01

## Purpose and scope

This contract fixes stable machine identifiers before parsers, schemas, database models, recommendation logic, or UI adapters are implemented. Persian wording remains a display label only. The machine-readable source of truth is `data/contracts/canonical-identifiers.v1.json`.

## Identifier rules

- `questionId` is one of `Q1`–`Q6`, `S7`, `S8`, `S10`, `S13`.
- `answerId` is `questionId.semanticAnswerKey`; it is never a screen index, option position, or display copy.
- `loanVariableId` is one of the eight fixed identifiers in the canonical guide.
- `categoryId` is unique within its `loanVariableId`; boundary semantics remain a `US-02.T02` parser/schema responsibility.
- `loanId` is an opaque immutable UUID assigned during approved ingestion. It is not a bank name, loan name, spreadsheet row, slug, or source hash.
- `sourceRowFingerprint` is provenance metadata only and must never be exposed as a business identifier.

## Source mapping

| Current route | Canonical `questionId` | Source questionnaire row |
| --- | --- | ---: |
| `/question/3` | `Q1` | 1 |
| `/question/4` | `Q2` | 2 |
| `/question/5` | `Q3` | 3 |
| `/question/6` | `Q4` | 4 |
| `/question/7` | `Q5` | 5 |
| `/question/8` | `Q6` | 6 |
| `/question/9` | `S7` | 7 |
| `/question/10` | `S8` | 8 |
| `/question/11` | `S10` | 10 |
| `/question/12` | `S13` | 13 |

The first two questionnaire routes are intentionally outside this contract. Implementation of this route adapter is deferred to `US-07.T02`; this task only locks its identifiers.

## Category contract

The JSON contract contains exactly the source-defined category counts: 8 for `maxAmount`, 6 for `monthlyInstallment`, 6 for `maxRepaymentMonths`, 5 for `interestRate`, 2 for `depositRequired`, 5 for `depositHoldingMonths`, 4 for `loanToDepositRatio`, and 3 for `guaranteeType`.

No category boundary is inferred here. Known source gaps or ambiguous boundary wording are recorded by `US-02.T02`/`T03` and require a versioned, testable decision before ranking.

## Change control

Changing any identifier is a breaking data-contract change. It requires a new contract version, migration/compatibility plan, data-decision or ADR, static validation update, and review before merge. Changing Persian display text alone must not change an identifier.
