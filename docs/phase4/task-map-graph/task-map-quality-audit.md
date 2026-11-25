# گزارش ممیزی Stage 4 بر مبنای HEAD فعلی PR #256

## مبنای بررسی و وضعیت PR

این گزارش در چند نوبت بازبینی Stage 4 به‌روزرسانی شده است؛ شناسه‌های تاریخی هر نوبت در Snapshotها و توضیحات PR آمده‌اند. در نوبت جاری، HEAD هنگام شروع `99aaa11ec8b6c290c98a8d657e7398dac32804ef` بود. PR شمارهٔ ۲۵۶ باز، Draft، ادغام‌نشده و mergeable است. HEAD مبنا `main` در `c9e74532d4291e9ed1a7ddd3523ee84f09c940a2` است. Commitهای پیشین `c4ef91e47de27ccce387cabdf4a3e5bb9b07a698` و `3d4d596735474392ad1dd9cf98c7015d790ddbff` نتایج اعتبارسنجی و جداسازی Snapshot تاریخی/جاری را ثبت کرده بودند. این گزارش و relationهای بعدی در شاخهٔ همان PR منتشر می‌شوند؛ وضعیت PR همچنان Open، Draft، ادغام‌نشده و mergeable باقی می‌ماند.

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

Relation Overlay جاری شامل ۹۶ رابطه است: ۵۰ `handoff`، ۱۷ `depends_on`، ۲۸ `requires_contract` و ۱ `requires_policy`. همهٔ ردیف‌ها Source Locator و Plan Locator معتبر دارند. در Overlay، ۳۴ رابطه در سطح Task، سه رابطه در سطح Subtask و ۵۹ رابطه در سطح Package هستند. هیچ رابطهٔ `parallel_safe` اثبات یا ثبت نشده است.

اثر اجرایی روابط ثبت‌شده: ۱۲ `HARD_ORDER`، ۲۶ `CONTRACT_ORDER`، ۳۳ `POLICY_IMPACT`، ۲۲ `IMPACT_ONLY` و ۳ `BLOCKED_BY_DECISION`. در ترکیب گراف و Overlay هیچ چرخهٔ ترتیب سخت وجود ندارد. `SOFT_ORDER` در Overlay به‌عنوان اثر مستقل ثبت نشده؛ روابطی که منبع آن‌ها تقدم سخت نمی‌دهد به `IMPACT_ONLY` یا نوع اثر صریح خود محدودند و به ترتیب قطعی تبدیل نشده‌اند.


### وضعیت relationهای Package-level و دامنهٔ ممیزی

در Mapping اصلاح‌شده ۵۹ رابطه در Scope سطح Package باقی مانده‌اند: ۵۷ مورد `SOURCE_SCOPED` و دو مورد با وضعیت `PACKAGE_ONLY` که اثرشان صریحاً `BLOCKED_BY_DECISION` است (`REL-STAGE4-014` و `REL-STAGE4-034`). هر ۵۹ مورد Package-level اکنون Locator، علت نبود Task/Subtask canonical در همان Locator، و یادداشت اثر بر ترتیب اجرا دارند. اثرهای Package-scope: ۲۸ `POLICY_IMPACT`، ۲۲ `IMPACT_ONLY`، ۶ `CONTRACT_ORDER`، یک `HARD_ORDER` و دو `BLOCKED_BY_DECISION`. هیچ‌کدام به‌عنوان Mapping کامل Task-level شمرده نمی‌شوند؛ بستهٔ مصرف‌کننده و جهت رابطه فقط تا سطحی ثبت شده که منبع مشخص می‌کند.

بازبینی تکمیلی منشأ Handoff نشان داد H04:001 در جدول Entitlement بخش C04 در Plan:4059–4060 به‌عنوان قرارداد C04 و پذیرش برنامه‌ریزی A01/A02 آمده است؛ الزامات A01:011/A02:007 و Taskهای A01:003/A02:003 نیز مصرف همین قرارداد را تصریح می‌کنند. Mapping اکنون دو رابطهٔ C04→Task را `CONFIRMED` و `RESOLVED` با اثر `CONTRACT_ORDER` ثبت می‌کند. H04:001 به H04:003 نسبت داده نشده است: H04:003 در :4049 رابطه‌ای جدا برای مصرف‌کنندگان آینده با تخصیص مقصد باز است؛ R01–R10 همچنان فقط Package-scoped و آینده‌نگرند.

برای هر ۶۰ رابطهٔ Package-level اولیه، Plan locatorهای handoff/dependency، مقصدهای Package، وضعیت تخصیص Task و اثر اجرایی دوباره خوانده شد. Handoff:H05B:004 از Package به سه Subtask دقیق ارتقا یافت (پایین‌تر مستند شده است). هرجا منبع Task را فقط pending یا آینده معرفی می‌کند، endpoint به Task ارتقا نیافت. بررسی exhaustively همهٔ Story/AC/Testهای ۳۶ Package برای کشف crosswalk دیگری که در Plan نیامده باشد، هنوز حد اثبات‌پذیر این بازبینی را دارد؛ بنابراین هیچ ادعای نبودن Task در همهٔ منابع مطرح نمی‌شود.


### Handoff:H04:003

Plan در Locator :4059–4060، H04:001 را برای قرارداد Entitlement متعلق به C04 و پذیرش برنامه‌ریزی A01/A02 ذکر می‌کند؛ :7611/:7625 و :7745/:7768 ارتباط آن با REQ و Taskهای دقیق مصرف‌کننده را تأیید می‌کنند. بنابراین دو ردیف C04→A01:003 و C04→A02:003 در Mapping `CONFIRMED`/`RESOLVED` و `CONTRACT_ORDER` هستند. H04:003 در :4049 جداست و تخصیص مقصدش باز می‌ماند؛ هیچ alias یا رابطهٔ هم‌ارزی ثبت نشده است.

برای R01–R10، Plan مصرف‌کنندهٔ بالقوهٔ آینده را بیان می‌کند و تخصیص واقعی هر مصرف به بسته/Task مشخص را باز می‌گذارد. Package endpointها فقط Scope بالقوه‌اند؛ وضعیت `SOURCE_SCOPED`، اطمینان باز و اثر `IMPACT_ONLY` دارند. این محدودیت هنوز اثر واقعی بر تخصیص Task و زمان‌بندی اجرای هر مصرف‌کننده دارد و در Stage 4 به‌صورت باز ثبت شده است.


### Handoff:H05B:004

Plan:4559 صریحاً این handoff را برای A02:REQ:013–015 می‌پذیرد و می‌گوید A01 مصرف‌کنندهٔ این handoff نیست. Crosswalk مستقیم Plan، REQ:013 را به TASK:ASSISTANT:A02:001.S04 در :7777 و ردیف Requirement را در :7751، REQ:014 را به TASK:ASSISTANT:A02:003.S04 در :7785 و :7752، و REQ:015 را به TASK:ASSISTANT:A02:002.S04 در :7781 و :7753 وصل می‌کند. REL-STAGE4-028 Package-level با سه ردیف مستقل Subtask-level جایگزین شد؛ جهت C05B→A02 حفظ شده و هر سه با `POLICY_IMPACT` ثبت شده‌اند. برای این handoff HARD_ORDER استنباط نشده است. Replay این سه endpoint و Locatorها را جداگانه اعتبارسنجی می‌کند.

### DEP:C05A:003 و DEP:C05A:004

در DEP:C05A:003، Plan:4068 مقصد C04 را برای `TASK:CORE:C04:001` و `TASK:CORE:C04:006` دقیق می‌کند؛ این دو Task در REL-STAGE4-057/058 با provider در سطح Package:C05A ثبت شده‌اند و شاهد :4262 به همان ردیف‌ها افزوده شده تا رابطهٔ تکراری C04→C05A حذف شود. Task دقیق provider در C05A هنوز تعیین نشده است. C06 در Package scope باقی می‌ماند؛ A01/A02 و R01–R10 در :4262 صرفاً مصرف‌کنندگان آینده‌اند و `SOURCE_SCOPED`/`IMPACT_ONLY` می‌مانند.

DEP:C05A:004 چهار مصرف‌کننده را نام می‌برد. برای A01 و A02، Taskهای `TASK:ASSISTANT:A01:001` و `TASK:ASSISTANT:A02:001` در Plan:7623 و :7766 مصرف route/capability را مشخص می‌کنند؛ دو relation به Task consumer دقیق ارتقا یافته‌اند و به‌علت نامشخص‌بودن Task provider در C05A، `PARTIALLY_RESOLVED` هستند. R02 و C06 در :4263 Package-level باقی مانده‌اند. Handoff:C05A:004 برای A01/A02 نیز به Taskهای مصرف‌کنندهٔ یادشده متصل شده است؛ Handoff:C05A:006 یک رابطهٔ جداگانه با مقصد A02 در سطح Package باقی می‌ماند چون :4272 تخصیص Task را pending می‌داند. ارجاع نامرتبط Handoff:H04:001 از این ردیف‌های C05A حذف شده است.

هیچ‌یک از این محدودیت‌های تخصیص به Phase 5 منتقل نشده است. Phase 5 صرفاً برای تبدیل گراف نهایی به تحویل‌دادنی‌های یک‌هفته‌ای است.

## ۱۳۴ تصمیم باز و ۲۲ مرجع ویژه

۱۳۴ شناسهٔ تصمیم باز، هرکدام دقیقاً یک بار وجود دارند. وضعیت محصولی همه `OPEN` و Mapping همه `BLOCKED` باقی است؛ در Snapshot جاری ۱۲۳ تصمیم `TASK`، ۹ تصمیم `MULTI_TASK` و ۲ تصمیم `PACKAGE` scope دارند. بازشماری Blob جاری نشان می‌دهد هر ۱۳۴ مورد Source Locator، Plan Locator، `decision_scope`، `affected_scope` و `execution_effect=BLOCKED_BY_DECISION` دارد؛ موردی با Plan Locator خالی یا اثر اجرایی خالی وجود ندارد. Locatorهای افزوده‌شده از `plan_refs` گره‌های canonical Task/Package گرفته شده‌اند. تصمیم باز به‌معنی حل محصولی یا تعیین مالک نهایی نیست.

هر ۲۲ مرجع ویژه بازبینی شده و همچنان OPEN/BLOCKED است. از چهار مرجع `AO:BP-C-0291:01`، `AO:BP-C-0294:01`، `AO:BP-C-0298:01` و `AO:BP-C-0300:01`، دو مورد 0291 و 0298 در سطح Package باقی‌اند چون پرسش‌های امکان‌سنجی معماری و سازگاری چندمؤلفه‌ای Task اجرایی مشخصی ندارند. 0294 به `TASK:ASSISTANT:A06:002` پیوند دارد: Plan:8273 مسئولیت حساب آزمون مجاز، اجرای غیرمخرب، ایزوله‌سازی نشست/دستگاه و شواهد امکان‌سنجی platform را صریحاً به این Task می‌دهد. 0300 به چهار Task کاتالوگ/Entitlement پیوند دارد: A01:002 (Plan:7624)، C04:001 (:3892)، C05A:001 (:4204) و C05B:001 (:4483). این‌ها دامنهٔ اثر تصمیم را مشخص می‌کنند؛ حساب و محیط آزمون یا فهرست‌های محصول/ابزار/پلن را موجود یا تصویب‌شده فرض نمی‌کنند.

## TASK:CORE:C13B:008

نام اصلی `/` در گراف immutable حفظ شده است. Overlay عنوان `مسیر مالی مجاز را بررسی کند` را با نوع `CONTEXT_DERIVED_LABEL` ثبت می‌کند. Plan در `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6006` شناسهٔ canonical Task و Story «C13B-S08 مسیر مالی مجاز را بررسی کند» را در یک ردیف می‌آورد؛ Locator و Blob SHA Plan در Mapping ثبت است. این برچسب از متن مستقیم Story گرفته شده و نام جدیدی برای گراف اصلی نیست.

## اتصال به کد موجود

۶۵۷ رکورد `NEW_IMPLEMENTATION` از Mapping بازتولید شده‌اند: ۳۰ `NON_CODE_REQUIREMENT`، ۶۲۴ `NO_CODE_EVIDENCE_FOUND`، ۳ `CODE_PARTIALLY_FOUND` و صفر `SEARCH_INCONCLUSIVE`. جست‌وجو در inventory پین‌شدهٔ کامل کد فعال شامل ۳۴۷ فایل انجام شده است؛ دامنه شامل کد برنامه، API/Route، مدل و مهاجرت، پیکربندی و قرارداد، تست و fixture، Docker و workflowها است. نتیجه به نبود Node در Graphify محدود نیست و نبود شاهد در این inventory را اثبات نبود کد در تمام نسخه‌ها نمی‌داند.

سه مورد Partial عبارت‌اند از `TASK:RAG:R10:001`، `TASK:RAG:R10:002` و `TASK:RAG:R10:003`. Locator فایل/خط، Blob SHA و نوع شاهد برای هرکدام در `stage4_code_search_audit.records` ثبت شده است. شواهد فعلی مسیر use case/scorer/API توصیه، مدل Snapshot/repository و scorer/partition را پوشش می‌دهد؛ adapter/قرارداد Adviser و رفتارهای اختصاصی باقی‌مانده هنوز کامل نیستند. Graphify تغییر نکرده و Node حدسی ساخته نشده است.

`NO_CODE_EVIDENCE_FOUND` یعنی در inventory فعال کد پین‌شدهٔ این بررسی شاهد مستقیم متناظر پیدا نشد؛ ادعای قطعی دربارهٔ نسخه‌های دیگر یا امکان استفادهٔ مجدد آینده نیست.

## Replay، کنترل‌های داخلی و Workflowها

Replay معنایی، اعتبار هویت‌ها و Locatorها، Scope تصمیم‌ها، Overlay، چرخه‌ها، جست‌وجوی کامل کد و Hash سه گراف را کنترل می‌کند. این ابزار قضاوت معنایی را از متن به‌شکل ماشینی تولید نمی‌کند؛ قضاوت‌های ثبت‌شده را با شواهد و پیکرهٔ ثابت بازبینی‌پذیر می‌سازد.

نتایج Commit `1e829e816eeaddec805381ea4b79b6dbace281bc` تاریخی‌اند و به HEAD جاری تعمیم داده نمی‌شوند. روی درخت محلی جاری، پس از به‌روزرسانی Projection برای Mapping، `replay_stage4.py --check-only` دو بار اجرا شد و هر دو PASS و byte-for-byte یکسان بودند؛ Projection SHA هر دو `b72d4e3f53565f13a2ce4d919146a3d865b902c41ed7a296e9d440bd53e841d2` است. `build_and_validate.py --check-only` نیز PASS شد: هر ۲۹ کنترل داخلی موفق بودند. چهار Workflow روی Commit قبلی `453c98abecea3883d9f7a6bcf8a42a8d8f914615` نتیجهٔ کلی `success` داشتند؛ Jobهای اختصاصی Quality gates، SAST/SCA، Container و US-13 به‌علت docs-only بودن تغییرها `skipped` ماندند و نباید PASS تلقی شوند. این نتایج تاریخی در این Snapshot به HEAD تازه تعمیم داده نمی‌شوند؛ شناسه و وضعیت اجرای HEAD جاری در توضیحات PR ثبت می‌شود.

## تفاوت با گزارش‌های قدیمی و محدودیت‌های باقی‌مانده

Snapshotهای تاریخی ۱۵/۲۴/۶۵۷، ۱۲۶ BLOCKED/۸ UNMAPPED و ۷۲ Overlay حفظ شده‌اند و وضعیت جاری نیستند. Snapshot پیش از این دور ۱۵/۲۷/۶۵۴، ۱۳۴ BLOCKED/۰ UNMAPPED و ۹۴ Overlay بود؛ وضعیت جاری پس از اصلاح H05B:004 همان شمارش Mapping و تصمیم‌ها با ۹۶ Overlay است. سه تغییر Mapping ناشی از بازبینی کد R10 است؛ ۸ تصمیم پیش‌تر UNMAPPED با اتصال شاهددار به Scope موجود به BLOCKED تغییر کردند، در حالی‌که تصمیم محصولی هر ۱۳۴ مورد OPEN باقی ماند. شمار رابطه‌ها از ۹۴ به ۹۶ افزایش یافت چون Handoff:H05B:004 به سه Subtask مستقیم A02 تفکیک شد؛ پیش از آن ۲۹ requires_contract به ۲۸ کاهش یافت چون C04→C05A تکراری در دو Task edge موجود ادغام شد؛ Handoff:C05A:006 مستقل به‌صورت Package-scoped حفظ شد و رابطه‌های A01/A02 در DEP:C05A:004 و Handoff:C05A:004 به Task مصرف‌کننده ارتقا یافتند.

محدودیت‌های واقعی باقی‌مانده: R01–R10 در H04:003 فقط مصرف‌کنندگان احتمالی آینده‌اند؛ C05A هنوز provider Task مشخصی برای بخشی از قراردادها ندارد؛ R02/C06 در روابط مربوط هنوز Task-level crosswalk ندارند؛ دو مرجع ویژه، 0291 و 0298، Package-only هستند؛ Handoff:H04:001 برای قرارداد Entitlement C04 به Taskهای A01/A02 با شاهد مستقیم تعیین تکلیف شده و H04:003 برای مقصدهای آینده همچنان جداگانه باز است. این‌ها به‌عنوان محدودیت Stage 4 ثبت شده‌اند و به Phase 5 منتقل نشده‌اند. دو مورد دارای اثر `BLOCKED_BY_DECISION` نیز تا تصمیم محصولی باز، ترتیب اجرایی نمی‌سازند. این محدودیت‌ها مانع ادعای تکمیل معنایی کامل هستند.


## تکملهٔ تطبیق تصمیم‌های باز با Task

شش مورد از هشت مرجع بازبینی‌شده به Task یا چند Taskِ دارای شاهد مستقیم در Plan/Task Graph scope شده‌اند: `AO:BP-TR-033-06:02` به C01:011 و A05:001؛ `AO:BP-TR-033-11:02` به C01:011؛ `AO:BP-TR-027-04:06` به C01:011 و A01:003/A02:003/A03:002/A03:003/A06:002؛ `AO:WL-C-0612:02` به C07:002؛ `AO:BP-C-0294:01` به A06:002؛ و `AO:BP-C-0300:01` به A01:002/C04:001/C05A:001/C05B:001. برای چهار مرجع ویژه، Replay این Task scopes و چهار مورد Package-only را به‌صورت صریح کنترل می‌کند.

`AO:BP-C-0291:01` و `AO:BP-C-0298:01` در سطح Package باقی مانده‌اند: Plan در مورد اول امکان‌سنجی/economics معماری محل اجرا را به Task اجرایی تخصیص نمی‌دهد؛ مورد دوم سازگاری متقابل چند مؤلفه را می‌پرسد، نه اجرای یک Task مستقل. نگاشت Task حدسی ایجاد نشده است. برای `AO:WL-C-0612:02`، تصمیم مرجع از Wallet W:423 و Plan:4932/:4980 برابر `OPEN:C08:04` است و AO دقیقاً در C07:002 قرار دارد (Plan:4829). `C13A-R13` در metadata گراف immutable به‌اشتباه به همین AO الصاق شده و در Plan:5875 به تصمیم متفاوت حسابداری/درآمد اشاره می‌کند. Mapping اکنون شناسهٔ مرجع و منشأ آن را صریح ثبت و خطای metadata گراف را جداگانه علامت می‌زند؛ گراف تغییر نکرده و تصمیم OPEN باقی است.

هر ۱۳۴ تصمیم همچنان `OPEN` و `BLOCKED` است. Scope جاری: ۱۲۳ `TASK`، ۹ `MULTI_TASK` و ۲ `PACKAGE`. هیچ گراف immutable یا وضعیت تصمیم محصولی تغییر نکرده است.
