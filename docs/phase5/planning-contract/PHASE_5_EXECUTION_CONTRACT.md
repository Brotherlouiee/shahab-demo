# قرارداد اجرایی پیشنهادی فاز پنجم — مأموریت 5.0

**وضعیت:** پیش‌نویس پیشنهادی؛ `PHASE_5_CONTRACT=PENDING_OWNER_APPROVAL`
**اجرای فاز پنجم:** `NOT_STARTED`
**مبنای داده:** Snapshot ثابت `phase4-45ed4ec10d34216cf935` از commit `8ce742b640bbcbb87be5fc29f3a5a28d92593dec`؛ اعتبارسنجی واقعی پیش از اصلاح در HEAD `3124c39ddec912eac146411be765df0bca0549a3` و در بررسی نهایی این شاخه نتیجه `CERTIFIED_SNAPSHOT_VALID` و ۲۷ Artifact داد.

## 1. هدف و مرز

فاز پنجم باید ساختار کار موجود (WBS) را به برنامه انتشار مبتنی بر تحویل‌دادنی‌های ارزشمند تبدیل کند. WBS به پرسش «چه کارهایی لازم است؟» پاسخ می‌دهد؛ ساختار انتشار به پرسش «کدام ترکیب کار می‌تواند در یک چرخه خروجی قابل استفاده، آزمون و انتشار ایجاد کند؟» پاسخ می‌دهد. یک Deliverable می‌تواند بخش‌هایی از چند Package را ترکیب کند؛ Package، Task و هفته معادل Deliverable نیستند.

مأموریت 5.0 فقط bootstrap، تثبیت قرارداد پیشنهادی، ثبت سیاست و تصمیمات باز، طراحی Schema/Graph/مدل‌ها، تعریف artifacts و معیار پذیرش و ارائه Draft PR برای مالک محصول است. این مأموریت تسک را به هفته تخصیص نمی‌دهد، effort/capacity/cost/token واقعی تخمین نمی‌زند، Deliverable اجرایی نهایی نمی‌سازد، Planning Engine تولیدی نمی‌سازد و هیچ مصوبه/تصمیم بازی را تصویب نمی‌کند.

## 2. وضعیت ورودی و قواعد معنایی

Snapshot Validator: Exit 0; `CERTIFIED_SNAPSHOT_VALID`; 27 Artifact; Git ancestry source commit→main برقرار. Manifest و فایل‌ها به همان commit pin شده‌اند. آمار گواهی‌شده: 36 Package، 189 Task، 471 Subtask (696 Work Node)؛ 15 MAPPED، 27 PARTIALLY_MAPPED، 654 NEW_IMPLEMENTATION؛ Source Coverage: 1,285 atomic obligations (1,149 Covered، 134 Open Decision، 2 Uncovered)؛ Combined Graph: 4,490 node، 11,435 edge، 181 community و 99 Overlay relation. داده‌ها در این مأموریت تغییر نمی‌کنند.

معنای وضعیت‌ها و یال‌ها باید عین قرارداد Phase 4 باقی بماند: MAPPED یعنی شواهد نگاشت، نه توسعه کامل؛ PARTIALLY_MAPPED درصد پیشرفت نیست؛ NEW_IMPLEMENTATION effort برابر ندارد؛ HARD_ORDER فقط در scope ثبت‌شده تقدم اجراست؛ CONTRACT_ORDER آمادگی قرارداد است، نه ترتیب اجرای همه Taskها؛ IMPACT_ONLY dependency اجرایی نیست؛ `contains` سلسله‌مراتبی است؛ نبود dependency، parallel-safe بودن را ثابت نمی‌کند. Package/Task/Subtask سه مجموعه مستقل کار نیستند و دوباره‌شماری ممنوع است. ۱۳۴ تصمیم OPEN/BLOCKED و دو Uncovered باید نمایان بمانند.

**توجه به پذیرش فاز ۴:** readiness برای مصرف فنی `READY` است، اما پذیرش رسمی `CONDITIONAL` باقی مانده. ۹ PASS، ۱۲ PARTIAL و ۱ BLOCKED عمومی ارتقا داده نمی‌شود. این بدهی‌ها خودکار مانع Phase 5 نیستند؛ محدودیت‌های ثبت‌شده همراه evidence حفظ می‌شوند.

## 3. منابع حاکم و وضعیت تصمیم

مرجع سیاست/نیازمندی Blueprint، سند کیف پول و Canonical Guide است؛ Task Execution Protocol و AGENTS/Git skill حاکم بر اجرا هستند. Phase 4 Snapshot و handoff، منبع pinned داده و معنای آن هستند. فهرست کامل ورودی‌های لازم در Manifest: دو primary input، ۱۶ reference input، سه optional human-review، شش audit-evidence؛ جمع ۲۷ artifact. دادهٔ زمان/هزینه Phase 4 مبنای برآورد قابلیت مالی نیست مگر مقایسه‌پذیری مأموریت اثبات شود.

۲۲ اصل Blueprint §5.2.1 در `source-policy-trace.csv` با شناسه، locator، معنا، اثر فاز پنجم، سازوکار و شواهد ردیابی شده‌اند. O5-01 تا O5-14، سیاست سه‌مرحله‌ای، A01–A09، F06 و کیف پول به‌عنوان مبنای مصوب/مرجع ثبت شده‌اند؛ موارد اجرایی، release evidence، آستانه، بودجه و ظرفیت واقعی همچنان بازند. O5-09 نسبت Discovery/Delivery را مصوب کرده: مبنا ۸۰/۲۰، کار بحرانی ۹۰/۱۰، کار نامطمئن ۷۰/۳۰ با timebox؛ این اعداد نسبت سیاستی‌اند، نه headcount یا ظرفیت اندازه‌گیری‌شده. F06 مکمل O5-10 است و گیت تازه نمی‌سازد. پیشنهادهای P5-D01..D16 در رجیستری `OPEN / PENDING_APPROVAL` باقی می‌مانند.

## 4. مراحل پیشنهادی فاز پنجم

1. **5.0 قرارداد و bootstrap:** این بسته و تصمیم‌نامه برای تصویب مالک؛ بدون زمان‌بندی.
2. **5.1 مدل داده و رجیستری پایه:** پس از تصویب، مدل canonical و اعتبارسنجی منبع‌ها؛ بدون allocation تا آماده‌شدن تصمیم‌ها و ورودی‌ها.
3. **5.2 کشف/تدوین Deliverable و Trace:** ساخت outcome candidates با ارجاع bidirectional به requirements/work nodes/code evidence و ثبت gaps؛ هر تصمیم محصولی باز مسدودکننده همان دامنه می‌ماند.
4. **5.3 estimate/capacity/value/risk:** فقط با اندازه‌گیری واقعی، مرجع مقایسه و approval parameters؛ Unknown حفظ شود.
5. **5.4 اولویت‌بندی و زمان‌بندی:** پس از تعیین قیود، ظرفیت و estimates؛ چرخه‌ها حداکثر ۷ روز تقویمی، بدون تعداد هفته از پیش.
6. **5.5 viewer/replanning/validation hardening:** ساخت ابزار تنها با consumer و معیار پذیرش روشن؛ audit trail برای هر بازتنظیم.
7. **5.6 closure/snapshot:** تنها بعد از گیت‌های مصوب و تصویب لازم؛ هر مرحله بعدی محتاج تصمیم مجزا است.

این ترتیب پیشنهاد اجرایی است و مصوبه نیست؛ مراحل 5.1 به بعد در این مأموریت اجرا نمی‌شوند.

## 5. مدل مفهومی Deliverable و Schema پیشنهادی

Deliverable واحد outcome-based برنامه انتشار است، نه واحد WBS. باید کاربر/اپراتور و مسئله مشخص، ارزش مستقل قابل مشاهده، مرز دامنه، پذیرش قابل اثبات و trace به منابع داشته باشد. Work references فقط آدرس‌اند؛ انتخاب بخشی از Task/Subtask و قواعد سهم‌دهی هنوز نیازمند D02 است. `Independent Value` یعنی نتیجه‌ای که بدون ادعای تکمیل کل مرحله قابل مشاهده است؛ محصول می‌تواند برای آزمون محدود/کاربر مجاز مصرف‌کننده داشته باشد و این به معنی انتشار عمومی نیست.

| فیلد | معنا/منبع | الزام/اعتبارسنجی | تصمیم/زمان تکمیل |
|---|---|---|---|
| Deliverable ID / Title / Description | شناسه یکتا و تعریف outcome؛ تولید از canonical planning data | Required؛ unique؛ title غیرتهی و description outcome-centered | P5-D01؛ 5.2 |
| User or Operator / User Problem / Independent Value / Observable Outcome | مصرف‌کننده و ارزش/نتیجه قابل مشاهده؛ منبع: تحقیق/تصمیم مالک/شواهد محصول | Required؛ actor و evidence/result قابل مشاهده | ارزش نهایی تأیید مالک؛ 5.2 |
| In Scope / Out of Scope / Product Stage | مرز برش و مرحله مصوب Blueprint | Required؛ stage فقط ۱–۳ مصوب؛ scope exclusion نباید الزام را حذف کند | Stage mapping در 5.2 و owner review |
| Capability References / Package References / Task References / Subtask References | شناسه‌های graph Phase4 | Required where relevant؛ refs resolve؛ ancestor/descendant double count منع | D02؛ 5.2–5.3 |
| Requirement References | Atomic obligation/requirement source IDs | Required؛ bidirectional trace؛ OPEN/UNCOVERED visible | 5.2; no silent disposition |
| Existing Code Evidence / Mapping Status | کد و وضعیت Mapping از snapshot pinned | Optional until evidence exists؛ cite code graph ID/path/line; preserve status semantics | 5.2 |
| Hard Dependencies / Contract Dependencies | source edges/effect audit | Required when present؛ type/scope/evidence; contract readiness جدا از execution order | D02; 5.2 |
| Policy Constraints / Open Decisions | O5/A/F06/wallet constraints و decision refs | Required; source pin; OPEN never approved implicitly | 5.1–5.2 |
| Acceptance Criteria / Test References | outcome oracle و test/evidence references | Required before commitment; test must check outcome/failure/edge where relevant | D13; 5.2–5.3 |
| Security Requirements / Release Gates | wallet/Blueprint risk/security and approved REL mapping | Required when relevant; exact release source text and evidence; no invented gates | D13; future release case |
| Monitoring / Rollback Requirements | A09/F06 safety and operational evidence | Required for release candidate as applicable; rollback compatibility checked | before release readiness |
| Effort Estimate Reference / Cost Estimate Reference / Token Estimate Reference | linked, typed, evidence-backed estimate records | Unknown may be explicit during proposal/discovery; **all applicable estimates, including cost, are required before any commitment** | D04–06; 5.3 |
| Resource Requirements / Uncertainty | role/tool/environment + range/confidence/evidence | declare unknown; validate against actual capacity only | D03/D12; 5.3 |
| Release Readiness / Planning Status | separate state dimensions | enum/version/transition rules; release-ready ≠ stage-complete; approval/evidence required | D13; 5.4 |

این Schema صرفاً پیشنهاد است و مبنای تخصیص قطعی Task نیست.

### 5.1.1. تصمیم فیلدبه‌فیلد برای Deliverable Schema (پیشنهادی)

در جدول زیر «تصمیم» یعنی آیا مقدار/تفسیر نیازمند تأیید مالک است؛ فیلدهای صرفاً reference به‌خودی‌خود تصمیم محصولی تازه نمی‌سازند. Required یعنی شرط اعتبار Schema پیشنهادی در مرحله گفته‌شده، نه داده‌ای که اکنون موجود است.

| فیلد | منبع تولید | الزام | اعتبارسنجی | نیاز به تصمیم مالک | تکمیل در |
|---|---|---|---|---|---|
| Deliverable ID | canonical planner / owner | الزامی | unique, stable, namespace | تصمیم شناسه/نسخه مالک | 5.1 |
| Title | owner-authored outcome title | الزامی | non-empty, user-readable | بله | 5.2 |
| Description | product evidence and owner scope | الزامی | outcome-focused; no implementation-only wording | بله | 5.2 |
| User or Operator | research/current product role | الزامی | known actor ID/role; mark unknown | بله اگر actor disputed | 5.2 |
| User Problem | research/approved source | الزامی | trace to evidence; no invented need | بله | 5.2 |
| Independent Value | approved outcome hypothesis/evidence | الزامی | observable without implying stage complete | بله | 5.2 |
| Observable Outcome | acceptance evidence/test source | الزامی | measurable/observable; no invented threshold | بله | 5.3 |
| In Scope | approved requirements + selected WBS slices | الزامی | references resolve; scoped portion explicit | بله | 5.2 |
| Out of Scope | owner-approved boundary | الزامی | cannot silently remove source obligation | بله | 5.2 |
| Product Stage | Blueprint approved three-stage policy | الزامی | enum stage 1/2/3; no implicit stage 4 | مصادیق نیازمند review | 5.2 |
| Capability References | capability/plan graph | در صورت ارتباط | IDs resolve and owner boundary valid | در صورت new mapping | 5.2 |
| Package References | certified task graph | الزامی در صورت کار mapped | resolve; hierarchical parent not independent effort | خیر، reference only | 5.2 |
| Task References | certified task graph | الزامی در صورت کار mapped | resolve; unique allocation invariant | برای selection/allocation | 5.2–5.3 |
| Subtask References | certified task graph | در صورت تخصیص بخشی | resolve; do not sum with allocated ancestor | برای partial allocation rule | 5.3 |
| Requirement References | Evidence Join Index/approved source | الزامی | source id resolves; status preserved | اگر disposition changes | 5.2 |
| Existing Code Evidence | certified code graph/current code | اختیاری تا وجود شواهد | source ID/path/line/hash as available | for claim of existing behavior | 5.2 |
| Mapping Status | certified Phase 4 mapping | الزامی برای mapped WBS ref | preserve exact source status; never progress percentage | خیر, immutable source label | 5.2 |
| Hard Dependencies | task graph explicit HARD_ORDER + approved dependencies | در صورت وجود | source scope/effect/evidence; DAG validation | new edge requires owner/source | 5.2 |
| Contract Dependencies | task graph contract effects | در صورت وجود | contract readiness; never auto-schedule full Task order | edge reclassification requires approval | 5.2 |
| Policy Constraints | Blueprint/O5/A01..09/F06/wallet | الزامی | source version and constraint class | policy change always owner | 5.1–5.2 |
| Open Decisions | decision register + Phase4 134 OPEN | الزامی when relevant | OPEN/BLOCKED + affected scope + owner | resolution requires explicit owner | 5.1 |
| Acceptance Criteria | user/operator outcome + policy | الزامی before commitment | precondition/action/oracle/failure boundary | threshold/policy requires owner | 5.3 |
| Test References | approved test plan/CI/evidence | الزامی before commitment | exists, relevant, version matches | test scope changes reviewed | 5.3 |
| Security Requirements | wallet/security/Blueprint A rules | الزامی when relevant | control and evidence, fail-closed boundaries | exceptions require authorized owner | 5.2–release prep |
| Release Gates | approved O5-10 R1–R4/RG/REL source | الزامی for release candidate | exact gate/version mapping and evidence; no new gate | owner release authorization | release prep |
| Monitoring Requirements | A09/F06 and value measurement | الزامی for applicable release | minimum-data/privacy and owner/SLI source | thresholds require approval | release prep |
| Rollback Requirements | F06, compatibility and recovery source | الزامی for applicable release | compatible code/data/API/snapshot/job target and evidence | rollback exception owner | release prep |
| Effort Estimate Reference | estimate registry/model | قبل از schedule commitment | type/unit/range/source/uncertainty; Unknown allowed until then | model/estimate policy pending | 5.3 |
| Cost Estimate Reference | evidence-backed development and operating cost records | پیش از هرگونه تعهد، مستقل از وجود cost constraint | ساخت و بهره‌برداری، tool cost و token cost جدا؛ currency/period/source required؛ UNKNOWN تعهد را مسدود می‌کند | مبنای برآورد و تعهد نیازمند تصویب مالک | 5.3 |
| Token Estimate Reference | provider usage/model record | when agent token cost applies | actual vs predicted, provider/model/version/source | pricing assumptions owner | 5.3 |
| Resource Requirements | role/tool/environment inventory | before schedule commitment | owner/period/quantity/capacity evidence | availability supplied by owner | 5.3 |
| Uncertainty | estimate/risk evidence | الزامی پیش از commitment | confidence state and unknown blockers; numeric band only if measured | threshold convention owner | 5.3 |
| Release Readiness | release case and evidence | الزامی before release | separate state machine; pass requires actual gate evidence | release owner per O5-10 | 5.4/release |
| Planning Status | canonical plan lifecycle | الزامی | proposed/ready/blocked/committed/done enum + legal transitions | status transitions require configured authority | 5.1 onward |

## 6. گراف پیشنهادی

نام: **Phase 5 Deliverable Planning Graph**؛ projection مستقل از canonical source آینده و ارجاع‌دهنده به شناسه‌های immutable فاز چهارم. هیچ Node/Edge به گراف فاز چهارم افزوده نمی‌شود. تعریف رسمی هر Node/Edge، endpoint، cardinality، properties، lifecycle، evidence، وضعیت تصویب و validation در [planning-contract-schema.json](planning-contract-schema.json) ثبت شده است؛ این Schema نیز پیشنهادی و منتظر تأیید مالک است.

مدل ۹ نوع گره موجود را با رابطه‌های لازم کامل می‌کند. یک `EXTERNAL_REFERENCE` به‌عنوان آدرس نوع‌دارِ گراف/Requirement/Test/Evidence بیرونی اضافه می‌شود تا ارجاع دقیق ممکن باشد؛ این Node محتوای Phase 4 را کپی یا تغییر نمی‌دهد. `MILESTONE` با `CONTRIBUTES_TO_MILESTONE`، `ESTIMATE` با `HAS_ESTIMATE` و `INFORMS_ESTIMATE`، و `DISCOVERY` با `REDUCES_UNCERTAINTY_FOR`، `INFORMS_ESTIMATE` و `INFORMS_DECISION` رابطهٔ رسمی دارند. رابطه‌های trace-only خودبه‌خود تقدم یا تخصیص زمان ایجاد نمی‌کنند.

### قابلیت چند‌هفته‌ای

چرخهٔ مصوب همچنان حداکثر هفت روز تقویمی است. سه مدل بررسی شده‌اند: (A) یک Deliverable با چند Week و رکورد exception؛ (B) یک outcome/parent با sliceهای هفت‌روزهٔ مستقل و قابل آزمون؛ (C) تفکیک Deliverable انتشار از Work Packageهای اجرایی. پیشنهاد موقت B است؛ تصویب نشده است. در B، رابطهٔ نوع‌دار `HAS_WORK_SLICE` parent outcome را به sliceهای مستقل وصل می‌کند؛ هر slice حداکثر یک Week از طریق `SCHEDULED_IN` دارد و parent فقط roll-up است و دوباره‌شماری نمی‌شود. هیچ slice میانی معادل انتشار محصول نیست.

هر گزینهٔ چند‌هفته‌ای پیش از تعهد به رکورد exception نیاز دارد: دلیل عدم تقسیم ایمن/ارزشمند، گزینه‌های تقسیم و علت رد، وابستگی‌ها، سقف زمان تقویمی و سقف جداگانه هزینه توسعه/بهره‌برداری با تأیید مالک، خروجی میانی و oracle آزمون برای هر چرخه، تاریخ بازبینی، و قاعده reconciliation تخمین والد/برش‌ها. تا تصویب سقف‌ها، مقدار آن‌ها UNKNOWN/PENDING_APPROVAL است و تعهد انجام نمی‌شود.

## 7. ظرفیت و تخمین پیشنهادی

رجیستری Machine-readable تخمین در `planning-contract-schema.json` همه اقلام و stateها را تعریف می‌کند: مدت تقویمی، نفرساعت، runtime عامل، هزینه توسعه، هزینه بهره‌برداری، token، tool cost، نیاز زیرساخت، ظرفیت، ریسک، عدم‌قطعیت، شاهد، فرض‌ها و وضعیت تأیید. برای هر قلم، واحد، مرحله لازم، شاهد، حالت فقدان داده و اثر بر تعهد ثبت شده است.

`UNKNOWN` صفر نیست؛ `NOT_MEASURED` به‌معنای نبود هزینه نیست؛ `ESTIMATED` با `MEASURED` فرق دارد؛ `NOT_APPLICABLE` بدون rationale/evidence رد می‌شود. هزینه توسعه، بهره‌برداری، ابزار و توکن جدا هستند؛ نفرساعت، runtime عامل و زمان تقویمی جمع یا جایگزین هم نمی‌شوند. هر estimate باید source/method/version، فرض‌ها، uncertainty و approval state داشته باشد؛ دادهٔ عددی واقعی برای این مأموریت ساخته نشده است.

هیچ مقدار نامعلوم در مرحلهٔ پیشنهاد به‌خودی‌خود تخمین صفر نمی‌شود، اما رکوردهای لازم باید state صریح داشته باشند. گذار به `COMMITTED` بدون برآورد معتبر و شاهد برای تمام اقلام ضروری، ظرفیت تأییدشده و مجوز مالک مجاز نیست. هیچ استثنای عمومی برای هزینه به‌علت نبود `cost constraint` تعریف نمی‌شود. قواعد و انتقال lifecycle پیشنهادی‌اند و نیازمند تصویب مالک هستند.

## 8. ارزش و اولویت‌بندی

Inputs: user value, operator value, complexity, development cost, time, risk, prerequisite readiness, downstream effect, reuse, rework reduction, uncertainty, learning value, release readiness and approved product stage. Separate:

- **Hard constraints:** security/legal/financial integrity, explicit `HARD_ORDER`, stage policy, valid owner permission, approved release gate, capacity limit, unresolved dependency decision in its actual scope. Failure blocks; no score can compensate.
- **Optimization objectives:** among feasible candidates, compare value, learning, reuse, delay/rework avoided, cost/time and uncertainty. No weights, thresholds or actual ranking approved here.

Options in P5-D08: WSJF; owner-weighted scoring; or constraint-first Pareto/decision table. Proposed sequence is filter hard constraints, expose feasible candidates with evidence ranges, then owner prioritizes. Avoid false precision; tie-breaks and weights require owner approval. Do not rank real tasks in 5.0.

## 9. زمان‌بندی و بازبرنامه‌ریزی

Only after deliverables, dependencies, approved estimates and capacity exist: generate windows of at most seven calendar days; capacity includes coding, testing, review, correction, deployment; obey hard order and approved product-stage sequence; keep Discovery/Delivery ratio per O5-09; no duplicate effort; distinguish `Release Readiness` from `Stage Completion`; open decisions block only affected work; future cycles may replan; already released artifacts and contracts remain immutable/compatible. Number of weeks emerges from feasible scope + measured capacity + validated estimates + hard constraints + approved priorities; no duration or number of weeks can be computed now.

Replan event requires new evidence/actual/decision/capacity change; record old/new plan version, change reason, impact, affected outcomes/gates, owner and approval. Preserve prior schedule and release evidence; no silent scope, policy, architecture, gate, price or financial behavior change.

## 10. خروجی‌های کل فاز پنجم

Registry in `output-artifact-registry.json` covers 18 outputs: it recommends one canonical `A00 planning-source.json`, with all schedule, graph, CSV, Markdown, HTML and report views derived. That recommendation is OPEN under D14. Markdown, HTML and CSV are not independent authorities. Each artifact has producer, consumer, use, dependency, stage and validation. Viewer, engine, validator and test suite are produced only when an identified consumer and approved acceptance justify implementation. Mission 5.0 does not create those operational artifacts.

## 11. معیارهای پذیرش و وضعیت

P5-B01…B16 are the acceptance registry. A gate is PASS only from an actual command/result/evidence. `SKIPPED`, `NOT_EXECUTED`, `NOT_MEASURED`, `PENDING_APPROVAL`, `PENDING_CI` remain distinct. Blocking gate failure prevents `MISSION_5_0_COMPLETE`; a rejected/unavailable external review or CI must be stated, not synthesized. Acceptance gates describe reviewable controls and are proposed where they add new Phase 5 process; they do not replace O5-10 release gates.

## 12. محدودیت و موارد خارج از دامنه

No phase4 rebuild/remapping/source coverage replay; no reopening prior accepted audit scope; no new product code; no real task/week allocation; no finalized value rank/engine; no estimate/number fabricated; no decision approval; no merge/deploy. Phase 4 known gaps remain visible and are not automatically blockers. Any newly found specific planning-impact defect must include artifact+locator, scope of impact, evidence and correction recommendation; absent proof, no broad audit is initiated.

## 13. تصمیمات مورد نیاز از مالک به ترتیب پیشنهادی

1. P5-D01 Deliverable definition and separation from WBS.
2. P5-D14 canonical source/model and output derivation (sets single-truth architecture).
3. P5-D02 allocation granularity and double-count rule.
4. P5-D10 owner decision/blocker scope representation.
5. P5-D13 outcome acceptance and link to existing release gates.
6. P5-D03/D11 real capacity capture and application of O5-09.
7. P5-D04–06 estimate/cost/token model and comparable data classes.
8. P5-D07/D08 value/priority objective and weights.
9. P5-D12 uncertainty model.
10. P5-D09 scheduling algorithm and 7-day cycle operationalization.
11. P5-D15 validator scope; P5-D16 replan protocol.

The order is proposed; dependencies permit regrouping. No approval is presumed by this list.
