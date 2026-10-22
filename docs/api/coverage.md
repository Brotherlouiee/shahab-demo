# ماتریس پوشش API — US-09.T081 / ممیزی US-12.T01

> **شاهد تازهٔ HTTP کانتینری:** هر ۱۹ عملیات جدول زیر روی API کانتینری و PostgreSQL تازه با fixture رسمی تست اجرا شد؛ انتظار/واقعی و موارد منفی در [گزارش اجرا](../progress/us-09-t081-local-verification-2026-10-21.md) ثبت است. `GET /health/ready` بدون token عمداً ۴۰۴ بود؛ مسیر مثبت آن در آزمون محلی قبلی با token خصوصی ۲۰۰ بود. تاریخچه و نشان پیش و پس از restart API غیرخالی ماندند؛ انقضای پرسشنامه ۴۱۰ و نشست حساب ۴۰۱ شد. ستون «نتیجهٔ آنلاین» همچنان مربوط به HTTPS دو شخص واقعی است و باز می‌ماند.

> **نتیجهٔ محلی ۲۰۲۶-۱۰-۲۱:** [آزمون HTTP واقعی روی Docker/PostgreSQL مستقل لپ‌تاپ](../progress/us-09-t081-local-verification-2026-10-21.md) احراز هویت mock، دو نشست، پروفایل، پرسشنامه، کنترل مالکیت، logout و restart را پوشش داد؛ توصیه روی کاتالوگ خالی ۵۰۳ داد. سپس fixture رسمی با مجوز صریح مالک از مسیر محافظت‌شدهٔ تست در PostgreSQL موقت دیگری منتشر شد و تست integration با `TestClient`، توصیهٔ ۲۰۰، جزئیات وام، تاریخچه و نشان‌ها را گذراند. ستون «نتیجهٔ آنلاین» پایین عمداً باز می‌ماند: محیط HTTPS محدود و داده/config مصوب عملیاتی فراهم نیستند؛ آزمون محلی جای پذیرش آنلاین نیست.

> وضعیت تازهٔ ۲۰۲۶-۱۰-۲۱: [ممیزی production](../progress/us-09-t081-online-audit-2026-10-21.md) چند پاسخ خواندنی و منفی را ثبت کرده و [آمادگی محیط محدود](../progress/us-09-t081-restricted-environment-readiness-2026-10-21.md) ظرفیت و موانع را روشن کرده است. ستون «نتیجهٔ آنلاین» در جدول زیر مختص محیط **test محدود هدف T081** است؛ چون آن محیط هنوز provision نشده، هیچ‌یک از ۱۹ عملیات در آن پاس نشده‌اند.

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

### شاهد محلی قرارداد ۱۹ عملیات

| عملیات | Docker/API روی loopback | fixture محافظت‌شده روی PostgreSQL موقت |
| --- | --- | --- |
| logout | ۲۰۴ و نشست بعدی ۴۰۱ | اجرا نشد |
| درخواست OTP | ۲۰۰ mock، شمارهٔ نامعتبر ۴۲۲ | ۲۰۰ mock برای دو حساب |
| بازیابی نشست | ۲۰۰، پس از restart نیز ۲۰۰ | ۲۰۰ پس از ساخت دوبارهٔ app |
| تأیید OTP | ۲۰۰ mock برای دو حساب | ۲۰۰ mock برای دو حساب |
| فهرست نشان‌ها | ۲۰۰ خالی | ۲۰۰ شامل یک مورد برای مالک، خالی برای حساب دوم |
| حذف نشان | ۲۰۴ برای مورد ناموجود | ۲۰۴ و فهرست خالی بعدی |
| افزودن نشان | ۴۰۴ برای وام ناموجود | ۲۰۴ و فهرست دارای مورد |
| liveness | ۲۰۰ | اجرا نشد |
| readiness | ۴۰۴ بدون token؛ ۲۰۰ با token خصوصی | اجرا نشد |
| جزئیات وام | ۴۰۴ برای وام ناموجود | ۲۰۰ برای وام منتشرشده |
| نوشتن پروفایل | ۲۰۰؛ تغییر شمارهٔ حساب دیگر ۴۰۳ | اجرا نشد |
| خواندن پروفایل | ۲۰۰؛ داده پس از restart باقی ماند | اجرا نشد |
| ساخت پرسشنامه | ۲۰۱ | ۲۰۱ |
| خواندن پرسشنامه | ۲۰۰ مالک؛ ۴۰۳ حساب دیگر | ۴۰۳ حساب دیگر |
| نوشتن پاسخ | ده PUT با ۲۰۰؛ ۴۰۳ حساب دیگر؛ ورودی نامعتبر ۴۲۲ | ده PUT با ۲۰۰ |
| فهرست تاریخچه | ۲۰۰ خالی | ۲۰۰ شامل یک مورد برای مالک؛ خالی برای حساب دوم و پس از hide |
| پنهان‌سازی تاریخچه | ۴۰۴ برای شناسهٔ ناموجود | ۲۰۴ مالک؛ ۴۰۴ حساب دوم؛ ردیف DB محفوظ |
| جزئیات تاریخچه | ۴۰۴ برای شناسهٔ ناموجود | ۲۰۰ مالک؛ ۴۰۴ حساب دوم و پس از hide |
| توصیه | ۴۲۲ پرسشنامهٔ ناقص؛ ۵۰۳ کاتالوگ خالی | ۲۰۰، config `1.1.0` و ۱۰۲ نتیجه |

ستون دوم، HTTP به API محلی با دیتابیس مستقل است؛ ستون سوم، `TestClient` روی کد همین نسخه و PostgreSQL موقت است. هیچ‌کدام آزمون HTTPS دو آزمونگر، MFA واقعی یا دادهٔ مصوب عملیاتی نیستند. سناریوهای انقضای زمان‌مند و تمامی حالت‌های منفی هر عملیات هنوز پوشش کامل ندارند.

## قرارداد امنیت و زمان

نشست حساب پس از verify عمر مطلق ۳۶۰۰ ثانیه دارد؛ GET session فقط زمان باقی‌مانده را می‌دهد. نشست پرسشنامه و پاسخ خام TTL جداگانهٔ ۱۸۰۰ ثانیه دارند. challenge OTP برابر ۱۲۰ ثانیه، حداکثر پنج تلاش و سهمیه پنج درخواست در ۱۲۰ ثانیه است. account UUID و وضعیت تازهٔ DB authority هستند؛ phone یا cache مرورگر مجوز نیستند.

برای resume/write/recommend، cookie تصادفی سازنده لازم است؛ bearer به‌تنهایی جای آن نیست. نشست bound همان حساب فعال را می‌خواهد. PUT bookmark با `{}` یا historyId معتبرِ حساب خود و DELETE idempotent همان مسیر، پس از commit پاسخ 204 می‌دهند. archive حساب API/UI عمومی ندارد.

## شواهد و تکمیل آنلاین

تست‌های موجود `backend/tests/test_api_documentation.py` پوشش مستقل decoratorها، یکتایی operationId، drift چهار artifact و سیاست docs/auth را می‌سنجند. نتیجهٔ اجرای این نوبت در [ممیزی](../release/us-12-t01-documentation-audit.md) است؛ شواهد قدیمی SDK/Newman یا CI به revision جدید تعمیم داده نمی‌شوند.

طبق [runbook](../runbook/api-testing.md)، برای هر ۱۹ عملیات status واقعی و SHA runtime/data/config و بازخوانی persistence ثبت شود. حساب دوم در context جدا، proof، انقضا، خروج، profile/history و save/list/remove نشان‌شده‌ها بررسی شوند. فقط status و نام عملیات در گزارش مشترک باشد؛ token/cookie/phone/answers و ID خصوصی ثبت نشوند. T081 تا شواهد واقعی محیط خودش باز است.
