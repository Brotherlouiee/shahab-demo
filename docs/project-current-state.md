# Project current state

## US-13.T03.01 — تصمیم no-move برای CSS مشترک درباره ما (۲۰۲۶-۱۰-۱۳)

- `activeTaskId: US-13.T03.01`؛ base `main=b8487f25f9aa8bb3b00145b36ed21b8f8f45f8dd` (مرج PR #128). `AboutPage` قبلاً در T02.01 استخراج شده؛ **در این تسک هیچ CSS/React/asset/entry/API/data تغییر نمی‌کند**.
- `src/App.css:6111` از rule مشترک `.hp-account-page,.hp-about-page,.hp-saved-loans-page` و قواعد خاص About در همان خط تشکیل شده و `:6115` هدر مشترک چندین صفحه را استایل می‌کند؛ جابه‌جایی بی‌مدرک CSS می‌تواند cascade/profiles/history را تغییر دهد. طبق سند جامع و [checkpoint T03.01](progress/us-13-t03-01.md) این segmentها آگاهانه در `App.css` می‌مانند؛ **هیچ CSS module مستقل ساخته‌شده ادعا نمی‌شود**.
- test-only gate در frozen US13: برابری computed styles، bounding rect، متن و شمار عناصر About/shared header در 390/430/1440 با baseline اصلی؛ به‌علاوه آزمون hard zero-pixel و ناوبری و همهٔ CI. **نتیجهٔ نهایی فقط از CI SHA نهایی قابل پذیرش است**. سند تداوم تا پایان User Story تغییر نمی‌کند.
- پس از PR موفق و مرج مالک، `T02.02` طبق registry؛ اگر تفکیک واقعی CSS بعدها ایمن شد، task/PR مستقل و consumer graph لازم دارد.


## US-13.T02.01 — استخراج محدود صفحه درباره ما (۲۰۲۶-۱۰-۱۳)

- `activeTaskId: US-13.T02.01`؛ مبنا `main=3d3eac0813808abb50f83eb017d0282e215ef52c`؛ فایل ثابت refactor `f5e50da0ea29b7d933a813736a2616169ee9b8f3`.
- فقط تابع AboutPage به `src/features/about/AboutPage.jsx` منتقل شده و با prop `AccountHeader` به هدر موجود متصل است؛ **۱۱۳۸ کاراکتر بدنهٔ تابع پس از نرمال‌سازی export/signature عیناً برابر نسخهٔ قبل است**. `src/App.css` SHA ثابت `f0fe7d22bb5d1dc147f04ee5f6c769166ddaef41`؛ هیچ CSS/متن/آیکن/asset/فرم/API تغییر نکرده است.
- baseline مستقل `US-13` برای خانه، ورود و درباره‌ما در سه viewport + characterization کلیک بازگشت و برند در دو viewport؛ روی SHA نهایی CI باید تأیید شود. [checkpoint](progress/us-13-t02-01.md).
- **ادامه:** پس از سبزشدن CI و مرج صریح مالک، T03.01 فقط با نقشهٔ selector/cascade و بدون تغییر واقعی ظاهر انجام شود؛ نه T02 کامل/نه پایان User Story. سند تداوم تا پایان US-13 تغییر نمی‌کند.


## US-13.T01 — inventory و خط مبنای محافظت فرانت (۲۰۲۶-۱۰-۱۳)

**تطابق مستقلِ جدید:** از artifact CI نسخهٔ پایه، ۹ تصویر اصلی/کاندید صفحهٔ home/about/login در ۳۹۰/۴۳۰/۱۴۴۰ **صفر تفاوت پیکسلی** داشتند؛ آزمون صریح صفر tolerance به collector افزوده شد. هنوز حالت‌های login OTP، فرم/پرسشنامه، result/compare/profile/history و تعامل منو خارج از این ۹ نمونه‌اند و باید پیش از extraction هر بخش گیت اختصاصی داشته باشند.


**شاهد اجرایی افزوده‌شده:** یک workflow جداگانه فقط برای capture تصاویر مستقل home/about/login در ۳ viewport ایجاد شد. همراه snapshot، geometry assert می‌شود؛ برابری پیکسلی جامع هنوز بدون بررسی شواهد اعلام نمی‌شود. `playwright.config.mjs` فقط در حضور متغیر محیطی اختصاصی، سرور baseline جداگانه را اضافه می‌کند؛ اجرای عادی بدون آن unchanged است. هیچ JSX/CSS/asset/runtime/API تغییر نمی‌کند.


- `activeTaskId: US-13.T01`؛ پایهٔ ثابتِ پیش از ریفکتور `main=f5e50da0ea29b7d933a813736a2616169ee9b8f3` پس از مرج PR #125. **هیچ ریفکتور React/CSS آغاز نشده است.**
- [مستند موجودی، ماتریس و رجیستری](ui/us-13-t01-frontend-baseline.md) و [checkpoint](progress/us-13-t01.md): نقشهٔ ۳۱۷۲ خط JSX و ۶۱۴۹ خط CSS، state/route و مالکیت/مصرف‌کننده‌های مشترک، پیشنهاد زوج‌های بسیار کوچک و تست لازم.
- **صادقانه باز:** تصویر مستقل برای همهٔ مسیرها، حالت‌ها و viewportها و characterization network هنوز تمام نشده است. existing visual card CI فقط subset را اثبات می‌کند. هیچ T02/T03 بدون baseline معتبر همان قسمت و آزمون خطایابی قابل انجام نیست؛ T01 تا تحقق معیار baseline جامع نمی‌تواند Done کامل تلقی شود.
- طبق استثنای صریح مالک این task فقط مستندات و ابزار اختصاصی browser-baseline/CI را تغییر می‌دهد؛ سند تداوم v15 چون US-13 پایان نیافته، تغییر نمی‌کند. merge/deploy/main write/DB reset ممنوع و انجام نشده است.


## تصمیم اجرایی جاری — US-13 پیش از US-12 (۲۰۲۶-۱۰-۱۳)

**اعتبارسنجی پس از اصلاح تصویری:** PR #124 به `main` با SHA `f1a738767c1479433515565f9ea55e02df3a697f` مرج شده است. آزمون کارت نشان‌شده با رندر ایزوله و شرط برابری کامل پیکسل‌ها در آن PR سبز شد. PR برنامهٔ #123 همچنان مستندسازی است؛ پذیرش آن فقط بر اساس CI تازهٔ همین PR با مبنای اصلاح‌شده سنجیده می‌شود، نه failure تاریخی پیش از مرج #124. هیچ baseline/CSS/UI برای این تغییر برنامه‌ریزی دست‌کاری نشده است.



- **activeTaskId: US-13.PLAN-ORDER-20261013**؛ تصمیم صریح مالک: پس از مرج این PR، `US-13.T01→T04` با baseline مستقل و حفظ کامل UI/behavior/CSS/state/network و چهار CI، **پیش از** `US-12.T01` انجام شود.
- پس از ریفکتور، `US-12.T01/T02` و قسمت مستقل از سرور `T03/T04/T04A` روی SHA **پس از refactor** آماده/تست شوند؛ هیچ نشر Docker Hub بدون حساب/Secrets و مجوز، هیچ preview/post-deploy بدون سرور به‌صورت Done ثبت نشود.
- سپس دفتر معوقات آنلاین و registry موجود با شواهد/مسئول/ترتیب/وضعیت تازه اصلاح شود؛ با فراهم‌شدن سرور، `US-09.T081 → T07`، سایر gateهای باز US-10/US-11/US-12 و در انتها `US-12.T05` انتشار/آزمون آنلاین تکمیل شوند.
- مرجع: [ADR-0009](adr/0009-offline-refactor-before-release.md) و تصمیم الزام‌آور در [سند جامع](SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md). **PR این تصمیم فقط docs است**؛ هنوز T01 اجرا نشده؛ ادعای Done برای معوقات یا تغییر دیتابیس/ظاهر وجود ندارد. `main` تأییدشدهٔ پیش از branch: `a05747e43cefe78a266673d1c8f6840d78f200ce`. سند تداوم طبق قاعدهٔ پایان داستان untouched.


## US-11.T05 — نگهداری عملیاتی و ارزیابی بازیابی (۲۰۲۶-۱۰-۱۳)

- activeTaskId: US-11.T05؛ مرج PR #120 و main `7be7283d` تأیید شد؛ شاخه `feat/us-11-t05-retention-operations`.
- ابزار تک‌نوبتی scheduler-ready با dry-run پیش‌فرض و کد 2 برای backlog؛ آزمون‌های موجود PostgreSQL درباره expiry، history، hidden/archived و rollback حفظ شده‌اند. [checkpoint](progress/us-11-t05.md).
- **باز:** scheduler و هشدار آنلاین، load/performance smoke روی staging، backup encryption و restore rehearsal روی DB ایزوله، تصمیم retention/ACL. کد و CI جایگزین شواهد این‌ها نیستند؛ هیچ DB owner تغییر نکرده. سند تداوم در پایان User Story بر اساس وضعیت صادقانه به‌روزرسانی می‌شود.


## US-11.T04 — ثبت رخداد امن و پایش عملیاتی (۲۰۲۶-۱۰-۱۳)

- activeTaskId: US-11.T04؛ پس از merge PR #119، main `d646a363`؛ شاخه `feat/us-11-t04-observability-incident`.
- scope: redaction/allowlist لاگ، metrics تجمعی و alert داخلی بدون PII، incident response؛ هیچ endpoint مدیریتی/عمومی جدیدی ندارد.
- [checkpoint](progress/us-11-t04.md) و [راهنمای رخداد](security/incident-response.md). شواهد CI روی SHA آخر در PR ثبت می‌شود؛ sink آنلاین/alert receiver، policy retention/ACL و reverse proxy canary طبق دفتر معوقات سرور **باز** هستند. سند تداوم طبق قاعدهٔ پایان داستان ثابت است.


## US-11.T03 — ممیزی امنیت کد و وابستگی (۲۰۲۶-۱۰-۱۳)

- activeTaskId: US-11.T03؛ main پس از مرج PR #117، SHA `5a25d1e6`؛ شاخه `feat/us-11-t03-security-scanning`.
- SAST و SCA مستقل روی Python/Node و secret scan در CI؛ smoke خواندنی DAST تنها روی HTTPS مجاز، بدون اجرای مخفیانه روی میزبان ناشناس؛ [checkpoint](progress/us-11-t03.md).
- چهار CI مصوب دست‌نخورده؛ اجرای آخر و یافته‌ها در PR بررسی می‌شوند. DAST آنلاین بدون host مجاز **اجرا نشده** و مانع release است؛ T04/T05 مستقل، تداوم در پایان user story.


## US-11.T02H — سخت‌سازی امنیت انتقال (۲۰۲۶-۱۰-۱۳)

- activeTaskId: US-11.T02H؛ مبنا main `755ffdc4` بعد از مرج G در PR #116؛ branch `feat/us-11-t02h-transport-hardening`.
- محدوده: API middleware security headers/no-store/Origin CSRF/body limit؛ CORS allowlist و negative tests؛ schema/score/data/UI unchanged.
- پذیرش: چهار job CI روی head، آزمون منفی/مالکیت و محدودیت‌های host/proxy/provider ثبت شود؛ deployment آنلاین مستقل است.
- [checkpoint](progress/us-11-t02h.md). سند تداوم تا پایان User Story ثابت؛ T03/T04/T05 مستقل و نیازمند gate هستند.


## US-11.T02G — بایگانی نسل حساب (۲۰۲۶-۱۰-۱۳)

- activeTaskId: US-11.T02G؛ مبنا `f4a617c8` بعد از مرج PR #114؛ branch مستقل `feat/us-11-t02g-account-archive`.
- محدوده: use case داخلی بایگانی account_id با status/archived_at و revoke تمام credentialهای همان نسل در transaction واحد؛ هماهنگی قفل حساب و partial-unique active phone؛ حفظ profile/history/hidden/bookmarks.
- مصرف عمومی: هیچ API/دکمه/صفحه حذف حساب اضافه نشد؛ caller/operator authorization برای فعال‌سازی آینده جدا لازم است، این تابع به request عمومی وصل نیست.
- تست: قرارداد SQLite و دو آزمون PostgreSQL واقعیِ multi-device/re-login و race روی CI؛ نتیجه نهایی باید از SHA همان PR خوانده شود و قبل از آن «موفق» گزارش نشود. PostgreSQL موجود کاربر reset/migrate نشده.
- سند تداوم طبق قاعده پایان US-11 بدون تغییر؛ PR #115 تداوم v14 هنوز باز و دارای failure تصویری سابق است. گام بعدی فقط پس از gate معتبر G، `US-11.T02H`.
- [checkpoint](progress/us-11-t02g.md). US-13 همچنان مرحله آخر پس از US-12 است.


## US-11.T02A.1 — طراحی account identity/lifecycle (۲۰۲۶-۱۰-۱۲)

- activeTaskId: US-11.T02A.1؛ base 2e63479ae5e1034a50e9386cc42e2c3846ed8c27 بعد از PR #107 مرج‌شده، branch مستقل docs/us-11-t02a1-account-contract.
- actualScope: ADR 0008، قرارداد/ERD هدف account UUID/status و profile 1:1، owner/composite FK و lifetime/race/backfill/rollback؛ ERD/dictionary/3NF reference و ردیف‌های مستقل A.1/A.2 در guide، CHANGELOG/checkpoint.
- schema واقعی هنوز user_profiles.phone-PK است؛ source ORM/DDL/runtime/UI/API/data/scoring تغییر نکرده. diagram هدف اجرایی یا آزمایش persistence نیست؛ account_sessions/bookmarks آینده C/F جدا.
- A.1 acceptance: design consistency و AC01–AC16 آزمون آینده، preserve policy/Golden Rules/US-13 و چهار CI؛ نتایج نهایی در PR.
- nextTaskId: US-11.T02A.2 پس از مرج/gate، migration/backfill/adapters با PostgreSQL واقعی؛ F01/F02 هنوز باز و B/E رفعشان می‌کنند. legacy token owner نباید با phone به نسل تازه map شود.
- [قرارداد](database/account-identity-lifecycle.md)، [checkpoint](progress/us-11-t02a1.md). سند تداوم ثابت و US-13 آخرین کار؛ merge/deploy این تسک انجام نمی‌شود.


## تصمیم‌های جاری حساب و ترتیب T02 — ۲۰۲۶-۱۰-۱۲

- activeTaskId: تکمیل policy/task plan در PR #107، نه اجرای T02.
- مرجع PD01–PD08 در guide: raw کامل/نیمه‌کاره ۳۰ دقیقه حذف؛ نتیجه snapshot، history/hide/account archive همیشگی، نسل تازه account با phone قبلی؛ آخرین form/profile جدا از history؛ account bookmarks همه deviceها؛ browser PII پس از خروج پاک؛ restore status و purge expired؛ یک ساعت absolute و بدون OTP تکراری برای نشست معتبر.
- ترتیب اجرای مستقل T02A هویت/ERD سپس migration → B proof/ownership → C session → D اصلاح جریان ورود → E purge → F bookmarks/logout → G archive lifecycle بدون UI جدید → H transport/full hardening. T04 log و T05 scheduler/backup/restore باقی می‌مانند.
- nextTaskId: US-11.T02A.1 پس از مرج و دستور مربوط؛ F01/F02 باز تا اصلاح/تست. تصویب سیاست، رفع خطر یا فعال‌سازی یک ساعت نیست.
- تصمیم‌های محصولی قبلی در موضوع متناظر پاسخ گرفته‌اند؛ log/audit/backup rotation/access و legacy browser bookmark migration جدا ثبت شوند، بدون مدت/consent حدسی.
- این بخش بر صف/سیاست‌های قبلی زیر مقدم است. runtime/schema/UI/scoring/retention تغییر نکرده و US-13 بعد از US-12 پابرجاست.


## US-11.T01 — بازبینی تهدید و حریم خصوصی (۲۰۲۶-۱۰-۱۲)

- activeTaskId: US-11.T01؛ درخواست مستقیم مالک پس از مرج PR #106، base ae52f112dc16b9e07447a195725560f54263c981. branch مستقل docs/us-11-t01-threat-privacy.
- Scope: review مستند سراسری تهدید/چرخه داده، تطبیق کد و fixture هدفمند؛ بدون runtime/API/schema/retention/UI/scoring/deploy.
- Review findings: F01 read/write با sessionId و proof ثابت قابل ساخت، F02 تعارض FK history با purge، F03 پوشش ناکامل PII logger، F04 cache شخصی پس از logout، F05 policy erasure، F06 provider/session تولیدی، F07 زیرساخت/backup هنوز اثبات‌نشده.
- Evidence: ۳۱ تست موجود موفق و بازتولید مصنوعی دو client و SQLite FK روشن؛ PostgreSQL این purge و امنیت محیط واقعی اینجا اثبات نشده‌اند. یافته‌های F01/F02 باز و blocker release هستند؛ CI آن‌ها را رفع نمی‌کند.
- Output: [مدل تهدید](security/threat-model.md)، [privacy/retention](security/privacy-retention-review.md)، [checkpoint](progress/us-11-t01.md).
- nextTaskId: candidate US-11.T02 برای hardening با subtasks/acceptance یافته‌ها؛ logging T04 و restore T05 باقی‌اند. آنلاین T081/T07 و تولیدی باز تا شواهد واقعی؛ US-13 همچنان آخرین کار پس از US-12 است و شروع نشده.
- Review Done تنها پس از PR/gateهای لازم؛ policy جدید فعال نشده و تصمیم P01–P06 مالک باز است. سند تداوم تا پایان داستان تغییر نمی‌کند. وضعیت‌های قبلی زیر تاریخی‌اند.


## تصمیم جاری مالک — US-13 آخرین کار پروژه (۲۰۲۶-۱۰-۱۲)

- activeTaskId: US-13.PLAN-ORDER؛ فقط اصلاح برنامه پس از مرج PR #105.
- دستور جدید بر تمام صف‌های قدیمی زیر و candidate ریفکتور پیش از US-11 مقدم است: نام US-10R به US-13 تغییر کرد؛ همان چهار تسک و احتیاط‌ها، بعد از تکمیل بک‌اند و تمام gateهای US-01 تا US-12 اجرا می‌شوند.
- ترتیب بعد از US-10: US-11 → US-12 → US-13. US-11/US-12 به refactor وابسته نیستند. US-12 انتشار خودش را تکمیل می‌کند؛ پایان کل توسعه به gate معتبر US-13.T04 منتقل شد. هیچ gate امنیت/استقرار حذف نشده است.
- nextTaskId: candidate US-11.T01 پس از دستور/بررسی dependency؛ T081 آنلاین/T07 و blockerهای لازم ابتدا واقعاً تکمیل شوند. نه US-13.T01 و نه استخراج صفحه/CSS اکنون شروع نمی‌شود.
- نام قدیمی US-10R alias تاریخی همین داستان است؛ داستان دوم/کار تکراری نیست. شواهد و برنامه قدیم حفظ و تاریخی علامت‌گذاری شدند.
- محدوده فقط docs/CHANGELOG؛ appearance/behavior/runtime/API/DB/scoring/asset bytes ثابت. سند تداوم v13 دست‌نخورده است؛ صف جاری این بخش و guide مرجع‌اند.
- مبنا 9d065cf596d92f8969256d0080dc0b6725585ed3؛ branch مستقل docs/us13-refactor-last؛ [checkpoint جاری](progress/us-13-plan.md). گزارش تست هدفمند، زمان و چهار CI commit نهایی در PR ثبت می‌شود.


## US-10R — برنامه‌ریزی ریفکتور محافظه‌کارانه فرانت (۲۰۲۶-۱۰-۱۱)

- activeTaskId: US-10R.PLAN؛ یوزر استوری مستقل به درخواست مالک بین US-10 و US-11 تعریف شد. این برنامه بر candidate قبلی US-11.T01 در صف فعلی مقدم است؛ شماره‌های موجود ثابت‌اند.
- Base main: 0a518bf6261f26a754fdfff6e290f5be763c0f54 پس از مرج PR #104؛ branch مستقل docs/us-10r-frontend-refactor-plan. فقط guide، CHANGELOG، این وضعیت و checkpoint برنامه تغییر می‌کنند.
- T01: inventory و baseline قبل از تغییر؛ T02/T03: انتقال هر بخش و CSS آن در PRهای کوچک متوالی با حفظ cascade/state؛ T04: cleanup اثبات‌شده و gate کامل. runtime و ظاهر/رفتار در این PR تغییر نکرده‌اند؛ baseline تصویری هنوز تولید نشده است.
- شرط قطعی: ظاهر/رفتار دقیقاً حفظ شود؛ API/DB/data/scoring/asset bytes بدون تغییر. componentهای نتیجه/جزئیات موجود دوباره ساخته نشوند. screenshot همراه characterization تعامل/شبکه لازم است.
- nextTaskId: US-10R.T01 پس از مرج PR برنامه و بررسی مبنا؛ US-11 پس از gate US-10R. بخش آنلاین US-09.T081 و T07 همچنان باز/معوق‌اند؛ هیچ deploy/production claim.
- بررسی هدفمند/زمان و محدوده: [checkpoint](progress/us-10r-plan.md). چهار gate CI روی SHA نهایی در PR ثبت می‌شود. سند تداوم v13 در این PR تغییر نکرده است؛ وضعیت‌های قبلی زیر تاریخی‌اند.

## Owner-directed continuity v13 checkpoint (2026-10-11)

- activeTaskId: owner-requested continuity-v13; documentation only, explicitly authorized after US-10.T05 merged. This request overrides the deferred continuity-update rule for this refresh only.
- estimatedWorkScope/completionBudget: one bounded docs PR; reconcile handoff/current-state/CHANGELOG, verify links/status/history/diff and mandatory CI. No runtime, UI, API, data, schema, authority provisioning or deployment.
- Safe Git: independent Codex-owned docs/continuity-v13-us10 branch from main 9bf688a8d2da9921a045889985ebef5cf19eae86; other local checkouts and user edits/evidence untouched. Remote commit preserves the full main tree.
- Dependency/acceptance: PR #103 merged; feature CI 38145252408 and merge CI 38145538923 all four jobs successful. v13 must reflect merged T01–T05, preserve profile/history/D-005, distinguish CLI limits from production activation and keep T081 online/T07 open.
- Review: AGENTS, full canonical guide and TASK_EXECUTION_PROTOCOL reread; authoritative doc, recent merged PRs and exact-main docs checked. Required raw-source reread is not triggered by this documentation-only change; no source bytes change.
- Test plan: document version/precedence and current task queue, all new relative links against main tree, historical-section preservation, allowlist, whitespace and secret scan. No runtime suite is necessary locally; four existing CI gates remain required on the final remote commit.
- actualScope: continuity v13 authoritative section 0C and current sections 17–19/22; this checkpoint and CHANGELOG only. No product behavior changes. Historical checkpoints remain as dated evidence.
- nextTaskId: candidate US-11.T01 only after explicit owner instruction and dependency/gate review; when infrastructure is ready, complete online US-09.T081 then US-09.T07. No automatic advance or production-readiness claim.
- Phase timer started at task entry in UTC; actual review/edit/verification/Git/CI durations and final SHA are recorded in the PR after CI, rather than inferred from commit times or forcing another documentation-only CI cycle.
- End gate: targeted checks before first push; final four-job CI evidence in PR. No merge/deploy authorized or performed by this refresh.


## US-09.T081 — implementation checkpoint (2026-10-11)

- activeTaskId/nextTaskId: US-09.T081; contract/tooling patch prepared, online hosting/access gate blocked. T07 has not begun.
- Base main: 1e719ce85bfda05e8e3ce956e658ab1681b2bdcc; Codex-owned branch feat/us-09-t081-api-testing.
- Complete operation inventory, OpenAPI/Postman export, pinned cookie-preserving Swagger, opt-in health schemas and CI drift/browser checks are implemented; docs/auth production policy unchanged.
- 41 focused tests, format/lint/Mypy, boundary/secret scan, OpenAPI validation and real local Newman health requests passed. Final SHA/CI evidence belongs in the PR, not inferred here.
- All online operation results remain unverified: approved HTTPS API/PostgreSQL host, tester network/access and costs are not supplied. No deployment or production/SMS claim.
- Scope, review, source identities, execution time and next-step blocker: [US-09.T081 checkpoint](progress/us-09-t081.md), [manual guide](api/manual-testing.md), [coverage](api/coverage.md), [hosting runbook](runbook/api-testing.md).
- Story continuity stays unchanged; historical next-task statements below are superseded.


## US-09.T081 — Interactive online API testing / corrected planning checkpoint (2026-10-10)

- Scope: inspect FastAPI docs/config/routes and official Swagger/Postman documentation; define the new task before T07. Documentation only; implementation/publishing not started.
- Base main: d100325c3c6fa626e08b5a4bcfe5d41e72e9e128.
- Feasibility: existing non-production /docs, /redoc and /api/v1/openapi.json support a single OpenAPI source. Static Swagger can be hosted before live API deployment; Postman can import/share a collection derived from the same schema.
- Corrected owner requirement: one shareable online Swagger or Postman surface must list all implemented API operations and support real manual requests. Read-only documentation/artifacts are insufficient. Inventory/coverage is a future acceptance requirement, not work already completed.
- Dependencies: approved restricted online API environment, HTTPS, PostgreSQL, migrations/publication and valid test identities are part of T081. Reuse this environment in T07 for frontend/story verification. Preserve local/test-only mock restrictions and production docs policy; no raw data/secrets.
- Validation: checked task ID uniqueness, T081-before-T07 placement, acceptance/implementation distinction and documentation-only scope. No runtime tests or deployment are claimed.
- nextTaskId: US-09.T081 implementation after planning PR is accepted; then US-09.T07. Older next-task statements below are superseded for this owner-directed ordering.
- Timing: phase-level timer was not started at turn entry; durations are not claimed from Git timestamps.



## Owner-directed continuity v12 checkpoint (2026-10-10) — authoritative documentation update

- Scope/budget: one documentation-only PR; refresh the continuity handoff, CHANGELOG and this checkpoint. No runtime, migration, data or design edits.
- Base: main `6d31bde1bc27ecdf1fabe3f423b660b3930f1b78` after merged PR #93; feature head `69a0abf7b8deef4b26a8abbd7484bd4fe9ef9858`.
- Evidence: feature CI 38073092052 and merged-main CI 38073493793 succeeded; all four main jobs passed.
- Owner authorization: explicit request to update continuity despite the normal story-end rule. This refresh does not declare US-09 complete.
- Acceptance: v12 names current main/evidence; records profile, same-origin cookie restoration, questionnaire ownership proof, immutable history/cursor/hide, migrations and browser-local bookmark separation; removes obsolete next-task instructions from current sections.
- Validation: inspected canonical guide/current repository contracts and related ADRs; checked Markdown structure, version/date/ref/CI consistency, changed-file scope and absence of runtime edits. Runtime tests are not rerun for this documentation change; this PR's required CI remains the merge gate.
- nextTaskId: US-09.T07 real infrastructure and URL verification, after resolving any final owner acceptance defects. Previous entries below are historical; do not restart completed tasks from them.
- Limitations: no independent final visual acceptance, real SMS, production authentication or public full-stack deployment is asserted.


## US-09.T06 implementation checkpoint (2026-09-26)

- `activeTaskId`: `US-09.T06`; `actualScope`: canonical session to approved category impacts, source-backed scoring, real API and active result/detail route. D-005 uses only answer-conversion numeric weights; one-to-one factors use their independent source; mapping-matrix numbers are not read.
- Tests: full official-source SQLite HTTP flow (102 approved loans, ten answers, 14 needsReview, published conditions), 116 backend tests, source-cell and neutral cases; record PostgreSQL and Chromium CI results in the PR after completion. These tests do not prove a public staging URL.
- `nextTaskId`: `US-09.T07` persistent staging PostgreSQL and published import, deployed API/Netlify integration and real URL owner verification. Production remains US-12. Keep the User Story continuity document unchanged until the whole US-09 ends.


## US-09.T05B implementation checkpoint (2026-09-26)

- `activeTaskId`: `US-09.T05B`; `estimatedWorkScope`/`completionBudget`: approved snapshot read, real loan-detail projection, existing T05A publication reuse/backfill, PostgreSQL integration tests, docs and PR. `actualScope`: those boundaries; no session mapper, recommendation endpoint, frontend route or deployment.
- Source integrity: same six official Git blobs listed in the T05A checkpoint below, unchanged. D-005: only answer-conversion weights are authoritative; numeric mapping-matrix coefficients are ignored. Separate one-to-one compatibility cells remain source-backed.
- New migration `a62c0b5b005b` stores version-scoped display facts. Snapshot read checks active published members, approved config and eight variables in one SQL statement. Loan details read exact conditions and facts of the same member version. An existing T05A catalogue has an explicit source-checked, transactional, idempotent facts backfill. The T05A materialization/approval path remains the durable publisher; no parallel generic publisher was introduced.
- Tests: focused SQLite/API and PostgreSQL CI verify score/review partition, exact conditions, backfill reuse/rollback, missing/incomplete/superseded/draft states, typed failure and public allowlist. Record final run in PR. No persistent service/database or Netlify integration is claimed by CI.
- `nextTaskId`: `US-09.T06` live session/API/UI, then `US-09.T07` persistent staging DB, approved import, Netlify connection and real-URL verification. Production release remains US-12. The continuity document is unchanged until the entire US-09 (including T07) ends.

## US-09.T05A implementation checkpoint (2026-09-26)

- `activeTaskId`: `US-09.T05A`; `estimatedWorkScope` / `completionBudget`: canonical source audit, D-005, deterministic source/config extraction, schema/materialization, focused and CI gates, documentation and PR in one bounded task. `actualScope`: same; no public API or deployment.
- Official six Git blobs: questionnaire `26c70261829442e0676b85ac552bd6f7255f5faf`; categories `f2121e0e7f109d03cce432e4119978ba51ebb915`; questionnaire mapping `2721940cdc5ae17fc952d20f947d949a61317fcd`; answer conversion `f14d0d82a13708e87eea93c1d96ff14f4797c10b`; one-to-one compatibility `7eeed38450067f7fe3ba6be4846999d768ed697c`; loans `0854a5c3ad6b7640ddb7d6d9ae24ae0b2a4733fc`. No source bytes changed.
- D-005 product-owner decision: only answer-conversion coefficients are authoritative weights; the mapping matrix's five differing numbers are ignored. Independent one-to-one compatibility matrix yields 720 coefficients.
- Source audit: 102 loans/conditions, 88 rankable and 14 needsReview; 816 variable assignments, 30 question groups, 150 answer weights, 720 compatibility cells. Three values above the approved maxAmount ceiling remain unmapped.
- Migration `91d5a005a01a` and `materialize_official_sources` provide durable versioned rows, source provenance and a single active publication with explicit operator approval. Exact manifest digests block edited content bearing a valid source hash; identical active publication is reused, and transaction failure rolls back. Previously published loans without this active official catalogue fail closed pending row-level reconciliation, avoiding duplicate import.
- Tests: focused backend tests passed locally; PostgreSQL migration/materialization passed in GitHub Actions' disposable PostgreSQL service. The repository also defines a local Docker Compose PostgreSQL volume, but this execution environment did not run it. `netlify.toml` builds only the frontend; no continuously hosted PostgreSQL instance is identified or claimed here. No persistent catalogue publication has occurred. Future local or hosted publication requires selecting that database, auditing it, then explicitly invoking the approved command; source counts are not database-state evidence.
- `nextTaskId`: `US-09.T05B` after the T05A gate, then `US-09.T06` live integration. US-09 is incomplete. The User Story continuity document remains unchanged until the story ends.

## Active task

- activeTaskId: US-09.T05A (new ordered prerequisite; implementation pending)
- Status: task definition added to the canonical guide on `feature/us-09-live-integration`; no data, scoring, API, UI, deployment, or continuity document behavior changed by this planning amendment. US-09.T06 remains incomplete and follows a green T05A gate.
- Decision: the six verified UTF-16LE unitext sources, approved D-001–D-004 decisions, canonical guide and existing US-08 engine define the calculation. T05A materializes and verifies those rules and PUBLISHED loan/conditions serving data; it does not invent recommendation logic.
- Guide/source attestation: complete guide reread, `docs/recommendation-data-decisions.md` reread and six sources inspected via byte-preserving Git blob identities 26c70261829442e0676b85ac552bd6f7255f5faf, f2121e0e7f109d03cce432e4119978ba51ebb915, 2721940cdc5ae17fc952d20f947d949a61317fcd, f14d0d82a13708e87eea93c1d96ff14f4797c10b, 7eeed38450067f7fe3ba6be4846999d768ed697c, 0854a5c3ad6b7640ddb7d6d9ae24ae0b2a4733fc.
- Test plan for this documentation change: verify US-09 story row, execution matrix, full T05A criteria and T06 dependency agree; no runtime tests are claimed. T05A implementation must run the gates defined in the guide.
- Ordered sequence: US-09.T05A (data/config audit and durable materialization) → US-09.T05B (PostgreSQL snapshot, publication and loan-detail read adapters) → US-09.T06 (session-to-canonical mapping, recommendation endpoint and active frontend journey). The pure engine does not directly read session or ORM by design.
- Planning gate: T05B is defined, not implemented. No runtime tests or live recommendations are claimed by this documentation-only change.
- nextTaskId: US-09.T05A. Preserve `docs/PROJECT_CONTINUITY_DOCUMENT_SHAHAB_FINANCE_DEMO.md` until the entire US-09 is complete.

## Prior US-09.T06 discovery checkpoint

- activeTaskId: US-09.T06
- Status: in progress; US-09.T01–T05 and PR #44 are merged. This checkpoint is not a completion claim.
- Base branch: main at 4c76f266693580312e908a1f23b691c00d24bc25 (merge PR #44).
- Working branch: feature/us-09-live-integration
- estimatedWorkScope: connect canonical session, approved answer-to-preference conversion, published snapshot, server endpoint and active frontend result route; prove response allowlist and browser journey. No deployment.
- completionBudget: the first gate is approved data readiness. No score or published catalogue can be fabricated to satisfy an E2E.
- Acceptance: only the sessionId appears in the recommendation POST body; complete active canonical answers, approved configuration, PUBLISHED candidates, server scores/reasons, score-free needsReview, real details and safe errors. Quality, PostgreSQL migration, Chromium and security gates must pass.
- Source/guide attestation: full canonical guide and recommendation-data decisions reviewed. Six original source Git blob SHAs: questionnaire 26c70261829442e0676b85ac552bd6f7255f5faf; loan categories f2121e0e7f109d03cce432e4119978ba51ebb915; questionnaire mapping 2721940cdc5ae17fc952d20f947d949a61317fcd; answer weights f14d0d82a13708e87eea93c1d96ff14f4797c10b; one-to-one coefficients 7eeed38450067f7fe3ba6be4846999d768ed697c; loan source 0854a5c3ad6b7640ddb7d6d9ae24ae0b2a4733fc. The source contract identifies UTF-16LE; GitHub's text wrapper transcodes retrieval, so original blob SHA is the byte-preserving identity.
- Blocker discovered before implementation: the persisted model has LoanTerms for four numeric attributes but no persisted category assignments for all eight variables, no approved answer-to-category impact mapping consumed by the engine, no durable published catalogue import/pointer adapter, and no stored approved conditions text. The current SQLAlchemy catalogue adapter returns conditionsSourceText=None. The current in-memory publication repository explicitly forbids production use. A scored API or real details cannot safely be declared operational until these boundaries are supplied and verified.
- Decision: fail closed on unavailable approved data; do not invent mappings, scores, conditions or published loans. Preserve the User Story continuity document until the complete story is proven. No Netlify/deployment change.
- nextTaskId: US-09.T06 (remaining prerequisite: approved materialization and configuration, followed by session/API/UI integration and all gates).

## Previous checkpoint

## Evidence

- US-09.T05 start checkpoint: dependencies T01–T04 are merged. Acceptance requires a browser-executed contract from the existing result client and RTL/a11y result screen through the safe loan-details route, including score-free needs-review, manual controls and typed retry. Because the live endpoint is owned by T06, controlled HTTP responses may be used only inside the test harness and must not become production data or a route replacement.
- US-09.T05 end checkpoint: GitHub Actions #145 passed quality, PostgreSQL migration verification and Chromium E2E after the detail-link selector was made explicit. The fixture is reachable only beneath tests/, has no production import, sends the opaque session ID only in the request body, and verifies result-to-details browser handoff. T06 remains mandatory for real questionnaire/session/API/engine connection and preview verification; continuity remains unchanged until full US-09 completion.

- US-09.T04 start checkpoint: dependencies US-09.T01–T03 and the merged US-09.T06 Definition of Done are present. Acceptance requires lender filter, stable display sort without score ordering, RTL/a11y/responsive presentation and focused tests, without adding an API, session lookup, route wiring or static recommendation data.
- US-09.T04 end checkpoint: code review confirmed filtering preserves source membership/order before display sorting; the only alternate sort is stable lender name; score formatting is presentation-only; needs-review remains score-free; safe details links and typed loading/error states are rendered. GitHub Actions #141 passed quality, PostgreSQL migration verification and Chromium E2E. The follow-up documentation checkpoint commit will be verified by the same required gate. The next task remains US-09.T05 (browser E2E); T06 remains required before US-09 can be declared Done.
- Continuity-document rule: `PROJECT_CONTINUITY_DOCUMENT_SHAHAB_FINANCE_DEMO` remains unchanged until the end of the complete US-09 user story.

- US-09.T03 start checkpoint: dependency US-09.T02 is merged. Acceptance requires four distinct display outcomes with no scoring/reorder/filter logic moving into the browser boundary, plus contract tests, docs, CHANGELOG, checkpoint and green CI.
- US-09.T03 end checkpoint: code review confirmed server score/order preservation, score-free needs-review handling, no invented/reordered filtered item, and no API/storage/session/identity/React-route boundary crossing. GitHub Actions #135 passed all required gates; the next ordered task is US-09.T04 (manual filters, stable sort, accessibility and responsive RTL).
- Continuity-document rule: `PROJECT_CONTINUITY_DOCUMENT_SHAHAB_FINANCE_DEMO` remains unchanged until the end of the complete US-09 user story.


- US-09.T02 start checkpoint: dependency US-09.T01 is merged. Acceptance requires a minimal API client that carries only the in-memory opaque session ID in a JSON body, validates server data through the existing view model, has no client score/order/filter logic, and includes tests, docs, CHANGELOG, checkpoint and green CI.
- US-09.T02 end checkpoint: code review confirmed no response-body leakage, client-side score computation, reorder/filter, storage, session lookup, identity, raw-answer handling or React result page. GitHub Actions #132 passed all required gates; the next ordered task is US-09.T03 (distinct ranked, needs-review, no-candidate and zero-after-filter presentation states).
- Continuity-document rule: `PROJECT_CONTINUITY_DOCUMENT_SHAHAB_FINANCE_DEMO` remains unchanged until the end of the complete US-09 user story.


- US-09.T01 start checkpoint: US-08 is merged and its green engine regression gate is the dependency. Acceptance requires a small presentation-only view model, a documented server read-model contract, no score calculation or API/UI/persistence boundary crossing, tests, CHANGELOG, checkpoint and green CI.
- Full canonical guide, `docs/recommendation-data-decisions.md`, and all six verified UTF-16LE official sources were reread before implementation; source blob SHAs are recorded in the task PR.
- US-09.T01 end checkpoint: code review confirmed no API call, React page, client score calculation, reorder/filter, persistence, session, identity or raw-answer boundary crossing. GitHub Actions #128 passed all required gates; next ordered task is US-09.T02 (API client and actual response integration).
- Continuity-document rule: `PROJECT_CONTINUITY_DOCUMENT_SHAHAB_FINANCE_DEMO` remains unchanged until the end of the complete US-09 user story.

- US-08.T05 start checkpoint: dependency US-08.T04 is merged; scope fits one small test-only PR. Acceptance requires deterministic regression coverage for approved scoring policy, no boundary crossing into transport/persistence, documentation, CHANGELOG, checkpoint and green CI.
- Full canonical guide, `docs/recommendation-data-decisions.md`, and all six verified UTF-16LE official sources were reread before implementation; source blob SHAs are recorded in the task PR.
- US-08.T05 end checkpoint: code review confirmed test-only changes with no API, persistence, session, identity, raw-answer or configuration boundary crossing. GitHub Actions #123 passed all required gates; next ordered task is US-09.T01 (results read-model/contract planning and boundary work).

- US-08.T04 start checkpoint: dependency US-08.T03 is merged; scope fits one small application-layer PR. Acceptance requires an approved immutable read snapshot, deterministic results/traces from the pure engine, no transport/ORM dependency, focused fake-repository tests, docs, CHANGELOG, checkpoint and green CI.
- Full canonical guide, `docs/recommendation-data-decisions.md`, and all six verified UTF-16LE official sources were reread before implementation; source blob SHAs are recorded in the task PR.
- US-08.T04 end checkpoint: code review found no transport, database, session, identity or raw-answer boundary crossing. CI run #116 passed; next ordered task is US-08.T05 (expanded unit/property/golden coverage).

- US-08.T03 start checkpoint: estimated scope fits one small pure-domain PR; dependency US-08.T02 is merged; acceptance requires versioned/redacted trace evidence for each candidate decision, deterministic stable hashing, no raw session/user data, focused tests, documentation, CHANGELOG and green CI.
- Full canonical guide, `docs/recommendation-data-decisions.md`, and all six verified UTF-16LE official sources were reread before implementation; source blob SHAs are recorded in the task PR.
- US-08.T03 end checkpoint: code review found no API, persistence, session, identity or raw-answer boundary crossing. CI run #112 passed; next ordered task is US-08.T04 (RecommendLoans use-case composition).

- The full canonical guide and its three golden rules were reread before this task.
- The baseline, repository, and canonical-source inventories are complete.
- All six `.unitext` files are byte-verified UTF-16 LE sources.
- Documentation skeletons and an ADR template now establish stable locations for future architecture, API, database, pipeline, security, operations, and test evidence.
- The initial risk and ambiguity register is recorded in `docs/project-risk-register.md`; no risk is silently accepted.
- Canonical IDs for questionnaire questions/answers, loan variables, categories, routes, and future loan identity are versioned in `data/contracts/canonical-identifiers.v1.json` and statically validated.
- Pure, framework-independent schema and Persian scalar parser contracts are versioned and unit tested; ambiguous ranges/prose remain typed unknowns.
- A read-only source audit and provenance report record source hashes, structural coverage, numeric coefficient ranges, loan-row evidence, and blocking core-value issues.
- Versioned data decisions define the Q5 interest weight, neutral deposit-feature behavior, core-value ranking exclusion, and display-only source columns.
- Versioned golden contract fixtures cover every canonical question and the complete, neutral, and core-unknown loan-policy boundaries without asserting an engine score prematurely.
- A staged frontend/backend architecture scaffold and module map are created without moving the active Vite prototype.
- `US-03.T01` was merged in PR #5.
- Typed FastAPI application composition, environment settings, redacting logging and dependency providers are implemented without any product endpoint, database or deploy change.
- `US-03.T02` was merged in PR #6.
- Framework-free domain references and small application ports now define one-way dependencies; an AST validator blocks reverse imports and local cycles.
- `US-03.T03` was merged in PR #7.
- API v1 now has typed errors, server-generated correlation IDs, minimal public liveness and token-gated readiness without exposing dependency state.
- `US-03.T04` was merged in PR #8.
- A single local/CI quality command now runs formatting, linting, type checking, backend tests, architecture/data validators, secret scan and production build.
- `US-03.T05` was merged in PR #9; US-03 quality gate is complete.
- Conceptual bounded contexts, cardinalities, ownership/retention and physical-schema invariants are documented before ORM or migration work.
- `US-04.T01` was merged in PR #10.
- PostgreSQL 3NF physical tables, type/state semantics, constraint catalog and migration/rollback operations are specified before ORM/migration implementation.
- `US-04.T02` was merged in PR #11.
- SQLAlchemy 2.x metadata declares the core 3NF catalog/config/import constraints without creating a session, engine or schema.
- `US-04.T03` was merged in PR #12.
- Alembic owns versioned DDL; a bounded SQLAlchemy engine/session factory is isolated in the database infrastructure adapter.
- Docker Compose defines local-only API/PostgreSQL startup without committing operational credentials; GitHub Actions provisions PostgreSQL 16 for migration verification.
- Query contracts now own a small, reversible index set; a representative selective catalogue query must use the lender FK index according to PostgreSQL `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)`.
- `US-04.T05` was merged in PR #14 after PostgreSQL 16 migration and plan-verification CI passed.
- Raw source capture is now isolated from parsers and serving data: source bytes have an immutable SHA-256 identity and traceable capture metadata.
- Raw evidence now has strict, non-destructive staging checks for encoding, headers, row shape and duplicate source hashes.
- All eight approved loan variables now have a pure, conservative category-normalization boundary. Matrix gaps, capped-out amounts, free text, ranges, unknown and variable values remain typed evidence rather than inferred categories.
- Canonical rows now retain source-row fingerprints, typed construction rejections and rankability evidence; reviewable drafts require explicit approval before an atomic serving-version pointer can move.
- The internal import command now produces a typed, reviewable canonical plan and cannot connect to a database or publish data; the operations runbook fixes the safe hand-off and recovery sequence.
- Repeated manifest preparation is deterministic; ambiguous fields remain typed evidence, and a publish failure leaves the previous serving version active.
- Framework-free ListLoans and GetLoanDetails now depend on a serving-only port; source/draft/superseded data and provenance fields are blocked from their output.
- Typed loan response schemas now allowlist public catalogue facts and forbid raw conditions, provenance, serving-version and internal asset data.
- Approved conditions source text now has a pure plain-text bullet parser; nested list markers and blank lines are normalized without emitting HTML.
- The serving-only use cases now have a PostgreSQL/SQLAlchemy read adapter with an explicit `PUBLISHED` predicate; draft, raw, staging and superseded records cannot cross into the public-catalogue boundary.
- `US-06.T04` now composes a request-scoped `GetLoanDetails` endpoint at `GET /api/v1/loans/{loanId}`. It never accepts a source/version selector and returns typed unavailable/not-found errors without database details.
- The endpoint exposes approved terms and parsed plain-text `conditions` only; it omits raw conditions, provenance, approval metadata, serving-version IDs and internal logo references.
- The active Vite prototype's `src/features/loan-details/` fetches that contract and renders RTL loading, absent-detail, safe-error/retry and detail states. It has no hard-coded detail fallback and React renders every condition as text.
- `US-06.T05` adds four browser scenarios for RTL rendering, loading, typed absent detail, typed failure/retry, escaped hostile conditions and ignored invalid logo/link fields. The browser gate is isolated in CI and installs the pinned Chromium revision before execution.
- `US-07.T01` adds an approved questionnaire configuration artifact with the verified questionnaire source hash, all ten canonical required questions and fifty semantic answer IDs. Its pure loader rejects missing, reordered, duplicate or non-canonical answers before route/session/UI work begins.
- `US-07.T02` introduces the sole route adapter for `/question/3..12`. It translates public paths to canonical question IDs and back, while a documented compatibility bridge translates only those IDs to the prototype's existing screen indexes. Browser paths and indexes are never answer identifiers.

## Test record

| Command | Result |
| --- | --- |
| `npm run build` | Passed; Vite production build completed. |
| `npm run test:backend-core` | Passed; five settings, composition and redaction tests completed. |
| `python -m unittest discover -s backend/tests -p "test_*.py"` | Passed; 22 backend tests completed. |
| FastAPI composition boot with `SHAHAB_CORS_ALLOWED_ORIGINS` | Passed; comma-separated environment configuration was parsed safely. |
| `npm run validate:import-boundaries` | Passed; no prohibited reverse import or local circular dependency detected. |
| `python -m unittest backend.tests.test_application_ports` | Passed; four port and import-boundary tests completed. |
| `python -m unittest discover -s backend/tests -p "test_*.py"` | Passed; 26 backend tests completed after US-03.T03. |
| `npm run test:api-health` | Passed; liveness, readiness authorization and typed 404 behavior verified. |
| `python -m unittest discover -s backend/tests -p "test_*.py"` | Passed; 29 backend tests completed after US-03.T04. |
| `npm run quality` | Passed; Ruff format/lint, Mypy (22 source files), 31 backend tests, all validators, secret scan and production build completed. |
| `npm run quality` | Passed; conceptual data-model validator and 32 backend tests completed with all existing quality gates. |
| `npm run quality` | Passed; physical-schema specification validator and 33 backend tests completed with all existing quality gates. |
| `npm run quality` | Passed; SQLAlchemy metadata tests and 35 backend tests completed with all existing quality gates. |
| `SHAHAB_DATABASE_URL=sqlite:///… alembic upgrade head → downgrade base → upgrade head` | Passed; clean structural lifecycle check completed. |
| GitHub Actions PostgreSQL 16 migration job | Pending PR execution; it enforces empty-db upgrade, fixture write and downgrade on real PostgreSQL. |
| `npm run quality` | Passed; 38 backend tests (two PostgreSQL integration tests skipped locally), all quality gates and production build completed. |
| Alembic index lifecycle | Passed locally: initial migration + index migration upgrade, downgrade to base and repeated upgrade. |
| `python -m unittest backend.tests.test_normalization` | Passed; approved categories, Persian digits, boundary ownership, gaps, unknowns and text-only categories are covered. |
| `npm run quality` | Passed; 50 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-05.T03. |
| `python -m unittest backend.tests.test_serving_publication` | Passed; canonical-row rejection/eligibility, approval gate, diff and atomic-pointer failure behavior are covered. |
| `npm run quality` | Passed; 55 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-05.T04. |
| `python -m unittest backend.tests.test_import_preparation` | Passed; clean plan, typed issues/rejections, core needs-review preservation and non-publishing CLI behavior are covered. |
| `python -m unittest backend.tests.test_import_preparation backend.tests.test_serving_publication` | Passed; repeated import determinism, ambiguous input and previous-pointer preservation on publication failure are covered. |
| `npm run quality` | Passed; 61 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-05.T06. |
| loan catalogue use-case test | Passed; serving-only filtering, deterministic list ordering, missing detail and blank ID handling are covered. |
| loan response-schema test | Passed; camel-case allowlist, prohibited internal fields and validation errors are covered. |
| conditions parser test | Passed; bullets, line breaks, nested markers, empty text and HTML-as-text behavior are covered. |
| `npm run quality` | Passed; 70 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-06.T03. |
| `python -m unittest backend.tests.test_sqlalchemy_catalogue_adapter` | Passed; the durable adapter returns only published versions and rejects draft lookups. |
| `npm run quality` | Passed; 71 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after corrective US-06.R01. |
| `python -m unittest backend.tests.test_loan_detail_api backend.tests.test_loan_response_schemas` | Passed; approved detail allowlist, text bullets, typed not-found/unavailable errors and omitted internals are covered. |
| `npm run quality` | Passed; 74 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-06.T04. |
| `npx playwright test --list` | Passed; all four US-06.T05 browser scenarios were discovered and parsed. |
| `npm run build` | Passed; the active Vite frontend compiles with the new browser-test dependencies/configuration. |
| `npm run test:e2e` | Blocked locally only: the sandbox could not download the Playwright Chromium binary (network 502). CI has a dedicated browser-install-and-run job; this is not a test assertion failure. |
| GitHub Actions run #37 | Passed: quality gates, PostgreSQL migration verification and all four Chromium loan-details E2E scenarios. |
| `python -m unittest backend.tests.test_questionnaire_configuration` | Passed; ten canonical required questions, fifty canonical answer IDs and malformed/reordered answer rejection are covered. |
| Exact source/config comparison | Passed against the verified GitHub source blob; all ten prompts and fifty options match in source order. |
| `npm run quality` | Passed through format, lint, Mypy, 76 backend tests and prior validators locally; the final source-file validator cannot run in this scratch checkout because its already-versioned `.agents/documents` raw files are absent locally. |
| GitHub Actions run #41 | Passed: the complete checkout executed the source-file questionnaire validator, repository quality gate, PostgreSQL migration verification and Chromium E2E verification. |
| `npm run test:questionnaire-route-map` | Passed; all ten canonical forward/reverse route mappings, legacy index bridge, and unmapped-path rejection are covered. |
| `npm run quality` | Passed; 76 backend tests (2 PostgreSQL integration tests skipped locally), 3 route-adapter tests, source integrity validation, formatting, lint, typecheck, validators, secret scan and production build completed after US-07.T02. |
| `npm run test:e2e` | Browser binary unavailable locally; CI run #46 installed the pinned Chromium revision and passed all five scenarios, including the US-07.T02 all-routes browser case. |
| GitHub Actions run #46 | Passed: Quality gates, PostgreSQL migration verification, and Chromium browser verification on the final `US-07.T02` commit. |
| `npm run quality` | Passed; 67 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-06.T02. |
| `npm run quality` | Passed; 64 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-06.T01. |
| `npm run quality` | Passed; 59 backend tests (2 PostgreSQL integration tests skipped locally), formatting, lint/type checks, validators, secret scan and production build completed after US-05.T05. |
| GitHub Actions run #78 | Passed: quality gate (format/lint/Mypy, backend and client contracts, validators, secret scan, production build), PostgreSQL migration verification, and Chromium browser E2E on the final US-07.T04 commit. |

## Blockers and next task

- Docker/Compose is unavailable in this environment; real PostgreSQL migration integration is enforced in GitHub Actions.
- The prototype has no automated lint/typecheck/test suite yet; this remains recorded baseline risk.
- `US-01` was merged in PR #3.
- `US-02` was merged in PR #4.
- `US-05.T02` was merged in PR #16.
- `US-05.T03` was merged in PR #17.
- `US-05.T04` was merged in PR #18.
- `US-05.T05` was merged in PR #19.
- `US-05.T06` was merged in PR #20.
- `US-06.T01` was merged in PR #21.
- `US-06.T02` was merged in PR #22.
- Corrective `US-06.R01` was merged in PR #24.
- The current physical catalogue adapter has no persisted display-conditions column yet; until the approved import/persistence mapping supplies `LoanDetail.conditions_source_text`, the deployed endpoint correctly returns an empty `conditions` list rather than inventing terms. This is a data-hydration limitation, not a fallback to prototype data.
- Local Python dependencies are temporarily unavailable in this sandbox after runtime reset; CI reinstalled from the locked project configuration and passed quality/migration checks. The browser gate passed in CI run #37 and is the authoritative E2E execution.
- The local scratch checkout lacks the already-versioned `.agents/documents/*.unitext` raw files; no fallback or source alteration was introduced. GitHub Actions run #41 executed the authoritative exact-source gate against the complete repository successfully.
- `US-07.T03` is merged in PR #29 and `US-07.T04` is merged in PR #30. The next ordered task is `US-07.T05`; after it, the new mandatory `US-07.T06` persists anonymous questionnaire sessions/answers in normalized PostgreSQL tables with Redis cache, 30-minute expiry/cleanup, restart/cache-failure tests and synchronized ERD/schema documentation before `US-08` may start.

## Compatibility pointer

This is the canonical current-state checkpoint required by the guide. `docs/progress/current-state.md` is retained only as historical context for earlier commits.
