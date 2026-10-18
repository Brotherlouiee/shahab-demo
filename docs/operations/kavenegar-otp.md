# اتصال OTP کاوه‌نگار — US-11.T06

این PR آماده‌سازی اتصال است؛ الگوی مالک `OTP1` هنوز تأیید نشده و هیچ SMS واقعی
در آزمون‌ها فرستاده نمی‌شود. merge، Public کردن مخزن و استقرار مجوز جدا دارند.

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
