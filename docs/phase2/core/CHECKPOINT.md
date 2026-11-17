# Core/Wallet Phase 2 — checkpoint (C01 recovery)

**Derived from [CORE_REGISTRY.jsonl](CORE_REGISTRY.jsonl); no independent status authority.**

**C01 RA=PASS; IPA=PASS at planning-definition level. Core overall: NOT_COMPLETE.**

Source main: `f4167f8ceccec24cc10d70e158c82cbf3c9eeacf`. Recovery parent: `6a52b8ded941b39e4439b338e1c25f541a3b528e`. Recovery branch: `docs/phase2-c01-ra-ipa-recovery-20261117`.

Blueprint V1.6: `9681c2bf6c3149317c3788516748084cfb6eac7c`. Wallet V0.20: `1f3dc55f46b3a12b2eb33e647355e4a6a73dd37a`.

## Verified state

| Metric | Count |
| --- | --- |
| records | 2554 |
| source_units | 2230 |
| C01_reviewed | 510 |
| requirements | 40 |
| atomic_behaviours | 128 |
| enablers | 4 |
| tasks | 13 |
| subtasks | 39 |
| dependencies | 23 |
| AC | 40 |
| test_definitions | 40 |
| test_scenarios | 120 |
| product_test_executions | 0 |
| decision_gates | 9 |
| contracts | 7 |
| code_inspections | 28 |

The original 2,230 count is source units, not all JSONL records. 510 C01 units now carry RA dispositions; all non-C01 source-unit records are unchanged. 40 REQ, four Enablers, 13 Tasks and 23 dependency edges are preserved. 128 atomic behaviours, 40 AC, 40 test definitions/120 scenarios are linked. Product tests executed: zero.

## Recovery corrections

- Prior checkpoint predated six later commits and incorrectly reported RA/IPA NOT_STARTED.
- RA readback had PASS with units still U/I; C01 semantic classifications, qualifiers and precise references are now explicit.
- The old readable RA view predated IPA task creation. Both views now derive from the current registry.
- Restore explicit current-VM SigNoz prohibition, universal synchronous-call timeout and old-engine in-flight completion.
- Original candidate dispositions and 22 planning principles remain in the registry.

## Open decisions and implementation boundary

Nine OPEN_DECISION records cover physical schema/topology, worker technology, numeric resilience, telemetry/hosting, API support/EOL, runtime/environment evidence, release dossier, financial activation and secret lifecycle. Dependent implementation is BLOCKED_BY_DECISION. No code/deploy/banking or production test is authorized by planning PASS. C03/C05b/C07/C12a and other handoffs are not accepted packages.

## Evidence and checks

28 source inspections are pinned to commit/blob; they prove footprint, not runtime. Source/trace/DAG/unchanged-scope validation and eight corruption rejection checks passed. The embedded VALIDATE:C01:RECOVERY procedure reproduces checks. Semantic review and negative/concurrency sufficiency review are separate from structural PASS; both passes used the same agent. Independent high-risk specialist review remains a future release requirement.

## Safe restart and next boundary

- Read latest remote HEADs and source blobs; compare any new original-branch commits.
- Continue in the isolated recovery worktree/branch. Never reset/delete/force-push the original planning branch. Stable remote HEAD does not prove prior execution stopped.
- C01 last complete step: IPA planning definitions and validation. Next action in this mission: STOP; do not start C02.
- Before any later implementation, resolve applicable decisions, authorize task scope/environment and execute its defined tests; missing runtime evidence stays unknown.
- Preserve five planning stages: 18 Core/Wallet, 10 RAG/Adviser, 8 Assistant, integrated dependency graph, weekly roadmap under 22 principles.

## Execution discipline

Three golden rules retained: isolated staged changes; source/canonical/protocol constraints and phase-one design preserved; evidence/validation/checkpoint/commit before planning completion. This change touches only the three authorized planning files. Runtime, UI, scoring, data and workflows are unchanged. No previous plan/PR247 is an extraction source.

Timing: earlier review/specification duration was not measured. Recorded validation/publication interval starts `2026-11-17T10:09:54.508087+00:00`; commit timestamps do not measure active time. Token/cost figures are unavailable and are not estimated.
