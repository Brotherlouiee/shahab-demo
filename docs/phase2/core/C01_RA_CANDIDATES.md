# C01 — Requirement candidates (pre-RA)

**Status: RA_IN_REVIEW / IPA_NOT_STARTED. These are candidates, not an accepted specification or implementation authorization.**

Sources: Blueprint V1.6 (blob 9681c2bf6c3149317c3788516748084cfb6eac7c), Wallet V0.20 (blob 1f3dc55f46b3a12b2eb33e647355e4a6a73dd37a) at main f4167f8ceccec24cc10d70e158c82cbf3c9eeacf.

| Candidate ID | Source references | Candidate norm / boundary |
|---|---|---|
| REQ:CORE:001 | B:16-26؛ B:1956 | Core is a modular monolith with explicit internal module boundaries; no forced service-per-module split. |
| REQ:CORE:002 | B:16-26؛ B:788-794 | Adviser/RAG has independent deployment and independent data ownership from Core. |
| REQ:CORE:003 | B:16-26؛ B:2061-2063 | Assistant is an independent target service; R1 permits only its boundary/contracts, not running deployment. |
| REQ:CORE:004 | B:16-26؛ B:2061-2071 | R1 may reuse current VM, PostgreSQL and Redis, subject to validation; logical ownership remains separate. |
| REQ:CORE:005 | B:1192-1216؛ B:1212 | Service private schemas, data, jobs and transactions must have one owner; no direct cross-service private-table reads/writes. |
| REQ:CORE:006 | B:869-871؛ B:1212-1214 | Core exposes versioned and authorized data/domain/catalogue interfaces with minimal fields, provenance, version and error behavior. |
| REQ:CORE:007 | B:1825-1829؛ B:1986 | No cross-module cyclic dependencies or private ORM leakage; reuse existing common capabilities instead of parallel authorities. |
| REQ:CORE:008 | B:1192-1216؛ B:1627-1633 | Core retains deterministic loan recommendation, matching, reasons, loan rules and published serving Snapshot. |
| REQ:CORE:009 | B:1216؛ B:2075-2079 | A recommendation run uses one compatible published product Snapshot and rule version, never synthetic results after Core failure. |
| REQ:CORE:010 | B:1192؛ B:916-918 | Short deterministic operations use synchronous APIs; long owner-controlled work uses durable asynchronous Job workflows when needed. |
| REQ:CORE:011 | B:916-918؛ B:1835 | Each Job owner persists state/result in PostgreSQL and exposes versioned ports/adapters, safe cancel/resume and recovery. |
| REQ:CORE:012 | B:1192؛ B:1216؛ B:1833 | Use transactional outbox only where reliable events are necessary; consumers deduplicate and publishers recover safely. |
| REQ:CORE:013 | B:1192؛ B:1212-1216 | Keep local service transaction boundaries; no default cross-service distributed transaction or global database ownership. |
| REQ:CORE:014 | B:16-26؛ B:1192؛ B:1913 | Apply bounded timeouts, circuit breakers, limited transient retries with backoff, bulkheads and controlled degradation. |
| REQ:CORE:015 | B:1827؛ B:1907 | Contracts are defined in versioned OpenAPI/schema before breaking changes and tested for structural and semantic consumer compatibility. |
| REQ:CORE:016 | B:1827؛ B:1907؛ B:2075 | Breaking changes use new version or expand/migrate/contract with tested provider-consumer matrix and error contract. |
| REQ:CORE:017 | B:16-26؛ B:1917 | Separate typed/validated operational config, secrets, feature flags and business policies; financial policy cannot be a free-form toggle. |
| REQ:CORE:018 | B:16-26؛ B:1917؛ B:2106 | Config/flag changes require owner permission, diff, audit, secret protection, dependency checks and rollback safety. |
| REQ:CORE:019 | B:16-26؛ B:1192؛ B:1837 | OpenTelemetry logs/metrics/traces use nonidentifying correlation IDs; no OTP, token, identity or raw questionnaire in telemetry. |
| REQ:CORE:020 | B:16-26؛ B:1903؛ B:1913 | SLO, alerts, runbooks, CPU/RAM and incident controls require measured baselines, not invented thresholds. |
| REQ:CORE:021 | B:16-26؛ B:1903 | SigNoz is conditional evaluation; self-hosting on the current production VM requires approved resource evidence. |
| REQ:CORE:022 | B:1761-1762؛ B:2284-2288؛ B:2326-2332 | Preserve phase-one routes, identity, questionnaire, scoring, data publication and UI with targeted regression evidence. |
| REQ:CORE:023 | B:2282؛ B:2295-2299؛ B:2328 | Database evolution follows Alembic and PostgreSQL migration/restore checks; current migration count and runtime SHA require independent proof. |
| REQ:CORE:024 | B:1938-1940؛ B:2024-2058؛ B:2234-2238 | Distinguish stage completion from increment release readiness; Wallet/Billing cannot be hard dependencies of first RAG release. |
| REQ:CORE:025 | B:1942-2022؛ B:2189-2196 | Apply 22 implementation principles, one developer plus Codex capacity, evidence-backed estimates and Discovery/Delivery balance. |
| REQ:CORE:026 | B:2002-2022؛ B:2192؛ B:2198-2219 | Map R1-R4, RG/REL and F06 to every future release; safe rollback, security stop and independent high-risk review cannot be waived. |
| REQ:CORE:027 | B:2195؛ B:2232-2250 | Keep all approved scope including deferred wallet items; COV gate and bidirectional trace cannot be replaced by a feature checklist. |
| REQ:CORE:028 | B:1412-1443؛ B:2286-2290 | Keep Session Context, same-domain Conversation Continuity, User Memory and Case/Workflow State as separate authorities. |
| REQ:CORE:029 | B:2286-2290؛ B:1688-1690 | Reuse existing account authority; personal memory must be lawful, user-controllable and distinct from financial retained evidence. |
| REQ:CORE:030 | B:1194-1214؛ B:1604-1629 | Keep legal knowledge, product authority and user-private data separate; Core owns canonical product calculations. |
| REQ:CORE:031 | B:1770-1776؛ B:1921-1923؛ B:2254 | A01 overrides historical architecture comparison; old claim that architecture is undecided is superseded. |
| REQ:CORE:032 | B:1881-1903؛ B:2061-2075 | Require workload, cost and failure evidence before adding physical infrastructure or extracting further services. |
| REQ:CORE:033 | B:2236؛ W:51-60؛ W:1161-1175 | Wallet remains a modular Core financial capability, not a prerequisite of first RAG increment and not an external-merchant wallet. |
| REQ:CORE:034 | B:1253-1281؛ B:2079؛ B:2287 | R1 shell preserves current loan questionnaire/results and renders Assistant as inactive/coming soon. |
| REQ:CORE:035 | B:2106؛ B:2198-2217؛ B:2248-2256 | Release must verify environment-specific code/config/contract/Snapshot/Job rollback, authorization and risk-governance evidence. |
| REQ:CORE:036 | B:2326-2334؛ B:1913-1917 | CI-only or file presence must not be called semantic validation or production proof; record tests not executed separately. |

## Critical interpretation guards

- A01 at B:16–26 is the binding architecture. The historical assertion B:1923 that target architecture is unchosen is SUPERSEDED for this question; no architecture reset.
- RAG service knowledge and Assistant workflows do not become Core capabilities because Core owns their shared contracts.
- W:51–60 and W:1161–1175 are wallet scope/ledger decisions, not an instruction to build wallet in first RAG release.
- Every implementation choice still open (physical schema, tool, runtime limits, service separation, pricing and release date) stays OPEN.

## RA gate still pending

The inventory alone does not prove semantic coverage. Independently re-read all C01-relevant paragraphs, tables, diagrams and constraints, split composite candidates, check duplicates and owners, and map each to a reviewed source unit. No Story, Task, AC or Test may be approved until the package's RA review has passed. This artifact has no proposed software tasks.
