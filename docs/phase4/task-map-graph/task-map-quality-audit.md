# گزارش ممیزی Stage 4 بر مبنای HEAD فعلی PR #256

## مبنای بررسی و وضعیت PR

این گزارش از HEAD واقعی شاخه در آغاز ممیزی، `655daa9d349f00718b0c93ae2016decb4ffbb510`، و Blobهای همان شاخه بازتولید شده است. PR شمارهٔ ۲۵۶ باز، Draft، ادغام‌نشده و در وضعیت mergeable است. HEAD مبنا `main` در `c9e74532d4291e9ed1a7ddd3523ee84f09c940a2` است. فایل‌های Mapping و Replay روی Commit `aa30b45c57e2be4de84dfd08a0eb47324246b794` منتشر و از Blobهای GitHub با Blobهای فایل‌های مورد بررسی تطبیق شدند. این نسخهٔ گزارش، نتایج محلیِ همان Tree و گردش‌کارهای اجراشده روی آن Commit را ثبت می‌کند.

مقادیر snapshot قدیمی در `validation.historical_snapshots` داخل Mapping حفظ شده‌اند و با برچسب تاریخی مشخص‌اند؛ آن اعداد مبنای وضعیت فعلی نیستند. Snapshot جاری داخل `validation.stage4_audit` از داده‌های فعلی بازسازی شده است.

## شمارش Ledger و Task Graph

Ledger جاری: ۱٬۶۳۳ Candidate، صفر Pending، ۱٬۲۸۵ Atomic Obligation شامل ۱٬۱۴۹ Covered، صفر Partial، ۱۳۴ Open Decision و ۲ Uncovered.

Task Graph تغییرناپذیر شامل ۳۶ Package، ۱۸۹ Task، ۴۷۱ Subtask و ۶۹۶ Node است. ۶۸۸ Edge آن شامل ۶۶۰ `contains`، ۱۳ `depends_on`، ۱۱ `requires_contract`، ۳ `requires_policy` و ۱ `sequence_after` است.

Mapping جاری ۶۹۶ Node دارد: ۱۵ `MAPPED`، ۲۷ `PARTIALLY_MAPPED` و ۶۵۴ `NEW_IMPLEMENTATION`. نسبت به snapshot قدیمی ۱۵/۲۴/۶۵۷، ۳ رکورد از `NEW_IMPLEMENTATION` به `PARTIALLY_MAPPED` منتقل شده‌اند؛ این تغییر حاصل بازبینی شاهد کد موجود R10 است، نه تغییر گراف.

## سه گراف immutable

| گراف | Blob SHA | SHA-256 |
| --- | --- | --- |
| `knowledge-graph/phase2-reference-docs/semantic/graph.json` | `a43c1732e85eeebdf83709b9d76233e59ae1a1af` | `f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93` |
| `docs/phase4/task-map-graph/current-project-code-graph.json` | `c19d700b408206458d56798809ec1c7009e08acc` | `0a496833d1a58a6d07e58f3d5d2b59f2c0306a924d8573a687fc4067c549c982` |
| `docs/phase4/task-map-graph/new-project-task-graph.json` | `2393556b74016a437d9a126bee3b04cdcc42be25` | `deb940949583007628dccb89de538c8f3b278aef1c6f99d1386f613f107fa0f7` |

Replay پین‌های Blob SHA و SHA-256 این سه فایل را در هر اجرا کنترل می‌کند. هیچ Node، Edge، نام یا Metadata این گراف‌ها تغییر نکرده است.

## Mapping، Overlay و ترتیب اجرا

Relation Overlay شامل ۹۴ رابطه است: ۴۷ `handoff`، ۱۷ `depends_on`، ۲۹ `requires_contract` و ۱ `requires_policy`. همهٔ ردیف‌ها Source Locator و Plan Locator معتبر دارند. در Overlay، ۲۸ رابطه مستقیماً به Task/Subtask می‌رسند و ۶۶ رابطه در سطح Package هستند. هیچ رابطهٔ `parallel_safe` اثبات یا ثبت نشده است.

اثر اجرایی روابط ثبت‌شده: ۱۲ `HARD_ORDER`، ۲۵ `CONTRACT_ORDER`، ۳۲ `POLICY_IMPACT`، ۲۲ `IMPACT_ONLY` و ۳ `BLOCKED_BY_DECISION`. در ترکیب گراف و Overlay هیچ چرخهٔ ترتیب سخت وجود ندارد. `SOFT_ORDER` در Overlay به‌عنوان اثر مستقل ثبت نشده؛ روابطی که منبع آن‌ها تقدم سخت نمی‌دهد به `IMPACT_ONLY` یا نوع اثر صریح خود محدودند و به ترتیب قطعی تبدیل نشده‌اند.

### Handoff:H04:003

Plan در Locator `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:4049` صریحاً تخصیص Package مقصد را در خود Handoff باز می‌گذارد؛ Locator `:4053`، A01/A02 را فقط برای برنامه‌ریزی می‌پذیرد و می‌گوید نسخه/Schema باید پیش از اجرا آماده شود. به همین دلیل C04→A01/A02 فقط Package-scoped و `SOURCE_SCOPED` است: اعتماد منبع برای پذیرش برنامه‌ریزی تأییدشده است و اثر آن تقدم قراردادی در سطح Package است، بدون Task مصرف‌کنندهٔ حدسی.

برای R01–R10، Plan مصرف‌کنندهٔ بالقوهٔ آینده را بیان می‌کند و تخصیص واقعی هر مصرف به بسته/Task مشخص را باز می‌گذارد. Package endpointها فقط Scope بالقوه‌اند؛ وضعیت `SOURCE_SCOPED`، اطمینان باز و اثر `IMPACT_ONLY` دارند. این محدودیت هنوز اثر واقعی بر تخصیص Task و زمان‌بندی اجرای هر مصرف‌کننده دارد و در Stage 4 به‌صورت باز ثبت شده است.

### DEP:C05A:003 و DEP:C05A:004

در DEP:C05A:003، C04 و C06 مصرف‌کنندگان Package-level تأییدشدهٔ projection کاتالوگ/Capability هستند و رابطهٔ قرارداد پیش از پیاده‌سازی مصرف‌کننده لازم است. A01، A02 و R01–R10 در همان بند فقط زیر دامنهٔ Adviser/Assistant آینده قرار می‌گیرند؛ رابطهٔ آن‌ها `SOURCE_SCOPED`، با اطمینان باز و `IMPACT_ONLY` است و Task قطعی ندارد.

DEP:C05A:004 چهار مقصد R02، A01، A02 و C06 را برای routing/context/result نام می‌برد. هر چهار رابطهٔ Package-level `CONFIRMED` و `SOURCE_SCOPED` با اثر `CONTRACT_ORDER` هستند. Locator `:4263` رابطه و جهت مصرف را مستند می‌کند، اما Task/Subtask دقیق مقصدها را تعیین نمی‌کند؛ بنابراین آن‌ها به‌عنوان Mapping کامل Task-level گزارش نمی‌شوند.

هیچ‌یک از این محدودیت‌های تخصیص به Phase 5 منتقل نشده است. Phase 5 صرفاً برای تبدیل گراف نهایی به تحویل‌دادنی‌های یک‌هفته‌ای است.

## ۱۳۴ تصمیم باز و ۲۲ مرجع ویژه

۱۳۴ شناسهٔ تصمیم باز، هرکدام دقیقاً یک بار وجود دارند. وضعیت محصولی همه `OPEN` و وضعیت Mapping اجرایی همه `BLOCKED` باقی است؛ ۱۲۰ تصمیم به Task، ۸ به Package و ۶ به چند Task Scope دارند. برای هر ۱۳۴ تصمیم Source Locator، Plan Locator، Scope و `BLOCKED_BY_DECISION` ثبت شده است؛ هیچ Plan Locator خالی نمانده است. Locatorهای افزوده‌شده از `plan_refs` گره‌های canonical Task/Package گرفته شده‌اند. تصمیم باز به‌معنی حل محصولی یا تعیین مالک نهایی نیست.

هر ۲۲ مرجع ویژه بازبینی شده و همچنان OPEN/BLOCKED است. چهار مرجع `AO:BP-C-0291:01`، `AO:BP-C-0294:01`، `AO:BP-C-0298:01` و `AO:BP-C-0300:01` پس از بازبینی Blueprint، Plan، Wallet، package-execution index و Evidence Join Index در سطح Package باقی مانده‌اند. منابع برای اثرگذاری این تصمیم‌ها Scopeهای A04؛ A04/A06؛ A02/A04/C01؛ و A01/C04/C05A/C05B را نشان می‌دهند، اما Task یکتایی برای خود تصمیم‌ها crosswalk نمی‌کنند. به همین علت Task جعلی افزوده نشده و اثر اجرایی تا تعیین تصمیم مسدود است.

## TASK:CORE:C13B:008

نام اصلی `/` در گراف immutable حفظ شده است. Overlay عنوان `مسیر مالی مجاز را بررسی کند` را با نوع `CONTEXT_DERIVED_LABEL` ثبت می‌کند. Plan در `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6006` شناسهٔ canonical Task و Story «C13B-S08 مسیر مالی مجاز را بررسی کند» را در یک ردیف می‌آورد؛ Locator و Blob SHA Plan در Mapping ثبت است. این برچسب از متن مستقیم Story گرفته شده و نام جدیدی برای گراف اصلی نیست.

## اتصال به کد موجود

۶۵۷ رکورد `NEW_IMPLEMENTATION` از Mapping بازتولید شده‌اند: ۳۰ `NON_CODE_REQUIREMENT`، ۶۲۴ `NO_CODE_EVIDENCE_FOUND`، ۳ `CODE_PARTIALLY_FOUND` و صفر `SEARCH_INCONCLUSIVE`. جست‌وجو در inventory پین‌شدهٔ کامل کد فعال شامل ۳۴۷ فایل انجام شده است؛ دامنه شامل کد برنامه، API/Route، مدل و مهاجرت، پیکربندی و قرارداد، تست و fixture، Docker و workflowها است. نتیجه به نبود Node در Graphify محدود نیست و نبود شاهد در این inventory را اثبات نبود کد در تمام نسخه‌ها نمی‌داند.

سه مورد Partial عبارت‌اند از `TASK:RAG:R10:001`، `TASK:RAG:R10:002` و `TASK:RAG:R10:003`. Locator فایل/خط، Blob SHA و نوع شاهد برای هرکدام در `stage4_code_search_audit.records` ثبت شده است. شواهد فعلی مسیر use case/scorer/API توصیه، مدل Snapshot/repository و scorer/partition را پوشش می‌دهد؛ adapter/قرارداد Adviser و رفتارهای اختصاصی باقی‌مانده هنوز کامل نیستند. Graphify تغییر نکرده و Node حدسی ساخته نشده است.

`NO_CODE_EVIDENCE_FOUND` یعنی در inventory فعال کد پین‌شدهٔ این بررسی شاهد مستقیم متناظر پیدا نشد؛ ادعای قطعی دربارهٔ نسخه‌های دیگر یا امکان استفادهٔ مجدد آینده نیست.

## Replay، کنترل‌های داخلی و Workflowها

Replay معنایی، اعتبار هویت‌ها و Locatorها، Scope تصمیم‌ها، Overlay، چرخه‌ها، جست‌وجوی کامل کد و Hash سه گراف را کنترل می‌کند. این ابزار قضاوت معنایی را از متن به‌شکل ماشینی تولید نمی‌کند؛ قضاوت‌های ثبت‌شده را با شواهد و پیکرهٔ ثابت بازبینی‌پذیر می‌سازد.

دو اجرای `replay_stage4.py --check-only` روی Tree منتشرشدهٔ Commit `aa30b45c57e2be4de84dfd08a0eb47324246b794` PASS شدند و خروجی JSON byte-for-byte یکسان بود. SHA پروجکشن معنایی هر دو `2de89b2fe98312fe7ed7428eec45865974898ca3d52995b34725112c137a05d3` است؛ هر دو اجرای Replay صفر چرخه و ثابت‌بودن سه گراف immutable را تأیید کردند. اجرای `build_and_validate.py --check-only` PASS شد؛ هر ۲۹ کنترل داخلی PASS و شمارش Candidate/Obligation با مقادیر Ledger تطبیق داشت. هر چهار Workflow روی همان Commit `aa30b45c57e2be4de84dfd08a0eb47324246b794` نیز در GitHub Actions با نتیجهٔ `success` تمام شدند: Security SAST/SCA/secret gates؛ US-13 frozen frontend baseline evidence؛ Quality gates؛ Container build contract smoke. چون پس از این Commit، فقط متن همین گزارش به‌روزرسانی خواهد شد، نتیجهٔ Workflowهای Commit گزارش نهایی در توضیحات PR جداگانه و از روی HEAD واقعی ثبت می‌شود.

## تفاوت با گزارش‌های قدیمی و محدودیت‌های باقی‌مانده

Snapshotهای تاریخی ۱۵/۲۴/۶۵۷، ۱۲۶ BLOCKED/۸ UNMAPPED و ۷۲ Overlay دیگر وضعیت جاری نیستند. وضعیت فعلی ۱۵/۲۷/۶۵۴، ۱۳۴ BLOCKED/۰ UNMAPPED و ۹۴ Overlay است. سه تغییر Mapping ناشی از بازبینی کد R10 است؛ ۸ تصمیم پیش‌تر UNMAPPED با اتصال شاهددار به Scope موجود به BLOCKED تغییر کردند، در حالی‌که تصمیم محصولی هر ۱۳۴ مورد OPEN باقی ماند؛ Overlay نیز در به‌روزرسانی قبلی کامل شد و این اصلاح، رابطه‌ای حدسی اضافه نمی‌کند.

محدودیت‌های واقعی فعلی عبارت‌اند از تخصیص نشدن Task مصرف‌کننده برای H04:003 و تخصیص Task دقیق مقصدهای Package-level در DEP:C05A:003/004؛ چهار تصمیم ویژه نیز در Scope Package می‌مانند چون منابع Task تصمیم را تعیین نمی‌کنند. این موارد با Scope، اثر اجرایی و Locator ثبت شده‌اند و تا زمان شاهد دقیق، مانع ادعای تکمیل معنایی Mapping آن روابط‌اند.
