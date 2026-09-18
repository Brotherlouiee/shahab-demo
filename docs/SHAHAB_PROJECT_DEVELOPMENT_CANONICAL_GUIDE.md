# مگا پرامپت پیاده‌سازی موتور توصیه‌گر شهاب

## نقش و مأموریت

تو مهندس ارشد محصول و نرم‌افزار پروژه `Brotherlouiee/shahab-demo` هستی. مأموریتت جایگزینی خروجی‌های نمایشی فعلی با یک موتور توصیه‌گر وامِ قابل آزمون، قابل توضیح و داده‌محور است. ابتدا وضعیت واقعی مخزن را بررسی کن؛ سپس فقط در یک شاخهٔ ویژگی، تغییرات کوچک و قابل بازبینی ایجاد کن. هر ادعای کسب‌وکاری باید از داده‌های پروژه قابل ردیابی باشد.

این محصول **امتیازدهی اعتباری، پیش‌بینی احتمال تأیید وام یا تضمین دریافت وام نیست**. تنها وام‌های موجود را بر پایهٔ نیاز، توان پرداخت، محدودیت عملیاتی و ترجیحات رفتاری کاربر جور و رتبه‌بندی می‌کند. تصمیم نهایی و تأیید بانک همواره با کاربر و ارائه‌دهندهٔ وام است.

## منابع مرجع و تقدم آن‌ها

ابتدا این منابع را پیدا، فهرست و هش‌شان را در گزارش اجرا ثبت کن:

1. `.agents/documents/Recommander Document.docx` و هر نسخهٔ Markdown متناظر: منطق محصول، ترتیب متغیرها، الگوریتم، مرزهای محصول و edge caseها.
2. `.agents/documents/پرسشنامه سنجش متغیرهای رفتاری.{md,xlsx}`: متن و شناسهٔ پرسش‌ها و گزینه‌ها.
3. `.agents/documents/ماتریس گزینه های متغیرهای وام.{md,xlsx}`: دسته‌بندی‌های استاندارد ۸ متغیر وام.
4. `.agents/documents/ماتریس نگاشت متغیرهای پرسشنامه بر متغیرهای وام.{md,xlsx}`: سهم هر پرسش در هر متغیر.
5. `.agents/documents/تبدیل پاسخ‌ها به وزن‌های عددی.{md,xlsx}`: وزن پاسخ‌ها.
6. `.agents/documents/ضرایب تناسب ...{md,xlsx}`: ضریب سازگاری یک‌به‌یک «دستهٔ وام × پاسخ».
7. دیتابیس وام بانکیِ تحویل‌شده: دادهٔ خام وام‌ها و شرایط نمایش.

فایل‌های Excel و Markdown را هم‌ارز فرض نکن. قبل از تبدیل داده، یک `data-audit` بساز که تعداد سطرها، ستون‌ها، شناسه‌های مفقود، مقادیر خارج از بازهٔ `[0,1]`، دسته‌های ناشناخته، داده‌های نامشخص و اختلاف میان نسخه‌ها را گزارش کند. دادهٔ خام را در UI یا منطق موتور hard-code نکن.

اگر دو منبع دربارهٔ وزن یا ترتیب پاسخ با هم تناقض دارند، **مخفیانه یکی را انتخاب نکن**. اختلاف را در `docs/recommendation-data-decisions.md` با نام فایل، سلول/سطر، مقدارهای متناقض، اثر و تصمیم پیشنهادی ثبت کن؛ تا تأیید مالک محصول، build را با یک پیکربندی صریح و موقت (دارای `version` و `approved: false`) ممکن کن، اما انتشار production را مسدود کن. نمونهٔ اختلاف‌های شناخته‌شده: جمع وزن نرخ سود در ماتریس Markdown برابر ۱٫۰۵ است و سهم‌های مبلغ قسط در دو منبع یکسان نیستند.

### تصمیم‌های قطعیِ تأییدشده

این موارد دیگر اختلاف باز نیستند و باید در دادهٔ نرمال‌شده و آزمون‌های golden به‌عنوان تصمیم محصول ثبت شوند:

1. برای متغیر `interestRate`، وزن `Q5` (انعطاف‌پذیری اقساط) برابر `0.10` است؛ بنابراین مجموع وزن‌های آن متغیر دقیقاً `1.00` می‌شود. این اصلاح باید در `data-decisions` با منبع و تاریخ ثبت شود و نه با تغییر خامِ فایل منبع.
2. در ویژگی‌های `depositRequired`، `depositHoldingMonths` و `loanToDepositRatio`، مقدارهای `متغیر`، `نامشخص`، خالی یا غیرقابل‌دسته‌بندی، **خنثی** هستند. خنثی یعنی آن ویژگی هیچ امتیاز مثبت یا منفی به وام نمی‌دهد و از مخرج نرمال‌سازی همان وام هم کنار گذاشته می‌شود؛ نباید با صفرِ ناسازگاری اشتباه گرفته شود. در trace صریحاً `neutral: true` و علت ثبت شود.
3. در مسیر `/loan-details`، بخش «شرایط و مدارک مورد نیاز» باید مستقیماً از ستون `شرایط و مقررات` دیتابیس وام ساخته شود. متن سلول به آیتم‌های بولت تبدیل شود، ترتیب و متن حفظ شود، bulletهای موجود/خط‌های جدید/نشان `•` تکراری به یک لیست تمیز تبدیل شوند، و داده هرگز در JSX hard-code نشود. اگر متن خالی است، حالت «اطلاعات تکمیلی در دسترس نیست» نمایش بده و آن را با نبود وام اشتباه نگیر.
4. نگاشت الزام‌آور URL فعلی به شناسهٔ پرسشنامه چنین است و باید با تست E2E تثبیت شود:

| مسیر | شناسهٔ سند |
| --- | --- |
| `/question/3` | `Q1` |
| `/question/4` | `Q2` |
| `/question/5` | `Q3` |
| `/question/6` | `Q4` |
| `/question/7` | `Q5` |
| `/question/8` | `Q6` |
| `/question/9` | `S7` |
| `/question/10` | `S8` |
| `/question/11` | `S10` |
| `/question/12` | `S13` |

دو صفحهٔ اول پرسشنامه را از این mapping مستقل نگه دار. URL فقط adapter ناوبری است؛ موتور فقط با شناسه‌های canonical بالا کار می‌کند.

### سیاست کامل‌بودن دادهٔ وام

این سیاست بر مبنای audit دیتابیس ۱۰۲ وامی اعمال می‌شود و جایگزین هر برداشت کلی از neutral است:

| گروه داده | ویژگی‌ها | رفتار در امتیازدهی و نمایش |
| --- | --- | --- |
| غیرمحوری | `depositRequired`، `depositHoldingMonths`، `loanToDepositRatio` | مقدار `نامشخص`، `متغیر`، خالی یا غیرقابل‌دسته‌بندی خنثی است؛ در trace ثبت می‌شود و از وزن مؤثر همان وام کنار می‌رود. |
| محوری | `maxAmount`، `monthlyInstallment`، `maxRepaymentMonths`، `interestRate` | مقدار `نامشخص`، `متغیر`، خالی یا غیرقابل‌دسته‌بندی، وام را از **رتبه‌بندی اصلی** خارج می‌کند؛ امتیاز خنثی برای این چهار ویژگی ممنوع است. |
| نمایشی/غیرمستقیم | `requiredDepositAccount` و دیگر ستون‌های غیرمستقیم | دادهٔ نامشخص به‌صورت برچسب «نامشخص» نمایش داده می‌شود و به‌تنهایی مانع ranking نیست. |

برای مقدار `متغیر` در گروه محوری، importer ابتدا فقط با قواعد نسخه‌دار و قابل‌آزمون تلاش می‌کند بازه یا گزینه‌های مشخص را از ساختار داده/شرایط همان وام استخراج کند. اگر نتیجه چندپهلو، حدسی یا فاقد منبع ساختاری باشد، آن را unknown ثبت کن؛ parsing حدسی از متن آزاد ممنوع است. اگر مقدار قابل طبقه‌بندی شد، وام می‌تواند وارد ranking شود؛ در غیر این صورت در مجموعهٔ `needsReview` می‌ماند.

موتور باید دو خروجی مستقل داشته باشد:

- `rankedRecommendations`: فقط وام‌های دارای دستهٔ معتبر برای هر چهار ویژگی محوری؛ این‌ها امتیاز تطابق و رتبه می‌گیرند.
- `needsReview`: وام‌های فاقد دادهٔ قابل‌طبقه‌بندی در دست‌کم یک ویژگی محوری؛ این‌ها با `rankingExcludedReasons` نمایش داده می‌شوند و **هرگز** score، رتبه یا برچسب «پیشنهاد سازگار» نمی‌گیرند.

در UI، بخش دوم پس از نتایج اصلی با عنوانی مانند «گزینه‌هایی که برای مقایسهٔ دقیق به اطلاعات بیشتری نیاز دارند» نمایش داده شود. نمونه علت: «نرخ سود این طرح در دادهٔ فعلی مشخص نیست.» اگر `rankedRecommendations` خالی اما `needsReview` غیرخالی است، پیام «دادهٔ کافی برای رتبه‌بندی دقیق موجود نیست» نمایش بده؛ آن را با «هیچ وامی یافت نشد» یکی نکن.

فایل audit باید تعداد وام‌های هر گروه، نام/شناسه و دلیل هر حذف از ranking را گزارش کند. در وضعیت audit فعلی، نمونه‌های قابل‌بررسی شامل یک نرخ سود نامشخص، ۹ حداکثر مبلغ متغیر، ۱۲ مبلغ قسط متغیر و ۴ مدت بازپرداخت متغیر هستند؛ این اعداد را hard-code نکن و در هر اجرای audit دوباره محاسبه کن.

## محدودهٔ داده و واژگان ثابت

از شناسه‌های لاتین پایدار استفاده کن و متن فارسی فقط برچسب نمایشی باشد. هشت متغیر توصیه‌گر به ترتیب فیلتر عبارت‌اند از:

`maxAmount`, `monthlyInstallment`, `maxRepaymentMonths`, `interestRate`, `depositRequired`, `depositHoldingMonths`, `loanToDepositRatio`, `guaranteeType`.

دسته‌بندی هر متغیر باید دقیقاً از ماتریس گزینه‌ها ساخته شود: مبلغ ۸ دسته، قسط ۶، مدت ۶، سود ۵، سپرده ۲، خواب سپرده ۵، نسبت وام‌به‌سپرده ۴ و ضمانت ۳ دسته (`hardCollateral`, `thirdPartyUndertaking`, `personalUndertaking`). برای بازه‌های مرزی، قرارداد یکتا و مستند بساز؛ مثلاً بازهٔ پایین شامل ابتدا و بازهٔ بعدی شامل حد پایین خودش باشد. عددهای فارسی، فاصله‌ها، `تومان`، درصد، `متغیر` و `نامشخص` را با یک parser آزموده‌شده مدیریت کن؛ هرگز از متن نمایشی برای مقایسهٔ مستقیم استفاده نکن.

پرسش‌های canonical حداقل شامل `Q1` تا `Q6`، `S7`، `S8`، `S10` و `S13` هستند. گزینه‌ها باید `answerId` ثابت داشته باشند؛ به index صفحه یا ترتیب ظاهری وابسته نباش. پاسخ‌های ناقص باید قابل تشخیص باشند، نه اینکه وزن صفرِ بی‌صدا بگیرند.

## معماری مورد انتظار

بدون بازنویسی بی‌دلیل UI فعلی، کد را به مرزهای زیر تفکیک کن:

```text
src/features/recommendation/
  domain/       # نوع‌ها، category ids، schema و invariantها
  data/         # دادهٔ نرمال‌شده و نسخه‌دار؛ نه Excel در runtime مرورگر
  import/       # اسکریپت تبدیل Excel/CSV → JSON و data-audit
  engine/       # توابع pure برای امتیاز، مسیر، فیلتر و explainability
  ui/           # اتصال state پرسشنامه و صفحهٔ نتایج
  __tests__/    # unit, fixture, integration
```

Backend/منطق دامنه را در یک فایل بزرگ، component یا route پیاده‌سازی نکن. مرزهای زیر ضروری‌اند و هر ماژول باید مسئولیت واحد و API کوچک داشته باشد:

```text
src/features/recommendation/
  domain/entities/           # Loan, Answer, Category, RecommendationTrace
  domain/value-objects/      # Money, Percentage, Duration, CategoryId
  application/
    use-cases/               # RecommendLoans, GetLoanDetails, ValidateAnswers
    ports/                   # LoanRepository, RecommendationConfigRepository
  infrastructure/
    importers/               # Excel → normalized data (build-time)
    repositories/            # JSON/API adapter implementations
    parsers/                 # Persian value and conditions-list parsers
  engine/
    score-category.js
    traverse-candidate-tree.js
    normalize-loan-score.js
    apply-threshold.js
    build-trace.js
  presentation/
    questionnaire-route-map.js
    results-presenter.js
    loan-details-presenter.js
```

نام دقیق فایل‌ها می‌تواند با convention مخزن هماهنگ شود، اما مسئولیت‌ها نباید ادغام شوند. React فقط `use-case` را صدا می‌زند؛ در component هیچ parser Excel، فرمول امتیازدهی یا شرط کسب‌وکاری قرار نده. وابستگی‌ها رو به داخل باشند: `presentation → application → domain` و `infrastructure` فقط implementation portها باشد. برای رعایت SOLID، وابستگی‌ها inject شوند، use caseها به interface وابسته باشند، و تغییر یک source داده یا یک فرمول نیازمند ویرایش UI نباشد.

## معماری پایدار، مقیاس‌پذیر و قابل‌نگهداری

این بخش یک **قرارداد معماری** است، نه صرفاً پیشنهاد. هدف آن این است که افزودن قابلیت‌هایی مانند API واقعی بانک‌ها، پنل مدیریت وام، قوانین جدید، چند نوع تسهیلات، احراز هویت، تحلیل رفتار کاربر، A/B test یا تغییر کامل UI باعث نشود موتور توصیه‌گر دوباره نوشته شود.

### ۱. مرزهای محصول و ماژول‌ها

پروژه را بر پایهٔ قابلیت (feature) و درون هر قابلیت بر پایهٔ لایه سازمان‌دهی کن؛ نه بر اساس یک پوشهٔ بزرگ `components` یا `utils` مشترک. ساختار پیشنهادی:

```text
src/
  app/                         # composition root، router، providerها، bootstrap
  shared/                      # ابزارهای واقعاً عمومی و بدون وابستگی به توصیه‌گر
    ui/                        # Button, Modal, EmptyState؛ بدون منطق دامنه
    lib/                       # date/format/error helpers عمومی
    config/                    # environment validation و feature flags
  features/
    questionnaire/             # نمایش و ذخیره پاسخ‌های canonical
    recommendation/            # فقط منطق و UI توصیه‌گر
      domain/
      application/
      infrastructure/
      presentation/
      engine/
      tests/
    loan-details/              # use case و presenter جزئیات وام
  data/                        # خروجی نرمال و نسخه‌دار build-time؛ نه منطق
  scripts/                     # import، audit، migration و validation داده
  docs/architecture/           # ADR، قرارداد داده، runbook و تصمیم‌ها
```

اگر backend مستقل ایجاد شد، همان مرزها را در `server/` یا سرویس جدا با ساختاری معادل نگه دار. frontend نباید مستقیم به فایل Excel، دیتابیس یا provider بانکی وصل شود؛ فقط با یک API contract یا application port کار کند. تا زمانی که prototype client-only است، repository JSON همان contract را پیاده می‌کند تا جایگزینی با API واقعی بدون تغییر UI و engine ممکن باشد.

فقط مواردی که واقعاً میان چند feature مشترک‌اند وارد `shared/` شوند. تابعی که نام یا منطق وام، پرسشنامه یا recommendation دارد هرگز shared نیست. پوشه‌های مبهم مانند `helpers`, `misc`, `common`, `utils` بدون مالک دامنه ممنوع‌اند؛ اگر ابزار عمومی نیست، کنار همان feature قرار گیرد.

### ۲. قانون وابستگی و قراردادها

`domain` مستقل از React، HTTP، فایل، دیتابیس، Excel، زمان سیستم و framework است. `application` جریان کسب‌وکاری را هماهنگ می‌کند اما layout یا parsing فایل ندارد. `infrastructure` adapterهای بیرونی را پیاده می‌کند. `presentation` فقط ورودی UI را به command/use case و خروجی آن را به view model تبدیل می‌کند.

برای هر مرز یک قرارداد صریح و کوچک بساز:

- `LoanRepository`: `listRankableLoans()`, `listLoansNeedingReview()`, `getLoanById()`؛ نه یک متد چندمنظوره با ده‌ها flag.
- `RecommendationConfigRepository`: فقط خواندن نسخهٔ تأییدشدهٔ تنظیمات و وزن‌ها.
- `RecommendationEngine`: ورودی‌های typed/canonical و خروجی `RecommendationResult`; هیچ I/O نداشته باشد.
- `ConditionsListParser`: متن شرایط را به `string[]` امن تبدیل کند و هیچ JSX برنگرداند.
- `Clock`, `Logger`, `IdGenerator` فقط در صورت نیاز پشت interface قرار گیرند؛ abstraction بی‌مصرف نساز.

Composition root تنها محل ساختن adapterها و تزریق آن‌ها به use caseهاست. Component نباید بداند repository از JSON، API یا cache استفاده می‌کند. هیچ import از `infrastructure` در `domain` یا `engine` مجاز نیست؛ این قانون را با lint/import-boundary rule کنترل کن.

### ۳. اندازه و مسئولیت فایل‌ها

هر فایل باید یک دلیل روشن برای تغییر داشته باشد. به‌جای فایل‌های `recommendation-service.js` یا `App.jsx` چندصدخطی، عملیات را به واحدهای نام‌دار بشکن: `classifyLoan`, `scoreCategory`, `traverseCandidateTree`, `normalizeScores`, `buildTrace`, `parseConditions`, `mapQuestionRoute`.

- فایل بزرگ به‌تنهایی خطا نیست، اما اگر دو مسئولیت مستقل یا بیش از یک مسیر تغییر دارد، تقسیمش کن.
- یک component فقط هماهنگ‌کنندهٔ UI باشد؛ وضعیت محلی نمایش را نگه دارد اما قانون وام یا فرمول امتیاز را نه.
- توابع pure کوچک، ورودی/خروجی واضح و بدون mutation ترجیح دارند.
- objectهای بزرگ config را بر اساس variable و version تقسیم کن، نه یک فایل literal چندصدخطی.
- exportهای داخلی feature از یک facade محدود ارائه شود؛ featureهای دیگر به مسیرهای خصوصی آن import نکنند.
- circular dependency ممنوع است. هر بار که برای حل آن وسوسهٔ import متقابل ایجاد شد، مسئولیت‌ها یا contract اشتباه طراحی شده‌اند.

### ۴. رشد بدون بازنویسی

برای هر قابلیت جدید، ابتدا تعیین کن به کدام مرز تعلق دارد:

| تغییر آینده | محل صحیح |
| --- | --- |
| وزن/قانون جدید توصیه‌گر | config نسخه‌دار + engine + golden test |
| منبع جدید وام یا API بانک | adapter/repository جدید |
| پرسش جدید یا تغییر متن گزینه | questionnaire config + mapper + validation |
| فیلتر جدید صفحه نتایج | presentation/query state؛ بدون تغییر فرمول اصلی |
| محاسبه جدید مثل نرخ مؤثر | value object/domain service مستقل |
| پنل مدیریت وام | feature جدا که از application contract استفاده می‌کند |
| login، سطح دسترسی یا پروفایل | feature جدا؛ هرگز داخل engine |
| آزمایش A/B | feature flag در composition/config و trace نسخه‌دار |

اگر یک قابلیت بیش از یک مرز را تغییر می‌دهد، تغییرات را به commitهای مستقل و قابل تست تقسیم کن، اما contract و migration را اول بساز. از «generic engine» برای نیازهای فرضی نساز. انعطاف از قراردادهای کوچک، config نسخه‌دار، adapterها و تست‌های محکم می‌آید؛ نه از abstractionهای زیاد و کلاس‌های خالی.

### ۵. داده، نسخه‌بندی و تغییرات سازگار

هر schema داده باید `schemaVersion` داشته باشد و هر تنظیم توصیه‌گر `configVersion`, `approved`, `effectiveFrom`, `sourceReferences` و `decisionId`. importer باید idempotent باشد: اجرای مجدد روی همان ورودی باید خروجی یکسان بدهد. دادهٔ نرمال‌شده immutable تلقی شود؛ تغییر آن فقط از مسیر importer/migration و همراه audit ممکن است.

برای تغییرات ناسازگار، migration صریح بساز و هم‌زمان reader قدیمی را بی‌هشدار خراب نکن. feature flag یا adapter version اجازه می‌دهد نسخهٔ جدید ابتدا روی fixture و preview اجرا شود. trace هر نتیجه باید schema/config/data version را نگه دارد تا چند ماه بعد بتوان همان نتیجه را بازتولید و دیباگ کرد.

### ۶. مدیریت خطا، مشاهده‌پذیری و دیباگ

خطاهای expected مانند پاسخ ناقص، دادهٔ ناشناخته، no-result و timeout منبع داده باید typed/طبقه‌بندی شوند، نه اینکه همه با `catch` عمومی به پیام یکسان تبدیل شوند. UI فقط پیام امن فارسی دریافت می‌کند؛ جزئیات فنی در log/trace ساختاریافته ثبت می‌شود.

برای هر request یا اجرای recommendation یک `correlationId` بساز. در logهای ساختاریافته حداقل `correlationId`, `loanId`, `questionId`, `variable`, `categoryId`, `dataVersion`, `configVersion` و نوع خطا را نگه دار؛ پاسخ کاربر و اطلاعات شخصی را log نکن. داشبورد یا log بعدی باید بتواند نشان دهد کدام مرحله بیشترین exclusion، neutral value یا failure را دارد. این مشاهده‌پذیری برای تغییرات پیش‌بینی‌نشده دریچهٔ اصلاح است، نه بهانه‌ای برای ذخیره دادهٔ حساس.

### ۷. راهبرد refactor و کنترل بدهی فنی

قبل از تغییر، تست‌های موجود، contractهای public و مسیرهای وابسته را مشخص کن. ابتدا تست یا characterization test بنویس، سپس refactor کن، سپس رفتار قبلی را با test ثابت کن. refactor و تغییر کسب‌وکاری را در یک commit مخلوط نکن مگر جداسازی واقعاً ممکن نباشد؛ در آن حالت علت را در PR بنویس.

هیچ `TODO` بدون مالک، تاریخ بازبینی و لینک issue باقی نگذار. تکرار کوچک را فوراً abstraction نکن؛ بعد از مشاهدهٔ الگوی واقعی، آن را به ماژول مشترک استخراج کن. هر PR باید پاسخ دهد: «کدام مرز تغییر کرده؟»، «آیا API داخلی/داده شکسته؟»، «چه migration یا feature flag لازم است؟»، «چه تستی از regression جلوگیری می‌کند؟».

### ۸. گیت، کیفیت و release gate معماری

تعریف Done برای هر قابلیت شامل این موارد است: معماری مرزی رعایت شده، contract و data decision به‌روز است، unit/integration/E2E مرتبط پاس است، lint/typecheck و import-boundary check سبز است، documentation/ADR برای تصمیم مهم وجود دارد، trace خطا و rollback path مشخص است. هیچ feature جدیدی فقط با «درست کار کردن در مرورگر من» تمام‌شده نیست.

برای تغییرات پرریسک، ابتدا preview و fixture واقعی بساز؛ سپس PR بازبینی‌شده، سپس production. قابلیت جدید باید بتواند با feature flag خاموش شود یا با config version قبلی بازگردد، بدون اینکه داده یا نتایج قبلی را تخریب کند.

## امنیت، حریم خصوصی و تاب‌آوری در برابر دستکاری

هدف «نفوذناپذیری مطلق» نیست، چون چنین تضمینی واقع‌بینانه نیست. هدف، **دفاع در عمق** است: کاهش سطح حمله، حداقل‌سازی داده، محدودکردن اثر هر رخداد، تشخیص سریع، امکان بازیابی و جلوگیری از تکرار. هیچ قابلیت، API یا انتشار production بدون عبور از این release gate امنیتی کامل نیست.

### ۱. مدل تهدید و طبقه‌بندی داده

پیش از هر اتصال به backend، یک `docs/security/threat-model.md` بساز و برای هر دارایی، مهاجم، مسیر حمله، اثر، کنترل و مالک مشخص کن. حداقل تهدیدها: کاربر ناشناس، کاربر عادیِ مخرب، مدیر دسترسی‌گرفته، bot، مهاجم شبکه، dependency آلوده، credential افشاشده و خطای عملیاتی داخلی. مدل تهدید باید با هر قابلیت جدید یا تغییر داده به‌روزرسانی شود.

داده‌ها را دسته‌بندی کن:

| سطح | نمونه | سیاست |
| --- | --- | --- |
| عمومی | نام طرح، بانک و شرایط انتشارپذیر | integrity و منبع معتبر لازم است. |
| داخلی | نسخهٔ ماتریس‌ها، trace فنی، audit داده | فقط نقش‌های داخلی مجاز؛ بدون دادهٔ هویتی در لاگ. |
| حساس کاربر | پاسخ پرسشنامه، شماره تلفن، شناسهٔ کاربر، تاریخچهٔ نتیجه | کمینه‌سازی، رمزنگاری، کنترل دسترسی و retention محدود. |
| راز | کلید API، secret امضا، credential دیتابیس، کلید رمزنگاری | فقط secret manager؛ هرگز در کد، Excel، log، client، commit یا error message نیست. |

در نسخهٔ فعلی، پاسخ پرسشنامه را تا جای ممکن در client و session کوتاه‌عمر نگه دار. فقط اگر نیاز محصولی روشن وجود دارد آن را ذخیره کن؛ پیش از ذخیره، purpose، مدت نگهداری، مالک، روش حذف و رضایت کاربر را مستند کن. دادهٔ شخصی را برای آموزش، تحلیل یا اشتراک با شخص ثالث بدون مبنای روشن و رضایت مناسب بازاستفاده نکن.

### ۲. طراحی امن API و تبادل داده

تمام endpointهای production فقط از HTTPS با TLS معتبر استفاده کنند؛ HTTP را به HTTPS redirect کن و HSTS را پس از اطمینان از دامنه فعال کن. هر درخواست و پاسخ با schema validate شود؛ client قابل اعتماد نیست. API باید allowlist فیلدها داشته باشد، input را normalize کند، حد اندازهٔ body و timeout داشته باشد و خطاهای داخلی/stack trace را به client برنگرداند.

- برای هر endpoint مشخص کن: actor مجاز، purpose، input schema، output schema، rate limit، مجوز، audit event و خطاهای مورد انتظار.
- هر object را با شناسهٔ server-side و ownership check بخوان/ویرایش کن؛ دریافت ID از client هرگز به‌تنهایی مجوز نیست. این کنترل جلوی IDOR را می‌گیرد.
- پاسخ‌های recommendation و loan details نباید دادهٔ خصوصی کاربر دیگر، config محرمانه، کلید، path سرور یا trace کامل داخلی را برگردانند.
- CORS فقط برای originهای لازم، method/headerهای لازم و بدون wildcard همراه credential تنظیم شود.
- برای endpointهای تغییر‌دهندهٔ وضعیت، روش احراز هویت مناسب و در صورت cookie-based auth، CSRF protection و cookieهای `HttpOnly`, `Secure`, `SameSite` اعمال شود.
- rate limit، اندازهٔ request، pagination و quota برای جلوگیری از brute force، scraping مخرب و DoS سبک الزامی است. رفتار قابل قبول هنگام عبور: پاسخ عمومی `429`، بدون افشای داخلی، همراه `Retry-After` در صورت مناسب‌بودن.
- schema قرارداد API نسخه‌دار باشد؛ تغییر ناسازگار با version یا migration صریح منتشر شود.

### ۳. هویت، احراز هویت و مجوزها

اصل کمترین دسترسی را پیاده کن. نقش پیشنهادی حداقلی: `anonymous`, `user`, `support`, `data-editor`, `admin`, `service`. هر نقش فقط مجوزهای لازم را می‌گیرد؛ «admin به‌طور پیش‌فرض برای همه‌چیز» یا نقش‌های مبهم ممنوع است. authorization باید server-side و نزدیک use case اجرا شود، نه فقط با مخفی‌کردن دکمه در UI.

رمز عبور را خودت اختراع یا با الگوریتم ضعیف hash نکن. اگر product به حساب کاربری نیاز دارد، از provider/کتابخانهٔ معتبر استفاده کن و passwordها را فقط با password hashing مدرن و salt مدیریت کن. توکن‌ها کوتاه‌عمر، قابل ابطال و خارج از `localStorage` در سناریوی cookie-based باشند. refresh token، session revocation، MFA برای نقش‌های حساس، محدودیت تلاش ورود، recovery امن و logout سراسری را قبل از production طراحی و تست کن.

### ۴. حفاظت از داده، دیتابیس و یکپارچگی توصیه‌گر

دیتابیس نباید public باشد و اتصالش فقط از network/service identity مجاز باشد. account دیتابیس برای runtime حداقل مجوز لازم را داشته باشد؛ account جدا برای migration، read-only analytics و backup تعریف کن. queryها parameterized/ORM-safe باشند؛ query string با ورودی کاربر ممنوع است. constraintهای دیتابیس (primary/foreign key, unique, check, transaction) باید integrity را مستقل از UI حفظ کنند.

برای دادهٔ حساس در حالت سکون از encryption at rest ارائه‌دهنده و برای فیلدهای بسیار حساس از envelope encryption با کلید خارج از دیتابیس استفاده کن. کلیدها در secret/KMS نگهداری، دوره‌ای rotation و دسترسی‌شان audit شود. رمزنگاری جایگزین authorization یا backup امن نیست.

تمام تغییرات در دادهٔ وام، وزن‌ها، mappingها، config و تصمیم‌های audit باید append-only audit trail داشته باشد: actor، زمان، before/after، reason، version و correlation ID. کاربر عادی یا client هرگز نباید وزن‌ها، config، نسخهٔ داده یا score نهایی را تعیین یا overwrite کند. server باید recommendation را از دادهٔ تأییدشده محاسبه کند؛ اگر prototype محاسبه را در client انجام می‌دهد، آن را صرفاً نمایشی بدان و ادعای tamper-proof نکن.

برای تغییرات حساس، approval workflow و immutable version ایجاد کن: دادهٔ جدید ابتدا validate، سپس preview، سپس با نقش مجاز approved و قابل rollback شود. backup رمزنگاری‌شده، بازیابی آزمایش‌شده، retention و restore runbook لازم است. backup هم باید همان کنترل دسترسی production را داشته باشد.

### ۵. امنیت frontend، فایل و محتوا

از XSS جلوگیری کن: متن شرایط وام و همهٔ دادهٔ بیرونی را text render کن؛ `dangerouslySetInnerHTML` ممنوع است مگر sanitize allowlist‌شده، توجیه‌شده و تست‌شده. URLهای لینک و لوگو را validate/allowlist کن و برای تصویر fallback امن داشته باش. Content Security Policy حداقلی، `frame-ancestors`, `X-Content-Type-Options: nosniff`, `Referrer-Policy` و clickjacking protection را در deploy تنظیم کن.

فایل Excel فقط در مسیر trusted import پردازش شود؛ نوع، اندازه، sheet/columnهای مجاز و تعداد سطرها validate شوند. macro یا فرمت ناشناخته پردازش نشود. فایل بارگذاری‌شده با نام یا path کاربر ذخیره/اجرا نشود، path traversal رد شود و خروجی import قبل از publish audit شود. هیچ فایل source یا export حاوی اطلاعات شخصی بدون کنترل دسترسی و expiry در دسترس عمومی قرار نگیرد.

### ۶. secrets، dependency و زنجیرهٔ تأمین

secretها فقط از محیط امن/secret manager خوانده شوند و با schema startup validate شوند. `.env`، private key، token، backup و export حساس باید در `.gitignore` باشند؛ اما فقط `.gitignore` کافی نیست: secret scanner pre-commit و CI لازم است. در صورت افشای راز، آن را فوراً revoke/rotate کن؛ صرف حذف‌کردن از commit کافی نیست.

dependencyها را pin/lock کن، package manager lockfile را commit کن، dependency audit و vulnerability scan در CI اجرا کن، package ناشناس/بدون نگهداری را وارد نکن و به‌روزرسانی امنیتی را در PR جدا انجام بده. build باید reproducible باشد و artifact production از pipeline کنترل‌شده تولید شود، نه از لپ‌تاپ یا فایل build ناشناس.

### ۷. لاگ، پایش، پاسخ به رخداد و حریم خصوصی عملیاتی

لاگ‌ها ساختاریافته، کمینه و redact‌شده باشند. شماره تلفن، token، authorization header، cookie، پاسخ پرسشنامه، رمز، کلید، دادهٔ مالی دقیق و stack trace production نباید log شوند. alertهای حداقلی برای افزایش login failure، افزایش 403/429/5xx، تغییر غیرعادی config، export حجیم، شکست audit و دسترسی administrator تعریف کن.

یک `docs/security/incident-response.md` داشته باش: تشخیص، triage، محدودسازی، حفظ شواهد، rotation/revocation، اطلاع‌رسانی متناسب، بازیابی، postmortem بدون سرزنش و اقدام پیشگیرانه. برای هر رخداد، time line و تصمیم‌ها ثبت شوند. «خاموش‌کردن log» یا حذف شواهد راه‌حل نیست.

### ۸. تست امنیتی و release gate

تست امنیتی باید فقط روی محیط local/staging و حساب‌های آزمایشی انجام شود، نه علیه سامانهٔ ثالث یا production بدون مجوز صریح. هر تست باید automation‌پذیر باشد و نتیجه در PR ثبت شود. این سناریوها حداقل الزامی‌اند:

| سناریو | مراحل آزمون | پاسخ قابل قبول |
| --- | --- | --- |
| اعتبارسنجی ورودی | payload نامعتبر، فیلد اضافی، body بزرگ، type غلط، Unicode غیرمنتظره ارسال کن | `400/422` کنترل‌شده؛ بدون crash، ذخیره یا stack trace. |
| احراز هویت | endpoint محافظت‌شده را بدون/با token منقضی فراخوانی کن | `401` عمومی؛ هیچ داده‌ای نشت نکند. |
| مجوز و IDOR | کاربر A شناسهٔ دادهٔ کاربر B را درخواست/ویرایش کند | `403` یا `404` یکسان با سیاست؛ داده بدون تغییر بماند. |
| CSRF | با session cookie، درخواست تغییر‌دهنده را از origin نامعتبر شبیه‌سازی کن | درخواست رد شود؛ وضعیت تغییر نکند. |
| XSS | متن شرایط/نام وام حاوی payload بی‌خطر آزمون قرار بده | فقط متن نمایش داده شود؛ script/event اجرا نشود. |
| Injection | ورودی query، شناسه و فیلتر با الگوهای injection آزموده شوند | validation/parameterization؛ بدون خطای دیتابیس یا دادهٔ اضافه. |
| Rate limiting | درخواست‌های سریع بیش از quota به login/search/API بفرست | `429` و سرویس پایدار؛ quota بعد از window مشخص بازیابی شود. |
| CORS/headers | origin نامجاز و پاسخ headers بررسی شود | origin/credential ناخواسته مجاز نباشد؛ headers امنیتی حاضر باشند. |
| Secret leakage | source، build artifact، log و error response را با secret scan بررسی کن | هیچ secret معتبر یا دادهٔ حساس یافت نشود. |
| دادهٔ حساس | بررسی کن پاسخ کاربر در log، URL، analytics، cache عمومی یا client storage بلندمدت نیست | صفر نشت؛ retention و deletion مطابق policy. |
| دستکاری score/config | تلاش کن request/client state امتیاز، وزن یا version را تغییر دهد | server مقدار canonical را محاسبه/رد کند؛ audit event ثبت شود. |
| دیتابیس و migration | اجرای role غیرمجاز، query ناقص و migration شکست‌خورده را شبیه‌سازی کن | کمترین دسترسی، rollback امن، integrity و backup سالم. |
| dependency | audit/SCA و license policy روی lockfile اجرا شود | vulnerability بحرانی یا با exploit شناخته‌شده بدون mitigation پذیرفته نیست. |
| بازیابی | restore آزمایشی backup را در محیط جدا اجرا کن | داده و version صحیح، دسترسی محدود و زمان بازیابی ثبت‌شده. |

افزون بر این‌ها، SAST در هر PR، dependency/secret scan در CI و DAST سبک روی staging پیش از release اجرا شوند. هر یافتهٔ بحرانی یا high قابل exploitation، secret افشاشده، bypass مجوز، XSS تأییدشده، نشت دادهٔ حساس یا فقدان restore تست‌شده، **blocker انتشار** است. یافتهٔ medium فقط با owner، mitigation، deadline و پذیرش ریسک مستند می‌تواند موقتاً عبور کند؛ یافتهٔ low باید backlog مالک‌دار داشته باشد.

پیش از انتشار، یک checklist امضاشده/ثبت‌شده ایجاد کن: threat model به‌روز، schema و access control تست‌شده، secrets scan پاک، SAST/SCA/DAST نتیجه‌دار، backup restore تست‌شده، logging redacted، dependencyهای بحرانی رفع‌شده و plan واکنش رخداد موجود. هیچ‌کدام با تأیید شفاهی جایگزین نشوند.

## طراحی PostgreSQL، FastAPI و پایپ‌لاین داده

Backend قطعی پروژه **FastAPI + PostgreSQL** است. از backend موقتِ داخل React، endpointهای بدون schema، SQLite production یا اتصال مستقیم frontend به دیتابیس استفاده نکن. طراحی باید از ابتدا برای رشد تعداد وام‌ها، بانک‌ها، نسخه‌های داده، قوانین توصیه‌گر، کاربران و عملیات مدیریتی آماده باشد؛ اما فقط نیازهای واقعی را مدل کند و از جدول/میکروسرویس فرضی پرهیز کند.

### ۱. ساختار backend و استانداردهای پیاده‌سازی

ساختار پیشنهادی را در مخزن ایجاد و مستند کن:

```text
backend/
  app/
    main.py                    # FastAPI composition root
    api/v1/                    # routerهای versioned؛ فقط HTTP concerns
    core/                      # settings, security, logging, dependency wiring
    domain/                    # entity, value object, domain rule
    application/               # command/query use cases و portها
    infrastructure/
      db/                      # SQLAlchemy models, session, repositories
      importers/               # Excel → staging/core pipeline
      external/                # provider/API adapters
    schemas/                   # Pydantic request/response schemaها
    tests/                     # unit, integration, API, security, pipeline
  alembic/                     # migrationهای قابل تکرار و reviewable
  scripts/                     # import, audit, seed, backup verification helpers
  docs/
    architecture/
    database/
    api/
    data-pipeline/
    runbooks/
```

از FastAPI dependency injection برای session، authenticated actor، logger و use case استفاده کن. router هیچ query پیچیده، قانون scoring یا ORM composition نداشته باشد؛ router input schema را می‌گیرد، use case را صدا می‌زند و response schema برمی‌گرداند. Pydantic برای تمام مرزهای HTTP، environment settings و import payload الزامی است. ORM پیشنهادی SQLAlchemy 2.x است و migrationها باید با Alembic ایجاد شوند. اتصال PostgreSQL از pool کنترل‌شده با timeout، health check و transaction scope مشخص انجام شود.

### ۲. مدل دادهٔ نرمال و قابل‌گسترش

حداقل تا 3NF نرمال‌سازی کن: هر fact تنها یک منبع حقیقت داشته باشد، دادهٔ تکراری قابل‌مغایرت نداشته باشیم، و many-to-many با جدول واسط مدل شود. نرمال‌سازی را فقط وقتی با read-performance تعارض واقعی دارد و با measurement اثبات شده است، به‌صورت denormalization مستند و قابل بازسازی بشکن. JSONB برای دادهٔ واقعاً انعطاف‌پذیر/نسخه‌دار و غیرقابل‌پیش‌بینی مجاز است؛ برای ستون‌هایی که query، filter، join، constraint یا integrity لازم دارند جای جدول نرمال نیست.

مدل اولیه باید حداقل این موجودیت‌ها و روابط را بررسی و در ERD نهایی تعیین کند:

| حوزه | جدول‌های محتمل و مسئولیت |
| --- | --- |
| مرجع | `lenders`, `loan_products`, `loan_product_versions`, `loan_terms`, `guarantee_types`, `deposit_account_types` |
| طبقه‌بندی و توصیه‌گر | `loan_variables`, `variable_categories`, `questionnaire_versions`, `questions`, `answer_options`, `recommendation_config_versions`, `question_variable_weights`, `answer_category_compatibilities` |
| کاربر و نتیجه | `users` فقط در صورت نیاز، `questionnaire_sessions`, `questionnaire_answers`, `recommendation_runs`, `recommendation_results`, `recommendation_exclusion_reasons` |
| ورود و حکمرانی داده | `data_import_runs`, `data_source_files`, `staging_loan_rows`, `data_quality_issues`, `approval_records`, `audit_events` |

نام جدول و column به `snake_case`، کلیدها با `uuid` یا سیاست ID مستند و timestampها با `timestamptz` در UTC باشند. برای هر جدول، primary key، foreign key، `NOT NULL`، `UNIQUE`، `CHECK`، default، owner و retention مشخص کن. حذف فیزیکی برای دادهٔ حساس یا دارای سابقه فقط با policy و در صورت لازم soft-delete (`deleted_at`) باشد؛ از soft-delete بی‌دلیل برای همهٔ جدول‌ها استفاده نکن.

`loan_products` هویت پایدار طرح را نگه دارد و `loan_product_versions` شرایط نسخه‌دار آن را؛ رکورد توصیه همیشه به نسخهٔ دقیق وام و config دقیق وصل شود. مقدارهای محوری مثل نرخ، مبلغ، قسط و مدت باید typed/numeric باشند؛ متن فارسی خام فقط در source/staging یا فیلد توضیحی باقی بماند. نسبت وام به سپرده، سپرده و ضمانت با رابطه/کلید خارجی و category استاندارد مدل شوند، نه stringهای تکراری. برای وضعیت `unknown`, `variable`, `neutral` و `ranking_excluded` enum یا state صریح بساز؛ آن‌ها را در null مبهم پنهان نکن.

### ۳. ایندکس، query و کارایی

ایندکس را از queryهای واقعی طراحی کن، نه از روی حدس. برای foreign keyها، lookupهای loan/lender/version، فیلترهای رایج recommendation و constraintهای یکتا index مناسب ایجاد کن. `EXPLAIN (ANALYZE, BUFFERS)` را برای queryهای حیاتی در محیط نماینده اجرا و نتیجه را مستند کن. از N+1، `SELECT *`، pagination بدون order پایدار، joinهای غیرضروری و index بیش‌ازحد اجتناب کن.

pagination برای لیست‌ها cursor یا limit/offset محدود و order deterministic داشته باشد. عملیات import/bulk در batch و transactionهای کوتاه انجام شود؛ یک transaction بزرگ که lock طولانی ایجاد کند ممنوع است. indexهای سنگین یا migrationهای پرخطر با روش compatible/online و plan rollback اجرا شوند. cache فقط پس از اندازه‌گیری، با TTL/invalidation و بدون cache کردن دادهٔ حساس مشترک افزوده شود.

### ۴. پایپ‌لاین داده: raw → staging → core → serving

Excel منبع خام است، نه schema runtime. پایپ‌لاین باید idempotent، نسخه‌دار، قابل تکرار و قابل audit باشد:

1. **Ingest/raw:** فایل منبع را با hash، منبع، زمان دریافت، version و مالک ثبت کن؛ فایل اصلی immutable بماند.
2. **Staging:** هر سطر و مقدار خام را بدون ازبین‌بردن provenance وارد `staging_*` کن؛ validation اولیهٔ نوع، header، تعداد ستون، encoding و duplicate انجام بده.
3. **Normalize/core:** parserهای تست‌شده مبلغ/درصد/مدت/متن فارسی را به typeهای canonical تبدیل کنند؛ category، status و روابط مرجع ایجاد شوند.
4. **Validate/audit:** قواعد business، FK/unique/check، پوشش دسته‌ها، unknown/variable، ناسازگاری mapping، شمارش وام‌های rankable/needs-review و تغییرات نسبت به import قبلی را گزارش کن.
5. **Approve/publish:** فقط import تأییدشده با approval record به read model/serving version تبدیل شود. اجرای ناموفق یا ناقص نباید دادهٔ serving را تغییر دهد.
6. **Observe/rollback:** metrics، issueها، version و قابلیت برگشت به serving version قبلی ثبت شوند.

در pipeline هر تبدیل باید provenance داشته باشد: `source_file_id`, `source_row_number`, `source_column`, parser/version و rule decision. تغییر خام داده ممنوع است؛ correction با transformation یا نسخهٔ جدید ثبت می‌شود. مورد ambiguous را auto-correct نکن؛ به `data_quality_issues` بفرست تا role مجاز بررسی و approval کند.

### ۵. migration، seed و عملیات دیتابیس

تنها مسیر تغییر schema، Alembic migrationهای version-controlled است. هر migration باید upgrade و downgrade عملی، test شده، بدون data loss ناخواسته و همراه توضیح هدف/اثر/rollback باشد. migrationها را دستی روی production اجرا نکن؛ CI ابتدا روی DB خالی و سپس روی fixture نسخهٔ قبل اجرا کند. seed data از migration جداست و idempotent اجرا می‌شود؛ seed هرگز دادهٔ production را overwrite نمی‌کند.

برای هر release، ترتیب deployment مستند باشد: migration سازگار → deploy backend → backfill در job جدا → switch feature/config → حذف فیلد قدیمی در release بعد. تغییر breaking با expand/contract انجام شود، نه rename/drop ناگهانی. health/readiness endpoint باید آماده‌بودن اتصال DB و migration version مورد انتظار را بدون افشای secret بررسی کند.

### ۶. مستندات اجباری داخل مخزن

هم‌زمان با ایجاد schema، این فایل‌ها را بساز و در هر تغییر DB/API به‌روزرسانی کن:

- `docs/database/erd.md`: نمودار Mermaid ERD، cardinatlity، توضیح روابط و مرز هر bounded context.
- `docs/database/data-dictionary.md`: برای هر جدول/ستون، type، nullable، default، constraint، منبع، مثال غیرحساس و مالک.
- `docs/database/index-and-query-strategy.md`: queryهای کلیدی، indexهای مربوط، دلیل و نتایج `EXPLAIN`.
- `docs/database/migrations-and-rollback.md`: ترتیب migration، backfill، rollback و restore.
- `docs/data-pipeline/pipeline.md`: مراحل raw/staging/core/serving، validation، approval و runbook خطا.
- `docs/api/openapi.md`: نسخه‌بندی، authentication، endpointها، schema و error codeها؛ OpenAPI تولیدی FastAPI نیز در CI export شود.
- `docs/backend/module-map.md`: نقشهٔ پوشه‌ها، مسئولیت هر ماژول، dependency direction و راهنمای توسعهٔ قابلیت جدید.

ERD باید از schema واقعی ساخته یا در CI با آن تطبیق داده شود؛ نمودار دستیِ قدیمی قابل قبول نیست. هر PR که DB/API/backend را تغییر می‌دهد، باید همان PR مستندات مرتبط و لینک migration/test را هم تغییر دهد.

### ۷. استاندارد کامنت‌گذاری و مستندسازی کد

در تمام کدهای backend، کامنت‌های **مفصل ولی معنادار** بنویس. کامنت نباید صرفاً کد بدیهی را تکرار کند؛ باید «چرایی»، محدودیت دامنه، فرض، اثر امنیتی، دلیل تصمیم، invariant، مرز transaction، دلیل index یا ملاحظهٔ rollback را توضیح دهد. برای moduleهای عمومی docstring با هدف، ورودی/خروجی، خطا، side effect و مثال کوتاه بنویس. برای use caseها، parserها، queryهای غیر بدیهی، migrationها، decisionهای scoring و کنترل‌های امنیتی، توضیح کافی الزامی است.

کامنت منقضی بدتر از نداشتن کامنت است: همراه با تغییر کد، comment/docstring/docs مرتبط را به‌روزرسانی کن. `TODO` باید owner، دلیل و لینک issue داشته باشد. READMEهای کوتاه داخل هر bounded context باید نقش آن پوشه، public API و ممنوعیت dependency را توضیح دهند. کامنت نباید secret، دادهٔ واقعی کاربر یا جزئیات حساس عملیاتی را افشا کند.

### ۸. برنامهٔ تست دیتابیس و پایپ‌لاین

| سناریو | مراحل | معیار قبولی |
| --- | --- | --- |
| schema خالی | همه migrationها را روی PostgreSQL خالی اجرا کن | schema، constraint و ERD/data dictionary سازگارند. |
| upgrade واقعی | fixture نسخهٔ قبلی را migrate کن | داده از بین نرود، queryهای اصلی کار کنند و downgrade/test rollback مشخص باشد. |
| import تکراری | یک Excel یکسان را دو بار ingest کن | duplicate business record یا تغییر serving version ایجاد نشود. |
| دادهٔ خراب | header/نوع/عدد فارسی/مقدار ambiguous نامعتبر وارد کن | staging issue ثبت شود؛ core/serving دست‌نخورده بماند. |
| integrity | FK، unique، check و enum را نقض کن | DB عملیات را رد کند، نه UI یا application به‌تنهایی. |
| transaction | خطا در میانهٔ import یا approval بساز | atomic rollback؛ دادهٔ نیمه‌کاره منتشر نشود. |
| performance | queryهای ranking/details با حجم representative اجرا شوند | plan بررسی‌شده، N+1 ندارد و budget زمانی مستند پاس می‌شود. |
| concurrency | دو update/approval هم‌زمان شبیه‌سازی کن | isolation/locking مانع overwrite ناخواسته و version conflict شود. |
| authorization | roleهای مختلف repository/use case را امتحان کن | فقط role مجاز دادهٔ لازم را می‌خواند/می‌نویسد. |
| backup/restore | snapshot آزمایشی را در محیط جدا restore کن | schema، data version و audit trail قابل بازیابی هستند. |

قبل از انتشار، migration test، import/audit test، integration test FastAPI با PostgreSQL واقعی، performance smoke test، security gate و مستندات generated باید همگی سبز باشند. SQLite mock به‌تنهایی برای قبولی دیتابیس کافی نیست.

- از schema validation (مثلاً Zod یا معادل سبک) در مرز ورود داده استفاده کن.
- منبع داده باید از یک adapter جدا خوانده شود؛ prototype می‌تواند JSON نسخه‌دار داشته باشد، اما قرارداد adapter باید آمادهٔ API/دیتابیس باشد.
- فقط داده‌ای که شرط‌های ضروری نمایش دارد وارد candidateها شود: نام وام، نام ارائه‌دهنده، شرایط اصلی و روش اقدام/ثبت درخواست. موارد ناقص را با علت در audit ثبت کن.
- مدل باید برای هر نتیجه یک `RecommendationTrace` تولید کند: نسخهٔ داده/پیکربندی، پاسخ‌های ورودی، امتیاز هر دسته، مسیرهای معتبر، علت حذف، raw score، score نرمال‌شده و هش ثابت. این trace برای UI توضیح‌پذیری و دیباگ است؛ اطلاعات حساس کاربر را در لاگ عمومی ننویس.

## منطق موتور

### ۱. اعتبارسنجی و نرمال‌سازی

پاسخ‌ها را validate کن. هر پرسش لازم باید دقیقاً یک پاسخ شناخته‌شده داشته باشد. وام‌ها را از دادهٔ خام به نوع استاندارد تبدیل کن و دستهٔ هر ۸ متغیر را محاسبه کن. `unknown` یک مقدار معتبر برای نمایش خام نیست؛ اگر متغیر لازم برای یک مرحله unknown است، علتش باید در trace مشخص باشد.

### ۲. امتیاز دسته‌ها

برای هر `loanVariable` و `category`، ضریب سازگاری پاسخ‌ها را از ماتریس یک‌به‌یک بخوان. وزن پرسش را از پیکربندی نسخه‌دار بخوان. فرمول پایه:

```text
normalizedQuestionWeight = questionWeight × answerWeight
categoryScore(variable, category) = Σ(normalizedQuestionWeight × impactFactor)
```

همهٔ مؤلفه‌ها، جمع و منبع سلول/شناسه در trace ثبت شود. امتیازها را فقط با یک قانون مستند نرمال کن؛ rounding فقط برای نمایش است، نه مقایسه.

برای ویژگی خنثی، به‌جای قراردادن `0` در صورت کسر، contribution آن متغیر را از جمع و وزن مؤثر همان وام خارج کن. مثال: اگر `depositHoldingMonths` وام «نامشخص» است، امتیاز متغیرهای دیگر حفظ می‌شود و این متغیر نه وام را پاداش می‌دهد نه جریمه. `rawLoanScore`, `effectiveWeight` و فهرست `neutralVariables` باید همگی در trace دیده شوند تا نتیجه قابل بازتولید باشد.

### ۳. کشف candidate با جست‌وجوی درختی

برای هر متغیر، دسته‌ها را با `categoryScore` نزولی و با tie-break ثابت `categoryId` مرتب کن. با ترتیب هشت‌گانهٔ بالا درخت بساز، هر گره مجموعهٔ وام‌های منطبق با دسته‌های انتخاب‌شده تا آن مرحله است و شاخهٔ خالی فوراً prune می‌شود. مسیر معتبر باید شناسهٔ دسته‌ها و وزن‌ها را نگه دارد.

```text
pathScore = Π(categoryWeight در مسیر)
rawLoanScore = Σ(pathScore برای همهٔ مسیرهای معتبرِ آن وام)
normalizedScore = rawLoanScore / max(rawLoanScore بین candidateها) × 100
```

ترتیب پیمایش درخت مجاز نیست رتبهٔ نهایی را تعیین کند؛ sort نهایی فقط `normalizedScore DESC, stableLoanId ASC` است. در امتیاز برابر، رتبه‌بندی ثانویهٔ تجاری ایجاد نکن.

### ۴. هم‌زیستی با منطق فیلتر مرحله‌ای

اسناد از «فیلتر مرحله‌ای» و آستانهٔ پیشنهادی ۵۰٪ نیز صحبت می‌کنند. این را با درخت در یک abstraction سازگار کن: فیلتر مرحله‌ای همان تقاطع محدودیت‌ها در هر مسیر است، نه الگوریتم موازی با نتایج متناقض. `minimumMatchScore` باید پیکربندی نسخه‌دار با مقدار اولیهٔ 50 باشد. وام‌های زیر آستانه نمایش داده نشوند، ولی برای دیباگ در trace باقی بمانند. اگر مالک محصول حالت متفاوتی خواست، آن را با `strategy` صریح و آزمایش‌های مستقل اضافه کن؛ دو فرمول را مخلوط نکن.

### ۵. رفتارهای الزام‌آور

- candidate صفر: خطا نده؛ پیام بازبینی پاسخ/گسترش جست‌وجو و مسیر بازگشت بده.
- صفر نتیجه پس از فیلترهای دستی UI: آن را صریحاً از «هیچ وام سازگاری نیست» جدا نشان بده.
- نتایج زیاد: هیچ candidate معتبری را برای کوتاه‌کردن لیست حذف نکن.
- ترجیحات متضاد: حل یا دستکاری نکن؛ نزدیک‌ترین گزینه‌ها را با توضیح نشان بده.
- تغییرات شرایط وام: رکورد دارای `sourceUrl`, `sourceCheckedAt`, `dataVersion` باشد؛ منبع رسمی بانک بر دادهٔ قدیمی غلبه دارد.
- عبارت «بهترین وام»، «تأیید می‌شوید» یا ادعای قطعی استفاده نکن.

## تجربهٔ کاربری

جریان فعلی پرسشنامه را حفظ کن، اما داده‌محور کن. هر مرحله با `questionId` مدیریت شود، نه شمارهٔ hard-coded. قبل از حرکت بعدی، پاسخ لازم را validate کن. صفحهٔ نتیجه باید برای هر وام نام، بانک، شرایط مهم، امتیاز تطابق، دلیل‌های اصلی سازگاری، هشدارها و لینک/روش اقدام را نمایش دهد. «امتیاز تطابق» را با متن شفاف توضیح بده که مقایسهٔ شرایط با ترجیحات کاربر است، نه شانس دریافت وام.

RTL، موبایل و مسیرهای بازگشت را تست کن. حالت loading، دادهٔ نامعتبر، صفر candidate، صفر نتیجه پس از فیلتر دستی و خطای بارگذاری را جدا طراحی کن. هیچ آیکن یا تصویر external بدون fallback معتبر رندر نشود.

## تست و دیباگ؛ شرط پایان کار

یک pipeline قابل اجرا اضافه کن و پیش از پایان همه را اجرا کن:

1. `data-audit`: ساختار همهٔ فایل‌های ورودی، یکتایی شناسه‌ها، پوشش ۸ متغیر، پوشش همهٔ گزینه‌های پرسشنامه، وزن‌ها و ضرایب، بازهٔ `[0,1]`، مرزهای دسته‌ها، تکراری بودن وام، داده‌های نامشخص و وضعیت شرط‌های ضروری نمایش.
2. unit: parser اعداد فارسی، دسته‌بندی مرزی، `categoryScore`، prune درخت، جمع `pathScore`، نرمال‌سازی، threshold 50، tie determinism و trace.
3. fixture: حداقل یک سناریو برای هر پاسخ Q1–Q6/S7/S8/S10/S13 و golden fixturesی که نتیجه/اجزای امتیازشان ثابت است.
4. edge/integration: پاسخ ناقص، دسته/ضریب گمشده، وام ناقص، صفر candidate، فیلتر دستی صفر، نتایج زیاد، امتیاز مساوی، ترجیحات متضاد و دادهٔ `متغیر/نامشخص`.
5. property tests یا آزمون داده‌ای: score منفی نشود، score نرمال‌شده در `[0,100]` باشد، تغییر ترتیب رکوردهای ورودی رتبه‌های نامساوی را عوض نکند، و هیچ شاخهٔ خالی به candidate نرسد.
6. build/lint/typecheck و یک E2E مرورگر برای تکمیل پرسشنامه، رسیدن به نتیجه، بازگشت و نمایش هر حالت خطا.

### برنامهٔ اجرای تست‌ها

تست‌ها را فقط در انتهای کار اجرا نکن؛ بعد از هر گام زیر تست‌های همان گام را اجرا کن و تنها با نتیجهٔ سبز به گام بعد برو:

| گام | تست اجباری | معیار عبور |
| --- | --- | --- |
| داده و import | parser، schema، data-audit | همهٔ داده‌های قابل‌استفاده نرمال‌اند؛ دادهٔ unknown به neutral trace می‌رسد. |
| domain | دسته‌بندی مرزی، value objectها، mapping وزن‌ها | `interestRate.Q5 = 0.10` و مجموع وزن `1.00` است. |
| engine | score، tree، threshold، tie، neutral | unknown نه rank را بهتر می‌کند نه بدتر و در مخرج مؤثر وارد نمی‌شود. |
| application | repository fake، پاسخ ناقص، loan ناقص | use case بدون React و با fixture قابل اجراست. |
| UI | route mapping، conditions bullets، RTL | ده مسیر جدول به ID درست متصل‌اند؛ متن Excel به bulletهای صحیح نمایش می‌رسد. |
| E2E/release | جریان کامل، برگشت، no-result، فیلتر دستی، جزئیات وام | build، lint و E2E کامل سبز است. |

برای حالت neutral، دست‌کم این سه golden test داشته باش: (الف) وام کامل، (ب) همان وام با `نامشخص` در یکی از سه ویژگی، (ج) همان وام با دستهٔ مشخص ولی سازگاری پایین. حالت ب باید از حالت ج امتیاز بالاتری داشته باشد و trace آن `neutral` را ثبت کند؛ مقایسهٔ حالت الف و ب نباید به‌علت neutral، پاداش ساختگی بدهد.

برای `loan-details`، fixtureهایی شامل بولت با `•`، خط جدید، bullet تو در تو، متن ساده و سلول خالی بساز. test باید نشان دهد خروجی در ترتیب اصلی، بدون bullet خالی یا تکراری و بدون تزریق HTML رندر می‌شود.

برای route map، یک test جدولی و یک E2E بنویس که مستقیماً `/question/3` تا `/question/12` را باز می‌کند و `questionId` مورد انتظار را بررسی می‌کند. تغییر شمارندهٔ کلی سؤال، صفحهٔ اطلاعات فردی یا ترتیب UI نباید این mapping را بشکند.

## ترتیب اجرای بدون دوباره‌کاری

این ترتیب را رعایت کن؛ هیچ UI، API یا الگوریتمی را پیش از قرارداد داده و تست آن نساز:

1. **Baseline:** شاخه بساز، build فعلی و test فعلی را اجرا کن، ساختار و نقاط mock را ثبت کن. هیچ refactor نکن.
2. **قرارداد و audit داده:** schema، IDها، parserها، `data-audit` و data-decision versioned را بساز؛ اصلاح `interestRate.Q5=0.10`، neutral فقط برای سه ویژگی سپرده و سیاست exclusion از ranking برای چهار ویژگی محوری را اینجا ثبت کن. تست‌های این لایه باید پاس شوند.
3. **تبدیل داده:** Excel را فقط در build/import به JSON نرمال تبدیل کن؛ نتیجهٔ تبدیل را snapshot و validate کن. تا اینجا هیچ componentی تغییر نده.
4. **دامنه و موتور خالص:** entityها، ports و توابع engine را با fixture بساز. ابتدا unit و golden tests، سپس implementation. هیچ import از React در این لایه مجاز نیست.
5. **لایهٔ کاربرد:** `RecommendLoans` و `GetLoanDetails` را با repository adapter پیاده کن؛ integration test با fake repository اجرا کن.
6. **اتصال ناوبری پرسشنامه:** route map جدول بالا را در یک فایل واحد بساز، پاسخ‌های UI را به `answerId` canonical تبدیل کن، و فقط سپس جریان نتایج mock را به use case واقعی وصل کن.
7. **جزئیات وام:** presenter شرایط و مقررات را با parser امن به bulletها تبدیل کن؛ UI test و E2E آن را اجرا کن.
8. **سخت‌سازی UI:** loading/error/no-result، explainability، RTL و دسترسی‌پذیری را اضافه کن؛ منطق کسب‌وکاری را به UI برنگردان.
9. **release gate:** audit نهایی، تمام تست‌ها، build، lint/typecheck، E2E و مرور trace نمونه را اجرا کن. فقط در صورت سبز بودن همه و `approved: true` بودن تصمیم‌های داده‌ای، preview/production را پیشنهاد بده.

در هر گام، اگر تست شکست خورد، ابتدا همان لایه را اصلاح کن و به گام بعد نرو. «اصلاح موقت در UI» برای پوشاندن نقص داده یا موتور ممنوع است.

هنگام شکست، خروجی باید حداقل `dataVersion`, `configVersion`, `questionId`, `answerId`, `loanId`, `variable`, `categoryId` و مسیر محاسبه را بدهد؛ ولی اطلاعات شناسایی شخصی کاربر را چاپ نکند.

## روش کار گیت

1. از `main` شاخه‌ای مانند `feature/recommendation-engine` بساز.
2. اول commitهای کوچک و جدا: `docs/data-audit`، `feat(domain-data)`، `feat(engine)`، `feat(ui)`، `test(recommendation)`.
3. مستقیم روی `main` push نکن. Pull Request بساز و در آن منابع، اختلاف‌های داده، تصمیم‌های موقت، فرمان‌های تست و نتیجهٔ هر تست را بنویس.
4. داده، الگوریتم و ظاهر را در یک commit درهم نریز. برای هر تغییر مدل/وزن `configVersion` را افزایش بده و golden fixtureها را بازبینی کن.
5. هیچ secret، کلید، دادهٔ شخصی یا credential را commit نکن.

## تحویل نهایی

پس از پیاده‌سازی، گزارش کوتاهی بده که شامل این‌ها باشد: فایل‌های تغییرکرده، تصمیم‌های داده‌ای باز، تعداد وام‌های قابل استفاده/حذف‌شده با علت، نسخهٔ پیکربندی، نمونهٔ trace، فرمان‌های اجرا و تست، وضعیت build/E2E و لینک PR. اگر اختلاف داده‌ای هنوز تأیید نشده، آن را blocker انتشار production اعلام کن؛ در غیر این صورت نتیجه را در محیط preview منتشر کن.
