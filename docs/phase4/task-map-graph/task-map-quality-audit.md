# گزارش نهایی تکمیل شکاف‌های Stage 4

## مبنای انتشار و جمع‌بندی
این نسخه، یافته‌ها و شمارش‌های گزارش پیشین را با وضعیت واقعی شاخه در آغاز این پیگیری تطبیق می‌دهد و جایگزین snapshot قبلی می‌کند. HEAD واقعی GitHub در آغاز کار `6ff792a1b696e9b97f283aa69be5f84454fc44f9` بود؛ HEADهای قبلی در گزارش‌های تاریخی‌اند. این گزارش فقط دربارهٔ شواهد و خروجی‌های ثبت‌شده روی همان مبناست.
نتیجهٔ ممیزی `PASS_WITH_EXPLICIT_PACKAGE_ALLOCATION_LIMITS` است: هیچ endpoint رابطه‌ای `UNRESOLVED` نمانده؛ تصمیم‌های محصولی همچنان بازند؛ برای رابطه‌هایی که Plan فقط مصرف‌کنندهٔ بالقوه را در سطح Package معرفی می‌کند، تخصیص Task/Feature قطعی ادعا نشده است.
Ledger مرجع در کنترل مستقیم باقی ماند: ۱٬۶۳۳ Candidate، Pending=۰، ۱٬۲۸۵ Atomic Obligation، شامل ۱٬۱۴۹ Covered، صفر Partial، ۱۳۴ Open Decision و ۲ Uncovered تأییدشده. Task Graph: ۳۶ Package، ۱۸۹ Task، ۴۷۱ Subtask، جمعاً ۶۹۶ Node. هیچ‌یک از سه گراف immutable بازنویسی نشد.

## SHA و تغییرناپذیری گراف‌ها
| Artifact | مسیر | Blob SHA | SHA-256 | اندازهٔ بایت |
|---|---|---|---|---:|
| گراف مفهومی Blueprint و Wallet | `knowledge-graph/phase2-reference-docs/semantic/graph.json` | `a43c1732e85eeebdf83709b9d76233e59ae1a1af` | `f16e684dc773e9bf053e51da2a0a37e3b5ffaf88809e1b5d37f8befbf69e1c93` | 4131810 |
| گراف کد فعلی | `docs/phase4/task-map-graph/current-project-code-graph.json` | `c19d700b408206458d56798809ec1c7009e08acc` | `0a496833d1a58a6d07e58f3d5d2b59f2c0306a924d8573a687fc4067c549c982` | 4415738 |
| گراف Task | `docs/phase4/task-map-graph/new-project-task-graph.json` | `2393556b74016a437d9a126bee3b04cdcc42be25` | `deb940949583007628dccb89de538c8f3b278aef1c6f99d1386f613f107fa0f7` | 3013453 |
| Mapping (قابل‌تغییر در این پیگیری) | `docs/phase4/task-map-graph/task-map-mapping.json` | `d9c3c140d2f0638bd9d0f17d14ac6a2d472cbab0` | `d376d70f091aea548c6a5e3e66992f0e109202545ccd32251fc2a8891c1581e7` | 4227423 |

SHA سه گراف immutable با پین‌های محلی و GitHub برابر است. اسکریپت Replay در هر اجرا Blob SHA و SHA-256 هر سه گراف را تطبیق می‌دهد.

## دو رابطهٔ پیش‌تر مبهم
در هر دو رابطه endpointها اکنون به Packageهای canonical واقعی وصل‌اند؛ رابطه‌ها به Task ساختگی تقلیل نیافته‌اند. وضعیت `OPEN` در endpointهای مصرف‌کنندهٔ بالقوه بیانگر نبود تخصیص Feature/Task در خود Plan است، نه endpoint مفقود.

### Handoff:H04:003
Plan در `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:4049` مصرف Entitlement از API نسخه‌دار را ذکر می‌کند؛ در `:4053`، قرارداد C04 فهرست مصرف‌کنندگان پذیرفته‌شده برای برنامه‌ریزی را دارد. Overlay اکنون C04 را به `PACKAGE:A01` و `PACKAGE:A02` با وضعیت `PLANNING_ACCEPTED_PACKAGE` متصل می‌کند. Plan در `:4060` بسته‌های `R01–R10` را مصرف‌کنندهٔ احتمالی آتی می‌داند؛ برای هرکدام یک endpoint واقعی Package با `confidence=OPEN`، `execution_effect=IMPACT_ONLY` و `resolution_status=POTENTIAL_CONSUMER_PACKAGE_SCOPE` ثبت شده است. این ده رابطه تخصیص اجرایی Feature یا Task را ادعا نمی‌کنند؛ چنین انتسابی در منبع تعیین نشده است.

### DEP:C05A:003
Plan در `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:4262` C05a را ارائه‌دهندهٔ projection کاتالوگ/Capability معرفی می‌کند و C04، C06 و Adviser/Assistant آینده را مصرف‌کننده می‌داند. قراردادِ موردنیاز از دید مصرف‌کننده به ارائه‌دهنده ثبت می‌شود: `PACKAGE:C04 → PACKAGE:C05A` و `PACKAGE:C06 → PACKAGE:C05A` با قرارداد موجود، به‌علاوهٔ `PACKAGE:R01–R10 → PACKAGE:C05A` در سطح scope بالقوه با `confidence=OPEN` و `IMPACT_ONLY`. عبارت Adviser/Assistant دیگر endpoint نهایی مبهم نیست؛ بسته‌های RAG احتمالی Plan به‌صورت Packageهای واقعی تفکیک شده‌اند. تعیین Task/Feature دقیق همچنان شاهد صریح ندارد و جعل نشده است.

Overlay اکنون 94 رابطه دارد: `depends_on`=17, `handoff`=47, `requires_contract`=29, `requires_policy`=1. شمار اطمینان: `CONFIRMED`=69, `OPEN`=25. اثر اجرایی: `BLOCKED_BY_DECISION`=3, `CONTRACT_ORDER`=25, `HARD_ORDER`=12, `IMPACT_ONLY`=22, `POLICY_IMPACT`=32. تعداد endpointهای `UNRESOLVED` یا `UNRESOLVED_SOURCE_GAP`: صفر. چرخهٔ HARD_ORDER: صفر؛ ترتیب توپولوژیک Taskها: ۶۹۶ گره.

## هشت تصمیمی که قبلاً UNMAPPED بودند
هر ۱۳۴ تصمیم در Ledger/Mapping حفظ و `decision_status=OPEN` مانده‌اند. وضعیت `mapping_status=BLOCKED` اکنون یعنی دامنهٔ اثر اجرایی تصمیم به Package/Task پیوند دارد و تا تصویب تصمیم متوقف است؛ به معنی حل‌شدن تصمیم نیست. برای هشت رکورد زیر دامنهٔ Task/Package و Plan locator افزوده شد و `UNMAPPED_IN_TASK_GRAPH` باقی نمانده است:

| Open Decision | Package | Taskهای متأثر | Plan locatorهای مستقیم | وضعیت تصمیم / اثر |
|---|---|---|---|---|
| `AO:BP-C-0129:01` | `PACKAGE:R02`, `PACKAGE:R04` | `TASK:RAG:R02:003`, `TASK:RAG:R04:003` | `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6294`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6295`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6299`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6300`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6307`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6319`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6334`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6570`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6571`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6573`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6583`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6593`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6294;docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6570` | `OPEN` / `BLOCKED_BY_DECISION` |
| `AO:BP-C-0129:02` | `PACKAGE:R04` | `TASK:RAG:R04:002` | `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6568`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6569`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6592`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6600` | `OPEN` / `BLOCKED_BY_DECISION` |
| `AO:BP-C-0129:03` | `PACKAGE:R01`, `PACKAGE:R08` | `TASK:RAG:R01:004`, `TASK:RAG:R08:001` | `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6172`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6173`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6183`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6193`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7229`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7230`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7251`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6172;docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7229` | `OPEN` / `BLOCKED_BY_DECISION` |
| `AO:BP-C-0129:04` | `PACKAGE:R08` | `TASK:RAG:R08:001`, `TASK:RAG:R08:002` | `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7229`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7230`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7251`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7231`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7232`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7252`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7229;docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7231` | `OPEN` / `BLOCKED_BY_DECISION` |
| `AO:BP-C-0129:05` | `PACKAGE:R05` | `TASK:RAG:R05:001`, `TASK:RAG:R05:005` | `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6699`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6725`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6834`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6836`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6839`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6707`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6708`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6729`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6835`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6837`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6838`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6699;docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6707` | `OPEN` / `BLOCKED_BY_DECISION` |
| `AO:BP-C-0129:06` | `PACKAGE:R07` | `TASK:RAG:R07:003` | `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7102`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7103`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7104`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7121` | `OPEN` / `BLOCKED_BY_DECISION` |
| `AO:BP-C-0129:07` | `PACKAGE:R06` | `TASK:RAG:R06:002`, `TASK:RAG:R06:003` | `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6875`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6876`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6877`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6902`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7027`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7033`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6878`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6879`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6903`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7029`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6875;docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6878` | `OPEN` / `BLOCKED_BY_DECISION` |
| `AO:BP-C-0289:01` | `PACKAGE:R05`, `PACKAGE:R06` | `TASK:RAG:R05:005`, `TASK:RAG:R06:005` | `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6707`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6708`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6729`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6834`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6835`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6836`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6837`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6838`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6839`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6881`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6882`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6905`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7027`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7028`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7031`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7032`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:7033`; `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6707;docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6881` | `OPEN` / `BLOCKED_BY_DECISION` |

این هشت تصمیم از موضوعات کیفیت/آزمون و هفت تصمیم باز منبع/آستانه تشکیل می‌شوند. نام تصمیم و انتخاب محصولی باز مانده؛ فقط ارتباطش با scope اجرایی و اثر توقف ثبت شده است.

## عنوان TASK:CORE:C13B:008
عنوان گراف اصلی `/` تغییر نکرد. Overlay نام `مسیر مالی مجاز را بررسی کند` را با نوع `CONTEXT_DERIVED_LABEL` ثبت می‌کند: در همان ردیف Plan، Story برابر «C13B-S08 مسیر مالی مجاز را بررسی کند» کنار شناسه آمده و Subtaskهای زیرین همان مسیر را بسط می‌دهند. شاهد: `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md:6006`، Blob SHA سند Plan برابر `daa448b2dbb204b4ab081a38bc13548f1a8c8de6`. این نام محصولی جدید نیست؛ کپی عنوان Story صریح Plan در Overlay است.

## بازبینی ۶۵۷ مورد NEW_IMPLEMENTATION و جست‌وجوی قبلی ۵۹۲ مورد
پیکرهٔ کد پین‌شده شامل ۳۴۷ فایل و inventory SHA-256 برابر `3a28fabf5476abe813a0385297acf97242d5cf28fb3dfbb81ccdf9ff78b27071` است. جست‌وجو با شناسهٔ canonical و alias تأییدشده، نام Task/Package، اصطلاحات متمایز Plan و فایل‌های کد، API/Route، مدل/مهاجرت، قرارداد/پیکربندی، آزمون/Fixture، YAML و Docker انجام شد. تطابق واژگانی به‌تنهایی Mapping تلقی نشد. طبقه‌بندی نهایی برای کل ۶۵۷ رکورد:

| وضعیت نهایی | تعداد | تفسیر |
|---|---:|---|
| `NON_CODE_REQUIREMENT` | ۳۰ | Packageهای تجمیعی و محدوده‌های مدیریتی؛ فرزندان اجرایی جداگانه جست‌وجو شده‌اند. |
| `NO_CODE_EVIDENCE_FOUND` | ۶۲۴ | در پیکرهٔ پین‌شده شاهد مستقیم پیاده‌سازی متناظر پیدا نشد؛ این نتیجه نبود قطعی امکان استفادهٔ مجدد در آینده را اثبات نمی‌کند. |
| `CODE_PARTIALLY_FOUND` | ۳ | بخش‌هایی از R10 در کد فعال موجودند؛ اتصال نسخه‌دار Adviser و ورودی‌های تازه هنوز پیاده‌سازی جدید می‌خواهند. |
| `CODE_FOUND_NOT_IN_GRAPHIFY` | ۰ | کد متناظر خارج از گراف کد با شاهد قابل‌قبول پیدا نشد. |
| `SEARCH_INCONCLUSIVE` | ۰ | هر ۵۹۲ مورد پیشین دوباره بررسی و در یکی از وضعیت‌های بالا تعیین‌تکلیف شدند. |

سه مورد `CODE_PARTIALLY_FOUND` عبارت‌اند از `TASK:RAG:R10:001` (use case/scorer/API توصیه)، `TASK:RAG:R10:002` (snapshot/repository)، و `TASK:RAG:R10:003` (scorer و مدل partition). Mapping فقط به Nodeهای واقعاً موجود Graphify و فایل/خط دارای Blob SHA و SHA-256 وصل شده است. فهرست ۶۵۷ رکورد، روش، query و نتیجهٔ هر مورد در `stage4_code_search_audit.records` در Mapping ذخیره و در Replay بازتولید می‌شود.

## شمار Mappingها و تصمیم‌های باز
Mapping پوشش‌دهندهٔ ۶۹۶ Node است: `MAPPED`=15، `PARTIALLY_MAPPED`=27، `NEW_IMPLEMENTATION`=654. هر ۱۳۴ تصمیم یکتا یک‌بار حفظ شده و هر ۲۲ مرجع ویژه یکتا بازبینی شده است؛ در Mapping وضعیت scope تمام آن‌ها `BLOCKED` و وضعیت تصمیم خودشان `OPEN` است. شمارش اتم‌ها در Ledger مستقل با Mapping یکی نیست و هیچ وضعیت Candidate/Atomic در این پیگیری تغییر نکرد.

## Replay و اعتبارسنجی
ابزار بازپخش نسخه‌بندی‌شده `replay_stage4.py` علاوه بر JSON، شمار Nodeها، شناسه‌ها، endpointها، تصمیم‌ها، locatorها، چرخه، شواهد کد، پیکرهٔ ۳۴۷ فایلی و پروجکشن معنایی Mapping/Overlay را کنترل می‌کند. SHA پروجکشن معنایی ثبت‌شده: `97b001c972d5e34c296d34e72bceebc6dce7381f7942bc78e3c5881d2cf02831`.
در این پیگیری `build_and_validate.py --check-only` اجرا شد: ۲۹/۲۹ کنترل PASS؛ ۱٬۶۳۳ Candidate، ۱٬۲۸۵ Obligation، Source Locator، ارجاع‌های گراف و Ledgerها بدون خطا. Replay نهایی باید دو بار متوالی اجرا شود و خروجی معنایی آن byte-for-byte برابر بماند؛ نتیجهٔ نهایی در گزارش انتشار/PR پس از ثبت HEAD درج می‌شود.

## محدودیت واقعی باقی‌مانده و مرز Phase 5
هیچ endpoint گرافی مبهم یا مفقودی باقی نمانده است. بااین‌حال، Plan برای مصرف‌کننده‌های بالقوهٔ Adviser/Assistant در R01–R10 هنوز Feature/Task مشخصی را به Handoff/قرارداد تخصیص نمی‌دهد؛ به همین علت روابط مربوطه با confidence باز و فقط در سطح Package ثبت شده‌اند. این محدودیت پنهان یا به‌عنوان تخصیص قطعی گزارش نشده و در Overlay قابل ردیابی است. تصمیم‌های محصولی نیز باز باقی می‌مانند. هیچ رابطه، Mapping یا ترتیب اجرا به Phase 5 منتقل نشده؛ Phase 5 فقط برای تقسیم گراف نهایی به تحویل‌دادنی‌های یک‌هفته‌ای است.

## فایل‌های تغییرکرده در این پیگیری
- `docs/phase4/task-map-graph/task-map-mapping.json` — اصلاح دو خانوادهٔ رابطه، دامنهٔ هشت تصمیم، عنوان C13B:008 و نتیجهٔ کامل جست‌وجوی ۶۵۷ مورد.
- `docs/phase4/task-map-graph/replay_stage4.py` — اعتبارسنجی و بازتولید deterministic شواهد/رابطه‌ها و جست‌وجوی کد.
- `docs/phase4/task-map-graph/task-map-quality-audit.md` — همین گزارش نهایی و یافته‌های شاهددار.
