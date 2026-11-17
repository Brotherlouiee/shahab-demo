# Core/Wallet Phase 2 — checkpoint (WIP)

**State: IN_PROGRESS — no package RA/IPA accepted; no software implemented.**

## Immutable baseline
- Main commit: `f4167f8ceccec24cc10d70e158c82cbf3c9eeacf`.
- Blueprint V1.6 blob: `9681c2bf6c3149317c3788516748084cfb6eac7c`.
- Wallet V0.20 blob: `1f3dc55f46b3a12b2eb33e647355e4a6a73dd37a`.

## Canonical registry
- `docs/phase2/core/CORE_REGISTRY.jsonl` is the sole unit-level source register; it holds exactly 2,230 deterministic units indexed from both approved documents, including Markdown table rows and Mermaid diagrams.
- All source units are indexed only: `U` (unreviewed) or `I` (structural/index-only). **No requirement count or RA claim derives from this inventory.**
- Excluded as sources: deleted obsolete Phase 2 plan and audit, PR #247 and rebuild branches.

## Package execution order
1. C01 (RA then IPA pilot)
2. C02, C03, C04, C05a, C05b, C06
3. C07, C12a, C08, C09
4. C10, C11a, C11b, C12b, C13a
5. C13b, C14, cross-package semantic audit

## Current evidence / decisions
- Existing Phase 1 code inspected read-only: `backend/app/main.py`, `backend/app/api/v1/router.py`, `backend/app/accounts/access.py`, `backend/app/questionnaire/infrastructure/sqlalchemy_sessions.py`, `backend/app/recommendation/application/use_cases.py`, `backend/app/recommendation/engine/canonical_scoring.py`, `backend/app/data_pipeline/application/publish_serving_version.py`, `backend/app/infrastructure/db/models.py`, and Docker Compose files.
- Code files are **evidence of implementation footprint, not running/verified product acceptance**.
- Blueprint §22.8 line 1923 contains an older assertion that target architecture is not selected. The later explicitly approved A01 at lines 16–26 and §5.12 line 2140 governs; do not reopen architecture choice.
- No new fixed dates, budgets, physical storage choices or software tasks inferred from undecided implementation details.

## Restart protocol
- Read this checkpoint and latest branch HEAD; compare with recorded baseline; preserve concurrent work.
- Verify registry readback and size (<1 MB), then inspect relevant source units for C01 and independently challenge each proposed requirement.
- **Do not create accepted Story/Task/AC/Test until C01 RA passed.**
- After RA, inspect further live code evidence, perform C01 IPA and assess pilot method before moving to C02.
- Next source context to inspect: Blueprint A01 lines 16–26, §§5.2.1 lines 1960–2022, §§22.1–22.8 lines 1770–1923, A02–A09 lines 1192–1216 and cross-section 2254, Wallet §2 infrastructure and §7 ledger.

## Gates
- C01: RA=NOT_STARTED; IPA=NOT_STARTED.
- All other packages: RA=NOT_STARTED; IPA=NOT_STARTED.
- Core overall: **NOT_COMPLETE**. No PR, merge, or implementation as part of this planning checkpoint.
