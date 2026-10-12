# بررسی حریم خصوصی و نگهداری داده — US-11.T01

نسخه ۱؛ ۲۰۲۶-۱۰-۱۲؛ مبنای کد `ae52f112dc16b9e07447a195725560f54263c981`.
این سند رفتار موجود، سیاست مصوب و اجرای آینده را جدا می‌کند. تصمیم‌های PD01–PD08
مالک در ادامه PR #107 تصویب شده‌اند؛ کد/مدت runtime هنوز تغییر نکرده است و
انطباق قانونی یا رضایت اخذشده ادعا نمی‌شود.
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

## تصمیم‌های مصوب و موارد باقی‌مانده

مرجع واحد: [PD01–PD08 و تسک‌های T02A–H در سند جامع](../SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md).
دستور مالک در ۲۰۲۶-۱۰-۱۲ جای پیشنهاد نگهداری محدود profile/history یا erasure
فیزیکی آن‌ها را گرفته است: داده durable همیشگی نگه‌داری، hide/archive با status،
بازگشت همان status در backup؛ **raw پاسخ پس از ۳۰ دقیقه حذف**. این‌ها policy approved
هستند و هنوز implementation-approved/completed یا فعلیت TTL یک‌ساعته نیستند.

| تصمیم بازبینی قبلی | وضعیت پس از تصمیم مالک | اجرا/باقی‌مانده |
| --- | --- | --- |
| P01 پروفایل | PD05 مصوب: initial فقط phone، form آخرین ورودی profile، gender اختیاری؛ snapshot قبلی مستقل | T02A/D؛ اطلاع‌رسانی و دسترسی/حداقل‌سازی، بدون ادعای consent اخذشده. |
| P02 تاریخچه/حساب | PD02–PD04 مصوب: visible forever، hide retained forever؛ account archive نه erasure، phone مجدد حساب نسل تازه | T02A/B/E/G؛ archive access همه tokenها را ببندد، snapshot/lineage immutable؛ UI حذف حساب فعلاً اضافه نشود. |
| P03 browser/bookmarks | PD06 مصوب: همه bookmarks/سوابق account DB، logout پاک‌سازی اطلاعات browser شهاب | T02F؛ migration bookmarks محلی قدیمی تنها با منشأ معتبر/تصمیم انتقال، هیچ attach خودکار به login بعدی. |
| P04 audit داخلی | retention forever مصوب برای profile/history/archive؛ audit عملیات و log با آن یکی نیستند | مدت دقیق/access داخلی audit هنوز نیاز به تصمیم مستقل دارد؛ PII مشتری وارد reason نشود، حفاظت append-only حفظ. |
| P05 log/telemetry/artifact | حذف اطلاعات شخصی مرورگر مصوب است، ولی مدت log/CI artifact و دسترسی مشاهده‌گر تعیین نشده | T04 schema/allowlist/redaction/alerts و تصمیم جدا؛ production leakage ادعا نشده. |
| P06 backup/restore | PD07 مصوب: retained data با archived/hidden/account_id برگردند؛ raw expired قبل از سرو purge | T05 retention عملی backup/key/access/rehearsal؛ بازیابی archived به active یا account قدیم به جدید ممنوع. |
| ورود مجدد/TTL | PD08 مصوب: یک ساعت absolute؛ valid session بدون OTP، refresh بدون تمدید | T02C/D؛ عمر فعلی ۱۸۰۰ ثانیه تا پیاده‌سازی تغییر نکرده؛ نیاز به server expires_at واقعی و revoke. |

مدت جدید برای log/audit/backup rotation، گیرندگان تحلیل رفتاری و اطلاع‌رسانی محصول
حدس زده نمی‌شود. تصمیم مصوب forever مجوز دسترسی نامحدود/آموزش مدل/اشتراک ثالث
نیست؛ هدف behavioral analysis و حدودش در privacy contract مشخص شود.

## طرح اصلاح و اثبات (در T01 اجرا/فعال نمی‌شود)

۱. T02 ابتدا F01 را با proof/capability معتبر و ownership تمام session عملیات اصلاح
کند؛ تست deny قبل از دسترسی DB، cross-client/account، refresh و expiry لازم است.
۲. برای F02 مسیر purge پاسخ خام از evidence پایدار جدا طراحی شود؛ به‌جای حدس یا
drop FK، 3NF و snapshot قرارداد حفظ شود. PostgreSQL واقعی با expired مرتبط/
غیرمرتبط، batch failure/retry و restart، حذف پاسخ و حفظ history را ثابت کند.
۳. policyهای مصوب PD01–PD08 طبق T02A–H به schema/use case/runbook تبدیل شوند؛
dry-run count/audit بدون payload شخصی، transaction/idempotency و نقش محدود الزامی.
۴. T04 log همه sinkها را با داده synthetic آزمون کند؛ helper عمومی با free text
و PII فیلدهایی که redact نشده‌اند تطبیق داده شود. T05 scheduler/monitor/backup/
restore را در محیط جدا اثبات کند؛ افشای log production ادعا نشود.
۵. درخواست erasure با هویت معتبر ثبت، scope/نسخه policy و شمارش فقط غیرشخصی audit،
cache/export/backup propagation و تأیید نتیجه داشته باشد. SLA جدید و استثنای قانونی
فقط با تصمیم معتبر ثبت شوند، نه حدس توسعه‌دهنده.
۶. purge واقعی/انتشار provider/production نه در این PR و نه صرف CI مجاز نیست.
گزارش Doneِ review از Doneِ اصلاح runtime و پذیرش production جداست.

## US-11.T02A.2 — انتقال اجرایی هویت

profile/session/history به account UUID مستقل متصل شدند؛ phone کپی در profile/history حذف، snapshot unchanged، archive generations schema-ready. هیچ purge، retention، analytics access یا account deletion UI اجرا نشد؛ PD01–PD08 مصوب پابرجا و اجرای B–H/T04/T05 باقی است.

## US-11.T02B — proof معتبر پرسشنامه

secret فقط cookie HttpOnly و digest فقط DB؛ Redis/JSON/URL/log هیچ proof ندارند. TTL پاسخ ۳۰ دقیقه بدون تمدید؛ purge F02 در E است و expiry اثبات حذف نیست. legacy NULL fail-closed، snapshot/account data retained؛ هیچ حذف/بایگانی UI ساخته نشده.

## US-11.T02C — نشست مشترک یک‌ساعته

credential/OTP/quota موقت مطابق عمر مصوب۱h/۱۲۰s و bounded cleanup؛ token/code خام در DB/log نیست. profile/history/hidden/archive retained و purge خام E ثابت. restore backup باید credential/OTP را در T05 invalidate کند؛ این PR restore عملیاتی را ادعا نمی‌کند.

## US-11.T02E — پاسخ خام مستقل از snapshot

`questionnaire/infrastructure/retention.py` هر بار حداکثر۱۰۰ (حد سخت۱۰۰۰) نشست
expired را با ترتیب expiry/UUID و `FOR UPDATE SKIP LOCKED` انتخاب می‌کند. حذف
answers، EXPIRED کردن metadata مرتبط و حذف metadata غیرمرتبط در یک transaction
commit یا rollback می‌شوند. لینک history با هیچ فیلتر hidden/status کنار گذاشته
نمی‌شود: profile/account/run/item/reason/owner و data/config/loan/questionnaire
version حفظ می‌شوند؛ هیچ cascade، انتقال خام به archive/JSON یا تغییر scoring وجود ندارد.
metadata مرتبط شامل UUID، version FK، owner UUID، created/expires، state و digest
immutable (یا NULL legacy) برای FK/idempotency/evidence همراه history همیشگی
باقی می‌ماند؛ digest secret قابل بازیابی/پاسخ خام نیست و expiry/state هرگز اجازه
استفاده دوباره نمی‌دهند. metadata غیرمرتبط پس از expiry نیاز durable ندارد و حذف
می‌شود. قرارداد proof/owner و TTL۱۸۰۰ تمدید/تضعیف نمی‌شوند.

این موتور و CLI به‌تنهایی scheduler نیستند. F02 مسیر FK/runtime در E اصلاح می‌شود؛
بستن کامل operational retention همچنان نیازمند scheduler/monitor/restore-before-reopen
در T05 است. expiry denial یا batch خالی معادل حذف اثبات‌شده نیست.
[فرمان و حدود عملیاتی](../operations/raw-answer-retention.md) و
[شواهد E](../progress/us-11-t02e.md).

## US-11.T02F — نشان‌شده‌های حساب و پاک‌سازی خروج

PD06 اجرا: association owner UUID/loan version و optional same-owner historical
reference، نه client recommendation JSON/phone/score copy. source snapshot immutable؛
removed_at فقط نمایش را می‌بندد، retained همراه account/archive؛ no automatic legacy
upload. browser profile/form/bookmarks/result فقط memory، خروج کلیدهای shahab.* از
local/session storage و current history reference/React state پاک و credential فعلی
سرور revoke؛ proof cookieهای شهاب حذف. پاسخ دیررس/نسل هم‌شماره cache را احیا نمی‌کند.
خروج شبکه‌ناموفق، خطا و pending control flag غیرشخصی با retry-before-restore دارد؛
revoke offline ناممکن را موفق گزارش نمی‌کند. اطلاعات سایر appها پاک نمی‌شود.
سیاست legacy، محدودیت history قدیمی مرورگر، FK/rollback و شواهد در
[قرارداد F](account-bookmarks.md). PG/real browser و مستقل baseline visual لازم؛
F02 عملیاتی/T03–T05/H/production هنوز gateهای جدا هستند و UI حذف حساب ساخته نشد.
