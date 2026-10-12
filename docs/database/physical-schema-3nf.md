# Physical schema specification (3NF) — US-04.T02

## وضعیت و قرارداد اجرا

این فایل specification فیزیکی PostgreSQL است. `US-04.T03` باید مدل SQLAlchemy و portها را دقیقاً از آن بسازد و `US-04.T04` باید migration قابل upgrade/downgrade تولید کند. تا آن زمان هیچ جدول واقعی وجود ندارد؛ تغییر این قرارداد فقط با ADR و migration سازگار مجاز است.

## قواعد سراسری

- همهٔ PKها `uuid` با default تولیدشده در database؛ timestampها `timestamptz NOT NULL` در UTC هستند.
- identifierهای پایدار (`*_code`, `canonical_id`) `text` با `UNIQUE` و collation پیش‌فرض هستند؛ متن فارسی نمایشی هرگز کلید business نیست.
- مبلغ و نسبت `numeric` هستند، نه floating point؛ تاریخ/زمان در UTC؛ stateهای domain از `enum` PostgreSQL یا `CHECK` نام‌دار استفاده می‌کنند.
- FKها در حالت پیش‌فرض `RESTRICT`/`NO ACTION` هستند. حذف cascade فقط برای childهای واقعاً owned مانند answerهای یک session مجاز است و در migration مستند می‌شود.
- دادهٔ immutable شامل source، version و audit event است. `deleted_at` فقط برای sessionهای دارای policy retention مصوب بررسی می‌شود.

## مرجع و کاتالوگ وام

| جدول | ستون‌های تعیین‌کننده | constraints فیزیکی |
| --- | --- | --- |
| `lenders` | `lender_id uuid PK`, `canonical_name text`, `external_code text NULL`, timestamps | `UNIQUE(canonical_name)`؛ `UNIQUE(external_code)` when not null |
| `loan_products` | `loan_product_id PK`, `lender_id FK`, `canonical_name text`, `product_code text NULL` | `UNIQUE(lender_id, canonical_name)`؛ `UNIQUE(lender_id, product_code)` when not null |
| `loan_product_versions` | `loan_product_version_id PK`, `loan_product_id FK`, `version_number integer`, `publication_state`, `source_file_id FK NULL`, `effective_from/through` | `UNIQUE(loan_product_id, version_number)`؛ `CHECK(version_number > 0)`؛ بازهٔ تاریخ نامنفی |
| `guarantee_types` | `guarantee_type_id PK`, `canonical_id text`, `display_label text` | `UNIQUE(canonical_id)` |
| `deposit_account_types` | `deposit_account_type_id PK`, `canonical_id text`, `display_label text` | `UNIQUE(canonical_id)` |
| `loan_terms` | `loan_terms_id PK`, `loan_product_version_id FK`, چهار مقدار محوری numeric/integer و state متناظر، سه ویژگی سپرده و state متناظر، FKهای guarantee/deposit | `UNIQUE(loan_product_version_id)`؛ checkهای non-negative؛ state/value consistency طبق جدول زیر |

### state/value consistency در `loan_terms`

برای هر مقدار categorized یک جفت `(value, classification_state)` وجود دارد. `classification_state ∈ {classified, unknown, variable, neutral}` و constraint نام‌دار می‌گوید: `classified` فقط با value غیرNULL؛ `unknown/variable/neutral` فقط با value NULL. برای چهار ویژگی محوری (`max_amount`, `monthly_installment`, `max_repayment_months`, `interest_rate`) `unknown/variable` در serving به `ranking_excluded` منتهی می‌شود؛ برای سه ویژگی سپرده، همان state خنثی است. این تصمیم از policy نسخه‌دار US-02 می‌آید، نه از UI.

## پیکربندی پرسشنامه و توصیه‌گر

| جدول | ستون‌های تعیین‌کننده | constraints فیزیکی |
| --- | --- | --- |
| `loan_variables` | `loan_variable_id PK`, `canonical_id text`, `display_order smallint` | `UNIQUE(canonical_id)`؛ `UNIQUE(display_order)` |
| `variable_categories` | `variable_category_id PK`, `loan_variable_id FK`, `canonical_id text`, `ordinal smallint` | `UNIQUE(loan_variable_id, canonical_id)` و `UNIQUE(loan_variable_id, ordinal)` |
| `questionnaire_versions` | `questionnaire_version_id PK`, `version_code text`, `source_hash text`, `publication_state` | `UNIQUE(version_code)`؛ `UNIQUE(source_hash)` |
| `questions` | `question_id PK`, `questionnaire_version_id FK`, `canonical_id text`, `display_order smallint` | `UNIQUE(questionnaire_version_id, canonical_id/order)` |
| `answer_options` | `answer_option_id PK`, `question_id FK`, `canonical_id text`, `display_order smallint` | `UNIQUE(question_id, canonical_id/order)` |
| `recommendation_config_versions` | `config_version_id PK`, `version_code text`, `approved boolean`, `effective_from timestamptz`, `decision_id text` | `UNIQUE(version_code)`؛ approved config باید decision/source reference داشته باشد |
| `question_variable_weights` | FK config/question/variable, `weight numeric(8,6)` | `UNIQUE(config, question, variable)`؛ `CHECK(weight >= 0 AND weight <= 1)`؛ مجموع 1.00 با trigger/deferred validation در T03/T04 |
| `answer_category_compatibilities` | FK config/answer/category, `coefficient numeric(8,6)` | `UNIQUE(config, answer, category)`؛ `CHECK(coefficient >= 0 AND coefficient <= 1)` |

## Session، نتیجه و حریم خصوصی

| جدول | ستون‌های تعیین‌کننده | constraints فیزیکی |
| --- | --- | --- |
| `questionnaire_sessions` | `session_id PK`, `questionnaire_version_id FK`, `state`, `expires_at`, timestamps | `CHECK(expires_at > created_at)`؛ بدون PII یا پاسخ raw؛ index انتخابی روی sessionهای منقضی‌نشده/`expires_at` برای lookup و cleanup |
| `questionnaire_answers` | `questionnaire_answer_id PK`, `session_id FK`, `question_id FK`, `answer_option_id FK` | `UNIQUE(session_id, question_id)`؛ FK answer/question compatibility با composite FK یا trigger؛ `ON DELETE CASCADE` فقط از session به answerهای owned مجاز است |
| `recommendation_runs` | `recommendation_run_id PK`, `session_id FK`, `config_version_id FK`, `state`, `trace_schema_version` | config/version/session immutable پس از completion |
| `recommendation_results` | `recommendation_result_id PK`, `recommendation_run_id FK`, `loan_product_version_id FK`, `outcome_state`, `match_score numeric NULL`, `rank_position integer NULL` | `UNIQUE(run, loan_version)`؛ ranked ⇒ score/rank nonNULL; needs_review ⇒ score/rank NULL; `CHECK(match_score BETWEEN 0 AND 1)` |
| `recommendation_exclusion_reasons` | `reason_id PK`, `recommendation_result_id FK`, `reason_code text`, `loan_variable_id FK NULL` | `UNIQUE(result, reason_code, loan_variable_id)`؛ no free-text internal detail in public API |

### قرارداد persistence/cache در `US-07.T06`

- PostgreSQL منبع حقیقت نرمال‌شده برای `questionnaire_sessions` و `questionnaire_answers` تا `expires_at` است؛ یک session چند answer دارد و هر answer دقیقاً به یک session، question و answer option متصل است. پاسخ تکراری یا JSON/array پاسخ‌ها در session ذخیره نمی‌شود.
- Redis فقط cache TTLدار برای خواندن/نوشتن sessionهای فعال است و schema یا source of truth مستقل ایجاد نمی‌کند. cache key باید opaque/hash‌شده باشد؛ answer، session ID خام، PII و دادهٔ توصیه در key، log، metric یا trace قرار نمی‌گیرد.
- در cache miss یا outage Redis، سرویس باید به PostgreSQL fallback کند؛ write موفق زمانی تأیید می‌شود که persistence PostgreSQL موفق باشد. invalidation پس از write/delete/expiry لازم است.
- cleanup زمان‌دار و idempotent، sessionهای منقضی و answerهای owned آن‌ها را حذف می‌کند. migration، rollback، index evidence، restart/expiry/cache-failure integration test و به‌روزرسانی `erd.md` در همان PR اجباری است.

`users` عمداً در این schema اولیه وجود ندارد. در صورت افزودن هویت، sessionها به nullable `user_id` در migration expand/contract بعدی متصل می‌شوند و retention/consent جداگانه لازم دارد.

## ingest و حکمرانی داده

| جدول | ستون‌های تعیین‌کننده | constraints فیزیکی |
| --- | --- | --- |
| `data_import_runs` | `data_import_run_id PK`, `state`, `started_at`, `completed_at NULL`, `parser_version`, `initiated_by_reference NULL` | completion بعد از start؛ state transition کنترل‌شده |
| `data_source_files` | `data_source_file_id PK`, `data_import_run_id FK`, `sha256 char(64)`, `original_filename text`, `received_at` | `UNIQUE(sha256)`؛ raw binary خارج از DB/object store immutable |
| `staging_loan_rows` | `staging_row_id PK`, import/file FK, `source_row_number integer`, `raw_payload jsonb`, `normalization_state` | `UNIQUE(data_source_file_id, source_row_number)`؛ `CHECK(source_row_number > 0)`؛ JSONB فقط raw انعطاف‌پذیر |
| `data_quality_issues` | `issue_id PK`, import/staging FK NULL, `severity`, `rule_code`, `state`, `owner_reference NULL` | severity/state enum؛ issue بدون import ممنوع |
| `approval_records` | `approval_record_id PK`, import FK, `decision`, `actor_reference`, `decided_at`, `reason` | یک approval effective برای هر import با partial unique index در T05 |
| `audit_events` | `audit_event_id PK`, `approval_record_id FK NULL`, `entity_type`, `entity_id uuid`, `action`, `occurred_at`, `metadata jsonb NULL` | append-only؛ metadata redacted؛ no secret/PII payload |

## ملاحظات 3NF و transaction

- نام بانک فقط در `lenders`، هویت طرح فقط در `loan_products` و شرایط فقط در `loan_product_versions`/`loan_terms` نگهداری می‌شود. این مانع تناقض نرخ یا شرایط در result می‌شود.
- mappingهای many-to-many از جدول واسط استفاده می‌کنند؛ هیچ array/string تکرارشونده برای category یا answer نگهداری نمی‌شود.
- import: raw → staging → normalize/core → approval/publish در transactionهای کوتاه و مرحله‌ای انجام می‌شود. publish تنها پس از approval است؛ failure در staging/core نباید serving را تغییر دهد.
- query/result snapshot برای reproducibility به IDهای version/config وصل است، نه به دادهٔ de-normalized. هر denormalization آینده باید measurement، rebuild strategy و ADR داشته باشد.

## index و query evidence

فهرست indexهای اجرایی و قرارداد query مرتبط در `docs/database/index-and-query-strategy.md` نگهداری می‌شود. `US-04.T05` indexهای lookup-FK و ترتیب پرسشنامه را با migration برگشت‌پذیر افزوده و usage یک lookup انتخابی catalogue را در PostgreSQL 16 با `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` در CI اثبات می‌کند. این specification از عدد ثابت performance یا index بدون query contract اجتناب می‌کند.

## US-10.T03 — Implemented internal review/audit schema (ADR 0006)

Migration `b4d8e1f2a3c5`; all operational entity PKs UUID. Four additive tables:

| Object | Columns / constraints |
| --- | --- |
| operations_imports | import_id uuid PK; import_code text UNIQUE/nonblank; source_hash text (invalid hashes deliberately retained for review); parser_version text nonblank; preparation JSONB NOT NULL, schema_version=1 codec. |
| operations_versions | version_id uuid PK; version_code text UNIQUE/nonblank; import_id uuid FK/index; diff JSONB NOT NULL; UNIQUE(version_id, import_id) supports owner linkage. |
| audit_events | event_id uuid PK; event_order bigint GENERATED BY DEFAULT AS IDENTITY UNIQUE; event_type varchar(16) CHECK import/prepare/approve/publish/rollback; import_id uuid FK/index; version_id uuid nullable composite FK with import_id/index; actor_reference/reason text nonblank; occurred_at timestamptz; correlation_id uuid UNIQUE; before_state nullable and after_state NOT NULL varchar(16); before_version_id/after_version_id nullable UUID FKs. All other fields NOT NULL. Legal before/after state and pointer evidence CHECKs reject unknown/missing transitions (including SQL NULL). Partial UNIQUE import decision and version prepare/approve decision. |
| operations_workflow_head | head_id integer PK CHECK=1; version_id nullable UUID FK; migration seeds one NULL head. Locked per mutation. |
| approval_records | VIEW selecting approve event_id as approval_id, version_id, actor_reference, reason, occurred_at as decided_at, correlation_id. No duplicate decision storage. |

Append-only triggers reject UPDATE/DELETE/TRUNCATE for imports, versions and events.
Public mutation rights are revoked; production runtime role without DDL is T04.
Head/version state is derived from events; no mutable copy of approval. Immutable
row evidence is stored once on import, versions reference it. JSONB is an explicit
historical-document exception to 3NF, never operational query/filter fields. Live
3NF catalogue/core/serving and customer records are untouched. See audit runbook
for bounded keyset access and destructive backup-first downgrade.

## US-11.T02A.1 — قرارداد طراحی بعدی، هنوز غیر اجرایی

[قرارداد account identity/lifecycle](account-identity-lifecycle.md) و
[ADR 0008](../adr/0008-account-identity-lifecycle.md) schema هدف account UUID،
profile یک‌به‌یک و account-owner FK را مشخص می‌کنند. تنها accounts برای هویت
به مدل اصلی افزوده می‌شود؛ archive table موازی ساخته نمی‌شود. partial UNIQUE
active phone و consistency status/archived_at، composite owner/session FK، cutover
phone-PK و guard downgrade به T02A.2 تعلق دارند. جدول‌های access session/bookmark
در diagram آینده‌اند و اجرای C/F جدا دارند. مشخصات اجراشده فعلی و 3NF/audit
قبلی عوض نشده‌اند؛ A.1 هیچ DDL/backfill ندارد.

## US-11.T02A.2 — انتقال اجرایی هویت

phone فقط در accounts؛ profile.account_id PK/FK و owner_account_id رابطه‌ای. partial unique active phone، composite history/session FK و RESTRICT در aa11b02a2002 واقعی‌اند؛ کپی archive یا JSON profile ساخته نشده. بند A.1 بالا طراحی تاریخی است.

## US-11.T02B — proof معتبر پرسشنامه

یک fact سازنده در questionnaire_sessions، بدون جدول/JSON موازی؛ nullable برای legacy فاقد proof معتبر، hex64/immutable در PostgreSQL. metadata cache حامل authority نیست؛ روابط و snapshot unchanged. migration bb11b02b0001.
