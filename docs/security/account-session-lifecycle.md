# نشست مطلق یک‌ساعته و ابطال مشترک — US-11.T02C

مرجع PD08، ADR 0008 و قرارداد حساب؛ T02A/B مرج، C فقط lifecycle موجود را تغییر می‌دهد.
پروفایل/سوابق/پرسشنامه/scoring/ظاهر ثابت؛ هیچ قابلیت حذف حساب به کاربر ارائه نمی‌شود.

## مدل و مرز اعتماد

- account_access_sessions: token_digest SHA-256 PK، account_id FK RESTRICT، issued_at،
  expires_at، revoked_at؛ phone کپی نیست. رمز تصادفی ۲۵۶بیتی فقط در cookie HttpOnly
  و response ورود فعلی است، در DB/log/URL نیست؛ credential در localStorage نوشته نمی‌شود.
- صادرشدن پس از OTP معتبر و profile سالم؛ commit رکورد نشست قبل از پاسخ/cookie.
  خرابی DB یا ثبت token →503 بدون credential؛ challenge مصرف‌شده replay نمی‌شود.
  account/profile ایجاد اتمیک قبلی حفظ است؛ این PR ادعا نمی‌کند آن‌ها با OTP و token
  در یک تراکنش واحد‌اند. خطای store ممکن است profile سالم ایجادشده را باقی بگذارد؛
  token منتشر نمی‌شود و retry از challenge تازه است.
- PostgreSQL clock_timestamp authority مشترک workerها؛ expiry دقیقاً issued_at+۱h.
  trigger تغییر digest/account/issued/expiry و بازفعال‌کردن revoked را رد می‌کند.
  status همان account ID تازه بررسی می‌شود، نه lookup active با شمارهٔ token قدیمی.
- read/authorization قفل account سپس session دارد؛ G باید همان ترتیب را رعایت کند.
  برچسب مثبت cache authority نیست؛ refresh/restore/Q جدید روی issued/expires UPDATE ندارند.
  GET session فقط زمان باقی‌مانده ceil(seconds) را برمی‌گرداند؛ در ۳۶۰۰ رد، نه تمدید.
- logout همان credential را revoke می‌کند؛ replay در هر worker/restart رد می‌شود.
  چند نشست مستقل یک حساب مجاز؛ logout فعلی سراسری نیست. profile/history حذف نمی‌شوند.
  archive use case در G با تغییر status و revoke همه نشست‌های آن ID در همان transaction؛
  آن عملیات نباید قفل quota/OTP را بگیرد و هیچ UI/endpoint عمومی archive در C نیست.

## OTP و سهمیه مشترک

account_otp_challenges digest opaque، phone ورودی موقت، created/expires دقیق ۱۲۰s،
attempts<=۵ و consumed_at؛ account پیش از verify لازم نیست. هیچ code خام در DB نیست؛
MockOtpProvider فعلی فقط local/test و staging/production همچنان fail-closed.
Provider واقعی/provision SMS یا فعال‌سازی production تحویل این PR نیست.

account_otp_quota_events هر درخواست دو dimension hashed (phone/client شبکه)، زمان
UTC و UUID؛ پنجره همان ۵ request/۱۲۰s، quota مشترک تمام workerها. X-Forwarded-For
کلاینت trust نمی‌شود. advisory transaction lock ثابت 110203 در همین DB quota و
consume را serialize می‌کند؛ دو اتصال برای یک challenge فقط یک موفقیت دارند.
خطای code در DB commit می‌شود تا worker دیگر attempt را دور نزند؛ خطای storage
rollback و 503 عمومی، بدون fallback به memory در DB پیکربندی‌شده.

حدود قبلی ۱۰۲۴ challenge، ۲۰۴۸ dimension و ۱۰۲۴ نشست زنده، اکنون مشترک‌اند؛
revoked session تا expiry برای replay-denial می‌ماند ولی ظرفیت نشست فعال را نمی‌گیرد.
OTP/quota/session expired در درخواست‌های access پاک می‌شوند؛ نشست expired قابل استفاده
نیست حتی بدون اجرای cleanup. برنامه cleanup/metrics/load در T05 باید کم‌حجم بودن
زمان lock و سرویس محیط واقعی را اندازه بگیرد؛ این PR ظرفیت production را اثبات نمی‌کند.
این TTLهای موقت credential/OTP، سیاست نگهداری همیشگی profile/history را تغییر نمی‌دهند.

## migration و راه‌اندازی

revision افزایشی cc11b02c0001، parent bb11b02b0001؛ فقط سه جدول/index/constraint/trigger؛
هیچ business row/answer/history یا source backfill ندارد. DB منتخب/revision/count و
backup قابل‌بازیابی بررسی؛ همه writerها توقف؛ با نقش migration و private env:

```bash
python -m alembic upgrade head
```

سپس همه workerهای backend جدید راه‌اندازی و request→verify→restore/profile→logout
با cookie jar یا bearer خود tester آزمایش شوند. یک ورود مجدد برای tokenهای حافظه‌ای
قبلی لازم است؛ آن‌ها به شمارهٔ فعال resolve/backfill نمی‌شوند. downgrade به
bb11b02b0001 سه جدول موقت را حذف و credentials/challenges را invalid می‌کند؛ business
facts حفظ می‌شوند. writers باید متوقف و backend سازگار راه‌اندازی و ورود از نو انجام
شود؛ TTL قبلی ۳۰ دقیقه در binary قدیمی تصمیم مصوب C را اجرا نمی‌کند، roll-forward
ترجیح دارد و reopen قدیمی پذیرش release نیست. schema downgrade تنها آزمون DB disposable
است؛ reset volume/حذف profile/history برای rollback ممنوع.

DB مالک/لپ‌تاپ/production در این PR migrate نشده. بعد از restore backup، revocation
جدیدتر از backup ممکن است در آن نباشد؛ T05 باید تمام credential/OTPهای restoreشده
را پیش از بازگشایی invalidate کند و status/profile/history را حفظ کند؛ restore امن
با صرف برگرداندن فایل ادعا نمی‌شود. real host/T081/T07 و gateهای H/T03–T05 باقی‌اند.

## اثبات

clock tests memory+SQLite: ۳۵۹۹/۳۶۰۰، remaining بدون renew، digest-only، ابطال در store
دیگر، shared attempt/quota/single-use. PostgreSQL CI: migration/rollback و تمام business
facts؛ HTTP روی app/worker تازه برای request/verify/restore/logout، replay/restart؛
expiry immutable و ساعت کنترل‌شده؛ race دو connection؛ quota/attempt مشترک و fault
در credential INSERT بدون accessToken/cookie. آزمون‌های A.2/B/t06/operations و دو
browser suite موجود حفظ؛ نتیجه exact head در PR. SQLite جای proof PostgreSQL نیست.

AccountAccess memory فقط local/test بدون SQL (یا test double) است؛ بدون DB واقعی
verify نمی‌تواند profile persist کند. configured API از SQL adapter request-scoped
استفاده می‌کند؛ SQL Session/credential cache بین درخواست‌ها share نمی‌شوند. auth
مشتری هیچ مجوز داخلی نمی‌دهد. کاهش درخواست OTP در personal-info هنوز D است؛
bookmark/browser cleanup F، archive G، purge E و transport H مستقل‌اند.

## US-11.T02F — cleanup نشست

verify/session علاوه بر phone/remaining، accountId opaque سرور برای cache epoch؛
هیچ renewal یا پذیرش ID/phone client نیست. logout فعلی revoke می‌کند و همه cookieهای
creator با prefix شهاب از path /api/v1 حذف؛ business rows unchanged. network/storage
failure از پاک‌سازی حافظه جدا، pending revoke پیش از restore/login retry و stale
response generation guard. [قرارداد/محدودیت‌ها](account-bookmarks.md).

## US-11.T02G — بایگانی داخلی

`archive_account(account_id, db)` فقط use case داخلی است و به route کاربر وصل نیست. قفل advisory وابسته به phone و سپس account row برای جلوگیری از رقابت با `ensure_profile` و بعد ابطال همه `account_access_sessions` همان `account_id` در همان transaction استفاده می‌شود. بایگانی terminal است؛ فعال‌سازی دوباره نسل قدیمی ممنوع و ورود مجدد با phone تأییدشده نسل تازه و profile خالی می‌سازد. سوابق/پروفایل/نشان‌شده‌ها حفظ و تنها owner آن نسل قابل دسترسی است که پس از archive غیرفعال می‌شود. آزمون PostgreSQL واقعی، failure rollback و deployment همچنان gate مستقل دارند؛ هیچ UI حذف حساب یا operator endpoint ارائه نشده است.
