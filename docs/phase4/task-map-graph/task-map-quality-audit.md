# گزارش ممیزی Stage 4 بر مبنای HEAD فعلی PR #256

## مبنای بررسی و وضعیت PR

مبنای این بازبینی، HEAD واقعی PR در شروع آن، `271d4330f5df30d911f012e6fb1e1fa6c5a2d72d`، بود؛ relationها و گزارش در همان شاخه بر اساس منابع ثابت Plan و Task بازنگری شدند. PR شمارهٔ ۲۵۶ باز، Draft، ادغام‌نشده و در وضعیت mergeable است. HEAD مبنا `main` در `c9e74532d4291e9ed1a7ddd3523ee84f09c940a2` است. Commitهای پیشین `c4ef91e47de27ccce387cabdf4a3e5bb9b07a698` و `3d4d596735474392ad1dd9cf98c7015d790ddbff` نتایج اعتبارسنجی و جداسازی Snapshot تاریخی/جاری را ثبت کرده بودند. این گزارش و relationهای بعدی در شاخهٔ همان PR منتشر می‌شوند؛ وضعیت PR همچنان Open، Draft، ادغام‌نشده و mergeable باقی می‌ماند.

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

Relation Overlay جاری شامل ۹۴ رابطه است: ۴۸ `handoff`، ۱۷ `depends_on`، ۲۸ `requires_contract` و ۱ `requires_policy`. همهٔ ردیف‌ها Source Locator و Plan Locator معتبر دارند. در Overlay، ۳۴ رابطه به Task و ۶۰ رابطه در سطح Package هستند. هیچ رابطهٔ `parallel_safe` اثبات یا ثبت نشده است.

اثر اجرایی روابط ثبت‌شده: ۱۲ `HARD_ORDER`، ۲۶ `CONTRACT_ORDER`، ۳۱ `POLICY_IMPACT`، ۲۲ `IMPACT_ONLY` و ۳ `BLOCKED_BY_DECISION`. در ترکیب گراف و Overlay هیچ چرخهٔ ترتیب سخت وجود ندارد. `SOFT_ORDER` در Overlay به‌عنوان اثر مستقل ثبت نشده؛ روابطی که منبع آن‌ها تقدم سخت نمی‌دهد به `IMPACT_ONLY` یا نوع اثر صریح خود محدودند و به ترتیب قطعی تبدیل نشده‌اند.


### وضعیت relationهای Package-level و دامنهٔ ممیزی

در Mapping جاری دقیقاً ۶۰ ردیف Overlay در Scope سطح Package وجود دارد: ۳۲ ردیف `PACKAGE_ONLY` و ۲۸ ردیف `SOURCE_SCOPED`. در ۶۰ ردیف Package-level، اثرها ۲۹ `POLICY_IMPACT`، ۲۲ `IMPACT_ONLY`، ۶ `CONTRACT_ORDER`، یک `HARD_ORDER` و دو `BLOCKED_BY_DECISION` هستند. این‌ها رابطه‌های قطعی Task-level محسوب نمی‌شوند. برای ردیف‌های `PACKAGE_ONLY`، endpoint و اثر اجرایی در سطح Package ثبت شده‌اند؛ ردیف‌های `SOURCE_SCOPED` دامنهٔ صریح منبع را حفظ می‌کنند. موارد دارای `BLOCKED_BY_DECISION` عبارت‌اند از `REL-STAGE4-014` برای `DECISION:C05A:001` و `REL-STAGE4-034` برای `OPEN:C08:04`.

یک تناقض crosswalk مانع تعیین هویت قطعی Handoff entitlement است: Plan:4049، H04:003 را با مقصد Task نامشخص تعریف می‌کند؛ :4060 پذیرش برنامه‌ریزی A01/A02 را می‌گوید؛ اما Taskهای مصرف‌کننده در :7611/:7625 و :7745/:7768 به `Handoff:H04:001` ارجاع می‌دهند. تعریف canonical برای H04:001 در فهرست handoffهای Plan پیدا نشد. Mapping اکنون A01:003 و A02:003 را برای مصرف entitlement با وضعیت `PARTIALLY_RESOLVED` و `AMBIGUOUS` ثبت می‌کند؛ آن‌ها را به H04:003 نسبت نمی‌دهد. روابط H04:003 برای A01/A02 و R01–R10 همچنان Package-scoped هستند؛ برای R01–R10 فقط مصرف‌کنندهٔ بالقوهٔ آینده ثبت شده و Task مقصد وجود ندارد.

شمارش Overlay از Blob جاری بازتولید شده است؛ بازبینی مستقل همهٔ Taskهای candidate در ۳۶ Package با AC/Test هنوز کامل نیست و نباید از این شمارش به‌عنوان اثبات ممیزی exhaustive استفاده کرد.


### Handoff:H04:003

Plan در Locator `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:4049` صریحاً تخصیص Task مقصد H04:003 را باز می‌گذارد. Locatorهای :4053 و :4060 پذیرش برنامه‌ریزی A01/A02 را ثبت می‌کنند. برای مصرف entitlement، Taskهای A01:003 و A02:003 در منابع Task به Handoff:H04:001 ارجاع دارند؛ چون H04:001 در فهرست handoffها تعریف نشده، دو ردیف C04→Task با وضعیت `AMBIGUOUS`/`PARTIALLY_RESOLVED` ثبت شده‌اند، اما به H04:003 نسبت داده نشده‌اند. روابط جداگانهٔ H04:003 برای A01/A02 در Package Scope و `SOURCE_SCOPED` باقی‌اند تا crosswalk رسمی روشن شود.

برای R01–R10، Plan مصرف‌کنندهٔ بالقوهٔ آینده را بیان می‌کند و تخصیص واقعی هر مصرف به بسته/Task مشخص را باز می‌گذارد. Package endpointها فقط Scope بالقوه‌اند؛ وضعیت `SOURCE_SCOPED`، اطمینان باز و اثر `IMPACT_ONLY` دارند. این محدودیت هنوز اثر واقعی بر تخصیص Task و زمان‌بندی اجرای هر مصرف‌کننده دارد و در Stage 4 به‌صورت باز ثبت شده است.

### DEP:C05A:003 و DEP:C05A:004

در DEP:C05A:003، Plan:4068 مقصد C04 را برای `TASK:CORE:C04:001` و `TASK:CORE:C04:006` دقیق می‌کند؛ این دو Task در REL-STAGE4-057/058 با provider در سطح Package:C05A ثبت شده‌اند و شاهد :4262 به همان ردیف‌ها افزوده شده تا رابطهٔ تکراری C04→C05A حذف شود. Task دقیق provider در C05A هنوز تعیین نشده است. C06 در Package scope باقی می‌ماند؛ A01/A02 و R01–R10 در :4262 صرفاً مصرف‌کنندگان آینده‌اند و `SOURCE_SCOPED`/`IMPACT_ONLY` می‌مانند.

DEP:C05A:004 چهار مصرف‌کننده را نام می‌برد. برای A01 و A02، Taskهای `TASK:ASSISTANT:A01:001` و `TASK:ASSISTANT:A02:001` در Plan:7623 و :7766 مصرف route/capability را مشخص می‌کنند؛ دو relation به Task consumer دقیق ارتقا یافته‌اند و به‌علت نامشخص‌بودن Task provider در C05A، `PARTIALLY_RESOLVED` هستند. R02 و C06 در :4263 Package-level باقی مانده‌اند. Handoff:C05A:004 برای A01/A02 نیز به Taskهای مصرف‌کنندهٔ یادشده متصل شده است؛ Handoff:C05A:006 یک رابطهٔ جداگانه با مقصد A02 در سطح Package باقی می‌ماند چون :4272 تخصیص Task را pending می‌داند. ارجاع نامرتبط Handoff:H04:001 از این ردیف‌های C05A حذف شده است.

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

دو اجرای `replay_stage4.py --check-only` روی Candidate Tree ساخته‌شده از HEAD `271d4330f5df30d911f012e6fb1e1fa6c5a2d72d` PASS شدند و خروجی JSON byte-for-byte یکسان بود. SHA پروجکشن معنایی هر دو `af52dcfa18ee50e345adfabf8fd060b28dfa3f0497cd0c4610fd9a5a5d8ef1bc` است؛ هر دو اجرای Replay صفر چرخه و ثابت‌بودن سه گراف immutable را تأیید کردند. اجرای `docs/audits/phase2-source-coverage/build_and_validate.py --check-only` روی همین Candidate Tree PASS شد؛ هر ۲۹ کنترل داخلی PASS و شمارش Candidate/Obligation با Ledger تطبیق داشت. چهار Workflow منتشرشدهٔ Commit والد `271d4330f5df30d911f012e6fb1e1fa6c5a2d72d` با نتیجهٔ `success` بودند: Security SAST/SCA/secret gates (run 45586092351)، US-13 frozen frontend baseline evidence (run 45586092376)، Quality gates (run 45586093244)، Container build contract smoke (run 45586092362). این‌ها نتایج والد هستند و جای نتیجهٔ Workflow روی Commit نهایی را نمی‌گیرند؛ وضعیت HEAD نهایی باید از GitHub Actions جداگانه خوانده شود.

## تفاوت با گزارش‌های قدیمی و محدودیت‌های باقی‌مانده

Snapshotهای تاریخی ۱۵/۲۴/۶۵۷، ۱۲۶ BLOCKED/۸ UNMAPPED و ۷۲ Overlay دیگر وضعیت جاری نیستند. وضعیت فعلی ۱۵/۲۷/۶۵۴، ۱۳۴ BLOCKED/۰ UNMAPPED و ۹۴ Overlay است. سه تغییر Mapping ناشی از بازبینی کد R10 است؛ ۸ تصمیم پیش‌تر UNMAPPED با اتصال شاهددار به Scope موجود به BLOCKED تغییر کردند، در حالی‌که تصمیم محصولی هر ۱۳۴ مورد OPEN باقی ماند. شمار رابطه‌ها ۹۴ باقی ماند اما ۲۹ requires_contract به ۲۸ کاهش یافت چون C04→C05A تکراری در دو Task edge موجود ادغام شد؛ در مقابل یک Handoff:C05A:006 مستقل به‌صورت PACKAGE-scoped ثبت شد و رابطه‌های A01/A02 در DEP:C05A:004 و handoff route به Task مصرف‌کننده ارتقا یافتند.

محدودیت‌های واقعی فعلی شامل Taskهای تخصیص‌نیافتهٔ R01–R10 در H04:003، Taskهای provider در C05A برای بعضی قراردادهای C05A:003/004، مصرف‌کننده‌های R02/C06 در چند relation و چهار مرجع ویژهٔ Package-scoped است. شناسهٔ Handoff:H04:001 در منابع Task تعریف نشده و crosswalk آن با H04:003 باز مانده است. افزون بر این، ممیزی مستقل و exhaustive همهٔ ۶۶ رابطهٔ Package-level در برابر تمام Task story/AC/Testها و تفکیک lifecycle اثر هر یک از ۱۳۴ تصمیم هنوز انجام نشده است. این شکاف‌ها مانع ادعای تکمیل معنایی Stage 4 هستند؛ ۲۹ کنترل ساختاری و چهار Workflow موفق جایگزین آن بررسی معنایی نیستند.
