# گزارش ممیزی Stage 4 بر مبنای HEAD فعلی PR #256

## مبنای بررسی و وضعیت PR

این گزارش در چند نوبت بازبینی Stage 4 به‌روزرسانی شده است؛ شناسه‌های تاریخی هر نوبت در Snapshotها و توضیحات PR آمده‌اند. **یادداشت نسخه:** بخش‌های وضعیت جاریِ پیش از عنوان «الحاقیهٔ جاری: ممیزی روابط ۳۶ Package و قراردادهای C05A» Snapshot بازبینی پیشین‌اند؛ برای وضعیت فعلی رابطه‌ها، آن الحاقیه مرجع است. Snapshotهای عددی تاریخی حفظ شده‌اند. در نوبت جاری، HEAD هنگام شروع `99aaa11ec8b6c290c98a8d657e7398dac32804ef` بود. PR شمارهٔ ۲۵۶ باز، Draft، ادغام‌نشده و mergeable است. HEAD مبنا `main` در `c9e74532d4291e9ed1a7ddd3523ee84f09c940a2` است. Commitهای پیشین `c4ef91e47de27ccce387cabdf4a3e5bb9b07a698` و `3d4d596735474392ad1dd9cf98c7015d790ddbff` نتایج اعتبارسنجی و جداسازی Snapshot تاریخی/جاری را ثبت کرده بودند. این گزارش و relationهای بعدی در شاخهٔ همان PR منتشر می‌شوند؛ وضعیت PR همچنان Open، Draft، ادغام‌نشده و mergeable باقی می‌ماند.

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

برای هر ۶۰ رابطهٔ Package-level اولیه، Plan locatorهای handoff/dependency، مقصدهای Package، وضعیت تخصیص Task و اثر اجرایی دوباره خوانده شد. Handoff:H05B:004 از Package به سه Subtask دقیق ارتقا یافت (پایین‌تر مستند شده است). هرجا منبع Task را فقط pending یا آینده معرفی می‌کند، endpoint به Task ارتقا نیافت. این گزاره Snapshot پیش از بازبینی ۳۶ Package است؛ نتیجهٔ بازبینی جاری، شمارش شناسه‌ها و روش بررسی را در الحاقیهٔ انتهایی ثبت می‌کند.


### Handoff:H04:003

Plan در Locator :4059–4060، H04:001 را برای قرارداد Entitlement متعلق به C04 و پذیرش برنامه‌ریزی A01/A02 ذکر می‌کند؛ :7611/:7625 و :7745/:7768 ارتباط آن با REQ و Taskهای دقیق مصرف‌کننده را تأیید می‌کنند. بنابراین دو ردیف C04→A01:003 و C04→A02:003 در Mapping `CONFIRMED`/`RESOLVED` و `CONTRACT_ORDER` هستند. H04:003 در :4049 جداست و تخصیص مقصدش باز می‌ماند؛ هیچ alias یا رابطهٔ هم‌ارزی ثبت نشده است.

برای R01–R10، Plan مصرف‌کنندهٔ بالقوهٔ آینده را بیان می‌کند و تخصیص واقعی هر مصرف به بسته/Task مشخص را باز می‌گذارد. Package endpointها فقط Scope بالقوه‌اند؛ وضعیت `SOURCE_SCOPED`، اطمینان باز و اثر `IMPACT_ONLY` دارند. این محدودیت هنوز اثر واقعی بر تخصیص Task و زمان‌بندی اجرای هر مصرف‌کننده دارد و در Stage 4 به‌صورت باز ثبت شده است.


### Handoff:H05B:004

Plan:4559 صریحاً این handoff را برای A02:REQ:013–015 می‌پذیرد و می‌گوید A01 مصرف‌کنندهٔ این handoff نیست. Crosswalk مستقیم Plan، REQ:013 را به TASK:ASSISTANT:A02:001.S04 در :7777 و ردیف Requirement را در :7751، REQ:014 را به TASK:ASSISTANT:A02:003.S04 در :7785 و :7752، و REQ:015 را به TASK:ASSISTANT:A02:002.S04 در :7781 و :7753 وصل می‌کند. REL-STAGE4-028 Package-level با سه ردیف مستقل Subtask-level جایگزین شد؛ جهت C05B→A02 حفظ شده و هر سه با `POLICY_IMPACT` ثبت شده‌اند. برای این handoff HARD_ORDER استنباط نشده است. Replay این سه endpoint و Locatorها را جداگانه اعتبارسنجی می‌کند.

### DEP:C05A:003 و DEP:C05A:004

در DEP:C05A:003، Plan:4068 مقصد C04 را برای `TASK:CORE:C04:001` و `TASK:CORE:C04:006` دقیق می‌کند؛ این دو Task در REL-STAGE4-057/058 با provider در سطح Package:C05A ثبت شده‌اند و شاهد :4262 به همان ردیف‌ها افزوده شده تا رابطهٔ تکراری C04→C05A حذف شود. این وضعیت در Snapshot قبلی ثبت شده بود. الحاقیهٔ جاری provider را به `TASK:CORE:C05A:003` و C06/A01 را به Taskهای دارای crosswalk مستقیم ارتقا می‌دهد؛ A02 و R01–R10 در DEP003 همچنان Package-scoped می‌مانند.

DEP:C05A:004 چهار مصرف‌کننده را نام می‌برد. برای A01 و A02، Taskهای `TASK:ASSISTANT:A01:001` و `TASK:ASSISTANT:A02:001` در Plan:7623 و :7766 مصرف route/capability را مشخص می‌کنند؛ این وضعیت در Snapshot قبلی ثبت شده بود. الحاقیهٔ جاری provider را `TASK:CORE:C05A:004` می‌کند و A01/A02/C06 را Task-level می‌سازد؛ R02 در DEP004 و Handoff route در سطح Package باقی است. Handoff:C05A:006 جداست و مقصد Task آن همچنان pending است. ارجاع نامرتبط Handoff:H04:001 از این ردیف‌های C05A حذف شده است.

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

محدودیت‌های واقعی ثبت‌شده در Snapshot قبلی (و مواردی که همچنان برقرارند): R01–R10 در H04:003 فقط مصرف‌کنندگان آینده‌اند؛ DEP:C05A:003/004 اکنون provider و consumerهای قابل‌اثبات Task-level دارد؛ R02 در DEP:C05A:004 همچنان Package-only است؛ دو مرجع ویژه، 0291 و 0298، Package-only هستند؛ Handoff:H04:001 برای قرارداد Entitlement C04 به Taskهای A01/A02 با شاهد مستقیم تعیین تکلیف شده و H04:003 برای مقصدهای آینده همچنان جداگانه باز است. این‌ها به‌عنوان محدودیت Stage 4 ثبت شده‌اند و به Phase 5 منتقل نشده‌اند. دو مورد دارای اثر `BLOCKED_BY_DECISION` نیز تا تصمیم محصولی باز، ترتیب اجرایی نمی‌سازند. این محدودیت‌ها مانع ادعای تکمیل معنایی کامل هستند.


## تکملهٔ تطبیق تصمیم‌های باز با Task

شش مورد از هشت مرجع بازبینی‌شده به Task یا چند Taskِ دارای شاهد مستقیم در Plan/Task Graph scope شده‌اند: `AO:BP-TR-033-06:02` به C01:011 و A05:001؛ `AO:BP-TR-033-11:02` به C01:011؛ `AO:BP-TR-027-04:06` به C01:011 و A01:003/A02:003/A03:002/A03:003/A06:002؛ `AO:WL-C-0612:02` به C07:002؛ `AO:BP-C-0294:01` به A06:002؛ و `AO:BP-C-0300:01` به A01:002/C04:001/C05A:001/C05B:001. برای چهار مرجع ویژه، Replay این Task scopes و چهار مورد Package-only را به‌صورت صریح کنترل می‌کند.

`AO:BP-C-0291:01` و `AO:BP-C-0298:01` در سطح Package باقی مانده‌اند: Plan در مورد اول امکان‌سنجی/economics معماری محل اجرا را به Task اجرایی تخصیص نمی‌دهد؛ مورد دوم سازگاری متقابل چند مؤلفه را می‌پرسد، نه اجرای یک Task مستقل. نگاشت Task حدسی ایجاد نشده است. برای `AO:WL-C-0612:02`، تصمیم مرجع از Wallet W:423 و Plan:4932/:4980 برابر `OPEN:C08:04` است و AO دقیقاً در C07:002 قرار دارد (Plan:4829). `C13A-R13` در metadata گراف immutable به‌اشتباه به همین AO الصاق شده و در Plan:5875 به تصمیم متفاوت حسابداری/درآمد اشاره می‌کند. Mapping اکنون شناسهٔ مرجع و منشأ آن را صریح ثبت و خطای metadata گراف را جداگانه علامت می‌زند؛ گراف تغییر نکرده و تصمیم OPEN باقی است.

هر ۱۳۴ تصمیم همچنان `OPEN` و `BLOCKED` است. Scope جاری: ۱۲۳ `TASK`، ۹ `MULTI_TASK` و ۲ `PACKAGE`. هیچ گراف immutable یا وضعیت تصمیم محصولی تغییر نکرده است.


## الحاقیهٔ جاری: ممیزی روابط ۳۶ Package و قراردادهای C05A

این الحاقیه وضعیت واقعی شاخه در شروع این بازبینی (`167adb8b1a0f2f92400bd7c426ed573c4a3ab56b`) را پوشش می‌دهد؛ گراف‌های immutable و اسناد مرجع دست‌نخورده‌اند. فایل Mapping پس از این الحاقیه به‌روزرسانی شده است.

### قراردادهای C05A

| قرارداد | ارائه‌دهنده | مصرف‌کننده‌های Task-level تأییدشده | مصرف‌کنندهٔ Package-only | اثر اجرا |
|---|---|---|---|---|
| `DEP:C05A:003`، Catalog read API | `TASK:CORE:C05A:003`؛ Subtaskهای `.S01` projection/version، `.S02` خطا/فیلتر/scope، `.S03` دسترسی و منع جدول مستقیم | `TASK:CORE:C04:001`، `TASK:CORE:C04:006`، `TASK:CORE:C06:001`، `TASK:ASSISTANT:A01:002` | A02 و R01–R10 به‌صورت مصرف‌کنندهٔ آینده/Package scope؛ Task دقیق برای Adviserهای R و workflow A02 در این DEP تعیین نشده است | قرارداد نسخه‌دار باید پیش از پیاده‌سازی مصرف‌کننده تثبیت شود. مانع طراحی entitlement نیست؛ نبود contract مانع ادعای دسترسی خدمت و تکمیل consumer integration است. این DEP به‌تنهایی release را مسدود نمی‌کند؛ گیت فعال‌سازی C04 مستقل است. |
| `DEP:C05A:004`، route/context/result | `TASK:CORE:C05A:004`؛ Subtaskهای `.S01` ورود/تأیید حوزه، `.S02` route result/error، `.S03` backend validation/permission | `TASK:ASSISTANT:A01:001`، `TASK:ASSISTANT:A02:001`، `TASK:CORE:C06:001` | `PACKAGE:R02`؛ Plan مصرف R02 را نام می‌برد اما Task مقصد مشخصی نمی‌دهد | قرارداد route باید قبل از consumer integration/dispatch آماده باشد. Plan اجرای خدمت مقصد را به این قرارداد یکی نمی‌کند؛ نبود آن مانع تکمیل مصرف route و integration است، اما شروع تحلیل/طرح Taskهای مستقل یا release عمومی را به‌تنهایی نمی‌بندد. |
| `Handoff:C05A:006`، workflow parent/child | `TASK:CORE:C05A:005` در معنای قرارداد؛ سه Subtask قرارداد ارجاع/مالکیت/وضعیت را می‌سازند | Package A02 در Handoff | Task دقیق A02 در خود Handoff به‌صراحت pending allocation است؛ هرچند Task A02:001 owner target و parent/child را می‌پوشاند، اتصال مستقیم Handoff به آن Task در منبع تخصیص نیافته و در Overlay حدس زده نشد | A02 lifecycle بعد از ارجاع معتبر است؛ پیش از اجرای workflow قرارداد مقصد باید پذیرفته شود. این مورد همچنان SOURCE_SCOPED و مانع کامل‌شدن Task-level handoff/زمان‌بندی دقیق آن است. |

مبنای Task provider در Plan:4206–4208 و زیرکارهای همان ردیف؛ تعریف/جهت دو DEP در Plan:4262–4263؛ Taskهای مصرف‌کننده در Plan:3890،3973،4710،7623–7624،7766؛ crosswalk route در Plan:7595. قراردادهای C05A:003 و :004 هرکدام از سه Subtask مکمل تشکیل می‌شوند؛ هیچ Subtask منفردی به‌عنوان کل provider به consumer خاص وصل نشده است.

R02 برای `DEP:C05A:004` و `Handoff:C05A:004` در سطح Package باقی است: Plan:4263 و :7595 R02 را نام می‌برند اما crosswalk به R02 Task/Subtask نمی‌دهند. این محدودیت واقعی است؛ مقصد «احتمالی» جای endpoint دقیق نگرفته و رابطه، ترتیب Task-level یا ایمنی موازی را اثبات نمی‌کند.

### روابط جدید کشف‌شده در Plan

بازخوانی جدول Dependency در C05B و مقایسه با Task Graph و Overlay، سه رابطهٔ صریح Task-level را پیدا کرد که قبلاً در هیچ‌کدام از آن دو ثبت نشده بودند. هر سه در Plan:4554 آمده‌اند و ورودی/مالکیت در Task C05B:005، Plan:4543، تأیید می‌شود:

| شناسهٔ Overlay | مصرف‌کننده → پیش‌نیاز | نوع / اثر | معنای اجرایی |
|---|---|---|---|
| `REL-STAGE4-097` | `TASK:CORE:C05B:005` → `TASK:CORE:C05B:003` | `depends_on` / `HARD_ORDER` | Snapshot معتبر باید پیش از اجرای توصیه‌گر فراهم باشد. |
| `REL-STAGE4-098` | `TASK:CORE:C05B:005` → `TASK:CORE:C05B:004` | `requires_contract` / `CONTRACT_ORDER` | قرارداد خواندن نسخه‌دار محصول برای consumer لازم است. |
| `REL-STAGE4-099` | `TASK:CORE:C05B:005` → `TASK:CORE:C01:004` | `requires_contract` / `CONTRACT_ORDER` | منطق قطعی/scorer و معناشناسی golden در C01 حفظ و مصرف می‌شود. |

این‌ها فقط در سطح Task ثبت شدند؛ Task/subtask دقیق‌تر برای این روابط در متن Dependency نیست. فهرست مشترک Taskها در Wallet scenario crosswalk به‌تنهایی برای استنتاج جهت وابستگی کافی تلقی نشد.

### روابط موجود که دقیق‌تر شدند

- `REL-STAGE4-057/058`: provider از Package:C05A به `TASK:CORE:C05A:003` دقیق شد؛ consumerهای C04:001 و C04:006 در Plan:4068 آمده‌اند.
- `REL-STAGE4-063`: `TASK:CORE:C06:001` به‌عنوان consumer قرارداد Catalog و `TASK:CORE:C05A:003` به‌عنوان provider ثبت شد.
- `REL-STAGE4-064-A01`: consumer به `TASK:ASSISTANT:A01:002` و provider به `TASK:CORE:C05A:003` دقیق شد؛ A02 و R01–R10 package-scoped ماندند.
- `REL-STAGE4-066/067/068`: consumerهای A01:001، A02:001 و C06:001 به provider دقیق `TASK:CORE:C05A:004` متصل شدند.
- `REL-STAGE4-016`: Catalog projection handoff از C05A:003 به C06:001 دقیق شد.
- `REL-STAGE4-070/071/072`: route handoff از C05A:004 به A01:001، A02:001 و C06:001 دقیق شد. نوع اثر قبلی حفظ شد و به HARD_ORDER ارتقا نیافت.
- `REL-STAGE4-065` و `REL-STAGE4-069`: R02 همچنان Package-level باقی است؛ منبع مقصد Task مشخص نمی‌کند.
- `REL-STAGE4-073`: Handoff parent/child C05A→A02 جدا از route باقی است؛ تخصیص Task در Handoff:C05A:006 pending است.

### پوشش متن ۳۶ Package

روش شمارش: ۳۶ Package از locator کانونی گراف Task گرفته شد؛ همهٔ ۶۹۶ Node گراف (۳۶ Package، ۱۸۹ Task، ۴۷۱ Subtask) با Plan locatorهای ثبت‌شده مرور شدند. شناسه‌های Story، AC و Test از span هر Package نرمال و یکتا شمرده شدند؛ نام‌گذاری AC/TEST در قالب‌های قدیمی و `PKG-AC/TD` یک‌بار شمرده شده است. صفر به معنی آن است که در span کانونی آن Package شناسهٔ مستقل از نوع خواسته‌شده تعریف نشده؛ به معنی نبود معیار مشترک یا نبود ارجاع در package دیگر نیست. ستون روابط جدید بر اساس محل مصرف‌کننده آمده است.

| Package | Story | Task | Subtask | AC | Test | رابطهٔ جدید |
|---|---:|---:|---:|---:|---:|---:|
| C01 | 0 | 13 | 42 | 40 | 40 | 0 |
| C02 | 1 | 5 | 20 | 81 | 81 | 0 |
| C03 | 0 | 0 | 0 | 0 | 22 | 0 |
| C04 | 4 | 8 | 2 | 60 | 60 | 0 |
| C05A | 4 | 5 | 15 | 35 | 35 | 0 |
| C05B | 3 | 5 | 12 | 15 | 15 | 3 |
| C06 | 0 | 6 | 0 | 9 | 9 | 0 |
| C07 | 0 | 5 | 0 | 19 | 19 | 0 |
| C08 | 0 | 5 | 0 | 14 | 14 | 0 |
| C09 | 0 | 5 | 0 | 17 | 17 | 0 |
| C10 | 0 | 5 | 0 | 12 | 12 | 0 |
| C11A | 0 | 5 | 0 | 9 | 9 | 0 |
| C11B | 0 | 5 | 16 | 10 | 10 | 0 |
| C12A | 0 | 5 | 16 | 13 | 13 | 0 |
| C12B | 0 | 5 | 15 | 11 | 11 | 0 |
| C13A | 0 | 5 | 15 | 14 | 14 | 0 |
| C13B | 8 | 8 | 24 | 16 | 16 | 0 |
| C14 | 6 | 8 | 24 | 16 | 16 | 0 |
| R01 | 4 | 5 | 15 | 10 | 10 | 0 |
| R02 | 4 | 5 | 15 | 10 | 10 | 0 |
| R03 | 0 | 5 | 16 | 11 | 11 | 0 |
| R04 | 0 | 5 | 15 | 10 | 10 | 0 |
| R05 | 0 | 5 | 15 | 10 | 10 | 0 |
| R06 | 0 | 6 | 18 | 12 | 12 | 0 |
| R07 | 0 | 4 | 12 | 8 | 8 | 0 |
| R08 | 0 | 5 | 16 | 9 | 9 | 0 |
| R09 | 0 | 4 | 12 | 8 | 8 | 0 |
| R10 | 0 | 4 | 12 | 8 | 8 | 0 |
| A01 | 0 | 4 | 13 | 11 | 11 | 0 |
| A02 | 0 | 5 | 18 | 15 | 15 | 0 |
| A03 | 0 | 4 | 13 | 12 | 12 | 0 |
| A04 | 0 | 4 | 13 | 13 | 13 | 0 |
| A05 | 0 | 5 | 16 | 12 | 12 | 0 |
| A06 | 0 | 5 | 18 | 14 | 14 | 0 |
| A07 | 0 | 5 | 15 | 10 | 10 | 0 |
| A08 | 0 | 6 | 18 | 14 | 14 | 0 |
| **جمع** | **34** | **189** | **471** | **588** | **610** | **3** |

تماماً نبودن رابطه برای بعضی cross-referenceهای AC/Test به معنی parallel-safe بودن نیست. تنها ترتیب سخت تازه، C05B:005 پس از C05B:003 است. دو رابطهٔ قراردادی C05B و روابط C05A اثر قراردادی دارند و اجرای integration به آماده‌بودن قرارداد وابسته است، نه لزوماً شروع طراحی/پیاده‌سازی مستقل. Overlay جاری اکنون ۹۹ رابطه دارد: ۱۸ `depends_on`، ۳۰ `requires_contract`، ۵۰ `handoff` و یک `requires_policy`؛ Scope آن ۴۲ Task، ۳ Subtask و ۵۴ Package است. `parallel_safe` assertion=۰. بررسی Replay روی combined hard-order graph نتیجهٔ چرخه را ثبت می‌کند.

### حدود این بازبینی

این بازبینی روابط explicit و crosswalkهای مستقیم Story/Task/AC/Test را در تمام package spans پوشش داد، و همهٔ Task/Subtask Plan locatorها را اسکن کرد. یال «هم‌ذکری» میان چند Task در سناریوی مشترک، بدون واژه/جهت provider-consumer/precondition در منبع، به dependency تبدیل نشد. R02 و A02 در مواردی که Plan فقط Package را تخصیص می‌دهد package-scoped مانده‌اند. تصمیم‌های محصولی همچنان ۱۳۴ `OPEN` هستند؛ Stage 4 روابط فنی قابل‌اثبات را ثبت می‌کند و هیچ تصمیم محصولی را حل‌شده نمی‌خواند.

## ثبت اعتبارسنجی و CI انتشار این ممیزی

محتوای Mapping و Replay در Commit `19f3530546d836ab038e27795996445e5fa9c755` منتشر شد. روی همان محتوا، `replay_stage4.py --check-only` دو بار اجرا و خروجی‌ها byte-for-byte مقایسه شدند؛ هر دو PASS با Projection SHA `44e4970d7a40853d19dfd8b758466a04f0e8c19389f060d6b135869fab2dd5f5`، ۹۹ رابطه، ۱۳۴ تصمیم باز و بدون چرخه در ترتیب سخت. `build_and_validate.py --check-only` نیز PASS شد و هر ۲۹ کنترل داخلی خطا نداشتند. سه SHA گراف immutable با Blobهای GitHub تطبیق داشتند.

چهار Workflow مربوط به Commit `19f3530546d836ab038e27795996445e5fa9c755` همگی با conclusion کلی `success` خاتمه یافتند: Quality gates (run `45629931930`)، Security SAST/SCA and secret gates (`45629932009`)، Container build contract smoke (`45629932034`) و US-13 frozen frontend baseline evidence (`45629932205`). این نتیجه فقط به Workflowهای کلی مربوط است: Jobهای Migration و browser/API، ساخت image، route evidence، Quality gates تخصصی، SAST/SCA و بخشی از بررسی‌های اجرایی به‌دلیل docs-only بودن تغییرها `skipped` شدند و PASS اجرایی محسوب نمی‌شوند. Jobهای سبک مستندات موفق بودند و Secret scan در Workflow امنیتی اجرا و PASS شد.

این بند فقط نتیجهٔ اجرای ثبت‌شده برای Commit بالا را توصیف می‌کند؛ وضعیت Workflowهای هر Commit بعدی باید با SHA همان Commit جداگانه خوانده شود.
