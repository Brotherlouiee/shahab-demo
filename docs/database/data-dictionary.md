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
