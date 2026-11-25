# گزارش ممیزی Stage 4 بر مبنای HEAD فعلی PR #256

## مبنای بررسی و وضعیت PR

این گزارش از HEAD واقعی شاخه هنگام بازبینی زنده، `3d4d596735474392ad1dd9cf98c7015d790ddbff`، و Blobهای همان شاخه بازتولید شده است. PR شمارهٔ ۲۵۶ باز، Draft، ادغام‌نشده و در وضعیت mergeable است. HEAD مبنا `main` در `c9e74532d4291e9ed1a7ddd3523ee84f09c940a2` است. Commitهای بعدیِ `c4ef91e47de27ccce387cabdf4a3e5bb9b07a698` و `3d4d596735474392ad1dd9cf98c7015d790ddbff` به‌ترتیب نتایج اعتبارسنجی و جداسازی Snapshot تاریخی/جاری را ثبت کردند. PR در زمان این بازبینی همچنان Open، Draft، ادغام‌نشده و mergeable است. آخرین اجرای محلی Replay و کنترل‌های Ledger روی Tree همین HEAD انجام شد؛ نتایج چهار Workflow نیز از GitHub و برای همین HEAD خوانده شد.

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


### بازبینی همهٔ ۶۶ رابطهٔ Package-level

در Mapping جاری دقیقاً ۶۶ ردیف Overlay در Scope سطح Package وجود دارد: ۳۶ ردیف `PACKAGE_ONLY` و ۳۰ ردیف `SOURCE_SCOPED`. از نظر اثر اجرا، ۳۲ `POLICY_IMPACT`، ۲۲ `IMPACT_ONLY`، ۹ `CONTRACT_ORDER`، یک `HARD_ORDER` و دو `BLOCKED_BY_DECISION` ثبت شده‌اند. این‌ها رابطه‌های قطعی Task-level محسوب نمی‌شوند. برای ردیف‌های `PACKAGE_ONLY`، endpoint و اثر اجرایی در سطح Package ثبت شده‌اند؛ ردیف‌های `SOURCE_SCOPED` دامنهٔ صریح منبع را حفظ می‌کنند. موارد دارای `BLOCKED_BY_DECISION` عبارت‌اند از `REL-STAGE4-014` برای `DECISION:C05A:001` و `REL-STAGE4-034` برای `OPEN:C08:04`.

یک تناقض crosswalk مانع ارتقای H04:003 به Task-level است: C04 در Plan:4049، مقصد Task را نامشخص می‌گذارد؛ شرح عمومی :4053 و :4060، پذیرش برنامه‌ریزی A01/A02 را می‌گوید؛ اما جزئیات Taskهای A01/A02 در :7611/:7639 و :7745/:7782 entitlement را ذیل `Handoff:H04:001` ثبت می‌کنند، نه H04:003. Taskهای `TASK:ASSISTANT:A01:003.S04` و `TASK:ASSISTANT:A02:003.S01` نامزدهای دقیق و شاهددار برای مصرف entitlement هستند، ولی تا رفع اختلاف شناسهٔ handoff نمی‌توان آن‌ها را به H04:003 نگاشت قطعی کرد. برای R01–R10 منبع فقط مصرف‌کنندهٔ احتمالی آینده را می‌گوید و Task مقصد نمی‌دهد.

این بازبینی شمارش و ارجاع‌های Overlay را از Blob جاری بازتولید می‌کند؛ خودش اثبات نمی‌کند که تمام Taskهای candidate در ۳۶ Package به‌صورت مستقل با AC/Test تطبیق داده شده‌اند. این محدودیتِ دامنهٔ ممیزی باید پیش از ادعای تکمیل معنایی رفع شود.

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

دو اجرای `replay_stage4.py --check-only` روی Tree منتشرشدهٔ Commit `3d4d596735474392ad1dd9cf98c7015d790ddbff` PASS شدند و خروجی JSON byte-for-byte یکسان بود. SHA پروجکشن معنایی هر دو `2de89b2fe98312fe7ed7428eec45865974898ca3d52995b34725112c137a05d3` است؛ هر دو اجرای Replay صفر چرخه و ثابت‌بودن سه گراف immutable را تأیید کردند. اجرای `docs/audits/phase2-source-coverage/build_and_validate.py --check-only` روی همین Tree PASS شد؛ هر ۲۹ کنترل داخلی PASS و شمارش Candidate/Obligation با مقادیر Ledger تطبیق داشت. چهار Workflow روی همین HEAD در GitHub Actions با نتیجهٔ `success` ثبت شده‌اند: Security SAST/SCA/secret gates (run 45580582337)، US-13 frozen frontend baseline evidence (run 45580582286)، Quality gates (run 45580582279)، Container build contract smoke (run 45580582282). این نتایج با Workflowهای Commitهای قدیمی‌تر مخلوط نشده‌اند.

## تفاوت با گزارش‌های قدیمی و محدودیت‌های باقی‌مانده

Snapshotهای تاریخی ۱۵/۲۴/۶۵۷، ۱۲۶ BLOCKED/۸ UNMAPPED و ۷۲ Overlay دیگر وضعیت جاری نیستند. وضعیت فعلی ۱۵/۲۷/۶۵۴، ۱۳۴ BLOCKED/۰ UNMAPPED و ۹۴ Overlay است. سه تغییر Mapping ناشی از بازبینی کد R10 است؛ ۸ تصمیم پیش‌تر UNMAPPED با اتصال شاهددار به Scope موجود به BLOCKED تغییر کردند، در حالی‌که تصمیم محصولی هر ۱۳۴ مورد OPEN باقی ماند؛ Overlay نیز در به‌روزرسانی قبلی کامل شد و این اصلاح، رابطه‌ای حدسی اضافه نمی‌کند.

محدودیت‌های واقعی فعلی عبارت‌اند از تخصیص نشدن Task مصرف‌کننده برای R01–R10 در H04:003، تخصیص نشدن Task دقیق برای همهٔ مقصدهای DEP:C05A:003/004، و چهار تصمیم ویژه که منابع برای خود تصمیم‌ها Task یکتا تعیین نمی‌کنند. برای A01/A02، Plan در Taskهای `TASK:ASSISTANT:A01:003.S04` و `TASK:ASSISTANT:A02:003.S01` مصرف entitlement را دقیق می‌کند (Plan:7639 و :7782)، اما ردیف‌های همان بخش به `Handoff:H04:001` ارجاع می‌دهند، در حالی‌که منبع C04 در :4049 همین خانوادهٔ مصرف را `Handoff:H04:003` با تخصیص Package نامعلوم می‌نامد. این ناسازگاری شناسهٔ منبع اجازه نمی‌دهد Taskهای A01/A02 را بدون اصلاح/تأیید crosswalk به H04:003 منتسب کنیم؛ هر دو به‌عنوان نامزد شاهددار ثبت می‌شوند و سطح رابطه در Overlay Package باقی می‌ماند. بنابراین این مورد یک محدودیت معنایی واقعی است، نه صرفاً کمبود برچسب. این موارد با Scope، اثر اجرایی و Locator ثبت شده‌اند و مانع ادعای تکمیل معنایی Stage 4 هستند.
