# مستندات دیتابیس — مدل جاری و سابقهٔ طراحی

مبنای موجودی: `main=f5711e78df58366b65c7f00e29fa484ea5fb0b85` در ممیزی US-12.T01. مدل اجرایی `backend/app/infrastructure/db/models.py` شامل **۳۵ جدول** است؛ زنجیرهٔ **۱۸ migration** یک head به نام `ff11b02f0001` دارد. این موجودی ایستا اثبات upgrade/downgrade یا استقرار روی PostgreSQL نیست.

## مسیر مرجع

- [ERD](erd.md)، [dictionary](data-dictionary.md) و [طرح فیزیکی 3NF](physical-schema-3nf.md): بخش‌های آغازین طراحی US-04 تاریخی‌اند؛ افزوده‌های اجرایی US-09/10/11 و موجودی زیر وضعیت جاری را مشخص می‌کنند.
- [migration و rollback](migrations-and-rollback.md) و [cutover هویت حساب](account-identity-migration-runbook.md): توقف writer، backfill و guardها؛ `upgrade head` خودکار جای review این مراحل نیست.
- [index/query](index-and-query-strategy.md): قرارداد query و شواهد مرحله‌ای؛ latency محیط production ادعا نمی‌شود.
- [هویت نسلی](account-identity-lifecycle.md)، [نشست مشترک](../security/account-session-lifecycle.md)، [proof](../security/questionnaire-proof.md)، [bookmark](../security/account-bookmarks.md) و [پاک‌سازی خام](../operations/raw-answer-retention.md): قراردادهای امنیت/نگهداری جاری.

## موجودی جدول‌های ORM جاری

| مرز | جدول‌ها |
| --- | --- |
| کاتالوگ و serving | `lenders`، `loan_products`، `loan_product_versions`، `loan_terms`، `loan_variables`، `variable_categories`، `loan_category_assignments`، `loan_conditions`، `loan_serving_facts`، `serving_catalogue_versions`، `serving_catalogue_members` |
| پرسشنامه و config | `questionnaire_versions`، `questions`، `answer_options`، `recommendation_config_versions`، `question_variable_weights`، `answer_option_weights`، `answer_category_compatibilities`، `questionnaire_sessions`، `questionnaire_answers` |
| حساب و snapshot | `accounts`، `user_profiles`، `account_access_sessions`، `account_otp_challenges`، `account_otp_quota_events`، `recommendation_history_runs`، `recommendation_history_items`، `recommendation_history_item_reasons`، `account_bookmarks` |
| ورودی و عملیات | `data_import_runs`، `data_source_files`، `operations_imports`، `operations_versions`، `audit_events`، `operations_workflow_head` |

`approval_records` طبق ADR-0006 یک **view** روی audit_events است، نه جدول ORM یا دفتر تصمیم موازی. نام‌های مفهومی اولیه مانند `recommendation_runs`، `recommendation_results`، `recommendation_exclusion_reasons`، `staging_loan_rows`، `data_quality_issues`، `guarantee_types` و `deposit_account_types` در موجودی ORM فعلی جدول مستقل ندارند؛ از شکل قدیمی ERD نباید DDL یا وجود endpoint نتیجه گرفت. runtime snapshot در recommendation_history_* و evidence عملیات طبق ADRهای مربوط پیاده شده‌اند؛ این توضیح migration یا مجوز ساخت جدول جدید نیست.

مالکیت profile/history/bookmark بر UUID همان نسل حساب است؛ phone کلید ورود است. پاسخ خام پرسشنامه پس از TTL جداگانه پاک می‌شود، ولی snapshot و metadata مرتبط طبق قرارداد E حفظ می‌شوند. نشست حساب و OTP موقت، جدول و سیاست مستقل دارند؛ archive/hide/removed_at حذف فیزیکی history/profile نیستند. exceptionهای JSONB historical evidence و card snapshot از تصمیم‌های ADR-0006 و ADR-0011 می‌آیند و مجوز کپی raw answer نیستند.

SQLite و validator متنی جای PostgreSQL نیستند. بازبینی پس از US-13 و شواهد restore/retention/CI در دفتر معوقات موجود سند جامع باز می‌مانند؛ نتیجهٔ این نوبت در [گزارش ممیزی](../release/us-12-t01-documentation-audit.md) است.
