# ماتریس پوشش API — US-09.T081

وضعیت آنلاین همهٔ ردیف‌ها: **اجرا نشده؛ میزبان HTTPS/PostgreSQL و دسترسی تست‌کنندگان هنوز تعیین نشده‌اند.** حضور در schema اثبات اجرای موفق endpoint در محیط آنلاین نیست.

| method | مسیر | دسترسی/وابستگی | در OpenAPI و Postman | آزمون دستی روی URL آنلاین |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/account-access/logout` | حساب خود؛ DB در مسیرهای وابسته | بله | اجرا نشده |
| POST | `/api/v1/account-access/request` | mock فقط local/test؛ DB هنگام verify | بله | اجرا نشده |
| GET | `/api/v1/account-access/session` | حساب خود؛ DB در مسیرهای وابسته | بله | اجرا نشده |
| POST | `/api/v1/account-access/verify` | mock فقط local/test؛ DB هنگام verify | بله | اجرا نشده |
| GET | `/api/v1/health/live` | mock فقط local/test؛ DB هنگام verify | بله | اجرا نشده |
| GET | `/api/v1/health/ready` | token اپراتور | بله | اجرا نشده |
| GET | `/api/v1/loans/{loan_id}` | نسخهٔ PUBLISHED در DB | بله | اجرا نشده |
| PUT | `/api/v1/profiles` | حساب خود؛ DB در مسیرهای وابسته | بله | اجرا نشده |
| GET | `/api/v1/profiles/me` | حساب خود؛ DB در مسیرهای وابسته | بله | اجرا نشده |
| POST | `/api/v1/questionnaire/sessions` | نشست موقت؛ DB | بله | اجرا نشده |
| GET | `/api/v1/questionnaire/sessions/{session_id}` | نشست موقت؛ DB | بله | اجرا نشده |
| PUT | `/api/v1/questionnaire/sessions/{session_id}/answers/{question_id}` | نشست موقت؛ DB | بله | اجرا نشده |
| GET | `/api/v1/recommendation-history` | حساب خود؛ DB در مسیرهای وابسته | بله | اجرا نشده |
| DELETE | `/api/v1/recommendation-history/{history_id}` | حساب خود؛ DB در مسیرهای وابسته | بله | اجرا نشده |
| GET | `/api/v1/recommendation-history/{history_id}` | حساب خود؛ DB در مسیرهای وابسته | بله | اجرا نشده |
| POST | `/api/v1/recommendations` | نشست کامل؛ catalogue/config؛ cookie اثبات برای history | بله | اجرا نشده |

## شواهد محدود موجود

- تست مستقل route inventory، یکتایی operationId، drift و سیاست docs/security در `backend/tests/test_api_documentation.py` است.
- schema با `openapi-spec-validator` محلی معتبر شد؛ dependency جدید runtime اضافه نشد.
- SDK رسمی `postman-collection` هر ۱۶ درخواست را خواند؛ Newman به FastAPI واقعی محلی health/live=200 و readiness بدون capability=404 فرستاد. این اثبات import به workspace آنلاین Postman نیست.
- تست‌های هدفمند API مالکیت، cookie/proof و atomic history را بررسی می‌کنند؛ تست profile دارای adapter fake و تست history دارای SQLite/منابع رسمی است. هیچ‌یک PostgreSQL دائمی آنلاین نیست.
- آزمون Swagger در `tests/profile-live/api-documentation.spec.mjs` به job فعلی FastAPI/PostgreSQL/Chromium وصل است؛ نتیجهٔ آن روی SHA نهایی در PR ثبت می‌شود، نه از روی وجود فایل تست.
- دانلود Chromium محلی فایل ناقص برگرداند؛ نصب/مرورگر محلی موفق اعلام نمی‌شود. CI و تست روی URL آنلاین جدا هستند.

## تکمیل gate آنلاین

پس از آماده‌سازی محیط طبق [runbook](../runbook/api-testing.md)، ستون آخر با status واقعی/شاهد پالایش‌شده و SHA runtime/data/config تکمیل شود. همهٔ ۱۶ عملیات و خطاهای مالکیت/انقضا/خروج، persistence با بازخوانی و دسترسی مالک و تست‌کنندهٔ دوم الزامی‌اند. token/phone/answers/ID نشست را در ماتریس ثبت نکنید. T081 تا آن زمان باز است.

