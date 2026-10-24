# اتصال OTP کاوه‌نگار — US-11.T06

وضعیت ۲۰۲۶-۱۰-۲۴: مالک تأیید الگوی `OTP1`، نصب محرمانه‌ها، دریافت پیامک و ورود واقعی روی سایت را تأیید کرده است. گزارش و محدودیت شواهد در [checkpoint](../progress/us-11-t06-kavenegar-otp.md) ثبت‌اند؛ مراحل تنظیم پایین راهنما هستند و نباید بی‌دلیل دوباره اجرا شوند. CI/تست‌های خودکار معمول هیچ SMS واقعی نمی‌فرستند.

## ادامهٔ پذیرش محدود روی سایت

ابزار `scripts/verify_otp_live.py` با Python استاندارد روی ترمینال تعاملی خود مالک اجرا می‌شود. فایل از commit دقیق PR دریافت و hash آن بررسی شود؛ سپس `python3 verify_otp_live.py`. به کلید API، اتصال DB، نصب package، checkout پروژه یا ایمیج تازه نیاز ندارد. روی لپ‌تاپ یا سرورِ دارای دسترسی HTTPS به دامنهٔ ثابت shahabfintech.ir قابل اجراست؛ برنامه تغییر env یا restart انجام نمی‌دهد.

شمارهٔ خود مالک و دو کد SMS فقط در prompt مخفی وارد می‌شوند؛ هرگز در آرگومان/فایل/چت قرار نگیرند. حداکثر دو پیامک درخواست می‌شود. کد اول باید سریع وارد شود تا پیش از ۱۲۰ ثانیه، رد کد اشتباه و پذیرش کد درست بررسی شود. بعد از restore/profile، رد کد مصرف‌شده و خروج، token پیشین مجدداً بررسی می‌شود. کد پیامک دوم فقط برای رد پس از انقضای واقعی استفاده می‌شود؛ انتظار حداکثر حدود ۱۲۳ ثانیه دارد و هیچ نشست موفقی برای کد دوم ساخته نمی‌شود.

خروجی فقط stage/status و جمع‌بندی بدون PII است؛ فقط همین خروجی برای ثبت گزارش ارسال شود. این ابزار روی حساب مالک تنها نشست خودش را خارج می‌کند و profile/history را ویرایش نمی‌کند؛ ایجاد challenge/quota و نشستِ همین آزمون از مسیر عادی API اتفاق می‌افتد. روی شمارهٔ دیگران اجرا نشود. در 429/503/خطای شبکه/ورودی/انقضا، برنامه متوقف می‌شود؛ متن upstream یا traceback چاپ نمی‌شود و retry خودکار ندارد. اجرای ناموفق را موفق گزارش نکنید و قبل از تکرار علت و تعداد پیامک‌های قبلی بررسی شوند.

بررسی quota، پنج تلاش، خطای provider و یک ساعت انقضای نشست در تست‌های موجود مستقل انجام می‌شود؛ برای این پذیرش محدود، سرویس ثالث/production را خراب یا quota را با ارسال انبوه پر نمی‌کنیم. خروجی موفق ابزار به معنی آزمون همهٔ مسیرهای محصول یا پایان US-11 نیست.

## پیکربندی سرور

| متغیر | رفتار |
| --- | --- |
| SHAHAB_KAVENEGAR_OTP_ENABLED | پیش‌فرض false؛ انتخاب صریح provider |
| SHAHAB_KAVENEGAR_TEMPLATE_APPROVED | پیش‌فرض false؛ فقط پس از تأیید واقعی الگو true |
| SHAHAB_KAVENEGAR_API_KEY | SecretStr؛ کلید واقعی فقط روی سرور |
| SHAHAB_KAVENEGAR_TEMPLATE | نام دقیق الگوی تأییدشده؛ برای این حساب OTP1؛ default runtime ندارد |
| SHAHAB_OTP_CODE_SECRET | راز تصادفی مستقل حداقل ۳۲کاراکتر، ثابت و یکسان بین workerها |
| SHAHAB_KAVENEGAR_TIMEOUT_SECONDS | پیش‌فرض۵؛ بزرگ‌تر از۰ و حداکثر۱۰ثانیه |
| SHAHAB_DATABASE_URL | اتصال PostgreSQL با psycopg؛ بدون آن فعال‌سازی رد می‌شود |

برای راز مستقل، در محیط خصوصی خود سرور از `secrets.token_urlsafe(32)` استفاده کنید؛
خروجی را فقط در secret store همان سرور ذخیره کنید، نه در ترمینال اشتراکی، Git یا PR.
کلید کاوه‌نگار جای راز مستقل نیست. همه workerها هم‌زمان config یکسان بگیرند.
تنظیمات در `.env.example` خالی/خاموش‌اند؛ فایل `.env` واقعی ignored می‌ماند.

پس از تأیید الگو و مجوز تست، مقادیر خصوصی را روی سرور ثبت، هر دو flag را true و
mock را false کنید؛ backend را با config جدید راه‌اندازی کنید. در TEST، CI=true
یا GITHUB_ACTIONS=true فعال‌سازی sender واقعی حتی با کلید موجود رد می‌شود.
انتخاب live با config ناقص خطای امن startup می‌دهد؛ خاموش بودن پیش‌فرض، سایت را
از boot منع نمی‌کند. staging/production بدون live فعال، request ورود را 503 می‌دهند؛
کد عمومی آزمایشی پذیرفته نمی‌شود. نبود provider با حساب کاربری «واردشده» جعل نمی‌شود.

## قرارداد و امنیت

request و verify همان endpoint/payload قبلی را دارند. فقط HTTPS POST فرم‌encoded به
`api.kavenegar.com/v1/{API-KEY}/verify/lookup.json` با receptor/token/template/type=sms
انجام می‌شود؛ sender، API URL دلخواه، proxy محیطی، retry و redirect وجود ندارند.
TLS validation فعال، timeout محدود و پاسخ حداکثر۶۴KiB است؛ خطای شبکه، JSON نامعتبر،
رد الگو/اعتبار/سرویس، entries ناقص یا وضعیت شکست →503 عمومی بدون متن upstream.
پذیرش provider به معنی تحویل به گوشی نیست؛ live test باید دریافت واقعی را بررسی کند.
بدنه پاسخ، URL کلیددار، شماره، کد، شناسه پیام و exception upstream log/return نمی‌شوند.

challenge تصادفی ۲۵۶بیتی با prefix نسخه‌دار sms1 است؛ کد شش‌رقمی از
HMAC-SHA256(راز مستقل، domain separator + challenge) مشتق می‌شود. این روش PRF
به code column یا ذخیره کد خام نیاز ندارد؛ فقط digest challenge در schema موجود است.
دانستن challenge یا خواندن DB، بدون راز مستقل، امکان brute-force آفلاین کد را نمی‌دهد.
مقایسه constant-time و رقم فارسی/عربی پشتیبانی می‌شود. خود OTP شش‌رقمی و کوتاه است،
پس حفاظت آنلاین همان ۵تلاش، TTL۱۲۰ثانیه و quota مشترک۵درخواست/۱۲۰ثانیه باقی می‌ماند.
برای هر درخواست nonce تازه ساخته می‌شود؛ ورود مجدد worker وابسته به حافظه نیست.
mock challenge در live و sms challenge با کد ثابت mock پذیرفته نمی‌شوند.

رزرو quota/challenge قبل شبکه commit می‌شود و lock هنگام ارسال نگه داشته نمی‌شود.
شکست ارسال، challenge را consumed می‌کند اما quota را حفظ می‌کند؛ در نتیجه
خرابی provider راه دورزدن سهمیه نیست. timeout ممکن است پس از ارسال رخ دهد؛ retry
خودکار می‌تواند هزینه/پیامک تکراری ایجاد کند، پس کاربر challenge تازه درخواست می‌کند.
در صورت شکست DB در invalidation، خطای503 باقی می‌ماند و challenge به client تحویل
نمی‌شود. profile و نشست فقط پس از verify معتبر و persistence موفق صادر می‌شوند.
نشست۱ساعت مطلق، cookie HttpOnly، logout، account generation و تاریخچه تغییر نکرده‌اند.
routeهای request/verify از قبل sync هستند؛ I/O در threadpool FastAPI است، نه event loop.

## آزمون، فعال‌سازی و بازگشت

تست محلی:
`python -m unittest backend.tests.test_kavenegar_otp backend.tests.test_profile_access backend.tests.test_account_session_lifecycle`
از transport مصنوعی استفاده می‌کند؛ نه کلید واقعی و نه شبکه provider لازم است.
دو تست PostgreSQL به suite موجود `backend.tests.test_account_access_postgresql`
اضافه شده‌اند؛ CI همان فرمان قبلی را اجرا می‌کند. mock قراردادی SQLite اثبات race
PostgreSQL نیست؛ اجرای واقعی PostgreSQL و CI نهایی جدا در checkpoint ثبت می‌شوند.

پس از بالا آمدن سایت و تأیید کاوه‌نگار، فقط با شماره آزمایشی مجاز مالک:
request → دریافت واقعی SMS → verify درست/غلط → پروفایل/restore → logout؛
expiry/عدم replay و خطای provider هم بررسی شوند. هیچ شماره، کد، cookie یا key در
شاهد Git ثبت نشود. سپس وضعیت pending آنلاین تغییر می‌کند؛ این PR فاز۱ را Done نمی‌کند.

برای خاموش‌سازی اضطراری، live flag را false و backendها را restart کنید؛ در
production mock هرگز fallback نمی‌شود. revoke نشست‌های موجود تصمیم جدا و مطابق
runbook نشست است. با rotate راز OTP همه challengeهای زنده نامعتبر می‌شوند؛ منتظر
بمانید ۱۲۰ثانیه بگذرد و همه workerها را هماهنگ تعویض کنید. تعویض API Key به‌تنهایی
نشست‌های جاری را revoke نمی‌کند. هیچ schema downgrade/reset یا حذف profile لازم نیست.
بازگشت کد فقط PR revert مستقل؛ آسیب‌پذیری قدیمی lookup عمومی بازگردانده نشود.

منابع رسمی: [Lookup](https://kavenegar.com/rest.html)،
[Python SDK](https://github.com/kavenegar/kavenegar-python)،
[SDKها](https://kavenegar.com/sdk.html). اتصال مستقیم REST با stdlib برای عدم افزودن
وابستگی و کنترل redirect/timeout برگزیده شد؛ همان قرارداد رسمی است.
