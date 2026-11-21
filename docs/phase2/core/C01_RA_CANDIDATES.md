# C01 — بازاعتبارسنجی RA و برنامه اجرایی IPA

**نمای مشتق از [CORE_REGISTRY.jsonl](CORE_REGISTRY.jsonl)؛ مرجع مستقل نیست.**

**RA=PASS؛ IPA=PASS در سطح تعریف برنامه.** هیچ نرم‌افزار، آزمون محصول، انتشار، استقرار یا پذیرش بسته دیگری انجام نشده است. تصمیم‌های باز و مجوزهای اجرا جدا باقی می‌مانند.

## خط مبنا و ایمنی

- Source main: `f4167f8ceccec24cc10d70e158c82cbf3c9eeacf`
- Recovery parent: `6a52b8ded941b39e4439b338e1c25f541a3b528e`
- Recovery branch: `docs/phase2-c01-ra-ipa-recovery-20261117`
- Blueprint V1.6: `9681c2bf6c3149317c3788516748084cfb6eac7c`
- Wallet V0.20: `1f3dc55f46b3a12b2eb33e647355e4a6a73dd37a`
- Worktree مستقل؛ شاخه قبلی حفظ می‌شود. ادامه یا ادغام بعدی نیازمند بررسی HEAD و تغییرات جدید آن است.

## نتیجه و شمارش

| شاخص | مقدار |
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

این ۱۲۸ رفتار، تفکیک کنترل‌های داخل همان ۴۰ شناسه الزام‌اند؛ ۱۲۸ نیازمندی جدید یا ۱۲۰ آزمون اجراشده نیستند. ۳۹ زیرتسک از سه زیرتسک موجود هر تسک شناسه گرفته‌اند. چهار مورد بالادستی Technical Enabler هستند؛ User Story مصنوعی ایجاد نشده است.

## شواهد RA

۵۱۰ واحد دامنه قبلی با ارجاع نسخه‌دار، SHA متن، طبقه‌بندی و تعیین تکلیف C01 بازخوانی شدند. واحدهای خارج از دامنه بدون تغییرند. `st=RA` فقط مرور از منظر C01 را بیان می‌کند؛ handoff به بسته دیگر پذیرش آن بسته نیست. در واحدهای مرکب، `semantic_review.clauses` وضعیت‌های متفاوت حکم، شرط، مثال و تصمیم باز را نگه می‌دارد. مرجع رفتار اتمی، `req.behaviours` است.

| طبقه اصلی واحد | تعداد |
| --- | --- |
| APPROVED_EXPLICIT | 271 |
| CONTEXT | 154 |
| EXAMPLE | 22 |
| OPEN_DECISION | 10 |
| PROPOSAL | 51 |
| SUPERSEDED | 2 |

اصلاح‌های هدفمند: REQ:CORE:021 منع SigNoz روی ظرفیت ثبت‌شده VM فعلی را صریح می‌کند؛ REQ:CORE:037 Timeout را به همه فراخوانی‌های هم‌زمان بین‌سرویسی تعمیم می‌دهد؛ REQ:CORE:042 تکمیل Job جاری در موتور قبلی را حفظ می‌کند. جدول‌های فناوری و نمودارهای تاریخی زیر A01 تفسیر می‌شوند؛ Neo4j، Temporal، Broker و سه VM انتخاب قطعی تلقی نشده‌اند.

بازبینی دوم با تلاش برای نقض هر الزام انجام شد. هر دو مرور را همان عامل در دو گذر انجام داده است؛ بازبین انسانی/عامل مستقل ادعا نمی‌شود. بازبینی تخصصی مستقل تغییر پرریسک، شرط انتشار آینده باقی است.

| گیت | وضعیت |
| --- | --- |
| IPA | PASS |
| P0 | PASS |
| P1 | PASS |
| P2 | PASS |
| P3 | PASS |
| P4 | PASS |
| P5 | PASS |
| P6 | PASS |
| RA | PASS |

P0 منابع؛ P1 تعیین تکلیف دامنه؛ P2 انطباق/شروط؛ P3 مالک/تسک؛ P4 AC/تعریف آزمون؛ P5 قرارداد/وابستگی؛ P6 ساختار/ردیابی. PASS برنامه به معنی اجرای S1–S5، G-COV، RG/REL/F06 یا گیت مالی/انتشار نیست.

## Technical Enablerها

| شناسه | هدف | تسک‌ها |
| --- | --- | --- |
| TE:CORE:001 | Baseline and modular Core architecture | TASK:CORE:001, TASK:CORE:002, TASK:CORE:003 |
| TE:CORE:002 | Core/Adviser contracts, snapshots and job/event boundaries | TASK:CORE:004, TASK:CORE:005, TASK:CORE:006, TASK:CORE:008 |
| TE:CORE:003 | Resilience, configuration and privacy-aware telemetry | TASK:CORE:007, TASK:CORE:009, TASK:CORE:010 |
| TE:CORE:004 | Incremental rollout, capacity and finance boundary protection | TASK:CORE:011, TASK:CORE:012, TASK:CORE:013 |

## تسک‌های موجود و طرح نهایی C01

مالک تدوین همه موارد C01 است. ستون مالک پیاده‌سازی فقط handoff برنامه را مشخص می‌کند؛ هیچ بسته دریافت‌کننده در این مأموریت پذیرفته نشده است. `BLOCKED_BY_DECISION` مانع اجرای انتخاب وابسته است؛ وجود تعریف معیار/آزمون این مانع را رفع نمی‌کند. هیچ عدد زمان/هزینه/توکن یا تعهد هفتگی جعل نشده است.

### TASK:CORE:001 — Verify phase-one code/data/migration and regression baseline without assuming production state

مالک پیاده‌سازی: `C01`؛ وضعیت کد: `EXISTING_PARTIAL`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** locked main and safe read-only code inventory

**تحویل:** source-locked current-vs-target capability and migration baseline

**الزامات:** REQ:CORE:022, REQ:CORE:023

**قراردادها:** مرجع پایه؛ بدون قرارداد شبکه تازه

**گیت تصمیم:** DECISION:C01:06

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:001.S01 | Map real routes/schemas/dependencies and preserved behavior |
| TASK:CORE:001.S02 | Verify Alembic heads/history against actual PostgreSQL test environment |
| TASK:CORE:001.S03 | Record tag/release digest and E2E evidence; mark unknown if runtime inaccessible |

**AC:** AC:CORE:C01:022, AC:CORE:C01:023

**Test:** TEST:CORE:C01:022, TEST:CORE:C01:023

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `backend/app/api/v1/router.py` — Composes existing account, health, loans, questionnaire, profiles, recommendation/history and bookmarks; no Adviser route observed
- `backend/app/accounts/access.py` — OTP provider port, challenge/session lifecycle and actor authority exist
- `backend/app/questionnaire/infrastructure/sqlalchemy_sessions.py` — PostgreSQL-backed answers/flow, commits and rollback paths exist
- `src/home page.jsx` — Existing frontend asset is preserved; changes need accepted baseline
- `backend/tests/test_postgresql_migrations.py` — Destructive test setup downgrades base: use disposable test PostgreSQL only
- `docker-compose.prod.yml` — Pinned deployment configuration is not proof of actual VM image

### TASK:CORE:002 — Define and test modular Core boundaries and independent service data ownership

مالک پیاده‌سازی: `C01`؛ وضعیت کد: `EXISTING_PARTIAL`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** T001 baseline

**تحویل:** module ownership map, architecture policy test specification and service data authority matrix

**الزامات:** REQ:CORE:001, REQ:CORE:005, REQ:CORE:007, REQ:CORE:013

**قراردادها:** CONTRACT:C01:01

**گیت تصمیم:** DECISION:C01:01

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:002.S01 | Map module ownership and public ports |
| TASK:CORE:002.S02 | Specify forbidden private ORM/table access and dependency DAG |
| TASK:CORE:002.S03 | Specify local transaction boundaries and regression safety |

**AC:** AC:CORE:C01:001, AC:CORE:C01:005, AC:CORE:C01:007, AC:CORE:C01:013

**Test:** TEST:CORE:C01:001, TEST:CORE:C01:005, TEST:CORE:C01:007, TEST:CORE:C01:013

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `backend/app/main.py` — Composition root wires repositories and application middleware; ownership hardening needs architecture tests
- `backend/app/infrastructure/db/models.py` — Shared ORM models exist; not proof of validated phase-two private boundaries

### TASK:CORE:003 — Specify R1 Core/Adviser deployment and future Assistant boundary on existing infrastructure

مالک پیاده‌سازی: `C01`؛ وضعیت کد: `NEW`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** T002 authority map and R1 scope approval

**تحویل:** R1 topology and independent release-boundary acceptance contract without deployment

**الزامات:** REQ:CORE:002, REQ:CORE:003, REQ:CORE:004, REQ:CORE:049

**قراردادها:** CONTRACT:C01:02

**گیت تصمیم:** DECISION:C01:01, DECISION:C01:05

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:003.S01 | Define two R1 deployment units, Assistant interface only |
| TASK:CORE:003.S02 | Define shared-host resource and logical tenant/schema separation |
| TASK:CORE:003.S03 | Specify R1 boot/integration and no-Wallet dependency checks |

**AC:** AC:CORE:C01:002, AC:CORE:C01:003, AC:CORE:C01:004, AC:CORE:C01:049

**Test:** TEST:CORE:C01:002, TEST:CORE:C01:003, TEST:CORE:C01:004, TEST:CORE:C01:049

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `docker-compose.prod.yml` — Current services describe phase-one deployment; independent Adviser topology still design work
- `backend/app/api/v1/router.py` — No running Assistant/Adviser inferred from route inventory

### TASK:CORE:004 — Preserve deterministic loan recommendation under one published snapshot and expose versioned contract

مالک پیاده‌سازی: `C05b`؛ وضعیت کد: `REUSE`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** T001 baseline, T008 contract design

**تحویل:** Core recommendation consumer contract and golden/nonregression test plan

**الزامات:** REQ:CORE:008, REQ:CORE:009

**قراردادها:** CONTRACT:C01:02

**گیت تصمیم:** DECISION:C01:05

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:004.S01 | Freeze existing golden semantics and published snapshot authority |
| TASK:CORE:004.S02 | Specify synchronous recommendation result schema, version and provenance |
| TASK:CORE:004.S03 | Specify failure/invalid-snapshot handling without fabricated match |

**AC:** AC:CORE:C01:008, AC:CORE:C01:009

**Test:** TEST:CORE:C01:008, TEST:CORE:C01:009

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `backend/app/recommendation/application/use_cases.py` — RecommendCanonicalLoans reads one approved snapshot and passes it to execute_for_snapshot
- `backend/app/recommendation/engine/canonical_scoring.py` — Existing deterministic scorer is reuse target
- `backend/app/data_pipeline/application/publish_serving_version.py` — Publish and rollback require approved versions and local atomic repository methods
- `backend/tests/test_recommendation_engine_golden.py` — Existing golden suite is reuse evidence, not executed in planning
- `backend/tests/test_serving_publication.py` — Existing publication suite is a future regression target

### TASK:CORE:005 — Design service-owned durable job pattern without imposing one universal workflow engine

مالک پیاده‌سازی: `C03`؛ وضعیت کد: `NEW`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** T002 service ownership; owner-specific long-running use case

**تحویل:** versioned job pattern and worker-crash/migration test contract

**الزامات:** REQ:CORE:010, REQ:CORE:011, REQ:CORE:041, REQ:CORE:042

**قراردادها:** CONTRACT:C01:03

**گیت تصمیم:** DECISION:C01:02

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:005.S01 | Separate short synchronous calls from actual long jobs |
| TASK:CORE:005.S02 | Specify persistent job state/version and safe recovery |
| TASK:CORE:005.S03 | Define old-job completion vs new-engine routing criteria |

**AC:** AC:CORE:C01:010, AC:CORE:C01:011, AC:CORE:C01:041, AC:CORE:C01:042

**Test:** TEST:CORE:C01:010, TEST:CORE:C01:011, TEST:CORE:C01:041, TEST:CORE:C01:042

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `backend/app/questionnaire/infrastructure/sqlalchemy_sessions.py` — Existing persistence adapter illustrates boundaries, not a generic job engine

### TASK:CORE:006 — Specify transactional outbox and idempotent event consumption only for proven asynchronous flows

مالک پیاده‌سازی: `C03`؛ وضعیت کد: `NEW`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** T002 data ownership; demonstrable event consumer/use case

**تحویل:** minimal event/outbox protocol with fault-injection acceptance

**الزامات:** REQ:CORE:012, REQ:CORE:043, REQ:CORE:044

**قراردادها:** CONTRACT:C01:04

**گیت تصمیم:** DECISION:C01:02

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:006.S01 | Identify truly necessary reliable events |
| TASK:CORE:006.S02 | Specify atomic local writes and publisher recovery |
| TASK:CORE:006.S03 | Specify duplicate/out-of-order/unknown-schema consumer behavior |

**AC:** AC:CORE:C01:012, AC:CORE:C01:043, AC:CORE:C01:044

**Test:** TEST:CORE:C01:012, TEST:CORE:C01:043, TEST:CORE:C01:044

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `backend/app/data_pipeline/application/publish_serving_version.py` — Atomic publishing interface exists; does not establish an Outbox publisher

### TASK:CORE:007 — Specify bounded cross-service resilience and interactive/background isolation

مالک پیاده‌سازی: `C03`؛ وضعیت کد: `NEW`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** T003 and T008 service-contract interfaces

**تحویل:** fault matrix and testable resilience contract, numeric thresholds ESTIMATION_REQUIRED

**الزامات:** REQ:CORE:037, REQ:CORE:038, REQ:CORE:039, REQ:CORE:040

**قراردادها:** CONTRACT:C01:03, CONTRACT:C01:06

**گیت تصمیم:** DECISION:C01:03

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:007.S01 | Set timeout budget from tested path baseline |
| TASK:CORE:007.S02 | Bound transient retry and circuit state transitions |
| TASK:CORE:007.S03 | Separate concurrency pools and graceful degradation |

**AC:** AC:CORE:C01:037, AC:CORE:C01:038, AC:CORE:C01:039, AC:CORE:C01:040

**Test:** TEST:CORE:C01:037, TEST:CORE:C01:038, TEST:CORE:C01:039, TEST:CORE:C01:040

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `backend/app/core/config.py` — Some connection/provider timeouts exist; not a verified cross-service resilience matrix

### TASK:CORE:008 — Design Core API versioning and semantic provider/consumer compatibility verification

مالک پیاده‌سازی: `C03`؛ وضعیت کد: `EXISTING_PARTIAL`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** T002 authority matrix and existing API schema

**تحویل:** contract matrix and migration-safe OpenAPI evolution plan

**الزامات:** REQ:CORE:006, REQ:CORE:015, REQ:CORE:016

**قراردادها:** CONTRACT:C01:02

**گیت تصمیم:** DECISION:C01:05

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:008.S01 | Inventory existing versioned API and consumers |
| TASK:CORE:008.S02 | Specify schema-first compatible and breaking change protocol |
| TASK:CORE:008.S03 | Define consumer contract, semantic field and error tests |

**AC:** AC:CORE:C01:006, AC:CORE:C01:015, AC:CORE:C01:016

**Test:** TEST:CORE:C01:006, TEST:CORE:C01:015, TEST:CORE:C01:016

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `backend/app/api/v1/router.py` — Existing API v1 route authority is reused
- `backend/tests/test_recommendation_contract_fixtures.py` — Canonical fixture/version assertions exist; full provider/consumer matrix still absent

### TASK:CORE:009 — Separate typed runtime config, secrets, feature flags and protected financial business policy

مالک پیاده‌سازی: `C03`؛ وضعیت کد: `EXISTING_PARTIAL`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** T001 baseline and known policy owners

**تحویل:** four-category config contract and validation/rollback tests

**الزامات:** REQ:CORE:017, REQ:CORE:018, REQ:CORE:045, REQ:CORE:046

**قراردادها:** CONTRACT:C01:05

**گیت تصمیم:** DECISION:C01:09

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:009.S01 | Inventory present Settings and secret paths |
| TASK:CORE:009.S02 | Define schema, policy authorization, flag dependency and change audit |
| TASK:CORE:009.S03 | Design compatible config rollback and negative gate cases |

**AC:** AC:CORE:C01:017, AC:CORE:C01:018, AC:CORE:C01:045, AC:CORE:C01:046

**Test:** TEST:CORE:C01:017, TEST:CORE:C01:018, TEST:CORE:C01:045, TEST:CORE:C01:046

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `backend/app/core/config.py` — Pydantic Settings, SecretStr, env types and CORS validators exist; financial-policy versioned approval is separate
- `.github/workflows/security.yml` — Repository scan and dependency/SAST gates exist and must remain

### TASK:CORE:010 — Plan privacy-preserving OpenTelemetry and measured SLO/incident evidence

مالک پیاده‌سازی: `C03`؛ وضعیت کد: `EXISTING_PARTIAL`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** T001 operational footprint and realistic workload

**تحویل:** telemetry data-classification and SLO measurement/runbook acceptance contract

**الزامات:** REQ:CORE:019, REQ:CORE:020, REQ:CORE:021, REQ:CORE:047

**قراردادها:** CONTRACT:C01:06

**گیت تصمیم:** DECISION:C01:04

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:010.S01 | Map existing low-cardinality API observability |
| TASK:CORE:010.S02 | Specify trace context propagation without PII/OTP |
| TASK:CORE:010.S03 | Define measurement experiment and SigNoz decision gate |

**AC:** AC:CORE:C01:019, AC:CORE:C01:020, AC:CORE:C01:021, AC:CORE:C01:047

**Test:** TEST:CORE:C01:019, TEST:CORE:C01:020, TEST:CORE:C01:021, TEST:CORE:C01:047

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `backend/app/api/observability.py` — Bounded process-local counters and signals exist; explicitly not a durable monitoring sink or complete OpenTelemetry deployment
- `backend/tests/test_operational_observability.py` — Existing tests use privacy canaries and bounded counters; no production SLO proof

### TASK:CORE:011 — Implement planning-level stage/release separation and RG/REL/F06/COV evidence mapping

مالک پیاده‌سازی: `C01`؛ وضعیت کد: `REUSE`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** source-locked 22 principles and approved governance decision texts

**تحویل:** go/no-go and scope-completeness release evidence schema; no release authorized

**الزامات:** REQ:CORE:024, REQ:CORE:026, REQ:CORE:027, REQ:CORE:048

**قراردادها:** CONTRACT:C01:07

**گیت تصمیم:** DECISION:C01:07

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:011.S01 | Map risk and RG/REL/F06 controls without replacing them |
| TASK:CORE:011.S02 | Define stage completion vs incremental readiness evidence |
| TASK:CORE:011.S03 | Define independent high-risk reviewer, conditional go and rollback records |

**AC:** AC:CORE:C01:024, AC:CORE:C01:026, AC:CORE:C01:027, AC:CORE:C01:048

**Test:** TEST:CORE:C01:024, TEST:CORE:C01:026, TEST:CORE:C01:027, TEST:CORE:C01:048

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `.github/workflows/quality.yml` — Existing doc classification, quality, PostgreSQL and browser suites must remain
- `.github/workflows/security.yml` — Existing repository secret scan preserved

### TASK:CORE:012 — Protect modular Wallet/Ledger boundary and future service/contract integration without early financial activation

مالک پیاده‌سازی: `C07`؛ وضعیت کد: `NEW`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** W V0.20 and B A01/O5-13; finance-specific packages later

**تحویل:** wallet module boundary and finance handoff contract

**الزامات:** REQ:CORE:033

**قراردادها:** CONTRACT:C01:01, CONTRACT:C01:07

**گیت تصمیم:** DECISION:C01:01, DECISION:C01:08

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:012.S01 | Document closed-loop scope and Core module ownership |
| TASK:CORE:012.S02 | Prohibit external-merchant acceptance and early paid-flow assumption |
| TASK:CORE:012.S03 | Handoff ledger/credit policies to C07-C13 without duplicate implementation |

**AC:** AC:CORE:C01:033

**Test:** TEST:CORE:C01:033

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `backend/app/api/v1/router.py` — Financial Wallet route not observed; no Wallet implementation assumed

### TASK:CORE:013 — Benchmark real phase-two service capacity and justify any physical split or VM/telemetry deployment

مالک پیاده‌سازی: `C01`؛ وضعیت کد: `BLOCKED`؛ وضعیت اجرا: `BLOCKED_BY_DECISION`.

**ورودی:** authorized performance environment and safe workload; numeric budget gate pending

**تحویل:** evidence-based capacity decision; no arbitrary VM/SigNoz deployment

**الزامات:** REQ:CORE:032

**قراردادها:** CONTRACT:C01:06

**گیت تصمیم:** DECISION:C01:04, DECISION:C01:06

| زیرتسک | اقدام |
| --- | --- |
| TASK:CORE:013.S01 | Collect existing production/runtime resource baseline when authorized |
| TASK:CORE:013.S02 | Measure equal workloads and failure isolation |
| TASK:CORE:013.S03 | Compare cost and define explicit physical-extraction decision record |

**AC:** AC:CORE:C01:032

**Test:** TEST:CORE:C01:032

**شواهد خواندن کد، بدون ادعای آزمون اجراشده:**

- `docker-compose.prod.yml` — Configuration footprint only; no live CPU/RAM/concurrency evidence

## الزامات، شروط و آزمون‌های اختصاصی

برای هر الزام همه رفتارهای اتمی در نتیجه مثبت الزامی‌اند؛ سناریوی منفی و مرزی/هم‌زمانی باید جدا آزموده شود. همه تعریف‌ها `NOT_EXECUTED` هستند. fixture، محیط و شاهد نسخه‌دار در رکورد Test ثبت شده است.

### REQ:CORE:001 — Core is a modular monolith with explicit internal module boundaries; no forced service-per-module split.

مرجع: `B:20;B:1956`؛ مصوبه: `A01`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:002`.

**شرط:** All Core modules

**قید/استثنا:** No service-per-module mandate

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:001.B01 | Core remains a modular monolith |
| REQ:CORE:001.B02 | Module public boundaries and data authority are explicit |

**AC:CORE:C01:001 / TEST:CORE:C01:001** — `NOT_EXECUTED`

**محیط و fixture:** Static topology/module review plus architecture-policy fixture

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Compose Core with declared modules and public ports: deployment is one modular Core with a single owner per module |
| NEGATIVE | Propose one standalone service per module without evidence: architecture review rejects it |
| BOUNDARY_OR_CONCURRENCY | Add a module calling a private neighbour: boundary checker flags the edge rather than silently expanding public authority |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:002 — Adviser/RAG has independent deployment and independent data ownership from Core.

مرجع: `B:21;B:788;B:2063`؛ مصوبه: `A01, A02`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:003`.

**شرط:** Core and Adviser integration

**قید/استثنا:** A shared host is permitted, shared private-table authority is not

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:002.B01 | Adviser is independently deployable from Core |
| REQ:CORE:002.B02 | Adviser owns its knowledge data and accesses Core only through authorized contracts |

**AC:CORE:C01:002 / TEST:CORE:C01:002** — `NOT_EXECUTED`

**محیط و fixture:** Isolated Core/Adviser integration with PostgreSQL16 separate roles and versioned contract harness

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Deploy a compatible Adviser revision independently while Core version stays fixed: authorized API calls remain valid |
| NEGATIVE | Configure Adviser credentials to SELECT/UPDATE a Core-private table: DB access denied and no data leaked |
| BOUNDARY_OR_CONCURRENCY | Shared PostgreSQL instance with separate roles: own schema works while cross-schema grants remain absent |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:003 — Assistant is an independent target service; R1 permits only its boundary/contracts, not running deployment.

مرجع: `B:22-23;B:2063`؛ مصوبه: `A01`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:003`.

**شرط:** RAG R1

**قید/استثنا:** Future Assistant deployment needs its own approved release

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:003.B01 | R1 defines Assistant boundaries and versioned interfaces |
| REQ:CORE:003.B02 | R1 contains no running Assistant deployment or operational banking execution |

**AC:CORE:C01:003 / TEST:CORE:C01:003** — `NOT_EXECUTED`

**محیط و fixture:** R1 Compose/activation-manifest fixture; no production execution

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Review R1 manifest and interfaces: only Core/Adviser run; Assistant contract is recorded without worker or banking action |
| NEGATIVE | Enable Assistant worker or transactional route through a flag in R1: release gate blocks activation |
| BOUNDARY_OR_CONCURRENCY | A UI Coming Soon tab is allowed but cannot invoke an operational tool |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:004 — R1 may reuse current VM, PostgreSQL and Redis, subject to validation; logical ownership remains separate.

مرجع: `B:24;B:2063;B:2071`؛ مصوبه: `A01`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:003`.

**شرط:** Initial deployment planning

**قید/استثنا:** Physical separation requires security/capacity/resilience evidence and separate approval

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:004.B01 | Use current VM and PostgreSQL/Redis as a starting hypothesis, not proven capacity |
| REQ:CORE:004.B02 | Preserve logical service ownership on shared infrastructure |
| REQ:CORE:004.B03 | Do not infer three VMs or three database instances from three target services |

**AC:CORE:C01:004 / TEST:CORE:C01:004** — `NOT_EXECUTED`

**محیط و fixture:** Authorized shared-host performance sandbox; PostgreSQL16/Redis logical roles

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Evaluate existing-host Core/Adviser topology with measured limits and separate logical data roles |
| NEGATIVE | Demand three VMs solely from three target services: reject unsupported infrastructure commitment |
| BOUNDARY_OR_CONCURRENCY | Overload shared host in an authorized sandbox: report limit/hold decision without pretending existing host is sufficient |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:005 — Service private schemas, data, jobs and transactions must have one owner; no direct cross-service private-table reads/writes.

مرجع: `B:1192;B:1212;B:1825`؛ مصوبه: `A02, E02`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:002`.

**شرط:** All service and module private data

**قید/استثنا:** Only owner-authorized public contracts cross the boundary

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:005.B01 | Assign exactly one logical owner to private tables, schema, jobs and mutations |
| REQ:CORE:005.B02 | Deny direct cross-service private-table reads and writes |
| REQ:CORE:005.B03 | Deny direct cross-database foreign-key coupling and private tool access |

**AC:CORE:C01:005 / TEST:CORE:C01:005** — `NOT_EXECUTED`

**محیط و fixture:** PostgreSQL16 separate service roles plus import-boundary fixture

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Owner mutates own data through its transaction and exposes only permitted contract data |
| NEGATIVE | Adviser SELECT/UPDATE private Core table or import neighbour private ORM: deny and record boundary violation |
| BOUNDARY_OR_CONCURRENCY | Concurrent owner/consumer operations keep each commit local and reject a cross-database FK or consumer private-tool call |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:006 — Core exposes versioned and authorized data/domain/catalogue interfaces with minimal fields, provenance, version and error behavior.

مرجع: `B:869;B:1212-1214`؛ مصوبه: `A02, E02, B06`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:008`.

**شرط:** Core data, domain and catalogue consumers

**قید/استثنا:** Catalogue visibility alone grants neither personal-data access nor an action

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:006.B01 | Expose versioned contracts with owner, consumer, purpose and minimal fields |
| REQ:CORE:006.B02 | Enforce identity, scope and authorization before releasing data |
| REQ:CORE:006.B03 | Preserve stable reference, provenance, version/freshness, approval and access metadata |
| REQ:CORE:006.B04 | Absent valid data or authorization produces detectable error/completion request/safe stop, never table bypass or fabricated result |

**AC:CORE:C01:006 / TEST:CORE:C01:006** — `NOT_EXECUTED`

**محیط و fixture:** Core data/catalogue API fixture with PostgreSQL16 isolated roles, purpose/domain authorization and revocation races

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Authorized consumer with correct purpose requests minimal catalogue evidence: returns stable ID, source, version/freshness and approval |
| NEGATIVE | Unauthorized or wrong-domain consumer requests private field: deny before response and do not query private table as fallback |
| BOUNDARY_OR_CONCURRENCY | Revoke access between prior read and next call or supply stale/missing data: explicit stop/error, no fabricated recommendation |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:007 — No cross-module cyclic dependencies or private ORM leakage; reuse existing common capabilities instead of parallel authorities.

مرجع: `B:1827-1829;B:1986`؛ مصوبه: `A01, A07`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:002`.

**شرط:** Cross-module use and reuse

**قید/استثنا:** Reuse does not merge Adviser/Assistant domain logic or authorities

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:007.B01 | Prevent module dependency cycles |
| REQ:CORE:007.B02 | Forbid private ORM imports across public module boundaries |
| REQ:CORE:007.B03 | Reuse existing identity, permission and shared infrastructure authorities |

**AC:CORE:C01:007 / TEST:CORE:C01:007** — `NOT_EXECUTED`

**محیط و fixture:** Static import DAG and facade checks with forbidden-edge fixtures

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Build ownership map and directed imports through public ports, reusing existing account/permission authority |
| NEGATIVE | Inject domain-to-private-infrastructure import or cross-module ORM access: architecture check rejects |
| BOUNDARY_OR_CONCURRENCY | Add A-to-B and B-to-A edges or duplicate identity authority: cycle/parallel-authority check fails |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:008 — Core retains deterministic loan recommendation, matching, reasons, loan rules and published serving Snapshot.

مرجع: `B:1629-1633;B:2284`؛ مصوبه: `B06, A01`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:004`.

**شرط:** Loan recommendation in Adviser

**قید/استثنا:** Other domains need no recommendation engine merely because they have catalogue entries

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:008.B01 | Keep deterministic matching, ranking, reasons and rules in Core |
| REQ:CORE:008.B02 | Reuse the existing scorer and publication authority without reimplementing them in Adviser or frontend |
| REQ:CORE:008.B03 | Call Core synchronously for the short deterministic calculation |

**AC:CORE:C01:008 / TEST:CORE:C01:008** — `NOT_EXECUTED`

**محیط و fixture:** Existing backend golden/publication fixtures and Core/Adviser consumer harness

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Run existing golden loan fixtures through Core API consumer: matching, reasons and versions retain canonical meaning |
| NEGATIVE | Frontend/Adviser supplies its own computed score or modifies rules: consumer/integrity test rejects it |
| BOUNDARY_OR_CONCURRENCY | Present catalogue-only product in another domain: no dedicated engine is created without validated rules/use case |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:009 — A recommendation run uses one compatible published product Snapshot and rule version, never synthetic results after Core failure.

مرجع: `B:1216;B:2075;B:2326`؛ مصوبه: `A05, B06`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:004`.

**شرط:** Every loan recommendation run

**قید/استثنا:** Non-sensitive cache can be eventually consistent but cannot supply authoritative scoring

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:009.B01 | Use one valid published catalogue Snapshot and compatible rule version for the whole run |
| REQ:CORE:009.B02 | Concurrent publication never mixes versions within a result |
| REQ:CORE:009.B03 | Expose catalogue and rule versions, and reject invalid or unapproved input |
| REQ:CORE:009.B04 | Core failure produces explicit unavailability rather than synthetic recommendation |

**AC:CORE:C01:009 / TEST:CORE:C01:009** — `NOT_EXECUTED`

**محیط و fixture:** PostgreSQL16 publication/concurrent recommendation fixture and controlled Core outage

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Recommend with approved catalogue S1 and rule R1: result and reasons identify exactly S1/R1 |
| NEGATIVE | Supply draft/invalid Snapshot or sever Core API: return typed failure, no cached/synthetic match score |
| BOUNDARY_OR_CONCURRENCY | Publish S2/R2 while S1/R1 run is paused: old run finishes consistently at S1/R1 and next run uses a compatible published pair |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:010 — Short deterministic operations use synchronous APIs; long owner-controlled work uses durable asynchronous Job workflows when needed.

مرجع: `B:1192;B:2075`؛ مصوبه: `A03`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:005`.

**شرط:** Classifying a real operation

**قید/استثنا:** An independent broker is not a prerequisite

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:010.B01 | Use authenticated versioned synchronous API for short deterministic work |
| REQ:CORE:010.B02 | Use durable service-owned asynchronous Job only for actual long background work |
| REQ:CORE:010.B03 | Do not move short loan scoring behind a queue |

**AC:CORE:C01:010 / TEST:CORE:C01:010** — `NOT_EXECUTED`

**محیط و fixture:** Synchronous API and durable long-job harness without independent broker

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Short scoring call uses authorized synchronous API; actual long ingestion job returns durable job identity |
| NEGATIVE | Move scoring to mandatory broker or execute long job in request router with no durable state: reject design |
| BOUNDARY_OR_CONCURRENCY | No broker available but existing owner PostgreSQL/worker supported: long work remains recoverable while scoring stays synchronous |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:011 — Each Job owner persists state/result in PostgreSQL and exposes versioned ports/adapters, safe cancel/resume and recovery.

مرجع: `B:916-918;B:1835`؛ مصوبه: `A04`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:005`.

**شرط:** A service has a justified durable job

**قید/استثنا:** Redis is an optional execution queue, not authoritative state

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:011.B01 | Persist Job identity, state, attempts, error and result in owner PostgreSQL |
| REQ:CORE:011.B02 | Separate domain logic from engine via versioned Job/Workflow ports and adapters |
| REQ:CORE:011.B03 | Provide safe pause, resume and cancellation with audit and owner authority |

**AC:CORE:C01:011 / TEST:CORE:C01:011** — `NOT_EXECUTED`

**محیط و fixture:** PostgreSQL16 Job state plus controlled worker/cancel/resume races

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Create, pause and resume owned job: ID, state, attempts, error/result persist across process restart |
| NEGATIVE | Read status from transient LLM/session memory or consumer's private table: reject as authority |
| BOUNDARY_OR_CONCURRENCY | Cancel concurrently with completion/resume: one valid terminal outcome and durable audit, never duplicate side effect |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:012 — Use transactional outbox only where reliable events are necessary; consumers deduplicate and publishers recover safely.

مرجع: `B:1192;B:1216;B:1833`؛ مصوبه: `A05`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:006`.

**شرط:** A data change must emit a reliable event to a real consumer

**قید/استثنا:** No event bus, independent broker or distributed transaction required without demonstrated need

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:012.B01 | Commit business data and Outbox record in the same local transaction |
| REQ:CORE:012.B02 | Use outbox only for justified reliable asynchronous flows |
| REQ:CORE:012.B03 | Allow controlled eventual consistency only for non-sensitive cache/notification, not mixed financial Snapshots |

**AC:CORE:C01:012 / TEST:CORE:C01:012** — `NOT_EXECUTED`

**محیط و fixture:** PostgreSQL16 local transaction/Outbox fault injection

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Commit owner data and necessary Outbox event in one local transaction; non-sensitive cache may lag |
| NEGATIVE | Roll back business mutation: no event may escape; an event without real consumer does not justify a new broker |
| BOUNDARY_OR_CONCURRENCY | Crash at commit boundary and retry: event/data either both committed or neither, no mixed financial Snapshot accepted |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:013 — Keep local service transaction boundaries; no default cross-service distributed transaction or global database ownership.

مرجع: `B:1192;B:1216`؛ مصوبه: `A02, A05`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:002`.

**شرط:** Service data mutation

**قید/استثنا:** Cross-service distributed transaction is not the default

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:013.B01 | Keep transaction and commit authority local to data owner |
| REQ:CORE:013.B02 | Do not introduce a global database owner or distributed commit dependency |

**AC:CORE:C01:013 / TEST:CORE:C01:013** — `NOT_EXECUTED`

**محیط و fixture:** Isolated service DB transaction harness with remote service unavailable

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Commit a Core-owned mutation without remote commit authority while Adviser may be unavailable |
| NEGATIVE | Require Adviser commit to complete local Core transaction or grant global table ownership: reject boundary |
| BOUNDARY_OR_CONCURRENCY | Remote failure after local commit is handled by explicit contract/recovery, not silent two-phase commit or lost local state |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:015 — Contracts are defined in versioned OpenAPI/schema before breaking changes and tested for structural and semantic consumer compatibility.

مرجع: `B:1827;B:1907`؛ مصوبه: `A07`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:008`.

**شرط:** Every public contract change

**قید/استثنا:** Optional additions are compatible only when the consumer tolerates them

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:015.B01 | Owner changes versioned OpenAPI/Schema before implementation |
| REQ:CORE:015.B02 | Validate request/response structure, field meaning and financial units |
| REQ:CORE:015.B03 | Specify negative, boundary, property-based and consumer-driven contract tests |
| REQ:CORE:015.B04 | Treat financial semantic incompatibility as blocking, not a cosmetic schema warning |

**AC:CORE:C01:015 / TEST:CORE:C01:015** — `NOT_EXECUTED`

**محیط و fixture:** Versioned OpenAPI/provider-consumer/property-based fixture matrix

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Provider changes schema before implementation and runs consumer/property/negative fixtures covering financial field units |
| NEGATIVE | Keep JSON type unchanged but reinterpret match-percent as approval probability: semantic contract gate fails |
| BOUNDARY_OR_CONCURRENCY | Optional field plus intolerant old consumer: version matrix detects incompatibility; do not call it backward-compatible |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:016 — Breaking changes use new version or expand/migrate/contract with tested provider-consumer matrix and error contract.

مرجع: `B:1827;B:1907;B:2075`؛ مصوبه: `A07`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:008`.

**شرط:** Breaking field/type/meaning or consumer change

**قید/استثنا:** Shadow/Canary only after feasibility and capacity evidence

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:016.B01 | Use new version or expand/migrate/contract for breaking changes |
| REQ:CORE:016.B02 | Test a provider/consumer version matrix and block incompatible deployment |
| REQ:CORE:016.B03 | Error contract includes HTTP status, machine code, nonpersonal trace ID and transient/permanent/validation class |
| REQ:CORE:016.B04 | Identify impacted UI, Job and event consumers and controlled old-version retirement |

**AC:CORE:C01:016 / TEST:CORE:C01:016** — `NOT_EXECUTED`

**محیط و fixture:** Provider/consumer matrix, versioned error fixtures and deployment gate harness

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Introduce breaking schema via new version or tested expand/migrate/contract with provider-consumer combinations |
| NEGATIVE | Deploy an untested old/new pair or remove required field without migration: deployment blocked |
| BOUNDARY_OR_CONCURRENCY | Unknown field/version and transient/permanent/validation errors carry agreed status/code/nonpersonal trace; infeasible Canary cannot be mandated |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:017 — Separate typed/validated operational config, secrets, feature flags and business policies; financial policy cannot be a free-form toggle.

مرجع: `B:25;B:1917`؛ مصوبه: `A08`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:009`.

**شرط:** Configuration design

**قید/استثنا:** R1 needs no independent configuration-management service

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:017.B01 | Separate operational config, secrets, feature flags and business policies |
| REQ:CORE:017.B02 | Use typed versioned validated configuration |
| REQ:CORE:017.B03 | Financial business rules cannot become freely editable runtime toggles |

**AC:CORE:C01:017 / TEST:CORE:C01:017** — `NOT_EXECUTED`

**محیط و fixture:** Typed Settings plus four-category ownership/policy fixtures

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Inventory settings into runtime, secret, flag and business-policy classes with distinct owner/approval |
| NEGATIVE | Expose scoring coefficients as unrestricted runtime flag: reject as unauthorized policy mutation |
| BOUNDARY_OR_CONCURRENCY | R1 works without a new configuration microservice; typed config error stops activation rather than silently defaulting |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:018 — Config/flag changes require owner permission, diff, audit, secret protection, dependency checks and rollback safety.

مرجع: `B:1917;B:2106`؛ مصوبه: `A08`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:009`.

**شرط:** Configuration or flag change

**قید/استثنا:** A rollback must remain compatible with code, API, valid Snapshot and Job

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:018.B01 | Require authorized owner and pre-deployment Config Diff |
| REQ:CORE:018.B02 | Record actor, time, environment, permission and change history |
| REQ:CORE:018.B03 | Check dependency and secret safety before activation |
| REQ:CORE:018.B04 | Reject incompatible rollback or stop the affected capability |

**AC:CORE:C01:018 / TEST:CORE:C01:018** — `NOT_EXECUTED`

**محیط و fixture:** Config Diff/authorization/audit and rollback compatibility harness

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Authorized owner submits reviewed Config Diff and audit with actor/time/environment; compatible version activates |
| NEGATIVE | Unprivileged actor changes flag or secret appears in diff/log: reject activation without value disclosure |
| BOUNDARY_OR_CONCURRENCY | Rollback code/config/API/Snapshot/Job mismatch: block rollback and stop affected scope until a compatible version is approved |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:019 — OpenTelemetry logs/metrics/traces use nonidentifying correlation IDs; no OTP, token, identity or raw questionnaire in telemetry.

مرجع: `B:1192;B:1837`؛ مصوبه: `A09`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:010`.

**شرط:** Core/Adviser/Job observability

**قید/استثنا:** Clarity/RUM is not the operational telemetry authority

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:019.B01 | Use portable OpenTelemetry structured logs, metrics and traces |
| REQ:CORE:019.B02 | Propagate random nonpersonal correlation across service and Job boundaries |
| REQ:CORE:019.B03 | Observe contract errors, circuit state, pending job age/count, retries/final failure, Outbox lag and worker/publisher recovery |

**AC:CORE:C01:019 / TEST:CORE:C01:019** — `NOT_EXECUTED`

**محیط و fixture:** OpenTelemetry test collector plus worker/Outbox/circuit fault fixture

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Propagate a random trace across Core/API/job with structured logs/metrics/traces and state/contract versions |
| NEGATIVE | Instrument only generic request counts while omitting Outbox/job/circuit recovery: critical telemetry acceptance fails |
| BOUNDARY_OR_CONCURRENCY | Crash worker/publisher and replay: pending age/retry/final failure/lag/recovery visible without identifying metric labels |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:020 — SLO, alerts, runbooks, CPU/RAM and incident controls require measured baselines, not invented thresholds.

مرجع: `B:1837;B:1903;B:1913;B:2332`؛ مصوبه: `A09, F06`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:010`.

**شرط:** Critical-path SLO, alert or infrastructure claims

**قید/استثنا:** No numeric threshold or production capacity accepted from an unmeasured historical host

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:020.B01 | Measure SLI/SLO and Error Budget from a versioned baseline with owner |
| REQ:CORE:020.B02 | Prioritize alerts by user impact and define severity, escalation, runbook, containment, recovery and post-incident review |
| REQ:CORE:020.B03 | Define non-sensitive synthetic probe and alert/recovery drill |
| REQ:CORE:020.B04 | Measure CPU/RAM, latency, throughput, workload and per-success cost before capacity commitment |

**AC:CORE:C01:020 / TEST:CORE:C01:020** — `NOT_EXECUTED`

**محیط و fixture:** Authorized representative workload and non-sensitive synthetic incident sandbox

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Measure defined workload baseline, assign SLO/Error Budget owner and drill alert, escalation, runbook and recovery |
| NEGATIVE | Use historical VM size or arbitrary p95 as capacity guarantee: decision gate rejects claim |
| BOUNDARY_OR_CONCURRENCY | Synthetic non-sensitive Core/worker/DB fault triggers user-impact alert and post-incident evidence; instrumentation overhead measured |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:021 — SigNoz is a conditional evaluation; self-hosting on the current production VM is prohibited under recorded capacity; revised deployment requires new evidence and separate approval.

مرجع: `B:24;B:1837`؛ مصوبه: `A09, A01`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:010`.

**شرط:** Telemetry tool and deployment choice

**قید/استثنا:** Current recorded production VM capacity prohibits self-hosted SigNoz; new evidence and separate approval required for any revised choice

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:021.B01 | Treat SigNoz as selected for conditional evaluation of Cloud versus self-hosted |
| REQ:CORE:021.B02 | Do not deploy self-hosted SigNoz on the current production VM under recorded capacity |
| REQ:CORE:021.B03 | Decide retention, sampling, channel, security, cost and host only after measured evidence and approval |

**AC:CORE:C01:021 / TEST:CORE:C01:021** — `NOT_EXECUTED`

**محیط و fixture:** Security/cost/capacity decision review; never current production VM deployment

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Compare Cloud/self-hosted SigNoz using security, retention, sampling and capacity evidence in a decision dossier |
| NEGATIVE | Place self-hosted SigNoz on current production VM under recorded capacity: explicit rejection |
| BOUNDARY_OR_CONCURRENCY | Even an apparently spare host or new evidence does not silently grant deployment: require revised approval and cost/capacity evidence |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:022 — Preserve phase-one routes, identity, questionnaire, scoring, data publication and UI with targeted regression evidence.

مرجع: `B:1761-1762;B:2284-2288;B:2326-2332`؛ مصوبه: `A01, O5-12`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:001`.

**شرط:** Any phase-two change affecting phase one

**قید/استثنا:** Existing phase-one deferrals remain open, not silently promoted to done

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:022.B01 | Preserve routes, identity, questionnaire/proof, scoring and publication behaviour |
| REQ:CORE:022.B02 | Preserve accepted UI, RTL, accessibility and mobile/desktop paths |
| REQ:CORE:022.B03 | Retain existing CI/security gates and targeted regression evidence |
| REQ:CORE:022.B04 | Record differences against canonical guide, protocol, retrospective and handoff without changing sources |

**AC:CORE:C01:022 / TEST:CORE:C01:022** — `NOT_EXECUTED`

**محیط و fixture:** Existing isolated phase-one backend/PostgreSQL16/browser suites and accepted visual baseline

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Replay locked phase-one route/OTP/proof/questionnaire/golden/publication and approved UI baseline in isolated fixtures |
| NEGATIVE | Break a route, permit account-B access, change score or remove security gate: regression review blocks acceptance |
| BOUNDARY_OR_CONCURRENCY | Expired proof, refresh/restart and mobile/desktop RTL/a11y preserve prior semantics; deferred phase-one work stays open |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:023 — Database evolution follows Alembic and PostgreSQL migration/restore checks; current migration count and runtime SHA require independent proof.

مرجع: `B:2282;B:2295-2299;B:2328`؛ مصوبه: `O5-12`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:001`.

**شرط:** Database or runtime baseline claim

**قید/استثنا:** File count alone proves neither effective revisions nor runtime schema; no production access assumed

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:023.B01 | Use Alembic as DDL authority and independently inspect heads/history |
| REQ:CORE:023.B02 | Plan PostgreSQL 16 upgrade/downgrade, data preservation, rollback and restore checks before production migration |
| REQ:CORE:023.B03 | Correlate authorized runtime SHA/tag/image digest and schema, marking inaccessible state unknown |

**AC:CORE:C01:023 / TEST:CORE:C01:023** — `NOT_EXECUTED`

**محیط و fixture:** Disposable PostgreSQL16 only; Alembic graph/history and fixture restore; authorized runtime readback optional/unknown

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Inspect actual Alembic graph then exercise supported upgrade/downgrade and restore on disposable PostgreSQL16 with preserved fixture data |
| NEGATIVE | Infer schema readiness from migration-file count or Compose digest alone: mark claim unverified |
| BOUNDARY_OR_CONCURRENCY | Code tag/digest differs from accessible runtime or runtime inaccessible: report drift/unknown; never mutate production or reset user DB |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:024 — Distinguish stage completion from increment release readiness; Wallet/Billing cannot be hard dependencies of first RAG release.

مرجع: `B:1938-1940;B:2038-2043;B:2236`؛ مصوبه: `O5-01, O5-13`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:011`.

**شرط:** Release planning

**قید/استثنا:** Stage sequence is policy, not proof of every hard technical dependency

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:024.B01 | Track Release Readiness independently from full Stage Completion |
| REQ:CORE:024.B02 | Keep Wallet, billing, gateway and Assistant off RAG R1 hard prerequisites |
| REQ:CORE:024.B03 | Preserve the full stage scope after an early independent release |

**AC:CORE:C01:024 / TEST:CORE:C01:024** — `NOT_EXECUTED`

**محیط و fixture:** Stage/release and dependency-policy planning fixtures

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Record independently usable RAG increment and a separate full stage-coverage ledger |
| NEGATIVE | Label one early response feature Stage Complete or make Wallet/Assistant hard prerequisite of free RAG R1: reject |
| BOUNDARY_OR_CONCURRENCY | Parallel safe discovery does not waive stage-policy delivery gates and does not silently delete deferred features |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:026 — Map R1-R4, RG/REL and F06 to every future release; safe rollback, security stop and independent high-risk review cannot be waived.

مرجع: `B:2002-2004;B:2192;B:2198-2219`؛ مصوبه: `O5-10, F06`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:011`.

**شرط:** Any future release

**قید/استثنا:** Commercial risk acceptance cannot override valid security, safety, financial or legal blocker

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:026.B01 | Map versioned original RG/REL texts and R1-R4 risk class into each release dossier |
| REQ:CORE:026.B02 | Record Go/Conditional Go/Hold/No-Go with scoped authority, evidence and reason |
| REQ:CORE:026.B03 | Retain four budgets, limits, alerts, escalation authority and recovery reserve |
| REQ:CORE:026.B04 | Bind authorization to code/config/contract/Snapshot/audience/budget versions |
| REQ:CORE:026.B05 | Define stop, compatible rollback/restore, post-release monitoring and expiring non-auto-renewed Conditional Go |

**AC:CORE:C01:026 / TEST:CORE:C01:026** — `NOT_EXECUTED`

**محیط و fixture:** Original approved RG/REL text and versioned release dossier control fixtures

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Prepare dossier with original RG/REL version, risk class, four budgets, authority, recovery and scoped decision |
| NEGATIVE | Commercial owner accepts financial/security/legal blocker or replaces eight REL with F06 summary: No-Go/Hold |
| BOUNDARY_OR_CONCURRENCY | Conditional Go expires or code/config/Snapshot/audience/budget materially changes: require reevaluation; no auto-renewal or obsolete legal rollback |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:027 — Keep all approved scope including deferred wallet items; COV gate and bidirectional trace cannot be replaced by a feature checklist.

مرجع: `B:2195;B:2234-2250`؛ مصوبه: `O5-13, O5-14`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:011`.

**شرط:** Coverage and deferral accounting

**قید/استثنا:** No automatic stage four, growth budget or dated commitment follows from deferral

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:027.B01 | Maintain bidirectional versioned requirement/owner/task/test/release/deferral trace |
| REQ:CORE:027.B02 | Preserve all approved Wallet V0.20 and other capability scope, including deferred items |
| REQ:CORE:027.B03 | Retain selected/approved/released/deferred distinctions and approve scope/release changes |
| REQ:CORE:027.B04 | Keep G-COV-1..3 and referenced COV/AC controls without replacing them by a checklist |

**AC:CORE:C01:027 / TEST:CORE:C01:027** — `NOT_EXECUTED`

**محیط و fixture:** Registry and COV trace/deferral mutation fixtures

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Traverse source-to-REQ-to-task-to-AC/test-to-future-release and backwards including Wallet V0.20 deferrals |
| NEGATIVE | Remove an approved deferred Wallet feature because it is absent from first three stages: coverage gate fails |
| BOUNDARY_OR_CONCURRENCY | Change first required release or grow after stage3: effect review and owner decision required, no implicit stage4 or fabricated commitment |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:032 — Require workload, cost and failure evidence before adding physical infrastructure or extracting further services.

مرجع: `B:1871-1879;B:1883-1903;B:2071;B:2244`؛ مصوبه: `A01, O5-08, O5-14`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:013`.

**شرط:** Physical split, new host or service extraction proposal

**قید/استثنا:** User count or historical 2-vCPU/4GB host is not sufficient justification

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:032.B01 | Measure equal-workload latency, throughput, CPU/RAM, failure isolation, security/transaction risk and cost |
| REQ:CORE:032.B02 | Separate architecture overhead from intrinsic browser/model/workflow load |
| REQ:CORE:032.B03 | Require RFC and independent owner approval before any physical extraction or infrastructure commitment |

**AC:CORE:C01:032 / TEST:CORE:C01:032** — `NOT_EXECUTED`

**محیط و fixture:** Authorized identical-workload performance sandbox with cost/resource measurements

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Compare same representative workload with measured resource/failure/transaction/security/cost data in extraction RFC |
| NEGATIVE | Justify extra VM or service extraction only from user count or 2-vCPU/4GB statement: reject |
| BOUNDARY_OR_CONCURRENCY | Include browser/model load separately from process overhead; inconclusive measurement yields Hold, not an invented capacity number |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:033 — Wallet remains a modular Core financial capability, not a prerequisite of first RAG increment and not an external-merchant wallet.

مرجع: `B:2236;W:57;W:1167-1169`؛ مصوبه: `A01, O5-13, Wallet-1.4, 7.1`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:012`.

**شرط:** Wallet boundary planning

**قید/استثنا:** Legal applicability remains separately assessed; no external merchant acceptance

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:033.B01 | Keep Wallet as a modular Core financial capability |
| REQ:CORE:033.B02 | Keep credits closed-loop for Shahab services, suppliers are Shahab costs rather than independent merchants |
| REQ:CORE:033.B03 | Do not require Wallet activation for first RAG release |
| REQ:CORE:033.B04 | Handoff single IRR ledger, per-owner accounts and atomic balanced postings without selecting an external ledger vendor |

**AC:CORE:C01:033 / TEST:CORE:C01:033** — `NOT_EXECUTED`

**محیط و fixture:** Wallet interface/ledger contract review and isolated balanced-posting design fixture

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Review modular Wallet interface: only Shahab service credits, separate supplier cost, single IRR ledger with per-owner accounts |
| NEGATIVE | Treat supplier as independent credit merchant or make Wallet necessary for free RAG: reject boundary |
| BOUNDARY_OR_CONCURRENCY | Two accounts in one ledger can post atomically; gift accounting/vendor choice stays blocked for specialist decision, not assumed approved |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:037 — Every synchronous cross-service call must obey a bounded timeout budget; failures must be surfaced and contained.

مرجع: `B:1192;B:1913`؛ مصوبه: `A06`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:007`.

**شرط:** Every synchronous cross-service call

**قید/استثنا:** Circuit breakers are conditional on instability; the timeout budget itself is not

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:037.B01 | Bound each synchronous call by an approved timeout budget |
| REQ:CORE:037.B02 | Surface timeout and contain dependent failure without inventing success |

**AC:CORE:C01:037 / TEST:CORE:C01:037** — `NOT_EXECUTED`

**محیط و fixture:** Controlled synchronous provider with latency/late response injection

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Every synchronous cross-service path has measured/approved timeout and returns typed timeout within budget |
| NEGATIVE | Stable-seeming endpoint hangs indefinitely: timeout requirement still fails even without a breaker |
| BOUNDARY_OR_CONCURRENCY | At timeout/late-response boundary, no success fabricated and dependent request is contained under chosen budget |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:038 — Use circuit breaker where unstable external service can cascade failures; recover without spreading failure.

مرجع: `B:1192;B:1913`؛ مصوبه: `A06`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:007`.

**شرط:** Unstable dependency capable of cascading failure

**قید/استثنا:** No claim all calls require the same breaker thresholds

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:038.B01 | Open circuit on measured failure policy, fail fast while open and test controlled half-open recovery |
| REQ:CORE:038.B02 | Preserve independent capabilities during failure and recovery |

**AC:CORE:C01:038 / TEST:CORE:C01:038** — `NOT_EXECUTED`

**محیط و fixture:** Circuit state machine fixture with fake clock and controlled probe races

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Inject transient dependency failures: open, fail-fast, half-open probe and measured recovery follow approved policy |
| NEGATIVE | Circuit stays closed through cascading outage or opens unrelated independent capability: failure isolation test rejects |
| BOUNDARY_OR_CONCURRENCY | Simultaneous half-open probes obey controlled concurrency and restore only after recovery criterion |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:039 — Retry only transient/retriable outcomes with backoff and a bounded attempt count; uncertain financial effects are reconciled before retry.

مرجع: `B:918;B:1192;B:1913`؛ مصوبه: `A06, A04`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:007`.

**شرط:** Retry of a failed operation

**قید/استثنا:** Unknown financial effect must be reconciled before retry, not treated as transient failure

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:039.B01 | Retry only classified transient outcomes with backoff and bounded attempts |
| REQ:CORE:039.B02 | Do not retry permanent or validation errors |
| REQ:CORE:039.B03 | Use idempotency for side effects and reconcile unknown financial result before retry |

**AC:CORE:C01:039 / TEST:CORE:C01:039** — `NOT_EXECUTED`

**محیط و fixture:** Retry/failure-classification and idempotent side-effect/reconciliation harness

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Transient failure retries with bounded attempts/backoff and same effect-idempotency context |
| NEGATIVE | Validation/permanent error or unknown bank outcome triggers blind retry: reject; unknown enters reconciliation |
| BOUNDARY_OR_CONCURRENCY | Lost acknowledgement after financial success plus concurrent retry produces at most one effect after verified reconciliation |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:040 — Separate capacity of interactive requests and heavy background work using bulkhead or controlled concurrency.

مرجع: `B:1192;B:1913`؛ مصوبه: `A06`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:007`.

**شرط:** Interactive and heavy background work compete

**قید/استثنا:** Numeric concurrency/share needs measurement and approval

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:040.B01 | Separate interactive and background capacity with bulkhead/quota/concurrency control |
| REQ:CORE:040.B02 | A saturated or failed worker cannot exhaust interactive API capacity |
| REQ:CORE:040.B03 | Define visible controlled degradation rather than fabricated success |

**AC:CORE:C01:040 / TEST:CORE:C01:040** — `NOT_EXECUTED`

**محیط و fixture:** Separate-capacity interactive/worker load fixture in authorized sandbox

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Saturate heavy-worker pool with controlled fixtures while independent interactive requests keep reserved capacity |
| NEGATIVE | Shared unbounded pool starves interactive API: bulkhead acceptance fails |
| BOUNDARY_OR_CONCURRENCY | Worker crash/restart and queue surge remain within approved resource split; dependent capability degrades visibly |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:041 — Recover pending in-service jobs after worker restart while preserving owner authority and avoiding repeated effect.

مرجع: `B:918;B:1835`؛ مصوبه: `A04`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:005`.

**شرط:** Worker crash/restart with pending jobs

**قید/استثنا:** A recovery may not bypass current authorization or duplicate financial/publication effect

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:041.B01 | Resume pending owner-controlled jobs from persisted state after restart |
| REQ:CORE:041.B02 | Enforce idempotency across duplicate deliveries, concurrent workers and lost acknowledgements |
| REQ:CORE:041.B03 | Keep durable audit and trace of recovery outcome |

**AC:CORE:C01:041 / TEST:CORE:C01:041** — `NOT_EXECUTED`

**محیط و fixture:** PostgreSQL16 job queue/worker crash and duplicate-worker race fixture

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Restart worker with persisted pending jobs: owner resumes and records result/recovery trace |
| NEGATIVE | Restart relies on expired session state or skips current owner authorization: recovery denied |
| BOUNDARY_OR_CONCURRENCY | Two workers race on same job after lost ack: one effective mutation/publication, audit records replay without duplicate effect |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:042 — On engine migration, deliberately route new jobs to the new engine and complete in-flight jobs on the prior engine; adapters alone do not prove zero-change migration.

مرجع: `B:918;B:1835`؛ مصوبه: `A04`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:005`.

**شرط:** Workflow-engine/version migration

**قید/استثنا:** An adapter alone does not prove migration without code changes

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:042.B01 | Route new jobs deliberately to the new engine |
| REQ:CORE:042.B02 | Complete in-flight jobs on the prior engine under original compatible semantics |
| REQ:CORE:042.B03 | Test adapter/orchestration changes and failure/cancel/resume across migration |

**AC:CORE:C01:042 / TEST:CORE:C01:042** — `NOT_EXECUTED`

**محیط و fixture:** Old/new engine adapters and persisted job routing fixture

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Start J1 on old engine, switch routing, start J2 on new engine: J1 completes on old and J2 on new |
| NEGATIVE | Move J1 to new engine with changed semantics or claim interface proves free migration: reject |
| BOUNDARY_OR_CONCURRENCY | Cancel/resume/crash around routing switch: both engines respect version, current authority and exactly one business effect |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:043 — Event consumers deduplicate identity and enforce versioned ordering/compatibility; unknown versions are rejected or quarantined, never blindly applied.

مرجع: `B:1216;B:1833;B:1915`؛ مصوبه: `A05, A07`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:006`.

**شرط:** Event consumer receives delivery

**قید/استثنا:** Unknown schema is explicitly rejected/quarantined, not blindly applied

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:043.B01 | Deduplicate event identity before applying side effects |
| REQ:CORE:043.B02 | Handle duplicate and out-of-order delivery according to versioned contract |
| REQ:CORE:043.B03 | Test unknown-version handling and consumer compatibility |
| REQ:CORE:043.B04 | Version the event envelope with identity, schema version, time, origin and nonpersonal correlation; define required ordering and unknown-version rejection/quarantine |

**AC:CORE:C01:043 / TEST:CORE:C01:043** — `NOT_EXECUTED`

**محیط و fixture:** PostgreSQL16 consumer dedup plus version/order/race fixture

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Deliver versioned event with stable identity to compatible consumer: effect and dedup state applied safely |
| NEGATIVE | Deliver duplicate identity or unknown schema: no repeated effect; unknown version rejected/quarantined under contract |
| BOUNDARY_OR_CONCURRENCY | Deliver e2 before e1 and race duplicate deliveries: required ordering/version policy preserves coherent final state |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:044 — Outbox publisher must persist unsent local records and recover after commit-before-send crash without missing necessary events.

مرجع: `B:1216;B:1915`؛ مصوبه: `A05`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:006`.

**شرط:** Publisher crashes after local commit before send

**قید/استثنا:** Delivery can be at least once; effective application must remain idempotent

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:044.B01 | Keep unsent Outbox records durable and recover publishing after restart |
| REQ:CORE:044.B02 | Do not lose necessary events or repeat business effects after send/ack crash |
| REQ:CORE:044.B03 | Expose publisher lag, retry/final failure, recovery and periodic reconciliation |

**AC:CORE:C01:044 / TEST:CORE:C01:044** — `NOT_EXECUTED`

**محیط و fixture:** PostgreSQL16 Outbox/publisher kill-before-send/kill-before-ack fixture

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Crash publisher after local commit before send: unsent event survives restart and is delivered |
| NEGATIVE | Mark unsent record delivered or lose necessary event after crash: reconciliation/lag gate fails |
| BOUNDARY_OR_CONCURRENCY | Crash after send before ack and restart: resend is safe, consumer applies once; periodic reconcile finds any pending discrepancy |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:045 — Scoring, catalogue freshness and publication policies require versioned authorized change with regression evidence, never a free operational toggle.

مرجع: `B:406;B:1917`؛ مصوبه: `A08, C07`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:009`.

**شرط:** Scoring, catalogue freshness or publication-policy change

**قید/استثنا:** Technical rollback cannot activate obsolete legal evidence or incompatible Snapshot

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:045.B01 | Version policy changes with authorized approval, regression and controlled publication |
| REQ:CORE:045.B02 | Keep historical versions and reject invalid/obsolete Snapshot rollback |
| REQ:CORE:045.B03 | Do not mutate financial results through a free operational flag |

**AC:CORE:C01:045 / TEST:CORE:C01:045** — `NOT_EXECUTED`

**محیط و fixture:** Versioned policy/snapshot and golden scoring regression fixture

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Authorized scoring/freshness/publication policy change uses version, golden regression, approval and controlled publish |
| NEGATIVE | Use runtime flag to alter score or activate obsolete legal Snapshot on rollback: reject policy activation |
| BOUNDARY_OR_CONCURRENCY | Concurrent request and policy activation keep each run on valid version; history retained and incompatible rollback blocked |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:046 — Configuration and flags need schema validation, dependency validation, secret scanning, audit/change authorization and compatible rollback.

مرجع: `B:1917;B:2106;B:1690`؛ مصوبه: `A08`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:009`.

**شرط:** Config/flag deployment pipeline

**قید/استثنا:** Secret-storage tool and key-rotation period remain design decisions

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:046.B01 | Validate type, default, range and environment differences |
| REQ:CORE:046.B02 | Validate feature dependencies, kill switch and change authorization |
| REQ:CORE:046.B03 | Scan secrets and audit changes without exposing secret value |
| REQ:CORE:046.B04 | Test compatible rollback and block invalid config, leakage or unintended financial change |

**AC:CORE:C01:046 / TEST:CORE:C01:046** — `NOT_EXECUTED`

**محیط و fixture:** Typed config/env/policy/flag/secret canaries and rollback matrix

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Validate typed/default/range config, env diff, flag dependencies, kill switch, audit and secret scan before deployment |
| NEGATIVE | Invalid type/range, unauthorized policy edit, secret canary or unintended financial result: deployment blocked |
| BOUNDARY_OR_CONCURRENCY | Missing flag dependency or config rollback incompatible with API/Snapshot/Job fails; no automatic production fallback |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:047 — Telemetry and correlation identifiers must exclude real identities, OTPs, tokens and raw form/questionnaire payloads.

مرجع: `B:1192;B:1837;B:1690`؛ مصوبه: `A09, B05`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:010`.

**شرط:** Telemetry, analytics and correlation

**قید/استثنا:** Financial audit retention is independent of technical-log retention

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:047.B01 | Exclude identity, OTP, token, financial data and raw request/response/questionnaire payloads |
| REQ:CORE:047.B02 | Use safe low-cardinality labels and nonpersonal correlation IDs |
| REQ:CORE:047.B03 | Keep secrets outside model memory, RAG, chat logs and discovery, with least privilege and protected test/production separation |

**AC:CORE:C01:047 / TEST:CORE:C01:047** — `NOT_EXECUTED`

**محیط و fixture:** Synthetic privacy canaries, test telemetry collector and failure/retry paths

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Export success/error traces with synthetic identity/OTP/token/raw payload canaries: none occur in logs/metrics/traces/analytics/model memory |
| NEGATIVE | Inject secret in exception, URL, header or correlation and high-cardinality identifier label: reject leakage and relabel safely |
| BOUNDARY_OR_CONCURRENCY | Concurrent retries/errors across services retain nonpersonal correlation; permanent financial audit remains separate from technical log retention |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:048 — For high-risk releases require independent safety review, scoped change authority, stop and re-authorization after critical modifications.

مرجع: `B:2198-2219;B:2332`؛ مصوبه: `F06, O5-10`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:011`.

**شرط:** High-risk release or emergency stop

**قید/استثنا:** Preparer alone cannot approve safety; missing valid review holds/limits the risky scope

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:048.B01 | Require specialist safety review independent of change preparer |
| REQ:CORE:048.B02 | Honor documented blocker and authorized immediate operations/security stop without waiting for product owner |
| REQ:CORE:048.B03 | Require evidence of remedy, relevant tests and renewed authorization before restart |
| REQ:CORE:048.B04 | Material version/audience/budget change invalidates prior decision for affected scope |

**AC:CORE:C01:048 / TEST:CORE:C01:048** — `NOT_EXECUTED`

**محیط و fixture:** Independent-review, stop/restart and decision-version mutation fixtures

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Independent specialist reviews risky change and authorized operator can stop affected scope immediately |
| NEGATIVE | Preparer self-approves or business owner bypasses valid blocker: high-risk gate remains Hold |
| BOUNDARY_OR_CONCURRENCY | After stop or material version/audience/budget change, old approval cannot restart service: remedy/tests and new approval required |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

### REQ:CORE:049 — Wallet and billing are not default prerequisites for first RAG release; activating a paid flow still requires complete financial controls.

مرجع: `B:2236;B:1702-1708`؛ مصوبه: `O5-13, E04`؛ وضعیت: `APPROVED_EXPLICIT`؛ مالک: `CoreArchitecture`؛ تسک: `TASK:CORE:003`.

**شرط:** Paid flow activation versus first RAG release

**قید/استثنا:** Subscription sale has no default mandatory Wallet dependency

| رفتار اتمی / نتیجه قابل مشاهده | شرح |
| --- | --- |
| REQ:CORE:049.B01 | Prohibit implicit payment/Wallet prerequisite for first RAG release |
| REQ:CORE:049.B02 | Before a paid flow activates, require all applicable finance, entitlement, idempotency, reconciliation, audit and specialist-review controls |
| REQ:CORE:049.B03 | Preserve approved Wallet/E04 policies while leaving only explicitly open technical/numeric choices undecided |

**AC:CORE:C01:049 / TEST:CORE:C01:049** — `NOT_EXECUTED`

**محیط و fixture:** Free-RAG and disabled/paid activation policy/finance contract fixtures

| سناریو | ورودی و انتظار |
| --- | --- |
| POSITIVE | Free first RAG increment starts without Wallet; future paid-flow dossier lists applicable financial/entitlement controls |
| NEGATIVE | Activate paid service before idempotency/reconciliation/audit/permission controls, or force Wallet merely for subscription: reject |
| BOUNDARY_OR_CONCURRENCY | Flagged-off financial preparation grants no right to charge; unknown financial result reconciles before any repeat charge |

شاهد لازم: SHA و نسخه قرارداد/تنظیمات/Snapshot، محیط مجاز، فرمان و fixture، انتظار در برابر مشاهده، خروجی پاک‌سازی‌شده و شواهد دیتابیس/هم‌زمانی در صورت ارتباط. عبور صرف API یا وجود فایل معیار کافی نیست.

## وابستگی‌های ۲۳گانه

| از | به | نوع | دلیل |
| --- | --- | --- | --- |
| TASK:CORE:001 | TASK:CORE:002 | HARD | Phase-one footprint baseline constrains the ownership/import policy |
| TASK:CORE:002 | TASK:CORE:003 | HARD | Independent R1 topology requires one owner for each data/module boundary |
| TASK:CORE:001 | TASK:CORE:004 | HARD | Existing scorer/golden/publication must be inventoried before contract adaptation |
| TASK:CORE:008 | TASK:CORE:004 | CONTRACT | Recommendation consumer needs version/meaning/error compatibility, not copied scoring |
| TASK:CORE:002 | TASK:CORE:005 | HARD | A durable Job pattern needs one state owner and local transaction authority |
| TASK:CORE:002 | TASK:CORE:006 | HARD | Atomic data/Outbox commit requires a defined local data owner |
| TASK:CORE:005 | TASK:CORE:006 | CONTRACT | Only the justified owner-controlled long flow defines the needed event consumer; no mandatory event bus |
| TASK:CORE:003 | TASK:CORE:007 | CONTRACT | Fault containment targets the approved two-service R1 boundary |
| TASK:CORE:008 | TASK:CORE:007 | CONTRACT | Retry classification and timeouts depend on the service error/idempotency contract |
| TASK:CORE:002 | TASK:CORE:008 | HARD | Provider/consumer public API and denied private-table access follow authority map |
| TASK:CORE:001 | TASK:CORE:009 | HARD | Reuse typed Settings/secrets without reclassifying approved policy as runtime toggle |
| TASK:CORE:008 | TASK:CORE:009 | CONTRACT | Rollback config must remain compatible with API, Snapshot and job contracts |
| TASK:CORE:001 | TASK:CORE:010 | HARD | Existing metrics/logs baseline determines the telemetry gap; no production proof inferred |
| TASK:CORE:007 | TASK:CORE:010 | PREFERENCE | Resilience fault signals inform alerts; preference only, no hard block on defining observability |
| TASK:CORE:001 | TASK:CORE:011 | CONTRACT | Release dossier records the actual code/runtime unknowns and preserved phase-one baseline |
| TASK:CORE:004 | TASK:CORE:011 | CONTRACT | R1 release contract includes deterministic scoring and valid Snapshot evidence |
| TASK:CORE:009 | TASK:CORE:011 | POLICY | Release activation requires authorized compatible configuration and protected policy |
| TASK:CORE:010 | TASK:CORE:011 | POLICY | Critical-path release requires secure telemetry/runbook evidence, not a new arbitrary gate |
| TASK:CORE:002 | TASK:CORE:012 | CONTRACT | Wallet is a Core module with local ownership, not an external merchant service |
| TASK:CORE:011 | TASK:CORE:012 | POLICY | Any financial activation must preserve release governance without blocking free RAG |
| TASK:CORE:003 | TASK:CORE:013 | CONTRACT | Benchmark compares the scoped R1 topology, not an unapproved replacement architecture |
| TASK:CORE:007 | TASK:CORE:013 | CONTRACT | Load/failure experiments need stated failure isolation and resource-share contracts |
| TASK:CORE:010 | TASK:CORE:013 | CONTRACT | Telemetry measurement schema precedes benchmark; final numeric SLO follows benchmark, not vice versa |

یال‌ها از پیش‌نیاز به مصرف‌کننده‌اند. HARD قبل از طراحی وابسته؛ CONTRACT قبل از یکپارچه‌سازی؛ POLICY قبل از فعال‌سازی؛ PREFERENCE ترتیب ترجیحی است. نام قدیمی PRIORITY فقط به نام استاندارد PREFERENCE تبدیل شد و همان یال حفظ شد. قرارداد ابزار اندازه‌گیری T010 پیش از benchmark T013 است؛ عدد نهایی SLO پس از اندازه‌گیری می‌آید و چرخه وابستگی ایجاد نمی‌کند.

## تصمیم‌ها و قراردادهای باز

| تصمیم | موضوع | مالک | تسک متأثر |
| --- | --- | --- | --- |
| DECISION:C01:01 | Physical module/schema isolation and exact topology | C01 | TASK:CORE:002, TASK:CORE:003, TASK:CORE:012 |
| DECISION:C01:02 | Worker/queue technology and tested workflow migration mechanics | C03 | TASK:CORE:005, TASK:CORE:006 |
| DECISION:C01:03 | Timeout/retry/breaker thresholds and interactive resource shares | C03 | TASK:CORE:007 |
| DECISION:C01:04 | Operational telemetry retention/sampling/hosting/SLO/alert channel | C03 | TASK:CORE:010, TASK:CORE:013 |
| DECISION:C01:05 | Consumer schemas, version-support period, EOL and shadow/canary feasibility | C03 | TASK:CORE:003, TASK:CORE:004, TASK:CORE:008 |
| DECISION:C01:06 | Runtime SHA/tag/digest, Alembic/schema evidence and authorized performance environment | C01 | TASK:CORE:001, TASK:CORE:013 |
| DECISION:C01:07 | Per-release risk class, budget, reviewer and original RG/REL/COV control dossier | C01 | TASK:CORE:011 |
| DECISION:C01:08 | Financial activation, legal applicability, gift accounts and policy details | C07 | TASK:CORE:012 |
| DECISION:C01:09 | Secret storage, rotation/revocation and environment-isolation design | C03 | TASK:CORE:009 |

| قرارداد طراحی | مالک | مصرف‌کننده | وضعیت Schema |
| --- | --- | --- | --- |
| CONTRACT:C01:01 — Module public ports and data ownership | Core | Core modules | DESIGN_REQUIRED_NOT_PUBLISHED_API |
| CONTRACT:C01:02 — Core recommendation/catalogue evidence API | Core | Adviser; future Assistant | DESIGN_REQUIRED_NOT_PUBLISHED_API |
| CONTRACT:C01:03 — Service-owned Job/Workflow port | Each service owns its Job state | Authorized job consumer | DESIGN_REQUIRED_NOT_PUBLISHED_API |
| CONTRACT:C01:04 — Reliable event/Outbox envelope | Data owner service | Registered asynchronous consumer | DESIGN_REQUIRED_NOT_PUBLISHED_API |
| CONTRACT:C01:05 — Typed config/flag/policy change and rollback | Config or policy owner | Deployment/configuration consumer | DESIGN_REQUIRED_NOT_PUBLISHED_API |
| CONTRACT:C01:06 — Operational telemetry and critical-path incident evidence | Service operator | Authorized operations/security | DESIGN_REQUIRED_NOT_PUBLISHED_API |
| CONTRACT:C01:07 — Release and finance-boundary evidence dossier | Release owner | Independent reviewer and deployment gate | DESIGN_REQUIRED_NOT_PUBLISHED_API |

قراردادها نسخه برنامه دارند، نه API منتشرشده یا Schema فیزیکی نهایی. حل تصمیم‌ها پیش از توسعه/فعال‌سازی مربوط الزامی است. برای انتشار، متن اصلی مصوب RG/REL و نگاشت بندبه‌بند لازم است؛ این برنامه جایگزین آن نیست.

## بازتولید اعتبارسنجی

از ریشه مخزن اجرا شود. کد اعتبارسنجی در همان رجیستری نگهداری می‌شود و فایل یا دفتر موازی لازم نیست:

```bash
python - <<'PY'
import json
from pathlib import Path
rows = [json.loads(line) for line in Path('docs/phase2/core/CORE_REGISTRY.jsonl').read_text().splitlines()]
exec(next(r['code'] for r in rows if r.get('id') == 'VALIDATE:C01:RECOVERY'))
PY
```

اعتبارسنجی JSONL، شناسه، SHA منبع و کد، دامنه، روابط دوسویه، ۱۲۸ رفتار، AC/Test، تصمیم/قرارداد، DAG و حفظ واحدهای خارج C01 را کنترل می‌کند. هشت خرابی تزریقی (شناسه تکراری، AC مفقود، شرط خالی، واحد U، رفتار بی‌آزمون، ادعای کاذب اجرای آزمون، تغییر خارج دامنه و انتهای نامعتبر یال) همگی رد شدند. این‌ها آزمون خود برنامه‌اند و به‌جای آزمون محصول گزارش نمی‌شوند.

## مرز پایان

C01 در سطح تعریف برنامه پذیرفته است؛ همه اجراها و تصمیم‌های باز محفوظ‌اند. مأموریت اینجا متوقف می‌شود و C02 آغاز نمی‌شود. برنامه پنج‌مرحله‌ای: ۱۸ Core/Wallet → ده RAG/Adviser → هشت Assistant → گراف تلفیقی تقدم‌وتأخر → نقشه راه و تحویل هفتگی مطابق ۲۲ اصل. فقط C01 این مرحله انجام شده است.
