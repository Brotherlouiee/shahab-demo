# ADR 0007 — ابزار داخلی و اتصال تراکنشی serving

پذیرفته‌شده برای US-10.T04 به درخواست مالک؛ T03 مرج و CI موفق است.

CLI محدود انتخاب می‌شود تا route جدید مدیریتی در FastAPI عمومی باز نشود.
اپراتور token کوتاه‌عمر صادرشده پس از MFA را به ابزار می‌دهد؛ سرویس credential
مستقل دارد. authority OAuth introspection HTTPS پیکربندی‌شده با TLS معتبر،
issuer/audience/expiry/active و MFA بررسی می‌شود. roles فقط از پاسخ مورداعتماد
authority می‌آیند و پیش از هر اقدام دوباره دریافت می‌شوند. OTP مشتری، actor/role
در command و مخفی‌کردن UI مجوز نیستند. redirect/proxy و fallback غیرفعال‌اند.
RFC 7662 و RFC 8176 مبنا هستند؛ amr/roles/auth_time قرارداد صریح provider هستند.
بدون provider/secret معتبر، ابزار رد می‌کند؛ login/password/MFA جعلی ساخته نمی‌شود.

bridge در transaction repository اجرا می‌شود؛ همان materializer رسمی فعلی و
همان source/config digest را استفاده می‌کند. publication فقط نسخه‌ای را می‌پذیرد
که canonical rows/hash/parser دقیقاً به extraction رسمی برابر است. سطرها/config
از command دریافت نمی‌شوند. active catalogue drift رد می‌شود؛ audit failure همه
writeهای materializer/head را برمی‌گرداند. rollback نسخه داخلی فقط به catalogue
تأییدشده متناظر وصل می‌شود؛ داده تاریخی/approval بازنویسی نمی‌شود. منبع جدید یا
config جدید خارج از allowlist فعلی نیازمند توسعه/تصمیم داده جداست، نه bypass.

اجرای ابزار با account غیرمالک PostgreSQL و بدون DDL/superuser الزامی است؛
grantهای حداقلی به جدول‌های عملیات و materializer و sequenceها اعمال می‌شوند.
role provisioning بر عهده مالک deployment است؛ هیچ role/secret واقعی ساخته نمی‌شود.
تست این کنترل با role واقعی محدود در DB disposable CI انجام می‌شود.
