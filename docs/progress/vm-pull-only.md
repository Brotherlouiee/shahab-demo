# آماده‌سازی Compose ماشین VM بدون build

درخواست صریح مالک: فایل مستقل prod VM فقط برای pull و run ایمیج‌های منتشرشده؛
این آماده‌سازی، اجرای استقرار یا پایان T081/T07/T05 نیست و شناسهٔ جدیدی نمی‌سازد.
مبنا: main=8c105c7f446c66665e4af6c7c37f5d76f4607fac پس از PR143؛ شاخهٔ مستقل Codex.
سه قانون طلایی تأیید: مرحله‌ای، بازخوانی کامل راهنما، تحویل با تست/شاهد/مستندات.
کل راهنما با blob cf716dba4d7ac3f2fab2e4ce6ec97db593f8a5c6 و پروتکل با blob
7a2e369ee6bef86601cb79b3b02cbe82c9e15d96 و AGENTS و مهارت همکاری بازخوانی شدند.
منابع مرتبط: Compose توسعه، image manifest، تنظیم FastAPI و NGINX، runbook
استقرار/preview/rollback و مستندات رسمی Docker Compose.

وضعیت فعلی: Compose توسعه build و bind mount source و Vite دارد. مطلوب: فایل مستقل
با imageهای digest-pinned، PostgreSQL پایدار، Redis داخلی، proxy HTTPS same-origin،
health/restart و مهاجرت دستی جدا. build، نصب dependency، reload و mount سورس ممنوع.
دامنه: فایل Compose جدید و تنظیم/نمونه env/راهنما/test/CI مرتبط؛ کد برنامه، داده،
migration، sourceهای رسمی، Dockerfile و Netlify و Compose توسعه ثابت‌اند.
پیش‌نیاز اجرا: رازهای خصوصی، certificate معتبر و runtime DB role غیرمالک با schema
مجاز؛ ساخت فایل این پیش‌نیازها را ایجاد نمی‌کند. publication داده و OTP جدا می‌مانند.
حداقل اثبات: compose config واقعی، نبود build/source mount، migration و boot ایزوله
با DB مصنوعی، TLS و proxy/cookie با imageهای candidate در CI موجود؛ بدون secret registry.
خطر اصلی: proxy/scheme غلط، اجرای خودکار migration یا از دست‌رفتن DB؛ trust فقط IP
فرانت، مهاجرت profile دستی و volume پایدار بدون هیچ reset.
بودجه: یک تغییر زیرساختی محدود با آزمون و PR؛ Docker در این محیط موجود نیست، اجرای
Docker در CI مجاز انجام می‌شود. هیچ اقدام روی VM واقعی انجام نشده است.
زمان آغاز ابزار ثبت شده؛ وقفهٔ بین پیام ادامهٔ مالک و کار قبلی در زمان دیواری هست
اما به‌عنوان فعالیت فنی جمع نمی‌شود؛ تفکیک کامل آن ثبت نشده است.

## پیش از push

تعداد۳۶ unittest با CLI واقعی Compose5.6.0 موفق؛ binary رسمی با SHA256 منتشرشده
بررسی شد. ruff0.17.1، actionlint1.7.12، secret scanner و diff check موفق‌اند.
یک انتظار تست برای command=null سرویس بدون command اصلاح شد؛ رفتار Compose تغییر
نکرد. header/cookie/restart و migration هنوز باید در Docker CI واقعی اجرا شوند.
محیط محلی Docker ندارد؛ هیچ boot واقعی VM ادعا نمی‌شود. grant API صریح و مستقل
از role مهاجرت/اپراتور است و در CI با نقش مصنوعی و ممنوعیت عملیات/DDL بررسی می‌شود.
زمان‌سنج قابل استناد از11:05:18 UTC است؛ بخش پیش از آن و تفکیک فعالیت‌ها ثبت دقیق
ندارد. وقفهٔ گفت‌وگو را فعالیت فنی نام‌گذاری نمی‌کنیم. زمان CI در PR اضافه می‌شود.
سه قانون طلایی در تحویل محفوظ‌اند؛ این PR کد محصول، داده و ترتیب رجیستری را عوض نمی‌کند.

## تشخیص اولین CI

اجرای image39242265628 روی7820d66 در تست parse config شکست خورد: Compose در CI
کلید false مربوط به create_host_path را در JSON حذف می‌کند؛ CLI محلی آن را صریح
برمی‌گرداند. خطای اصلی KeyError در تست بود، نه boot محصول. انتظار تست با مدل bool
حذف‌شده=false هماهنگ شد؛ true همچنان رد و تنظیم false صریح در فایل حفظ می‌شود.
هیچ build/security assertion یا timeout تغییر نکرد؛ تست نزدیک پیش از push تکرار شد.
