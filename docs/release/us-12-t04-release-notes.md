# یادداشت انتشار پیش‌نویس — US-12.T04

**وضعیت: Unreleased / draft، بدون tag، تاریخ انتشار یا مجوز production.** مبنای این یادداشت `main=c17366f3bae710f58fa24ff0aa78ee192d68f5eb` پس از مرج #136 است؛ این SHA مرجع آماده‌سازی است، نه نسخهٔ مستقر. commit نهایی همین PR و CI آن در توضیحات PR ثبت می‌شوند. پیش از release پس از US-13، یادداشت و شواهد با SHA واقعی نهایی دوباره تطبیق داده شوند.

## از دید کاربر و سیستم

| حوزهٔ موجود در کد مبنا | رفتار و مرز ادعا |
| --- | --- |
| توصیهٔ وام | پاسخ‌های canonical در پرسشنامهٔ همان مرورگر به API می‌رسند؛ سرور فقط دادهٔ PUBLISHED و config تأییدشده را استفاده می‌کند. ranked، low compatibility و needsReview جدا هستند؛ نیازمند بررسی درصد/رتبه ندارد. درصد تطابق، احتمال تأیید یا تضمین دریافت وام نیست. |
| نمایش و مسیرها | نتیجه، فیلتر بانک/تطابق، جزئیات و شرایط امن، مقایسه، پروفایل، سوابق و نشان‌شده‌ها پیاده‌سازی شده‌اند. هیچ ثبت درخواست واقعی وام، پرداخت یا تحلیل AI خارجی از این یادداشت استنتاج نمی‌شود. |
| حساب و نگهداری | account UUID و نسل مستقل، نشست یک ساعت مطلق، proof و پاسخ خام پرسشنامه تا۳۰دقیقه؛ پروفایل/سوابق/نشان‌شده‌ها حساب‌محور. hide حذف فیزیکی snapshot نیست؛ بایگانی داخلی حساب UI عمومی ندارد. |
| OTP | اتصال کاوه‌نگار در #133 مرج شده، الگوی انتخاب‌شده OTP1 است. live و اعلام تأیید الگو پیش‌فرض خاموش‌اند؛ local/test کد mock دارند و staging/production به mock fallback نمی‌کنند. تأیید الگو و دریافت واقعی SMS هنوز شاهد مستقل می‌خواهند. |
| آماده‌سازی انتشار | #134 ممیزی مستندات، #135 پوشش آزمون و journey واقعی با FastAPI/PostgreSQL آزمایشی، #136 نمونهٔ غیرفعال preview و طرح smoke را تحویل داده‌اند. هیچ‌یک اثبات استقرار یا restore عملیاتی نیست. |

این PR فقط طرح/مستندات T04 را اضافه می‌کند؛ UI، backend، endpoint/payload، CSS/asset، dependency، workflow، schema/migration، ضرایب D-005، data/config version و تنظیم فعال Netlify/Compose بدون تغییر می‌مانند. ERD/schema و منابع خام نیازی به بازنویسی ندارند. CHANGELOG در Unreleased می‌ماند.

## محدودیت‌های شناخته‌شده و شرط انتشار

- **محیط واقعی:** T081→T07، TLS/proxy/cookie هم‌مبدأ، publication همان DB پایدار و smoke/restart هنوز شواهد سروری می‌خواهند. `/health/live` فقط سلامت پردازه است؛ readiness محافظت‌شده نیز جای audit کاتالوگ/schema نیست. [طرح T03](../runbook/preview-smoke.md).
- **provider و عملیات:** تأیید/فعال‌سازی OTP و آزمون شمارهٔ مجاز، authority/MFA/DB role ابزار عملیات، DAST و sink/alert واقعی بازند؛ CI یا پاسخ مصنوعی جای آن‌ها نیست. [OTP](../operations/kavenegar-otp.md)، [عملیات](../operations/operations-runbook.md).
- **بازیابی:** رمزنگاری/backup، RPO/RTO و retention مصوب، scheduler/cleanup و تمرین restore واقعی بازند. ابزار فعلی cleanup، invalidate سراسری credential یا آشتی‌دادن تغییرات پس از backup را انجام نمی‌دهد؛ نبود مسیر تأییدشدهٔ آن‌ها مانع بازگشایی restore است. [طرح بازگشت](../runbook/release-migration-rollback.md).
- **artifact:** دو image مستقل build/scan و انتشار/pull-by-digest هنوز T04A هستند. حساب/namespace/token و مجوز نشر registry وابستگی مستقل است، نه نیاز به VPS؛ هیچ digest/tag ساختگی یا latest تولید نمی‌شود.
- **نسخهٔ نهایی:** برنامه و ۲۰ جفت شناسهٔ US-13 دست‌نخورده‌اند؛ تکمیل refactor و آزمون‌های متأثر روی SHA نهایی و تمام gateهای باز قبل از T05 لازم‌اند. هر شش چک این PR فقط سلامت همین revision را نشان می‌دهند.

مرجع واحد معوقات سروری همان «جدول تسک‌های پس از استقرار» [سند جامع](../SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md) است؛ این فهرست توضیح اثر محدودیت بر release note است و هیچ ردیف/شناسهٔ موازی یا وضعیت Done تازه ایجاد نمی‌کند. نسخه/تاریخ انتشار، میزبان، مالک عملیات و RPO/RTO به‌جای حدس، تا تصمیم و شاهد واقعی خالی می‌مانند.

## بستهٔ تحویل نهاییِ آینده

فرم غیرفعال [release-evidence.json](../examples/release/release-evidence.json) فقط ساختار ثبت را فراهم می‌کند. در اجرای مجاز، SHA/tag نهایی، digest هر دو image، schema/data/config، CIها، محیط، نتیجهٔ smoke/restore و پذیرش مالک ثبت شوند؛ artifact خصوصی backup، phone، answer، cookie، credential و secret وارد Git نشوند. خروجی عمومی فقط مرجع پالایش‌شدهٔ شواهد باشد.

T04 اکنون تنها بخش مستقل سند/طرح را تحویل می‌دهد. rehearsal آنلاین T04، T04A و انتشار T05 انجام نشده‌اند؛ مرج این PR مجوز استقرار، migration، publication داده یا SMS نیست. قدم مستقل بعدی پس از پذیرش/مرج: `US-12.T04A.1`.
