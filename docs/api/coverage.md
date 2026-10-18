# ماتریس پوشش API — US-09.T081 / ممیزی US-12.T01

مبنای این بازبینی: `main=f5711e78df58366b65c7f00e29fa484ea5fb0b85`، ۱۹ عملیات در routerها، OpenAPI و Postman. **همهٔ شواهد آنلاین هنوز اجرا نشده‌اند**؛ وجود schema یا تست قرارداد، شاهد HTTPS/PostgreSQL آنلاین نیست.

| method | مسیر | دسترسی/وابستگی جاری | OpenAPI/Postman | نتیجهٔ آنلاین |
| --- | --- | --- | --- | --- |
| POST | `/api/v1/account-access/logout` | ابطال credential و پاک‌سازی cookie؛ DB | بله | اجرا نشده |
| POST | `/api/v1/account-access/request` | mock فقط local/test؛ challenge/quota مشترک در DB پیکربندی‌شده | بله | اجرا نشده |
| GET | `/api/v1/account-access/session` | حساب فعال خود؛ زمان باقی‌مانده، بدون تمدید | بله | اجرا نشده |
| POST | `/api/v1/account-access/verify` | challenge/code؛ ایجاد/بازیابی حساب و profile و نشست DB | بله | اجرا نشده |
| GET | `/api/v1/bookmarks` | حساب فعال خود؛ DB، keyset pagination | بله | اجرا نشده |
| DELETE | `/api/v1/bookmarks/{loan_id}` | حساب فعال خود؛ DB، desired-state و context متعلق به خود | بله | اجرا نشده |
| PUT | `/api/v1/bookmarks/{loan_id}` | حساب فعال خود؛ DB، desired-state و context متعلق به خود | بله | اجرا نشده |
| GET | `/api/v1/health/live` | عمومی؛ سلامت پردازه، بدون اثبات DB/catalogue | بله | اجرا نشده |
| GET | `/api/v1/health/ready` | توکن اختصاصی اپراتور؛ بدون اثبات DB/catalogue | بله | اجرا نشده |
| GET | `/api/v1/loans/{loan_id}` | فقط نسخهٔ فعال PUBLISHED در DB | بله | اجرا نشده |
| PUT | `/api/v1/profiles` | حساب فعال خود؛ phone برابر actor، persistence DB | بله | اجرا نشده |
| GET | `/api/v1/profiles/me` | حساب فعال خود؛ persistence DB | بله | اجرا نشده |
| POST | `/api/v1/questionnaire/sessions` | ساخت نشست موقت در DB و cookie تصادفی سازنده | بله | اجرا نشده |
| GET | `/api/v1/questionnaire/sessions/{session_id}` | proof سازنده؛ اگر bound است همان حساب فعال؛ DB | بله | اجرا نشده |
| PUT | `/api/v1/questionnaire/sessions/{session_id}/answers/{question_id}` | proof سازنده؛ اگر bound است همان حساب فعال؛ DB | بله | اجرا نشده |
| GET | `/api/v1/recommendation-history` | حساب فعال خود؛ snapshot در DB و keyset pagination | بله | اجرا نشده |
| DELETE | `/api/v1/recommendation-history/{history_id}` | حساب فعال صاحب snapshot؛ DB؛ DELETE فقط hide | بله | اجرا نشده |
| GET | `/api/v1/recommendation-history/{history_id}` | حساب فعال صاحب snapshot؛ DB؛ DELETE فقط hide | بله | اجرا نشده |
| POST | `/api/v1/recommendations` | نشست کامل و proof معتبر؛ catalogue/config؛ حساب bound برای history | بله | اجرا نشده |

## قرارداد امنیت و زمان

نشست حساب پس از verify عمر مطلق ۳۶۰۰ ثانیه دارد؛ GET session فقط زمان باقی‌مانده را می‌دهد. نشست پرسشنامه و پاسخ خام TTL جداگانهٔ ۱۸۰۰ ثانیه دارند. challenge OTP برابر ۱۲۰ ثانیه، حداکثر پنج تلاش و سهمیه پنج درخواست در ۱۲۰ ثانیه است. account UUID و وضعیت تازهٔ DB authority هستند؛ phone یا cache مرورگر مجوز نیستند.

برای resume/write/recommend، cookie تصادفی سازنده لازم است؛ bearer به‌تنهایی جای آن نیست. نشست bound همان حساب فعال را می‌خواهد. PUT bookmark با `{}` یا historyId معتبرِ حساب خود و DELETE idempotent همان مسیر، پس از commit پاسخ 204 می‌دهند. archive حساب API/UI عمومی ندارد.

## شواهد و تکمیل آنلاین

تست‌های موجود `backend/tests/test_api_documentation.py` پوشش مستقل decoratorها، یکتایی operationId، drift چهار artifact و سیاست docs/auth را می‌سنجند. نتیجهٔ اجرای این نوبت در [ممیزی](../release/us-12-t01-documentation-audit.md) است؛ شواهد قدیمی SDK/Newman یا CI به revision جدید تعمیم داده نمی‌شوند.

طبق [runbook](../runbook/api-testing.md)، برای هر ۱۹ عملیات status واقعی و SHA runtime/data/config و بازخوانی persistence ثبت شود. حساب دوم در context جدا، proof، انقضا، خروج، profile/history و save/list/remove نشان‌شده‌ها بررسی شوند. فقط status و نام عملیات در گزارش مشترک باشد؛ token/cookie/phone/answers و ID خصوصی ثبت نشوند. T081 تا شواهد واقعی محیط خودش باز است.
