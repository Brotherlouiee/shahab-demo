# Data dictionary مفهومی — US-04.T01

این dictionary contract طراحی است؛ columnها در `US-04.T02` نهایی می‌شوند. مالک یعنی مسئول کیفیت و معنای داده، نه لزوماً نویسندهٔ migration. retention پیشنهاد اولیه است و تا تصویب policy حریم خصوصی، هیچ job حذف خودکار ساخته نمی‌شود.

| جدول مفهومی | کلید و رابطهٔ اصلی | داده/منبع اصلی | مالک | retention و ملاحظهٔ امنیتی |
| --- | --- | --- | --- | --- |
| `lenders` | `lender_id`; 1→N `loan_products` | نام و شناسهٔ بانک از import تأییدشده | دادهٔ محصول | تا زمان ارائهٔ کاتالوگ؛ دادهٔ عمومی |
| `loan_products` | `loan_product_id`; FK `lender_id` | هویت پایدار طرح | دادهٔ محصول | تا زمان وجود سابقهٔ نسخه؛ حذف فیزیکی ممنوع |
| `loan_product_versions` | `loan_product_version_id`; FK product | نسخه، source/provenance، وضعیت publish | دادهٔ محصول | immutable؛ audit دائمی |
| `loan_terms` | 1→1 version؛ FK guarantee/deposit type | مقادیر typed نرخ، مبلغ، قسط، مدت و stateهای explicit | موتور توصیه‌گر | immutable؛ متن خام در این جدول نیست |
| `guarantee_types` | `guarantee_type_id` | دستهٔ canonical ضمانت | مالک محصول | مرجع نسخه‌دار |
| `deposit_account_types` | `deposit_account_type_id` | نوع حساب سپردهٔ canonical | مالک محصول | مرجع نسخه‌دار |
| `loan_variables` | `loan_variable_id` | هشت متغیر canonical | مالک محصول | مرجع نسخه‌دار |
| `variable_categories` | FK variable؛ unique `(variable, category_id)` | دسته‌بندی استاندارد | مالک محصول | مرجع نسخه‌دار |
| `questionnaire_versions` | `questionnaire_version_id` | نسخهٔ پرسشنامه و source hash | مالک محصول | immutable پس از publish |
| `questions` / `answer_options` | FK version/question | ID و متن canonical پرسش/گزینه | مالک محصول | متن قابل نمایش؛ بدون پاسخ کاربر |
| `recommendation_config_versions` | `config_version_id` | `approved`, `effective_from`, decision/source reference | مالک محصول | immutable؛ audit دائمی |
| `question_variable_weights` | FK config/question/variable | سهم پرسش در متغیر؛ مجموع معتبر | موتور توصیه‌گر | constraint مجموع در T02/T03 |
| `answer_category_compatibilities` | FK config/answer/category | ضریب سازگاری ۰..۱ | موتور توصیه‌گر | source/decision قابل‌ردیابی |
| `questionnaire_sessions` | `session_id`; FK version؛ 1→N `questionnaire_answers` | چرخهٔ پاسخ ناشناس، state و `expires_at` | محصول و حریم خصوصی | PostgreSQL source of truth تا ۳۰ دقیقه (implemented in US-07.T06)؛ بدون PII؛ cleanup idempotent |
| `questionnaire_answers` | FK session/question/answer option؛ `UNIQUE(session, question)` | انتخاب canonical کاربر | محصول و حریم خصوصی | owned by session؛ حذف با expiry session؛ log نشود |
| `recommendation_runs` | `run_id`; FK session/config | timestamp، trace version و state | موتور توصیه‌گر | برای reproducibility؛ بدون PII غیرضروری |
| `recommendation_results` | FK run/version | score/trace نسخه‌دار برای گزینهٔ rankable | موتور توصیه‌گر | نتیجه به version دقیق وصل است |
| `recommendation_exclusion_reasons` | FK result/run | دلیل typed حذف از ranking | موتور توصیه‌گر | قابل‌توضیح و غیرحساس |
| `data_import_runs` / `data_source_files` | run/file IDs | hash، دریافت، source owner | عملیات داده | immutable و audit دائمی |
| `staging_loan_rows` | FK import/file | raw row، شماره سطر و provenance | عملیات داده | دسترسی محدود؛ پاکسازی طبق policy |
| `data_quality_issues` | FK import/staging | severity، rule، state و owner | عملیات داده | تا closure + retention audit |
| `approval_records` / `audit_events` | FK import/actor | تصمیم publish و رویداد append-only | عملیات داده | tamper-evident/retention بلندمدت |

## قواعد ستون مشترک برای مرحلهٔ بعد

- همهٔ جدول‌ها: `id` UUID، `created_at` UTC؛ `updated_at` فقط برای aggregateهای mutable.
- raw text فارسی، hash source، `source_row_number`, `source_column`, parser version و decision ID در مسیر provenance نگهداری می‌شوند؛ در response API عمومی نمایش داده نمی‌شوند.
- `deleted_at` فقط برای session یا policyهای مصوب privacy بررسی می‌شود؛ کاتالوگ نسخه‌دار و audit event soft-delete عمومی نمی‌گیرند.
- مقدار نمونهٔ حساس، credential یا PII در این سند ثبت نمی‌شود.
- Redis جدول مفهومی/رابطه‌ای نیست: cache موقت و قابل‌بازتولیدِ sessionهای فعال است، نه منبع حقیقت. سیاست کامل آن در `docs/architecture/0009-anonymous-session-persistence-and-cache.md` ثبت شده است.

## US-09.T05A افزوده‌های فیزیکی

| جدول/ستون | کلید و محدودیت | کاربرد |
| --- | --- | --- |
| `loan_product_versions.source_row_number` | unique همراه `source_file_id` | سطر رسمی برای version |
| `loan_category_assignments` | PK `(loan_product_version_id, loan_variable_id)`؛ state/category سازگار | دسته و state هر یک از هشت متغیر |
| `loan_conditions` | PK/FK همان loan version؛ text خالی مجاز | متن خام شروط همان نسخه، پیش از parser امن |
| `answer_option_weights` | PK config/answer/variable؛ مقدار ۰..۱ | وزن پاسخ از جدول تبدیل، با سطر منبع |
| `answer_category_compatibilities` | PK config/answer/category؛ مقدار ۰..۱ | ضریب جدول تناسب یک‌به‌یک، با سطر/ستون |
| `serving_catalogue_versions` / `serving_catalogue_members` | یک active در PostgreSQL؛ عضویت نسخهٔ وام | pointer و membership انتشار نسخه‌دار با actor/reason |

## US-09.T05B

| جدول | قید | خواندن |
| --- | --- | --- |
| `loan_serving_facts` | PK/FK همان `loan_product_version_id`؛ ماه/نسبت نامنفی | نیاز به سپرده، ماه خواب، نسبت، ضمانت، حساب و logo reference فقط از نسخهٔ منتشرشده؛ مقدار نامعلوم عددی `NULL` است. |

آداپتور فقط اعضای active catalogue با نسخهٔ `PUBLISHED` و source file همان catalogue را می‌خواند؛ شرط همان loan version از `loan_conditions` می‌آید.


## user_profiles — اجرایی پس از US-11.T02A.2

| Column | PostgreSQL type | Null/default |
| --- | --- | --- |
| account_id | uuid PK/FK accounts ON DELETE RESTRICT | non-null؛ phone از accounts join می‌شود |
| first_name, last_name | varchar(60) | non-null, empty string |
| income, job | varchar(40) | non-null, empty string; API allowlist |
| gender | varchar(10) | non-null, empty string; female/male/empty |
| avatar_data_url | text | nullable; supported base64 raster; 100 KB server limit |
| created_at, updated_at | timestamptz | non-null, now(); ORM updates updated_at |

Source: migration aa11b02a2002؛ account/profile feature. PD02–PD07 حفظ دائمی profile/history/hidden/archive را مشخص می‌کنند؛ حذف خام ۳۰دقیقه‌ای مستقل است. API public phone از accounts می‌آید، فقط پروفایل همان account تغییر می‌کند.

## US-10.T03 actual audit dictionary

- operations_imports: immutable reviewed input aggregate; import_code is the T02
  external key, UUID is relational identity; source_hash/parser_version identify
  provenance; preparation is version-1 accepted/rejected/issue evidence.
- operations_versions: immutable prepared version identity and catalogue diff;
  import_id joins the exact stored source plan, no second copy of canonical rows.
- audit_events: event_id identity, event_order stable order (gaps allowed),
  event_type decision kind; actor_reference internal server subject; reason
  non-sensitive explanation; occurred_at UTC instant; correlation_id server UUID;
  import_id/version_id linked resource; before_state/after_state target transition;
  before_version_id/after_version_id head transition for publish/rollback.
- operations_workflow_head: exactly the seeded head_id=1 in application, nullable
  version_id until initial internal publication. Mutable lock/projection only.
- approval_records: relational VIEW of approve audit facts, not a copied table.

Exact types/nullability/constraints are in physical-schema-3nf.md. This implemented
additive schema supersedes the earlier conceptual approval/audit columns only;
customer-serving storage is unchanged. Evidence has no automatic retention purge.

## US-11.T02A.1 — dictionary هدف حساب؛ schema فعلی نیست

مرجع ستون/type/nullable/constraint واحد:
[قرارداد account identity/lifecycle](account-identity-lifecycle.md).

| موجودیت هدف | کلید و factهای اصلی | هدف/دسترسی/retention |
| --- | --- | --- |
| accounts (جدید در A.2) | account_id uuid PK؛ phone canonical immutable؛ status و created_at/archived_at؛ یک active phone | هویت هر دوره حساب؛ retained forever، archived دسترسی ندارد؛ phone در profile/history کپی نشود |
| user_profiles (کلید جدید در A.2) | account_id PK/FK؛ همان name/income/job/gender/avatar/timestamps موجود | profile جاری مستقل از snapshot؛ initial خالی جز phone در account؛ جنسیت اختیاری؛ archive retained |
| questionnaire_sessions (owner جدید در A.2) | owner_account_id nullable FK؛ session UUID و expiry موجود | anonymous تا bind معتبر؛ raw answers پس از ۳۰ دقیقه حذف، metadata لازم history حفظ |
| recommendation_history_runs (owner جدید در A.2) | owner_account_id NOT NULL FK و pair FK با session؛ unique session فعلی | visible/hidden snapshot همیشگی؛ owner و version immutable، hide≠erasure |
| account_bookmarks / account_access_sessions (آینده F/C) | account/version junction یا account-bound credential | تعریف جزئی/اجرای جدا؛ browser/phone مالکیت را تعیین نمی‌کند، TTL نشست یک‌ساعته مصوب هنوز اجرا نشده |

این بخش تصمیم طراحی است، نه تأیید وجود این ستون‌ها. مهاجرت در A.2 با legacy
mapping و حفظ counts/FK/snapshot روی PostgreSQL واقعی اثبات شود؛ کنترل F01/F02
در مراحل B/E رفع می‌شود و در A.1 رفع‌شده ادعا نمی‌شود.

## US-11.T02A.2 — ستون‌ها و قیود اجرایی جدید

| جدول/ستون | نوع / null/default | قیود و منبع |
| --- | --- | --- |
| accounts.account_id | UUID NOT NULL | PK، opaque immutable؛ تولید یک‌بار |
| accounts.phone | varchar(11) NOT NULL | `^09[0-9]{9}$`، immutable؛ partial UNIQUE فقط status active |
| accounts.status | varchar(16) NOT NULL، active | CHECK active/archived؛ archive terminal با trigger |
| accounts.created_at | timestamptz NOT NULL، now() | UTC؛ backfill همان profile created_at؛ immutable |
| accounts.archived_at | timestamptz NULL | active⇒NULL، archived⇒nonnull>=created_at؛ بایگانی retained |
| user_profiles.account_id | UUID NOT NULL | PK/FK accounts RESTRICT؛ phone duplicate حذف شده |
| questionnaire_sessions.owner_account_id | UUID NULL | FK accounts RESTRICT؛ index؛ NULL ناشناس؛ bind immutable |
| recommendation_history_runs.owner_account_id | UUID NOT NULL | FK accounts RESTRICT؛ index(owner,created_at,run_id) |
| session/history pair | UUID pair | session UNIQUE(id,owner)، history composite FK RESTRICT؛ unique session قبلی حفظ |

profile fields/shape و API allowlist همان‌اند؛ items/reasons/version/hidden_at
بدون تغییر. AccountActor شامل UUID و phone تازه از DB است؛ نقش اپراتور نیست.
جدول access_sessions و bookmarks هنوز آینده‌اند. migration قدیمی دست‌نخورده؛
[runbook](account-identity-migration-runbook.md) و تست PostgreSQL مرجع عملیات/rollback.
بخش target A.1 بالا طرح تاریخی است؛ این بخش وضعیت اجرای core identity را ثبت می‌کند.

## US-11.T02B — proof معتبر پرسشنامه

questionnaire_sessions.creator_proof_digest: varchar(64) NULL، بدون default؛ SHA-256 capability تصادفی، CHECK NULL یا hex64، immutable trigger، مالک feature پرسشنامه، lifetime همان expiry ۳۰ دقیقه. NULL legacy مجوز نیست؛ raw secret هرگز DB نیست. owner/session/history constraints ثابت؛ [قرارداد](../security/questionnaire-proof.md).
