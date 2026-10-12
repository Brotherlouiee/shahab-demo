# مدل تهدید سامانه شهاب — US-11.T01

نسخه ۱؛ بازبینی ۲۰۲۶-۱۰-۱۲؛ مبنا: `ae52f112dc16b9e07447a195725560f54263c981` پس از مرج PR #106.
این سند **بازبینی طراحی و کد** است، نه گواهی امنیت production، DAST یا رفع آسیب‌پذیری.
مدل‌های [پروفایل](profile-threat-model.md) و [audit عملیات](operations-audit-threat-model.md)
جزئیات حوزه‌ای را حفظ می‌کنند؛ این سند مرجع سراسری جاری و ثبت شکاف‌های بین حوزه‌هاست.
[بررسی داده و retention](privacy-retention-review.md) و
[checkpoint شواهد](../progress/us-11-t01.md) مکمل آن‌اند.

## محدوده، دارایی و مرز اعتماد

| دارایی/سطح | محل و هدف | مرز و مالک |
| --- | --- | --- |
| عمومی | وام PUBLISHED، facts/شرایط/asset تأییدشده | read model/API عمومی؛ مالک داده. پاسخ شخصی توصیه صرفاً به دلیل عمومی‌بودن وام، عمومی نیست. |
| حساس کاربر | phone، نام، درآمد/شغل/جنسیت/avatar، پاسخ پرسشنامه و سابقه توصیه | browser ↔ FastAPI ↔ PostgreSQL؛ مالک محصول برای purpose/retention، توسعه‌دهنده برای مالکیت. |
| داخلی | source/config نسخه‌دار، review/approval/audit/head، actor/reason/correlation | CLI مورد اعتماد ↔ authority HTTPS ↔ DB role محدود؛ مسئول عملیات. بدون دسترسی مشتری. |
| راز | OTP/challenge، account token/cookie، proof، credential DB/authority/readiness، backup key | private environment/provider؛ مالک زیرساخت. هیچ secret واقعی در Git/URL/log نیست. |
| شواهد آزمون/عملیات | screenshot/trace، access log، export، backup، CI artifact | کانال‌های مستقل از API؛ مسئول امنیت/زیرساخت. مصنوعی بودن fixture و دسترسی/retention این کانال‌ها لازم است. |

browser/payload/storage غیرقابل اعتماد است. client واقعی می‌تواند Cookie/header دست‌ساز
بفرستد؛ HttpOnly جلوی خواندن JavaScript را می‌گیرد، اما authenticity مقدار ثابت را
ثابت نمی‌کند. UUID غیرقابل حدس، جای ownership یا proof معتبر را نمی‌گیرد.

| جریان | کنترل مشاهده‌شده در کد | مرز اثبات |
| --- | --- | --- |
| ورود مشتری → پروفایل | mock فقط local/test؛ token تصادفی digest‌شده با TTL/revoke؛ ensure_profile پیش از تحویل دسترسی؛ /me و phone سمت سرور | مالکیت واقعی تلفن، provider SMS و نشست durable/shared تولیدی پیاده/فعال‌شده ادعا نشده‌اند. |
| پرسشنامه ناشناس → پاسخ | canonical validation و انقضای ۳۰ دقیقه؛ PostgreSQL پاسخ‌ها، Redis فقط metadata با TTL | read/write فعلی sessionId را می‌پذیرند؛ proof/owner را کنترل نمی‌کنند (F01). |
| توصیه → تاریخچه حساب | scoring سرور از snapshot مصوب؛ owner CAS و unique session؛ transaction کامل run/item/reason، owner filter و hidden_at | cookie proof فعلی مقدار ثابت دارد؛ proof ساختگی برای session هنوز bindنشده پذیرفته شد (F01). حساب دیگر نمی‌تواند رکورد bindشده را با CAS تصاحب کند، اما این ضعف proof را رفع نمی‌کند. |
| عملیات داخلی → publication | grant تازه، HTTPS issuer/audience/expiry/MFA؛ DB role غیرمالک؛ materializer/head/audit اتمیک؛ source/config رسمی | authority/grant تولیدی provision نشده؛ DB owner/superuser خارج از حفاظت trigger است. |
| داده → log/artifact/backup | پیام خطای محدود، timing ثابت، redaction marker credential | redaction عمومی phone/answers/free text را پوشش نمی‌دهد؛ proxy/uvicorn/backup واقعی بررسی نشده‌اند. |

## مهاجمان و سناریوها

| ID | مهاجم/دارایی و مسیر | کنترل موجود و شکاف | اقدام/مالک و معیار اثبات |
| --- | --- | --- | --- |
| TM01 | ناشناس یا کاربر مخرب با sessionId افشاشده؛ خواندن/نوشتن ترجیحات، ساخت proof | validation/TTL هست؛ UUID و cookie ثابت کافی نیستند | F01؛ T02 توسعه‌دهنده backend: دو client، proof گمشده/ساختگی/دیگری/منقضی رد، بدون read/write/history؛ browser سازنده معتبر و Back/refresh حفظ. |
| TM02 | حساب A با شناسه history/profile حساب B | /me، actor سمت سرور، query owner، CAS و 404 تاریخچه | T02 regression امنیت موجود حفظ؛ source پاسخ هیچ داده B ندهد؛ hide/lookup حساب دیگر بدون تغییر DB. |
| TM03 | bot؛ OTP brute-force، ایجاد session/محاسبه زیاد، فهرست بزرگ | OTP پنج تلاش/۱۲۰ ثانیه، ظرفیت محدود؛ history limit حداکثر ۵۰ | T02 quota/body/timeout برای تمام ورودی‌های لازم؛ مشترک/چندworker و origin/proxy معتبر؛ 429/پایداری بدون افشای داده. |
| TM04 | شبکه/وب‌سایت ثالث؛ cookie theft/CSRF/cache اشتراکی | HttpOnly/SameSite=Lax local، bearer حافظه؛ HTTPS/CORS/CSRF کامل محیط هنوز اثبات نشده | T02 و T07/آنلاین T081؛ TLS، Secure، CSRF/origin، no-store موفق/خطا و cross-origin negative روی محیط مجاز؛ production mock ممنوع. |
| TM05 | XSS/محتوای خارجی/فایل avatar؛ سوءاستفاده از storage | avatar type/signature/100KB، متن شرایط امن و asset کنترل‌شده | T02 input/content/CSP و local cache F04؛ SVG/HTML خام اجرا نشود، URL/asset نامعتبر fallback امن. |
| TM06 | credential داخلی افشاشده یا اپراتور دسترسی‌گرفته | independent MFA/service identity، explicit permission، freshness، TLS/redirect rejection، role محدود | T02/T04 و عملیات: revocation، least privilege، عدم دسترسی customer tables؛ non-sensitive reason و منع secret در command/log. |
| TM07 | اپراتور/خطای انسانی؛ source/config/approve/rollback دستکاری | immutable linkage/approval، digest canonical، CAS، تراکنش audit/publication | آزمون PostgreSQL T03/T04 موجود؛ حفظ source رسمی/D-005؛ UPDATE خام یا bypass CLI ممنوع؛ scope config جدید task جدا. |
| TM08 | DB owner/dependency آلوده؛ حذف audit/سرقت DB | append-only trigger role محدود را کنترل می‌کند؛ owner می‌تواند DDL کند | T03 supply-chain/secret scan، T05 separation/network/backup؛ external tamper-proof ادعا نشود؛ کنترل حساب migration/owner و شواهد restore. |
| TM09 | خطای پاک‌سازی؛ نگهداری پاسخ خام پس از expiry | TTL فقط read را می‌بندد؛ FK history مانع delete session می‌شود | F02؛ T02 برنامه حذف پاسخ مستقل و linkage evidence، T05 scheduler/monitoring؛ real PostgreSQL expiry با history/unlinked، retry و rollback بدون حذف snapshot. |
| TM10 | log/trace/analytics/export/backup؛ افشای PII | redaction credential و timing محدود موجود؛ پوشش کامل نیست | F03/F07؛ T04 ساختار/allowlist و proxy log، T05 backup/restore retention؛ synthetic canary PII/secret در هیچ sink باقی نماند. |
| TM11 | کاربر دستگاه مشترک؛ خواندن cache پس از logout | accountProfile پاک می‌شود؛ personalInfo.* و savedLoans باقی می‌مانند | F04؛ مالک محصول purpose/storage تصمیم بگیرد؛ T02 اصلاح غیرنمایشی مصوب و آزمون login/logout/refresh بدون تغییر طراحی. |
| TM12 | حذف اشتباه/نگهداری بی‌انتها یا restore داده حذف‌شده | hide نگهداری را عوض نمی‌کند؛ profile/history/audit policy کامل نیست | F05/F07؛ مالک محصول + امنیت/عملیات: جدول تصمیم‌ها، erasure/recovery با lineage، عدم orphan یا پاک‌کردن audit لازم؛ T05 restore مجاز و پالایش‌شده. |

## یافته‌ها و blockerهای انتشار

ارزیابی شدت، triage مهندسی همین بازبینی است؛ CVSS رسمی یا exploit production نیست.
**F01/F02 تا رفع و اثبات، مانع انتشار داده کاربران/production هستند.**
هیچ یافته با سبزکردن CI یا پذیرش مبهم «بعداً» بسته نمی‌شود.

| ID / اولویت | شاهد و وضعیت | مالک اجرایی / شرط بسته‌شدن |
| --- | --- | --- |
| F01 / High، باز و بازتولیدشده | questionnaire.resume/write بدون proof؛ proof Cookie مقدار «1». دو client مستقل: read=200، write=200، recommendation بدون proof=403 ولی cookie ساخته‌شده=200 قبل از اولین owner bind. شناسه از fixture داده شد؛ enumeration، XSS یا exploit روی سرویس واقعی ادعا نمی‌شود. | backend / US-11.T02؛ capability تصادفی server-verified با TTL/ownership مناسب به تمام عملیات session و history وصل، طراحی migration/compatibility صریح و regression واقعی دوحساب/دوclient. UUID تنها و مقایسه constant رد. |
| F02 / High، باز؛ قرارداد و FK بازتولید | history_run.session FK بدون ON DELETE؛ delete_expired ابتدا answers سپس session را حذف می‌کند و transaction با history به FK خطا می‌خورد. SQLite با foreign_keys=ON شکست/rollback را نشان داد؛ PostgreSQL این سناریو اینجا اجرا نشد. هیچ scheduler production احراز نشد. | backend/عملیات / T02 سپس T05؛ پاسخ خام در TTL مصوب حذف شود، snapshot نگه‌داری مصوب داشته باشد؛ migration در صورت نیاز افزایشی/نرمال، بدون cascade حذف تاریخچه. real PostgreSQL، batch مخلوط، retry، restart و پاک‌سازی monitorشده. |
| F03 / Medium شکاف کنترل، باز؛ خطر بالا اگر PII به sink برسد | core.logging markerها phone/answers/income/name را redact نمی‌کنند؛ آزمایش helper: phone و answers باقی، token redact. timing موجود از label ثابت استفاده می‌کند؛ **نشت واقعی log production مشاهده نشده**. | backend/امنیت / US-11.T04؛ schema/allowlist log و تست sink واقعی، positional/free text/URL/error/authority، proxy مستقل. تا آن زمان واردکردن PII به log ممنوع. |
| F04 / Medium، رفتار storage تأیید | home personalInfo نام/phone/income/job و accountProfile را localStorage می‌کند؛ logout فقط accountProfile را حذف می‌کند. savedLoans سراسری browser است. token در module memory، نه localStorage. | محصول + backend / تصمیم privacy سپس T02؛ purpose/مدت/حذف/shared-device و سازگاری flow ثبت و آزموده شود؛ T01 cache را تغییر نمی‌دهد، redesign/refactor US-13 شروع نمی‌شود. |
| F05 / تصمیم محصول/حریم خصوصی، blocker تولیدی باز | profile/history/hidden history بدون TTL/erasure مصوب؛ audit append-only با حذف کاربر تعارض محتمل دارد. hide=204 حذف فیزیکی/erasure نیست. | مالک محصول/امنیت/عملیات پیش از release؛ تصمیم‌های P01–P06 سند retention و اجرای قابل‌اثبات در taskهای مربوط. |
| F06 / آمادگی تولیدی، blocker باز | mock مشتری مالکیت واقعی تلفن نیست؛ token/session/account quota فرایندمحلی و restart/multiworker مشترک نیست. authority داخلی تولیدی provision نشده و unavailable deny است. | مالک provider + backend/زیرساخت / T02 و gate استقرار؛ provider مستقل/نشست/revocation/quota و customer/operator جدایی با test واقعی، بدون فعال‌سازی mock production. |
| F07 / زیرساخت، blocker اثبات باز | TLS/شبکه DB/CORS/CSRF/headers، log proxy، encryption/backup/restore/retention و آنلاین دوسرویس هنوز محیط واقعی اثبات ندارند. | زیرساخت/امنیت / T02–T05، T081/T07/US-12؛ environment/version/owner و شواهد واقعی. صرف دامنه خریده‌شده یا CI جای این کنترل‌ها نیست. |

## شواهد و بازبینی بعدی

کدهای اصلی: [questionnaire routes](../../backend/app/api/v1/questionnaire.py)،
[recommendation binding](../../backend/app/api/v1/recommendations.py)،
[history repository](../../backend/app/recommendation/infrastructure/history.py)،
[models](../../backend/app/infrastructure/db/models.py)،
[cleanup](../../backend/app/questionnaire/infrastructure/sqlalchemy_sessions.py)،
[logging](../../backend/app/core/logging.py)،
[frontend cache](../../src/home%20page.jsx)،
[internal authority](../../backend/app/operations/infrastructure/introspection.py).

۳۱ آزمون existing profile/session/history/operations authorization در snapshot دارای
blobهای برابر main پاس شدند. بازتولیدها فقط روی TestClient و SQLite موقت، identities
مصنوعی و بدون سرویس خارجی/داده کاربر اجرا شدند. این آزمون‌ها امنیت سراسری یا صحت
PostgreSQL cleanup را ثابت نمی‌کنند. جزئیات fixture/command/result در checkpoint است.

برای هر اصلاح، ID یافته، owner، acceptance/test، SHA و نتیجه واقعی به‌روز شود؛
«باز»، «رفع‌شده در کد» و «تأییدشده روی محیط مستقر» جدا هستند. بازبینی مجدد با هر
تغییر auth/session/owner، retention/erasure/backup، provider/deploy، import/audit و
قرارداد داده لازم است. US-11.T01 با تحویل **review** پایان می‌یابد؛ داستان US-11،
رفع F01/F02، فعال‌سازی production یا US-13 با این PR Done نمی‌شوند.
