# بررسی حریم خصوصی و نگهداری داده — US-11.T01

نسخه ۱؛ ۲۰۲۶-۱۰-۱۲؛ مبنای کد `ae52f112dc16b9e07447a195725560f54263c981`.
این سند رفتار موجود، شکاف و تصمیم لازم را جدا می‌کند؛ سیاست تازه/مدت فرضی را
فعال نمی‌کند و مدعی انطباق قانونی یا رضایت اخذشده نیست.
[مدل تهدید و یافته‌های F01–F07](threat-model.md) مرجع triage است.

## موجودی داده و چرخه عمر فعلی

| داده/هدف | محل، گیرنده/دسترسی | expiry و حذف واقعی | شکاف/تصمیم |
| --- | --- | --- | --- |
| پاسخ canonical؛ ادامه پرسشنامه و توصیه | questionnaire_answers در PostgreSQL؛ service با sessionId؛ owner_phone پس از bind | read تا ۳۰ دقیقه؛ delete_expired درخواست حذف answers/session می‌کند؛ scheduler احراز نشده و history FK می‌تواند کل transaction را rollback کند | F01/F02؛ expiry دسترسی ≠ erasure فیزیکی. هدف حذف خام در ۳۰ دقیقه پابرجاست؛ برنامه مستقل حفظ history لازم. |
| session metadata؛ resume/cache | PostgreSQL UUID/version/created/expires/owner؛ Redis hash key با UUID/version/times | Redis ex برابر زمان باقی‌مانده؛ cache miss/failure به DB برمی‌گردد | Redis پاسخ خام ندارد؛ حذف Redis پاسخ DB را حذف نمی‌کند. linkage owner+history هم حساس است. |
| OTP challenge؛ ورود development | حافظه phone، attempts، expiry؛ quota از digest phone/client | challenge ۱۲۰ ثانیه/پنج تلاش، prune هنگام دسترسی؛ verify موفق مصرف؛ restart ازبین‌بردن حافظه | pruning on access به معنی job حذف دقیق در clock نیست. mock اثبات تلفن نیست. |
| account capability/cookie؛ دسترسی حساب | digest token+phone در حافظه؛ token در module memory و cookie HttpOnly/SameSite=Lax | TTL سرور ۱۸۰۰ ثانیه و revoke؛ cookie max_age، frontend restore؛ process restart | revocation/shared store و quota production لازم؛ هیچ token browser storage نیست. |
| پروفایل؛ اطلاعات شخصی و نمایش نام | user_profiles.phone/name/income/job/gender/avatar/update؛ actor-auth /me و write | TTL و endpoint erasure ندارد؛ logout رکورد DB را حذف نمی‌کند | purpose/حداقل فیلد/رضایت/مدت/حقوق دسترسی و حذف P01؛ phone identifier کم‌انتروپی است، hash ساده anonymization نیست. |
| تاریخچه نتیجه؛ سوابق برای همان حساب | history runs/items/reasons، owner FK، session FK و loan version؛ API owner/newest cursor | retry session unique، hide فقط hidden_at و خروج از لیست/detail؛ رکورد محفوظ | P02؛ روزهای retention برای visible/hidden مقرر نیستند. snapshot شامل پاسخ خام نیست، ولی score/فهرست/date/owner ترجیح را آشکار می‌کنند؛ داده عمومی محسوب نشود. |
| cache فرم/پروفایل؛ پیشنهاد قبلی UI | localStorage personalInfo.firstName/lastName/phone/income/job و accountProfile | expiry ندارد؛ logout فقط accountProfile را پاک می‌کند | P03/F04؛ origin scripts/دستگاه مشترک می‌خوانند؛ cache مجوز احراز هویت نیست. حذف/مدت تازه در T01 اعمال نمی‌شود. |
| bookmarks؛ ذخیره وام مرورگر | localStorage shahab.savedLoans و داده نمایش سروری | toggle/remove؛ بدون DB/account scoping/TTL | storage مشترک origin/browser؛ شخصی است، با history پایدار حساب متفاوت؛ سیاست P03. |
| operational source/version/audit | جداول عملیات، audit actor/reason/correlation، approval view؛ DB role internal | append-only، بدون purge خودکار؛ owner DDL مستقل | actor/reason می‌تواند identifying باشد؛ purpose/مدت/PII ممنوع و ارتباط حذف کاربر P04. داده پاسخ/phone مشتری نباید وارد reason شود. |
| application/access/authority log و trace | app logger محدود، timing label ثابت؛ proxy/provider/CI مستقل | retention/recipient واقعی محیط هنوز ثبت نشده | P05/F03؛ marker credential کامل PII نیست، free text/URL/stack/positional args کنترل مستقل می‌خواهند. |
| backup/export/test evidence | هنوز host/backup production مشخص/آزموده نشده | expiry/deletion/restore rehearsal احراز نشده | P06/F07؛ copy حذف‌شده نباید بی‌سیاست با restore دوباره سرو شود؛ key/access و deletion propagation نیازمند طرح‌اند. |

## purpose و کمینه‌سازی

- پاسخ پرسشنامه فقط برای توصیه و resume کوتاه‌مدت؛ raw answers به تاریخچه، log،
  analytics، export عمومی یا provider SMS/internal authority منتقل نشوند.
- phone برای account linkage و نام برای sidebar؛ income/job/gender/avatar از نظر
  ضرورت واقعی محصول بازبینی شوند. اختیاری‌بودن/فیلدهای مجاز از schema فعلی جدا از
  consent است؛ T01 فیلد/UX را تغییر نمی‌دهد.
- snapshot تاریخی را می‌توان بدون پاسخ خام خواند؛ پاک‌سازی raw باید مرجع وام و
  data/config version و مالکیت/قابلیت بازخوانی snapshot را خراب نکند. direct UPDATE/
  حذف cascade history برای حل F02 مجاز نیست؛ طراحی و migration در task مستقل.
- public loan catalogue با personalized score/history متفاوت است. shared cache،
  URL، access log و screenshot واقعی می‌توانند داده حساس را افشا کنند.
- هیچ reuse برای training، analytics، تبلیغات یا third party از توسعه فعلی نتیجه
  گرفته نمی‌شود. provider جدید پیش از فعال‌سازی باید fields/recipient/purpose/
  retention/access/region را ثبت کند؛ این سند انتقال واقعی داده را تأیید نمی‌کند.
- pseudonymized actor/hashed phone همچنان ممکن است قابل پیوند باشند؛ anonymization
  یا compliance صرفاً با hash/UUID/hidden_at ادعا نشود.

## تصمیم‌های باز؛ پیشنهاد ≠ سیاست فعال

هیچ مدت جدید دلخواهی برای profile/history/audit/backups در این review تصویب نمی‌شود.
مالک محصول تصمیم purpose/مدت/روش حذف را با مسئول امنیت و عملیات ثبت می‌کند؛ تا
پیش از این تصمیم‌ها و اجرا/اثبات مربوط، تولید با داده واقعی کاربران مجاز اعلام نشود.

| ID | تصمیم و مالک | خروجی لازم پیش از release |
| --- | --- | --- |
| P01 | محصول: هدف/ضرورت پروفایل و فیلدها، اطلاع‌رسانی/رضایت و دسترسی/اصلاح/حذف | policy version، field allowlist، گیرندگان، مدت با rationale، مسیر احراز هویت درخواست و اثر حذف FKها؛ حفظ طراحی مصوب تا change جدا. |
| P02 | محصول + backend: visible/hidden history و erasure | مدت محدود و مبدأ شمارش، تفاوت hide/حذف، ماهیت immutable evidence، روش حذف/ناشناس‌سازی مصوب بدون orphan و lookup حساب دیگر؛ user expectation صریح. |
| P03 | محصول + frontend/security: cache و bookmarks دستگاه مشترک | purpose/expiry/account scoping و logout cleanup مصوب، حفظ suggestion/back/refresh، آزمون xss/shared-device؛ حذف credential از cache پابرجاست. |
| P04 | عملیات/security: audit و retention/conflict | customer PII ممنوع، actor reference قابل‌کنترل، duration/access/approved erasure یا exception با rationale؛ هیچ weakening trigger برای پاک‌سازی عمومی. |
| P05 | security/infra: log/telemetry/CI artifact | allowlist و sink، retention/deletion، نقش مشاهده‌گر، redaction/canary و proxy/provider policy؛ تصویر/trace فقط fixture مصنوعی. |
| P06 | infra/محصول: backup/export/restore/deletion propagation | encryption/key/access، retention schedule، restore rehearsal جدا، حذف/استثنا و quarantine پس از restore با reconciliation پیش از سرو داده، owner و evidence. |

## طرح اصلاح و اثبات (در T01 اجرا/فعال نمی‌شود)

۱. T02 ابتدا F01 را با proof/capability معتبر و ownership تمام session عملیات اصلاح
کند؛ تست deny قبل از دسترسی DB، cross-client/account، refresh و expiry لازم است.
۲. برای F02 مسیر purge پاسخ خام از evidence پایدار جدا طراحی شود؛ به‌جای حدس یا
drop FK، 3NF و snapshot قرارداد حفظ شود. PostgreSQL واقعی با expired مرتبط/
غیرمرتبط، batch failure/retry و restart، حذف پاسخ و حفظ history را ثابت کند.
۳. policyهای مصوب P01–P04 در taskهای لازم به schema/use case/runbook تبدیل شوند؛
dry-run count/audit بدون payload شخصی، transaction/idempotency و نقش محدود الزامی.
۴. T04 log همه sinkها را با داده synthetic آزمون کند؛ helper عمومی با free text
و PII فیلدهایی که redact نشده‌اند تطبیق داده شود. T05 scheduler/monitor/backup/
restore را در محیط جدا اثبات کند؛ افشای log production ادعا نشود.
۵. درخواست erasure با هویت معتبر ثبت، scope/نسخه policy و شمارش فقط غیرشخصی audit،
cache/export/backup propagation و تأیید نتیجه داشته باشد. SLA جدید و استثنای قانونی
فقط با تصمیم معتبر ثبت شوند، نه حدس توسعه‌دهنده.
۶. purge واقعی/انتشار provider/production نه در این PR و نه صرف CI مجاز نیست.
گزارش Doneِ review از Doneِ اصلاح runtime و پذیرش production جداست.
