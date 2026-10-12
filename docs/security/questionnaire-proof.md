# proof سازنده و مالکیت پرسشنامه — US-11.T02B

مرجع PD01/PD08، ADR 0008 و قرارداد account identity؛ F01 به این تغییر تعلق دارد.
فقط امنیت مسیر موجود: هیچ تغییر طراحی، scoring، raw source یا گزینه حذف حساب نیست.

## قرارداد اجراشده

- POST session یک secret تصادفی ۲۵۶بیتی (`token_urlsafe(32)`) می‌سازد؛ cookie مخصوص
  UUID همان session با HttpOnly/SameSite=Lax/path فعلی و Max-Age=1800. HTTPS یا
  staging/production Secure نیز دارد؛ HTTP local/test برای آزمون موجود باقی است.
- فقط SHA-256 secret در questionnaire_sessions.creator_proof_digest ثبت می‌شود،
  atomically با ساخت session. JSON، URL، log و Redis secret/digest دریافت نمی‌کنند.
  پاسخ API همان sessionId/expiresAt/answers است؛ پاسخ شخصی موفق no-store است.
- پیش از resume/write/recommend، secret قالب معتبر، digest با compare_digest،
  expiry/state تازه و در صورت bound، همان account ID فعال کنترل می‌شوند. شناسه
  تنها، cookie ثابت/ساختگی، secret پرسشنامه دیگر و حساب دیگر رد می‌شوند.
- PostgreSQL authority با row lock است؛ Redis/cache هیچ مجوزی صادر نمی‌کند.
  owner/account status پیش از mutation تازه است. پس از commit پاسخ/قبل return
  recommendation دوباره gate اجرا می‌شود؛ repeatable-read catalogue پس از scoring
  پایان می‌یابد تا owner جاری در snapshot قدیمی بررسی نشود. scoring/نسخه نتیجه ثابت.
- history save علاوه بر actor، digest تأییدشده را در CAS owner و expiry کنترل می‌کند؛
  unique session، composite FK و owner immutable قبلی حفظ. proof بعداً عوض نمی‌شود.
- session ناشناس فقط proof سازنده نیاز دارد؛ پس از bind به حساب، proof و همان حساب
  هر دو لازم‌اند. logout به معنی anonymous access به پاسخ bound نیست. تاریخچه
  snapshot از API حساب‌محور خودش خوانده می‌شود و proof پرسشنامه برای تاریخچه‌خوانی
  قدیمی لازم نیست؛ raw answers عمر مستقل ۳۰ دقیقه دارند.
- عدم وجود و proof نامعتبر 403 عمومی یکسان دارند؛ proof معتبرِ منقضی 410؛ refresh/
  Back هیچ secret تازه، cookie تمدیدشده یا expiry جدید نمی‌سازند. شناسه URL مسیر
  API موجود است، secret/پاسخ هیچ‌وقت در آن نیستند.

## migration و سازگاری

Revision افزایشی `bb11b02b0001`، parent `aa11b02a2002`: ستون nullable digest، CHECK
قالب hex64 و trigger immutable. داده/ID/owner/profile/history/item/reason/answer
قبلی دست‌نخورده؛ NULL legacy یعنی proof قابل‌اعتماد نداریم، نه مجوز ایجاد آن.
proof ثابت قبلی قابل backfill امن نیست؛ پرسشنامه قدیمی resume/recommend نمی‌شود و
کاربر باید جریان جدیدی شروع کند. سوابق snapshot از حساب همچنان قابل خواندن‌اند.

در DB منتخب ابتدا revision/schema/count و backup معتبر بررسی، تمام API writerها
متوقف و migration با نقش محدود و نسخه جدید اجرا شود؛ سپس تمام workerها restart
و smoke جدید انجام شود. این PR روی DB مالک migration اجرا نکرده است. حذف/reset
volume یا answer/history، تغییر UUID یا cookie جعلی برای سازگاری ممنوع است.

Downgrade آزموده ستون/trigger جدید را حذف می‌کند و answers/snapshot را حفظ می‌کند؛
اما proofها دیگر معتبر نیستند. backend قدیمی F01 را برمی‌گرداند؛ روی سرویس قابل
دسترسی rollback به old binary **مجاز نیست**. تا roll-forward امن، مسیرهای پرسشنامه/
recommend در ingress باید بسته بمانند؛ schema downgrade به معنی release امن نیست.
در CI فقط DB disposable با rollback بسته/آزموده استفاده می‌شود؛ deployment انجام نشده.

## آزمون و مرز اثبات

test_questionnaire_proof: دو client/حساب، proof missing/constant/forged/other، عدم
افشای پاسخ/ایجاد history/تغییر پاسخ، bound owner و anonymous-after-logout، retry once،
expiry و refresh بدون تمدید، secret در JSON نیست و cookie flags.

test_questionnaire_proof_postgresql: fixture legacy و حفظ snapshot/answers، proof NULL
fail-closed، upgrade/downgrade، restart و proof durable از DB، digest immutable،
جریان recommendation واقعی و حساب دیگر با proof کپی‌شده. تست‌های A.2، t06 و profile
live قبلی همراه چهار CI حفظ شدند؛ نتیجه روی head نهایی در PR ثبت می‌شود. F01 فقط
پس از CI مربوط بسته است؛ حمله خارجی/production/DAST ادعا نمی‌شود.

F02 purge، نشست durable/یک‌ساعته C، OTP تکراری D، bookmarks F، archive G، H transport/
CSRF/headers و log/backup T04/T05 جدا هستند. سرقت secret از browser آلوده یا DB مالک
خارج از تضمین capability است؛ این کنترل دفاع ضد ID/constant proof است، نه ضد XSS
یا مالک DB. هیچ دکمه/متن/route حذف حساب در فرانت ساخته نشده است.
