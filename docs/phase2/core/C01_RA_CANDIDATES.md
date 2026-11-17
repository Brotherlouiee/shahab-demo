# C01 — پذیرفته‌شده در Requirement Acceptance (RA)

**گیت C01 RA = PASS ؛ گیت C01 IPA = NOT_STARTED.** این سند نمای خوانا از رجیستری واحد `CORE_REGISTRY.jsonl` است و یک دفتر مستقل/موازی نیست. برنامه فاز دوم هنوز WIP است؛ هیچ کد، انتشار یا تغییر معماری از این مرحله مجاز نشده است.

## منابع قفل‌شده

- main = `f4167f8ceccec24cc10d70e158c82cbf3c9eeacf`
- Blueprint V1.6 blob = `9681c2bf6c3149317c3788516748084cfb6eac7c`
- Wallet V0.20 blob = `1f3dc55f46b3a12b2eb33e647355e4a6a73dd37a`

## ثبت ممیزی معنایی مستقل

- مرور اول: ۳۶ نامزد با استخراج و ثبت مرجع؛ مرور دوم: بررسی ضدنمونه و تقدم A01 بر تاریخچه، تشخیص هم‌پوشانی/مالکیت و تجزیه رفتارها.
- تعداد نامزدهایی که بدون پذیرش اولیه تعیین تکلیف شدند: ۹؛ دسته‌ها: یک مجموعه مرکب تفکیک‌شده، اصل‌های اجرایی به رجیستری سیاست منتقل‌شده، چهار handoff بین‌بسته‌ای، مورد تاریخی superseded، مورد تکراری و کنترل روش‌شناختی.
- ۱۳ الزام مستقل جدید ناشی از تفکیک Timeout، Circuit Breaker، Retry، Bulkhead، Job recovery، Outbox، تنظیمات و حریم خصوصی اضافه شد.
- رجیستری شامل ۲۲ اصل اجرایی جداگانه با شناسه‌های `POL:BLUEPRINT:5.2.1:01` تا `22` است، نه یک «الزام کلی» غیرقابل‌آزمون.
- بررسی دامنه C01: ۲۴ بازه/بخش اصلی و ۴۹ ارجاع اضافه از جست‌وجوی کل دو سند؛ ۵۱۰ واحد منبع در دامنه بررسی. این عدد واحد منبع است، نه الزام.
- هیچ REQ پذیرفته‌شده بدون Source Unit و مرجع وجود ندارد؛ مسیرهای RAG، Assistant، مالی و UI خارج از C01 به بسته مالک ارجاع داده شدند.

## ۴۰ الزام پذیرفته‌شده

| شناسه | مرجع | گزاره مصوب/الزام معماری | مالک منطقی |
|---|---|---|---|
| REQ:CORE:001 | B:16-26؛ B:1956 | Core is a modular monolith with explicit internal module boundaries; no forced service-per-module split. | CoreArchitecture |
| REQ:CORE:002 | B:16-26؛ B:788-794 | Adviser/RAG has independent deployment and independent data ownership from Core. | CoreArchitecture |
| REQ:CORE:003 | B:16-26؛ B:2061-2063 | Assistant is an independent target service; R1 permits only its boundary/contracts, not running deployment. | CoreArchitecture |
| REQ:CORE:004 | B:16-26؛ B:2061-2071 | R1 may reuse current VM, PostgreSQL and Redis, subject to validation; logical ownership remains separate. | CoreArchitecture |
| REQ:CORE:005 | B:1192-1216؛ B:1212 | Service private schemas, data, jobs and transactions must have one owner; no direct cross-service private-table reads/writes. | CoreArchitecture |
| REQ:CORE:006 | B:869-871؛ B:1212-1214 | Core exposes versioned and authorized data/domain/catalogue interfaces with minimal fields, provenance, version and error behavior. | CoreArchitecture |
| REQ:CORE:007 | B:1825-1829؛ B:1986 | No cross-module cyclic dependencies or private ORM leakage; reuse existing common capabilities instead of parallel authorities. | CoreArchitecture |
| REQ:CORE:008 | B:1192-1216؛ B:1627-1633 | Core retains deterministic loan recommendation, matching, reasons, loan rules and published serving Snapshot. | CoreArchitecture |
| REQ:CORE:009 | B:1216؛ B:2075-2079 | A recommendation run uses one compatible published product Snapshot and rule version, never synthetic results after Core failure. | CoreArchitecture |
| REQ:CORE:010 | B:1192؛ B:916-918 | Short deterministic operations use synchronous APIs; long owner-controlled work uses durable asynchronous Job workflows when needed. | CoreArchitecture |
| REQ:CORE:011 | B:916-918؛ B:1835 | Each Job owner persists state/result in PostgreSQL and exposes versioned ports/adapters, safe cancel/resume and recovery. | CoreArchitecture |
| REQ:CORE:012 | B:1192؛ B:1216؛ B:1833 | Use transactional outbox only where reliable events are necessary; consumers deduplicate and publishers recover safely. | CoreArchitecture |
| REQ:CORE:013 | B:1192؛ B:1212-1216 | Keep local service transaction boundaries; no default cross-service distributed transaction or global database ownership. | CoreArchitecture |
| REQ:CORE:015 | B:1827؛ B:1907 | Contracts are defined in versioned OpenAPI/schema before breaking changes and tested for structural and semantic consumer compatibility. | CoreArchitecture |
| REQ:CORE:016 | B:1827؛ B:1907؛ B:2075 | Breaking changes use new version or expand/migrate/contract with tested provider-consumer matrix and error contract. | CoreArchitecture |
| REQ:CORE:017 | B:16-26؛ B:1917 | Separate typed/validated operational config, secrets, feature flags and business policies; financial policy cannot be a free-form toggle. | CoreArchitecture |
| REQ:CORE:018 | B:16-26؛ B:1917؛ B:2106 | Config/flag changes require owner permission, diff, audit, secret protection, dependency checks and rollback safety. | CoreArchitecture |
| REQ:CORE:019 | B:16-26؛ B:1192؛ B:1837 | OpenTelemetry logs/metrics/traces use nonidentifying correlation IDs; no OTP, token, identity or raw questionnaire in telemetry. | CoreArchitecture |
| REQ:CORE:020 | B:16-26؛ B:1903؛ B:1913 | SLO, alerts, runbooks, CPU/RAM and incident controls require measured baselines, not invented thresholds. | CoreArchitecture |
| REQ:CORE:021 | B:16-26؛ B:1903 | SigNoz is conditional evaluation; self-hosting on the current production VM requires approved resource evidence. | CoreArchitecture |
| REQ:CORE:022 | B:1761-1762؛ B:2284-2288؛ B:2326-2332 | Preserve phase-one routes, identity, questionnaire, scoring, data publication and UI with targeted regression evidence. | CoreArchitecture |
| REQ:CORE:023 | B:2282؛ B:2295-2299؛ B:2328 | Database evolution follows Alembic and PostgreSQL migration/restore checks; current migration count and runtime SHA require independent proof. | CoreArchitecture |
| REQ:CORE:024 | B:1938-1940؛ B:2024-2058؛ B:2234-2238 | Distinguish stage completion from increment release readiness; Wallet/Billing cannot be hard dependencies of first RAG release. | CoreArchitecture |
| REQ:CORE:026 | B:2002-2022؛ B:2192؛ B:2198-2219 | Map R1-R4, RG/REL and F06 to every future release; safe rollback, security stop and independent high-risk review cannot be waived. | CoreArchitecture |
| REQ:CORE:027 | B:2195؛ B:2232-2250 | Keep all approved scope including deferred wallet items; COV gate and bidirectional trace cannot be replaced by a feature checklist. | CoreArchitecture |
| REQ:CORE:032 | B:1881-1903؛ B:2061-2075 | Require workload, cost and failure evidence before adding physical infrastructure or extracting further services. | CoreArchitecture |
| REQ:CORE:033 | B:2236؛ W:51-60؛ W:1161-1175 | Wallet remains a modular Core financial capability, not a prerequisite of first RAG increment and not an external-merchant wallet. | CoreArchitecture |
| REQ:CORE:037 | B:1192؛ B:1913 | Each unstable synchronous dependency must obey a bounded timeout budget; failures must be surfaced and contained. | CoreArchitecture |
| REQ:CORE:038 | B:1192؛ B:1913 | Use circuit breaker where unstable external service can cascade failures; recover without spreading failure. | CoreArchitecture |
| REQ:CORE:039 | B:1192؛ B:1913 | Retry only transient/retriable outcomes with backoff and a bounded attempt count; uncertain financial effects are reconciled before retry. | CoreArchitecture |
| REQ:CORE:040 | B:1192؛ B:1913 | Separate capacity of interactive requests and heavy background work using bulkhead or controlled concurrency. | CoreArchitecture |
| REQ:CORE:041 | B:916-918؛ B:1835 | Recover pending in-service jobs after worker restart while preserving owner authority and avoiding repeated effect. | CoreArchitecture |
| REQ:CORE:042 | B:916-918؛ B:1835 | On changing workflow engine/version, route new jobs deliberately and complete in-flight jobs under compatible prior semantics. | CoreArchitecture |
| REQ:CORE:043 | B:1192؛ B:1216؛ B:1833 | Event consumers must deduplicate by event identity and tolerate duplicate/out-of-order or unrecognized-version deliveries. | CoreArchitecture |
| REQ:CORE:044 | B:1216؛ B:1915 | Outbox publisher must persist unsent local records and recover after commit-before-send crash without missing necessary events. | CoreArchitecture |
| REQ:CORE:045 | B:406؛ B:1917 | Scoring, catalogue freshness and publication policies require versioned authorized change with regression evidence, never a free operational toggle. | CoreArchitecture |
| REQ:CORE:046 | B:1917؛ B:2106 | Configuration and flags need schema validation, dependency validation, secret scanning, audit/change authorization and compatible rollback. | CoreArchitecture |
| REQ:CORE:047 | B:1192؛ B:1837 | Telemetry and correlation identifiers must exclude real identities, OTPs, tokens and raw form/questionnaire payloads. | CoreArchitecture |
| REQ:CORE:048 | B:2198-2219؛ B:2332 | For high-risk releases require independent safety review, scoped change authority, stop and re-authorization after critical modifications. | CoreArchitecture |
| REQ:CORE:049 | B:2236؛ B:1702-1708 | Wallet and billing are not default prerequisites for first RAG release; activating a paid flow still requires complete financial controls. | CoreArchitecture |

## ۹ نامزد رد/انتقال/تجزیه‌شده

| شناسه نامزد | تعیین تکلیف | دلیل |
|---|---|---|
| REQ:CORE:014 | SPLIT_TO_037_040 | رفتارها و آزمون‌های مستقل از حکم مرکب تفکیک شدند |
| REQ:CORE:025 | PROCESS_22_PRINCIPLES | از الزام اجرایی تفکیک شد |
| REQ:CORE:028 | HANDOFF_C02_R02_A02 | مالک تخصصی بسته دیگر؛ شناسه مستقل Core تولید نشود |
| REQ:CORE:029 | HANDOFF_C02 | مالک تخصصی بسته دیگر؛ شناسه مستقل Core تولید نشود |
| REQ:CORE:030 | HANDOFF_C05b_R06 | مالک تخصصی بسته دیگر؛ شناسه مستقل Core تولید نشود |
| REQ:CORE:031 | SUPERSEDED_HISTORICAL_CONTEXT | گزاره قدیمی با A01 ناسازگار و فاقد اعتبار مصوبه جاری است |
| REQ:CORE:034 | HANDOFF_C06_R10 | مالک تخصصی بسته دیگر؛ شناسه مستقل Core تولید نشود |
| REQ:CORE:035 | MERGED_WITH_REQ_CORE_026 | از الزام اجرایی تفکیک شد |
| REQ:CORE:036 | QUALITY_PROTOCOL_NOT_PRODUCT_REQUIREMENT | از الزام اجرایی تفکیک شد |

## مسائل باز اما غیرمسدودکننده RA

- فیزیک Schema، فناوری اجرای Job، مدت TTL و نگهداری، ظرفیت قابل اتکای VM، هزینه، SLO و نرخ‌های مالی بازند؛ ورود به برنامه اجرایی باید برای هر Task نشان دهد که گیت تصمیم مربوط پیش از توسعه/انتشار کجاست.
- زمان اولین انتشار RAG و ایجاد/فعال‌سازی Wallet/اشتراک به معنای مجوز ساخت فوری نیست. برای مسیر مالی، تصمیم‌های مصوب W و E04 محفوظ‌اند.
- ادعای «معماری هنوز انتخاب نشده» در B:1923 تاریخی است و به سبب A01 و B:2140، معیار تصمیم معماری نیست.

## مرز بعدی

گام بعد C01 IPA است: Technical Enabler و Task فقط از همین ۴۰ REQ پذیرفته‌شده ساخته شود؛ برای هر رفتار AC و Test قابل‌رد و شناسه مستقل، بدون Story مصنوعی. کنترل کفایت: امکان موفق‌شدن آزمون‌ها هم‌زمان با نقض الزام اصلی بررسی شود. هیچ تعهد زمان/هزینه بدون شاهد پذیرفته نیست.
