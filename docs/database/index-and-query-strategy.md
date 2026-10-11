# Index and query strategy — US-04.T05

## اصل تصمیم

این indexها از query contractهای V1 آمده‌اند، نه از حدس یا تلاش برای پوشش تمام ستون‌ها. در این مرحله هنوز endpoint محصولی یا repository اجراشونده وجود ندارد؛ بنابراین قراردادها محدود، قابل‌ردیابی و همراه با تست PostgreSQL ثبت شده‌اند. هر query جدید باید پیش از index جدید، cardinality و plan اندازه‌گیری‌شده داشته باشد.

## قرارداد query و index

| Query contract | Order/shape پایدار | Index | دلیل |
| --- | --- | --- | --- |
| فهرست طرح‌های یک بانک | `WHERE loan_products.lender_id = :id`؛ API بعدی order قطعی دارد | `ix_loan_products_lender_id` | lookup مرجع بانک بدون scan کل catalogue |
| نسخه‌های یک طرح | `WHERE loan_product_versions.loan_product_id = :id` | `ix_loan_product_versions_loan_product_id` | واکشی نسخه‌های immutable یک طرح |
| فیلتر serving بر اساس انتشار | `WHERE publication_state = 'PUBLISHED'` | `ix_loan_product_versions_publication_state` | شروع query recommendation/list از نسخهٔ منتشرشده |
| پرسش‌های یک نسخه | `WHERE questionnaire_version_id = :id ORDER BY display_order` | `ix_questions_version_display_order` | ترتیب نمایش پایدار و بدون sort اضافی |
| گزینه‌های سؤال/categoryهای متغیر | lookup با FK | indexهای child-FK | جلوگیری از scan هنگام ساخت config |
| provenance فایل منبع | `WHERE data_import_run_id = :id` | `ix_data_source_files_data_import_run_id` | audit یک import بدون scan تمام فایل‌ها |

unique constraintهای موجود نیز index هستند و index تکراری نمی‌سازیم: `lenders.canonical_name`، `(lender_id, canonical_name)`، `loan_terms.loan_product_version_id`، `(questionnaire_version_id, canonical_id)` و `(config_version_id, question_id, loan_variable_id)`.

## شواهد EXPLAIN واقعی

تست integration `backend/tests/test_postgresql_migrations.py` روی PostgreSQL 16 واقعی در GitHub Actions، ۱٬۰۰۰ بانک/طرح نماینده می‌سازد و این query را اجرا می‌کند:

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT loan_product_id, canonical_name
FROM loan_products
WHERE lender_id = :selective_lender_id;
```

معیار قبولی: plan باید `Index Scan` یا `Bitmap Index Scan` روی `ix_loan_products_lender_id` داشته باشد؛ `Seq Scan` برای این lookup انتخابی پذیرفته نیست. test هم migrationهای index را upgrade و downgrade می‌کند تا rollback واقعاً indexها را حذف کند.

## مرزهای کارایی و امنیت

- `SELECT *`، pagination بدون order قطعی، N+1 و joinهای بدون query contract ممنوع‌اند.
- indexهای هم‌پوشان یا index روی دادهٔ حساس بدون اندازه‌گیری ممنوع است.
- creation indexهای پرهزینه روی production بزرگ در migration بعدی با `CREATE INDEX CONCURRENTLY`، plan rollback و ADR انجام می‌شود؛ migration فعلی فقط schema خالی/ابتدایی را هدف دارد.
- cost/time ثابت نیست؛ CI plan shape را assert می‌کند، نه عدد شکننده.

## US-10.T03 audit access

Unique import_code/version_code lookups; indexes on version.import_id and
 event.import_id/version_id; partial unique initial-import and prepare/approve
 decisions. Unique event_order supports bounded keyset pagination; composite
ix_audit_actor_order(actor_reference,event_order) supports actor-scoped keysets.
No JSONB index: preparation/diff are historical evidence, not list predicates.
Singleton head lock intentionally serializes rare administration. Public scoring
reads are unaffected. PostgreSQL tests use EXPLAIN with a selective event_order
predicate to verify the ordered-key index path (costs are not asserted).
