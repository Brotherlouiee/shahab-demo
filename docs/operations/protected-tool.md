# ابزار داخلی محافظت‌شده — US-10.T04

ابزار: `python -m scripts.operations_tool --command /private/command.json`.
هیچ endpoint جدید در FastAPI/Swagger عمومی ایجاد نمی‌کند. اپراتور به دسترسی
سیستم اجرای ابزار، provider معتبر مستقل و DB role محدود نیاز دارد؛ OTP مشتری
و شماره تلفن یا role داخل JSON هرگز مجوز مدیریتی نیست.

## آماده‌سازی authority

مالک deployment باید یک OAuth authority با introspection **HTTPS**، TLS معتبر،
client authentication، audience مستقل `shahab-operations` و MFA اپراتور تنظیم کند.
محیط secret process: `SHAHAB_OPERATIONS_AUTHORITY` یک JSON دارای endpoint، issuer،
audience، client_id و client_secret است. service_client_ids فقط clientهای سرویس
مستقل و ca_file فقط CA مورداعتماد خصوصی اختیاری است. هیچ مقدار credential در
repository قرار نمی‌گیرد. `SHAHAB_DATABASE_URL` باید account غیرمالک باشد.

Token opaque در prompt بدون echo گرفته می‌شود. automation آن را از secret
manager در `SHAHAB_OPERATIONS_ACCESS_TOKEN` قرار می‌دهد؛ token را در argument،
command.json، history shell یا خروجی ننویسید. محیط ابزار را به فرانت منتقل نکنید.

پاسخ provider باید active boolean، sub، iss، aud، exp، iat، client_id و roles
صریح داشته باشد؛ انسان علاوه بر آن amr شامل mfa و auth_time در ۵ دقیقه اخیر.
مدت token حداکثر ۱۵ دقیقه است؛ MFA واقعی را خود provider انجام می‌دهد. سرویس
فقط client_id allowlist‌شده و نقش service دارد و تأیید/انتشار انسانی نمی‌کند.
ساخت client مستقل، صدور/ابطال token و سیاست MFA وظیفه provider است؛ این ابزار
login/password/MFA فیک نمی‌سازد. پاسخ نامعتبر، ابطال، timeout/5xx، redirect، TLS
نامعتبر و نبود پیکربندی، fail-closed هستند. provider extensions باید پیش از
فعال‌سازی با همین قرارداد تطبیق داده شوند؛ قابلیت تولیدی هنوز فعال نشده است.

## قرارداد دستور

فایل JSON حداکثر ۸ KiB؛ شناسه‌ها ۱۲۰ کاراکتر و reason حداکثر ۵۰۰. فیلد اضافی
حتی actor/role/hash/score رد می‌شود؛ خروجی فقط خلاصه bounded و شاهد issue است.

| operation | فیلدهای دقیق | مجوز |
| --- | --- | --- |
| import | import_id, reason | data.import؛ extraction رسمی موجود از فایل‌های trusted |
| review | import_id | data.review؛ count/issue plan ذخیره‌شده |
| prepare | import_id, version_id, reason | data.import؛ draft مرتبط و diff |
| approve | version_id, reason | data.approve؛ approval مستقل |
| publish | version_id, reason | data.publish؛ serving واقعی + audit در یک transaction |
| rollback | version_id, expected_current_version_id, reason | data.rollback؛ CAS و approval تاریخی |

نمونه غیرحساس command.json:

```json
{"operation":"review","import_id":"official-review-01"}
```

برای کارهای editor و admin دو grant مستقل، یا ترکیب صریح approved هر دو role
لازم است؛ admin به‌طور ضمنی import/review نمی‌گیرد. پیش از هر عمل authority
دوباره خوانده می‌شود؛ هیچ role از command/consumer session دریافت نمی‌شود.
Reason باید توضیح غیرحساس باشد؛ رمز، token، شماره مشتری یا پاسخ پرسشنامه ننویسید.

## scope انتشار و rollback

این release فقط extraction رسمی ۱۰۲ وام و config مصوب 1.1.0/D-005 را منتشر
می‌کند. rows/hash/parser دقیق و digestهای موجود materializer بررسی می‌شوند؛
source/config جدید با ارسال hash قدیمی یا JSON دلخواه پشتیبانی نمی‌شود. version
داخلی به public_code قطعی همان source/config نگاشت دارد؛ هیچ رکورد وام کپی نمی‌شود.
نسخه‌های بازبینی داخلی یک منبع یکسان، projection عمومی immutable یکسانی دارند؛
rollback آن‌ها head داخلی را برمی‌گرداند و catalogue یکسان را reuse می‌کند.
ادعای بازگردانی بین منابع/configهای هنوز تأییدنشده مطرح نیست. drift عمومی و
catalogue ناتمام به خطا منجر می‌شوند. state داخلی/serving/audit یک transaction
دارند؛ خطا هیچ «موفقیت انتشار» یا کاتالوگ ناقص باقی نمی‌گذارد.

## DB role و فعال‌سازی

migration را account جدا اجرا کند. runtime role نباید مالک جدول، عضو owner/
superuser/createrole/createdb/bypassrls یا دارای CREATE در public باشد؛ ابزار این
را پیش از عملیات بررسی می‌کند. account API یا superuser ابزار عملیات نیست.
برای role تعیین‌شده توسط deployment فقط:

- USAGE روی public؛ SELECT/INSERT روی جدول‌های import/core/config/serving مصرفی
  materializer و operations_imports/operations_versions/audit_events.
- SELECT/UPDATE روی operations_workflow_head؛ UPDATE روی serving_catalogue_versions.
- USAGE/SELECT روی audit_events_event_order_seq؛ SELECT روی approval_records برای
  analytics مجاز جداگانه اختیاری است.
- بدون UPDATE/DELETE/TRUNCATE روی شواهد و بدون دسترسی به user_profiles، پاسخ‌های
  questionnaire یا recommendation_history. فهرست دقیق grant مصرفی در fixture
  test_operations_tool_postgresql.TABLES و module map materializer قابل بازبینی است.

role واقعی/secret ایجاد یا deploy نشده است. فعال‌سازی بعداً با provider و حساب
محدود مالک و آزمون محیط مربوط انجام می‌شود؛ CI شاهد deployment نیست. برای
خاموش‌کردن، دسترسی اجرای CLI و credential authority را revoke کنید؛ داده/audit
را حذف نکنید. rollback کد adapter و tool، schema T03 را نگه می‌دارد.

آزمون: `python -m unittest backend.tests.test_operations_tool`؛ TLS authority
محلی و certificate معتبر آزمایشی، بدون mock کردن transport. PostgreSQL CI نیز
`test_operations_tool_postgresql` را با LOGIN role محدود واقعی و source رسمی اجرا
می‌کند. fixture provider صرفاً integration test است؛ MFA واقعی مالک ادعا نشده است.

مراجع: [RFC 7662](https://www.rfc-editor.org/rfc/rfc7662) و
[RFC 8176](https://www.rfc-editor.org/rfc/rfc8176)، ADR 0007 و audit-runbook.md.

## اجرای گام‌به‌گام و آموزش

[راهنمای عملیات T05](operations-runbook.md) نمونه‌های معتبر هر شش operation،
بازخوانی فقط‌خواندنی، تمرین rollback و آموزش منع ویرایش مستقیم دیتابیس را دارد.
