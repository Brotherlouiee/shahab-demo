# انتقال هویت حساب — US-11.T02A.2

مرجع: [قرارداد](account-identity-lifecycle.md)، ADR 0008، checkpoint
[US-11.T02A.2](../progress/us-11-t02a2.md). دو revision جدید، بدون بازنویسی migration
قبلی: `aa11b02a2001` expand، سپس `aa11b02a2002` contract؛ parent `b4d8e1f2a3c5`.
این سند مجوز اجرای production نیست؛ در این تسک فقط fixture/CI آزمایشی اجرا می‌شود.

## پیش‌نیاز و ترتیب cutover

۱. DB منتخب، revision واقعی، backup و restore آزمودهٔ همان محیط، نسخهٔ backend و
تعداد profile/session/history مشخص شوند؛ credential/export/PII در Git یا گزارش نیست.
سرویس API و همه writerهای customer را متوقف کن؛ از reset volume یا حذف داده استفاده نکن.
rollout ترکیبی backend قدیمی/جدید ممنوع است؛ جدید به schema contract نیاز دارد.
برای حجم بزرگِ اثبات‌شده، window/زمان قفل را در محیط نماینده اندازه بگیر؛ این PR
آنلاین‌بودن migration با هر حجمی یا ظرفیت production را ادعا نمی‌کند.

۲. با همان متغیر خصوصی `SHAHAB_DATABASE_URL` و نقش migration، expand را اجرا کن:

```bash
python -m alembic upgrade aa11b02a2001
python -m scripts.backfill_account_identity
```

فرمان دوم فقط revision/count را می‌خواند؛ صحت کامل داده در apply بررسی می‌شود.
phone canonical، orphan و owner متفاوت history/session blocker هستند. هیچ شماره
یا دادهٔ خراب normalize/merge حدسی نمی‌شود. شروع از revision غیرمنتظره نیازمند
audit مستقل است؛ `stamp` یا تغییر مستقیم ledger جای migration نیست.

۳. backfill مستقل و atomic، با writers متوقف:

```bash
python -m scripts.backfill_account_identity --apply
```

mapping در accounts ذخیره می‌شود؛ retry همان ID را reuse می‌کند. created_at account
از profile قدیمی است؛ facts و created/updated پروفایل، hidden_at، ID/version/items/
reasons/پاسخ‌ها تغییر نمی‌کنند. session ناشناس NULL می‌ماند. فقط session تاریخی
قبل از owner-bind که owner NULL دارد، از owner همان history یکتای ذخیره‌شده پر
می‌شود؛ owner غیرNULL متفاوت رد می‌شود. داده خام به accounts/history کپی نمی‌شود.
خروجی فقط count/revision است؛ caller نتیجه نامعلوم را با همان revision دوباره بررسی کند.

۴. پس از بررسی mapping و شمارش، contract را اجرا کن:

```bash
python -m alembic upgrade aa11b02a2002
```

contract backfill را زیر قفل دوباره بررسی می‌کند تا هیچ writer دیرهنگام از قلم
نیفتد؛ سپس PK profile، FK owner و composite session/owner را تغییر می‌دهد و
phone تکراری را حذف می‌کند. schema تغییر و backfill در transaction rollback می‌شوند.
قیود قدیمی session unique باقی‌اند؛ داده catalogue/scoring/audit دست‌نخورده است.

۵. تمام workerهای backend نسخه جدید را راه‌اندازی کن. نشست‌های قدیمی memory-only
با توقف همه workerها باطل می‌شوند؛ هیچ credential phone-only به active جدید lookup
نمی‌شود. کاربران یک بار دوباره وارد می‌شوند. نشست تازه پیش از انتشار به account ID
متصل و هر درخواست status همان ID را از DB اعتبارسنجی می‌کند؛ mock همچنان local/test.
نشست durable/یک‌ساعته در C است؛ TTL فعلی ۱۸۰۰ ثانیه اینجا تغییر نمی‌کند.

۶. schema/head، count، profile/history بازخوانی‌شده و نمونه مسیر OTP→profile→result→
history را روی محیط منتخب اثبات کن؛ stale credential و مالک دیگر رد شوند. سپس
ترافیک را باز کن. تنها CI fixture انجام‌شده، اثبات migration روی لپ‌تاپ/سرور مالک نیست.
بایگانی عمومی هنوز API/UI ندارد و G مستقل است؛ SQL UPDATE دستی کار اپراتور نیست.

## rollback

قبل از archive و چند نسل، writers را متوقف کن؛ ابتدا با binary همین نسخه و نقش
migration به expand یا parent بازگرد، سپس backend قدیمی را راه‌اندازی کن:

```bash
python -m alembic downgrade aa11b02a2001
```

این مرز phone/phone-FKهای قبلی را با mapping حفظ‌شده بازمی‌سازد؛ account IDs هنوز
در expand باقی‌اند و upgrade دوباره آن‌ها را reuse می‌کند. در صورت بازگشت کامل به
`b4d8e1f2a3c5`، mapping جدید حذف می‌شود اما همه داده‌های legacy نمایش‌پذیر حفظ‌اند؛
همه نشست‌ها باید از نو صادر شوند. downgrade به base فرمان عملیاتی rollback این
قابلیت نیست؛ base فقط در DB disposable آزمون استفاده می‌شود.

اگر حتی یک archived account یا چند نسل با phone مشترک وجود داشته باشد، downgrade
**پیش از هر DDL رد می‌شود**: schema قبلی status/چند profile را نمی‌تواند نمایش دهد.
داده retained حذف/merge/فعال نمی‌شود؛ راه درست roll-forward یا restore مجاز در محیط
جدا با reader account-aware است. برای عبور از guard triggerها/status را دستکاری نکن.
آزمون fixture guard، cleanup مخصوص DB disposable دارد؛ الگوی عملیات محصول نیست.

## شواهد لازم

`test_account_identity_postgresql` حفظ تمام factها و timestampها، hidden snapshot/
items/reasons/answers، mapping ثابت در retry و downgrade-expand-upgrade، audit شکست،
constraint مالک و رقابت واقعی دو connection و نسل/credential قبلی را بررسی می‌کند.
`test_postgresql_migrations`، `test_t06_postgresql` و browser profile-live مسیرهای
فعلی را حفظ می‌کنند. فرانت، طراحی، source bytes، catalogue و scoring تغییر ندارند.
F01 proof و F02 purge با این انتقال بسته نمی‌شوند؛ B/E باقی‌اند.
