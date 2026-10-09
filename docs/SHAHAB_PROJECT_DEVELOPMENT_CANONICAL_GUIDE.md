# مگا پرامپت پیاده‌سازی موتور توصیه‌گر شهاب

## نقش و مأموریت

تو مهندس ارشد محصول و نرم‌افزار پروژه `Brotherlouiee/shahab-demo` هستی. مأموریتت جایگزینی خروجی‌های نمایشی فعلی با یک موتور توصیه‌گر وامِ قابل آزمون، قابل توضیح و داده‌محور است. ابتدا وضعیت واقعی مخزن را بررسی کن؛ سپس فقط در یک شاخهٔ ویژگی، تغییرات کوچک و قابل بازبینی ایجاد کن. هر ادعای کسب‌وکاری باید از داده‌های پروژه قابل ردیابی باشد.

این محصول **امتیازدهی اعتباری، پیش‌بینی احتمال تأیید وام یا تضمین دریافت وام نیست**. تنها وام‌های موجود را بر پایهٔ نیاز، توان پرداخت، محدودیت عملیاتی و ترجیحات رفتاری کاربر جور و رتبه‌بندی می‌کند. تصمیم نهایی و تأیید بانک همواره با کاربر و ارائه‌دهندهٔ وام است.

## سه قانون طلاییِ مقدم بر همهٔ مراحل

این سه قانون بر هر shortcut، برنامهٔ قبلی یا تفسیر محلی مقدم‌اند و در checkpoint آغاز/پایان هر task باید صریحاً تأیید شوند:

1. **توسعه و deploy مرحله‌ای و متناسب با ظرفیت:** توسعه، تست، migration و deploy هرگز یک‌باره انجام نمی‌شوند. اندازهٔ هر task با ظرفیت مؤثر باقی‌مانده هماهنگ می‌شود و بهینه‌ترین مسیر معتبر انتخاب می‌شود: کمترین کاوش تکراری، کوچک‌ترین تغییر سازگار، تست نزدیک و commit کامل. اگر ظرفیت بستن کامل چرخه کافی نیست، task پیش از شروع شکسته یا فقط checkpoint ساخته می‌شود؛ کار نیمه‌تمام ممنوع است.
2. **بازخوانی کامل سند در هر مرحله:** پیش از شروع، ادامه یا بازگشت به هر user story، task، subtask، bug fix، refactor، migration، test یا deploy، Codex باید **کل این راهنما** را از ابتدا تا انتها دوباره بخواند و سپس منابع رسمی/ADR/data decision مرتبط را بررسی کند. بهینه‌سازی توکن از راه کوچک‌کردن task و خروجی‌ها انجام می‌شود، نه حذف بازخوانی کامل یا دورزدن هیچ اصل سند.
3. **پایان بدون نقصِ قابل‌اثبات:** هر مرحله فقط زمانی Done است که acceptance criterion، تست‌های لازم، security/quality review، مستندات، CHANGELOG، checkpoint و commit آن کامل باشند. داستان بعدی تنها پس از gate سبز داستان قبلی آغاز می‌شود و پایان پروژه فقط با عبور از `US-12.T05`، full release gate، preview/post-deploy verification و rollback آزموده‌شده معتبر است.

## منابع مرجع و تقدم آن‌ها

ابتدا این منابع را پیدا، فهرست و هش‌شان را در گزارش اجرا ثبت کن:

1. `.agents/documents/پرسشنامه سنجش متغیرهای رفتاری.unitext`: متن و شناسهٔ پرسش‌ها و گزینه‌ها.
2. `.agents/documents/ماتریس گزینه های متغیرهای وام.unitext`: دسته‌بندی‌های استاندارد ۸ متغیر وام.
3. `.agents/documents/ماتریس نگاشت متغیرهای پرسشنامه بر متغیرهای وام.unitext`: سهم هر پرسش در هر متغیر.
4. `.agents/documents/تبدیل پاسخ‌ها به وزن‌های عددی.unitext`: وزن پاسخ‌ها.
5. `.agents/documents/ضرایب تناسب یک به یک گزینه‌های هر یک از سئوالاتسناریوها با هریک از دسته بندی‌ها متغیرهای وام.unitext`: ضریب سازگاری یک‌به‌یک «دستهٔ وام × پاسخ».
6. `.agents/documents/دیتابیس وام های بانکی.unitext`: دادهٔ خام وام‌ها و شرایط نمایش.

فایل‌های `.unitext` منابع رسمی فعلی پروژه‌اند. آن‌ها را هم‌ارز یا بدون بررسی سازگاری فرض نکن. قبل از تبدیل داده، یک `data-audit` بساز که تعداد سطرها، ستون‌ها، شناسه‌های مفقود، مقادیر خارج از بازهٔ `[0,1]`، دسته‌های ناشناخته، داده‌های نامشخص و اختلاف میان منابع را گزارش کند. دادهٔ خام را در UI یا منطق موتور hard-code نکن.

### قانون مراجعهٔ اجباری در هر مرحله

این سند، مرجع دائمی توسعه است و رعایت اصول آن اختیاری نیست. پیش از شروع، ادامه یا بازگشت به **هر** user story، task، subtask، bug fix، refactor، migration، تست یا deploy، Codex باید ابتدا بخش «قواعد غیرقابل‌مذاکره»، وضعیت جاری، gateهای همان مرحله و بخش‌های مرتبط این راهنما را بخواند؛ سپس منابع `.unitext` مرتبط را بررسی کند. برای هر تغییری در موتور، داده، پرسشنامه، نتیجه یا دیتابیس، خواندن هر شش منبع `.unitext` الزامی است.

در هر مرحله، کل این راهنما باید دوباره خوانده شود؛ سپس برای اجرای همان task، فقط فایل‌های پروژه و منابع رسمیِ مرتبط باز شوند تا مصرف زمینه کنترل شود. هیچ پیاده‌سازی، اصلاح یا انتشار نباید پیش از ثبت نسخهٔ راهنما، تأیید بازخوانی کامل و منابع بررسی‌شده در checkpoint شروع شود. اگر کد، درخواست جدید یا داده‌ای با این راهنما ناسازگار بود، توسعه متوقف می‌شود تا تصمیم محصولی مستند ثبت شود؛ دورزدن خاموشِ اصول راهنما ممنوع است.

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

#### تصمیم فعلی دربارهٔ OTP و کاوه‌نگار

اتصال واقعی پیامک و OTP در این مرحله **خارج از محدودهٔ اجرا** است؛ ثبت‌نام، احراز هویت و تأییدهای قانونی کاوه‌نگار باید ابتدا توسط مالک محصول تکمیل شوند. تا آن زمان، پیاده‌سازی احراز هویت باید با یک port مستقل مانند `OtpProvider` و یک `MockOtpProvider` قابل‌آزمون برای local/test انجام شود. Mock فقط در محیط‌های غیرproduction مجاز است و باید کد را هرگز در log یا response غیرضروری افشا نکند.

use caseهای درخواست و تأیید OTP نباید به کاوه‌نگار، React یا route وابسته شوند. Provider واقعی آینده با نام `KavenegarOtpProvider` فقط در composition root و پس از فعال‌سازی صریح محیط production جایگزین mock می‌شود؛ قرارداد endpoint، مدل داده، rate-limit، هش و زمان انقضای OTP، audit event و منطق verify نباید تغییر کنند. کلید API، نام الگو و هر secret مربوط به کاوه‌نگار فقط در secret manager/environment نگهداری می‌شود و هرگز در repository، frontend، migration، fixture یا log وارد نمی‌شود. تا پیش از تأیید کتبی فعال‌سازی، CI و production باید استفاده از `KavenegarOtpProvider` را رد کنند.

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

## نقشهٔ اجرایی کامل: User Story، تسک و زیرتسک

این جدول ترتیب **الزام‌آور** اجرای پروژه است. Codex باید از `US-01` شروع کند و فقط پس از اتمام همهٔ تسک‌ها، زیرتسک‌ها و gateهای آن به داستان بعدی برود. پرش به UI، API، migration یا deployment مرحلهٔ بعد ممنوع است. در انتهای هر تسک، تست مرتبط اجرا، کد بررسی و در صورت نیاز refactor محدود انجام، مستندات به‌روز و یک entry در `CHANGELOG.md` ثبت می‌شود. اگر gate یک داستان قرمز است، همان داستان اصلاح می‌شود و هیچ workaround در لایهٔ بعدی مجاز نیست.

| ترتیب | User story و ارزش | تسک‌ها و زیرتسک‌های ترتیبی | Gate اجباری و خروجی |
| --- | --- | --- | --- |
| US-01 | **به‌عنوان مالک محصول، می‌خواهم مبنای قابل‌تکرار پروژه و منابع رسمی مشخص باشد تا توسعه بر حدس استوار نباشد.** | 1. ساخت شاخهٔ feature و ثبت baseline build/test.<br>2. inventory مخزن، وابستگی‌ها، mockها، routeها و وضعیت فعلی.<br>3. inventory همه فایل‌های `.agents/documents/*.unitext` با hash و نقش هر منبع.<br>4. ایجاد `docs/project-baseline.md`, `docs/source-inventory.md`, `CHANGELOG.md` و قالب ADR.<br>5. ثبت ریسک‌ها/ابهام‌های اولیه بدون تغییر منطق محصول. | Build فعلی قابل بازتولید است؛ inventory کامل است؛ هیچ فایل یا رفتار موجود بی‌دلیل تغییر نکرده؛ CHANGELOG entry `Unreleased` دارد. |
| US-02 | **به‌عنوان مالک محصول، می‌خواهم داده و قواعد توصیه‌گر canonical و قابل‌اعتبارسنجی باشند تا خروجی گمراه‌کننده تولید نشود.** | 1. تعریف IDهای canonical برای سؤال، پاسخ، متغیر، دسته و وام.<br>2. پیاده‌سازی schemaهای داده و parserهای مقدار فارسی.<br>3. ایجاد `data-audit` برای منابع unitext و ثبت provenance.<br>4. ثبت تصمیم‌های داده‌ای: `interestRate.Q5=0.10`، neutral سه متغیر سپرده، exclusion چهار متغیر محوری.<br>5. ساخت fixture و golden data کوچک و نسخه‌دار. | Audit بدون خطای blocking یا با issueهای مالک‌دار است؛ mappingها و وزن ۱٫۰۰ تست شده‌اند؛ `docs/recommendation-data-decisions.md` به‌روز است. |
| US-03 | **به‌عنوان توسعه‌دهنده، می‌خواهم اسکلت معماری تمیز و امن داشته باشم تا قابلیت‌ها بدون آشفتگی رشد کنند.** | 1. ایجاد ساختار `frontend/src` و `backend/app` طبق بخش معماری.<br>2. راه‌اندازی FastAPI، settings schema، logging redact‌شده و dependency wiring.<br>3. تعریف domain/application ports و جلوگیری از import معکوس/circular.<br>4. تعریف API v1، error model و health/readiness محدود.<br>5. ایجاد lint, format, typecheck, test runner و import-boundary checks در CI. | Backend boot می‌شود؛ test skeleton سبز است؛ secret در repo نیست؛ module map و ADR معماری نوشته شده‌اند. |
| US-04 | **به‌عنوان مالک داده، می‌خواهم PostgreSQL نرمال، نسخه‌دار و مستند باشد تا دادهٔ وام و نتیجهٔ توصیه قابل اعتماد بماند.** | 1. تبدیل مدل مفهومی به ERD و data dictionary پیش از model ORM.<br>2. طراحی 3NF برای lender، loan/version/terms، questionnaire/config و audit/import.<br>3. ایجاد SQLAlchemy model، constraint، enum state و repository port.<br>4. ساخت Alembic initial migration، migration test روی DB خالی و rollback test.<br>5. تعریف index/query strategy و بررسی queryهای پایه با `EXPLAIN`. | ERD با schema سازگار است؛ migration upgrade/downgrade می‌شود؛ FK/unique/check با test نقض می‌شوند؛ SQLite تنها oracle نیست. |
| US-05 | **به‌عنوان مسئول داده، می‌خواهم فایل unitext به دادهٔ تأییدشده تبدیل شود تا دادهٔ ناقص یا دستکاری‌شده وارد recommendation نشود.** | 1. ایجاد ingest raw با hash و source metadata.<br>2. پیاده‌سازی staging، validation header/type/row و ثبت issueها.<br>3. نرمال‌سازی typed به core و ساخت categoryها.<br>4. پیاده‌سازی audit، diff با import قبلی، approval و publish serving version.<br>5. ساخت command/runbook import و rollback.<br>6. تست import تکراری، داده خراب، atomic failure و ambiguous input. | pipeline idempotent و atomic است؛ core/serving فقط بعد approval تغییر می‌کند؛ provenance همه رکوردها قابل ردیابی است؛ `docs/data-pipeline/pipeline.md` کامل است. |
| US-06 | **به‌عنوان کاربر، می‌خواهم فهرست و جزئیات وام معتبر ببینم تا شرایط را درست بررسی کنم.** | 1. use caseهای `ListLoans` و `GetLoanDetails` با repository.<br>2. response schemaهای محدود و امن FastAPI.<br>3. parser شرایط و مقررات به bullet امن، بدون HTML خام.<br>4. اتصال صفحهٔ `loan-details` به API/view model، loading/error/empty state و RTL.<br>5. API/UI test برای bullet، داده خالی، لینک/لوگو نامعتبر و authorization لازم. | متن شرایط دقیقاً از source تأییدشده می‌آید؛ XSS اجرا نمی‌شود؛ هیچ داده حساس یا config داخلی در response نیست؛ E2E جزئیات وام سبز است. |
| US-07 | **به‌عنوان کاربر، می‌خواهم پرسشنامه درست، پایدار و قابل بازگشت باشد تا ترجیحاتم دقیق ثبت شود.** | 1. ساخت questionnaire version، question/answer config و validation.<br>2. پیاده‌سازی route adapter: `/question/3..12` به `Q1..Q6,S7,S8,S10,S13`.<br>3. use case شروع/ثبت/اعتبارسنجی session و retention policy.<br>4. اتصال UI بدون index hard-code؛ کنترل next/back، resume و پاسخ ناقص.<br>5. تست جدولی route map، API، RTL/accessibility و E2E تکمیل/بازگشت.<br>6. persistence پایدار session/answer در PostgreSQL، cache Redis، پاک‌سازی انقضا و آزمون restart/expiry. | هر route به ID صحیح می‌رسد؛ پاسخ ناقص ذخیره یا توصیه نمی‌شود؛ دادهٔ session در log/URL نیست؛ مسیر بازگشت پاسخ را خراب نمی‌کند؛ پاسخ معتبر پس از restart تا پایان TTL از PostgreSQL بازیابی می‌شود و Redis فقط cache قابل‌بازتولید است. |
| US-08 | **به‌عنوان کاربر، می‌خواهم موتور توصیه‌گر شفاف و قابل بازتولید باشد تا وام‌های سازگار را ببینم.** | 1. پیاده‌سازی pure domain engine: score category، tree pruning، path aggregation، normalization و threshold.<br>2. پیاده‌سازی neutral و `needsReview` طبق تصمیم داده.<br>3. تولید `RecommendationTrace` نسخه‌دار و redact‌شده.<br>4. use case `RecommendLoans` با transaction/read snapshot مناسب.<br>5. unit/property/golden test برای همه سؤال‌ها، tie، no-candidate، conflict و unknown. | Engine مستقل از FastAPI/React است؛ نتیجه deterministic است؛ score فقط برای `rankedRecommendations` است؛ trace همه علت‌ها را دارد؛ تست golden سبز است. |
| US-09 | **به‌عنوان کاربر، می‌خواهم نتیجه و علت آن را قابل فهم ببینم تا تصمیم نهایی خودم را بگیرم.** | 1. طراحی view model امتیاز، دلیل سازگاری، هشدار و روش اقدام.<br>2. اتصال صفحه نتایج به API، بدون محاسبه client-side قابل‌دستکاری.<br>3. نمایش جداگانه `rankedRecommendations`, `needsReview`, no-candidate و zero-after-filter.<br>4. فیلترهای دستی، sort پایدار، loading/error/accessibility و responsive RTL.<br>5. E2E قراردادیِ مرورگر با پاسخ کنترل‌شده، بدون ادعای اتصال زنده.<br>5A. audit و تکمیل پایدارِ دادهٔ وام‌ها و پیکربندی رسمی، طبق متن `US-09.T05A`.<br>5B. اتصال آداپتورهای خواندن snapshot و شرایط واقعی وام به use caseهای موجود، طبق متن `US-09.T05B`.<br>6. اتصال عملیاتی session پرسشنامه، endpoint واقعی توصیه‌ها، موتور سرور و صفحهٔ نتیجه؛ تحویل URL قابل‌آزمایش برای مالک محصول.<br>6A. حفظ UIهای توسعه‌یافته و اتصال کامل تمام routeهای قابل‌دسترسیِ وام به داده و قرارداد واقعی، سه حالت فیلتر «بیشترین تطابق/کمترین تطابق/وضعیت متغیر»، و حذف هر خروجی ساختگی، طبق متن `US-09.T06A`.<br>6B. ماژولار‌سازی واقعی componentهای نتیجه و جزئیات، طبق `US-09.T06B`.<br>6C. پایداری UI نتیجه، جزئیات و مقایسه، طبق `US-09.T06C`.<br>6D. تکمیل نمایش لوگوی واقعی، فیلترها، کارت‌های responsive و اعداد فارسی، طبق `US-09.T06D`.<br>6E. رساندن logo تأییدشدهٔ رکورد PUBLISHED به API توصیه‌گر و همهٔ کارت‌های نتیجه/مقایسه، طبق `US-09.T06E`.<br>6F. نگهداری SVGهای تأییدشده در assetهای پروژه، ثبت key/hash در serving facts و نمایش واقعی آن‌ها در همهٔ کارت‌ها، طبق `US-09.T06F`.<br>6G. مسیر URL-safe، نمایش واقعی و RTL پایدار logo/درصد در کارت‌های نتیجه و مقایسه، طبق `US-09.T06G`.<br>6H. ثابت‌سازی جای logo و هویت بانک در همهٔ کارت‌های وام، مستقل از طول نام بانک، طبق `US-09.T06H`.<br>6I. بازگردانی محافظه‌کارانهٔ صفحهٔ اطلاعات شخصی، OTP نمایشی، spinner و نمایش پروفایل محلی، طبق `US-09.T06I`.<br>6J. صحت نمایش رقم فارسی، مقیاس رنگ درصد تطابق، برچسب تحلیل مقایسه و SVG بانک ملی، طبق `US-09.T06J`.<br>6K. کنترل قابل‌استفادهٔ فیلتر بانک، ترتیب نمایش کمترین تطابق، ذخیرهٔ نمایشی و عنوان CTA نتیجه، طبق `US-09.T06K`.<br>6L. تکمیل کنترل ذخیره، بازگشت پایدار، انتخاب مقایسه، CTA جزئیات و asset بانک ملی، طبق `US-09.T06L`.<br>6N. اصلاح پاک و مستقلِ toolbar جزئیات و performance مسیرها، طبق `US-09.T06N`.<br>6O. بازیابی بی‌صدای session، cache جزئیات و قاب CTA مطابق نمونه، طبق `US-09.T06O`.<br>6P. حذف mock legacy، قاب قطعی CTA و جلوگیری از refresh جعلی، طبق `US-09.T06P`.<br>6Q. حذف قطعی fallback static صفحهٔ mock از HTML ورودی و آزمون refresh، طبق `US-09.T06Q`.<br>6R. ارتقای امنیتیِ قفل‌شدهٔ زنجیرهٔ build frontend و audit بدون آسیب‌پذیری، طبق `US-09.T06R`.<br>6S. نمایش سریع نتایج واقعی با یک snapshot و خلاصهٔ PUBLISHED در همان پاسخ، طبق `US-09.T06S`.<br>7. استقرار staging با PostgreSQL دائمی، ورود دادهٔ رسمی، اتصال Netlify به API و آزمون دستی/E2E روی URL واقعی طبق `US-09.T07`. | UI ادعای تأیید یا «بهترین وام» نمی‌کند؛ نیازمند بررسی score ندارد؛ همه حالت‌های خالی تمایز دارند؛ کاربر با تکمیل پرسشنامه، وام‌های منتشرشده و درصد تطابق محاسبه‌شده در سرور را می‌بیند، مورد نیازمند بررسی را بدون درصد می‌بیند و با انتخاب هر وام به جزئیات و شرایط/قوانین آن می‌رسد؛ E2E موبایل/desktop و آزمون دستی روی URL قابل‌آزمایش سبز است. |
| US-10 | **به‌عنوان مسئول عملیات، می‌خواهم داده و تنظیمات با مجوز و audit تغییر کنند تا دستکاری یا خطای انسانی کنترل شود.** | 1. نقش‌ها و permissions حداقلی برای import/approve/config.<br>2. use caseهای internal برای import، review issue، approve/rollback version.<br>3. append-only audit event و approval record.<br>4. endpoint/tool داخلی محافظت‌شده و test role/ownership.<br>5. runbook عملیاتی و آموزش عدم‌ویرایش مستقیم DB. | کاربر/Client عادی قادر به تغییر loan/config/score نیست؛ تمام تغییرات actor/reason/version دارند؛ authorization و audit test سبز است. |
| US-11 | **به‌عنوان تیم توسعه، می‌خواهم سرویس قابل مشاهده، مقاوم و امن باشد تا خطا قبل از آسیب کشف شود.** | 1. threat model و privacy/retention review.<br>2. TLS/CORS/headers/CSRF/rate-limit/input validation و secret management.<br>3. SAST/SCA/secret scan و staging DAST سبک.<br>4. structured logging, metric, alert و incident runbook.<br>5. load/performance smoke، backup encryption و restore rehearsal. | security gate کامل سبز است؛ یافته critical/high یا secret leak وجود ندارد؛ restore ثبت‌شده و موفق است؛ log داده حساس ندارد. |
| US-12 | **به‌عنوان مالک محصول، می‌خواهم انتشار قابل بازگشت و مستند باشد تا نسخهٔ نهایی با ریسک کنترل‌شده منتشر شود.** | 1. مرور همه ADRها، docs، API spec، ERD، data dictionary و changelog.<br>2. اجرای full CI: unit/integration/API/E2E/security/migration/pipeline/performance.<br>3. ایجاد preview با config/data version تأییدشده و smoke test.<br>4. ثبت release note، rollback plan، migration sequence و known limitationها.<br>5. فقط پس از PR review و همه gateهای سبز، production deploy؛ سپس post-deploy verification. | تمام user storyهای US-01 تا US-11 Done هستند؛ changelog و مستندات کامل‌اند؛ preview و post-deploy smoke سبز؛ rollback عملی است. این آخرین تسک پایان پروژه است. |

### ماتریس کنترل اجرای ریز

این ماتریس، backlog اجراییِ الزام‌آور است. هر شناسه دقیقاً یک commit/PR کوچک و قابل‌بازبینی دارد؛ اجرای شناسه‌ها به‌ترتیب سطر و سپس از چپ به راست انجام می‌شود. «محدودهٔ تغییر» allowlist است، نه مجوز تغییر بی‌دلیل: فایل دیگری فقط با ثبت دلیل در ADR/PR قابل تغییر است. پیش از شروع هر شناسه، Codex باید وضعیت dependency، acceptance criterion و test همان ردیف را در checkpoint ثبت کند.

| شناسه‌های ترتیبی | وابستگی | محدودهٔ اصلی تغییر | تست/خروجی اجباری پیش از عبور |
| --- | --- | --- | --- |
| `US-01.T01` شاخه و baseline → `T02` inventory مخزن → `T03` inventory/hash منابع → `T04` skeleton اسناد → `T05` ثبت ریسک | هیچ | `docs/project-baseline.md`, `docs/source-inventory.md`, `docs/adr/`, `CHANGELOG.md`؛ کد محصول ممنوع | build/test baseline، hash شش منبع، فهرست mock/route/dependency و checkpoint ثبت شود. |
| `US-02.T01` IDهای canonical → `T02` schema/parser → `T03` data-audit/provenance → `T04` data-decision → `T05` fixture/golden | همهٔ `US-01.*` | `backend/app/.../domain`, `scripts/`, `tests/fixtures/`, `docs/recommendation-data-decisions.md`؛ UI و DB runtime ممنوع | schema/parser/audit test؛ اثبات `Q5=0.10` و مجموع `1.00`؛ issueهای blocking مالک‌دار باشند. |
| `US-03.T01` scaffold → `T02` FastAPI/settings/logging → `T03` ports/boundaries → `T04` API v1/health → `T05` CI quality gates | همهٔ `US-02.*` | `backend/app/`, `frontend/src/app/`, `pyproject.toml`, CI workflow، module map و ADR معماری | boot API، settings validation، lint/format/typecheck/test skeleton و import-boundary check سبز؛ secret در diff نباشد. |
| `US-04.T01` مدل مفهومی/ERD → `T02` طراحی 3NF → `T03` ORM/constraint/port → `T04` migration اولیه → `T05` index/EXPLAIN | همهٔ `US-03.*` | `docs/database/`, `backend/app/.../models`, `alembic/`, migration/testها | ERD و data dictionary با schema همسو؛ upgrade/downgrade روی PostgreSQL واقعی؛ constraint و query-plan test سبز. |
| `US-05.T01` raw ingest → `T02` staging validation → `T03` normalizer/category → `T04` approval/publish version → `T05` import runbook → `T06` failure/idempotency tests | همهٔ `US-04.*` | `backend/app/data_pipeline/`, `scripts/`, `docs/data-pipeline/`, staging/core/serving migrationها | import تکراری خروجی یکسان دهد؛ failure اتمیک rollback شود؛ provenance و diff/approval قابل مشاهده باشد. |
| `US-06.T01` list/details use case → `T02` response schema → `T03` conditions parser → `T04` UI/API integration → `T05` API/UI/E2E tests | همهٔ `US-05.*` | `backend/app/loans/`, `frontend/src/features/loan-details/`, قرارداد API و تست‌ها | داده فقط از serving version؛ bullet امن، RTL، empty/loading/error؛ XSS و E2E جزئیات سبز. |
| `US-07.T01` questionnaire config → `T02` route adapter → `T03` session use case/retention → `T04` UI flow → `T05` route/API/E2E/a11y tests → `T06` PostgreSQL persistence/Redis cache/ERD | همهٔ `US-06.*` | `backend/app/questionnaire/`, `backend/app/infrastructure/`, `frontend/src/features/questionnaire/`, `docs/api/`, `docs/database/erd.md`, `docs/database/physical-schema-3nf.md`, `docs/architecture/` و تست‌ها | مسیرهای `/question/3..12` به ID ثابت برسند؛ پاسخ ناقص مسدود؛ next/back/resume و عدم نشت session تأیید شود؛ پس از restart پاسخ تا TTL از PostgreSQL بازیابی شود، cache-miss/failure به منبع پایدار degrade کند، Redis پاسخ/PII دائمی نباشد و ERD/schema هم‌زمان اعتبارسنجی شوند. |
| `US-08.T01` engine خالص → `T02` neutral/needsReview → `T03` trace → `T04` RecommendLoans use case → `T05` unit/property/golden | همهٔ `US-07.*` | `backend/app/recommendation/domain`, `application`, `engine`, repository port و fixtureها؛ React/FastAPI در engine ممنوع | deterministic score/tree/threshold؛ unknown سیاست‌مند؛ trace redact‌شده؛ همه golden/property testها سبز. |
| `US-09.T01` results view model → `T02` API integration → `T03` states جداگانه → `T04` manual filters/sort/a11y → `T05` E2E قراردادی → `T05A` audit/materialization داده و پیکربندی رسمی → `T05B` آداپتورهای پایدار snapshot و جزئیات → `T06` اتصال عملیاتی → `T06A` یکپارچگی UIهای توسعه‌یافته و فیلترهای واقعی → `T07` استقرار staging پایدار و آزمون URL واقعی | همهٔ `US-08.*` | `src/features/recommendation/ui/`، `src/features/loan-details/`، `backend/app/questionnaire/`، `backend/app/recommendation/`، `backend/app/loans/`، API presenter/contract، deploy/preview config و E2Eها | browser هرگز score محاسبه نکند؛ session معتبر فقط به endpoint واقعی برسد؛ ranked/needsReview/empty جدا باشند؛ نتیجه فقط از وام‌های منتشرشده و امتیاز server-calculated ساخته شود؛ کاربر از پرسشنامه تا جزئیات و شرایط/قوانین وام را در URL قابل‌آزمایش طی کند؛ E2E و آزمون دستی mobile/desktop سبز باشد. |
| `US-10.T01` RBAC → `T02` import/review/approve/rollback use case → `T03` audit event → `T04` internal endpoint/tool → `T05` operations runbook | همهٔ `US-09.*` | `backend/app/operations/`, authz policy، audit migration/test و `docs/operations/` | client عادی تغییر نمی‌دهد؛ role/ownership/append-only audit/rollback با test اثبات شود. |
| `US-11.T01` threat/privacy review → `T02` transport/app hardening → `T03` SAST/SCA/secret/DAST → `T04` logging/metrics/alerts → `T05` load/backup/restore | همهٔ `US-10.*` | `docs/security/`, deploy config، CI security jobs، monitor/runbook و security tests | critical/high و secret leak صفر؛ rate-limit و headers test؛ backup restore و performance smoke ثبت‌شده. |
| `US-12.T01` documentation review → `T02` full CI → `T03` preview/smoke → `T04` release/rollback note → `T05` reviewed production/post-deploy | همهٔ `US-11.*` | `CHANGELOG.md`, `docs/`, release config، PR/release note و deploy runbook | همهٔ storyهای قبلی Done؛ full gate/preview/post-deploy سبز؛ rollback تمرین‌شده. |

### پیش‌نیاز مستقل اتصال زنده — `US-09.T05A`

**هدف:** آنچه در شش منبع رسمی `.agents/documents/*.unitext` و تصمیم‌های تأییدشدهٔ `docs/recommendation-data-decisions.md` برای محاسبهٔ تطابق و نمایش وام تعریف شده است، به پیکربندی و دادهٔ serving نسخه‌دار، پایدار و قابل‌خواندن توسط `RecommendLoans` و `GetLoanDetails` تبدیل و با همان منابع راستی‌آزمایی شود. این تسک طراحی فرمول، ضریب، آستانه یا قاعدهٔ توصیهٔ تازه نیست. تصمیم‌های D-001 تا D-004 و منطق امتیازدهی/درخت/نرمال‌سازی/آستانهٔ مصوب همین راهنما و پیاده‌سازی `US-08` مرجع‌اند؛ اگر پیاده‌سازی با منبع یا تصمیم تأییدشده ناسازگار بود، اختلاف با سطر/سلول و اثر آن ثبت و طبق فرایند تصمیم‌گیری حل شود، نه با انتخاب خاموش یک مقدار.

**تصمیم D-005 (مالک محصول، ۲۰۲۶-۰۹-۲۶):** تنها ضرایب جدول «تبدیل پاسخ‌ها به وزن‌های عددی» برای وزن پرسش/پاسخ معتبرند. ضرایب عددی «ماتریس نگاشت متغیرهای پرسشنامه بر متغیرهای وام» در scoring و دادهٔ منتشرشده استفاده نمی‌شوند؛ رابطهٔ پرسش و متغیر آن می‌تواند به‌عنوان شناسه بازخوانی شود. ضریب سازگاری پاسخ با دسته از منبع مستقلِ «ضرایب تناسب یک به یک» با ارجاع سلول می‌آید. پنج اختلاف عددی ثبت‌شده با این اولویت حل شده‌اند؛ بایت منبع تغییر نمی‌کند.

**وابستگی و ترتیب:** `US-09.T01` تا `T05` و PR #44 merge شده‌اند. `T05A` بعد از `T05` و پیش از `T05B` اجرا می‌شود؛ شناسه و هدف `T06` تغییر نمی‌کند. `T05A` فقط پس از checkpoint، commit/PR و gate سبز Done است و تا آن زمان `T05B` آغاز و `T06` تکمیل‌شده اعلام نمی‌شود.

**کارهای الزام‌آور:**

1. کل این راهنما، `docs/recommendation-data-decisions.md`، قراردادهای موجود و هر شش منبع UTF-16LE را با حفظ بایت‌های اصلی و ثبت Git blob SHA بازخوانی کن. مسیر سؤال/گزینهٔ canonical و `answerId`های ثابت را به نگاشت پرسش ← متغیر وام، وزن عددی پاسخ و ضریب سازگاری یک‌به‌یک هر پاسخ با هر دسته متصل کن. ماتریس‌ها و تصمیم‌های نسخه‌دار موجود را مصرف کن؛ عدد، نگاشت یا ترتیب جدید از متن UI استنباط نکن. پوشش همهٔ پاسخ‌های لازم و هشت متغیر را با source reference تا سلول/سطر و golden test ثابت کن.
2. پیش از هر import یا backfill، رکوردهای موجود PostgreSQL را با فایل رسمی وام‌ها و نسخه/وضعیت انتشارشان audit کن: تعداد، شناسه‌ها، هشت متغیر، شرایط و مقررات، provenance و active pointer را گزارش بده. رکورد موجود را دوباره وارد نکن؛ اگر داده و اتصالش کامل است همان را مصرف کن. فقط شکاف اثبات‌شده را با migration/backfill یا adapter حداقلی برطرف کن تا categoryهای canonical هر هشت متغیر، نسخهٔ پیکربندی تأییدشده و وام‌های `PUBLISHED` در snapshot پایدار raw → staging → core → serving قابل‌خواندن باشند. هر تغییر باید idempotent، اتمیک، قابل rollback و provenanceدار و انتشار وابسته به approval باشد. دادهٔ `DRAFT`، staging یا نسخهٔ superseded وارد snapshot خواندنی موتور نشود. تغییر بایت‌های خام منابع ممنوع است.
3. متن ستون `شرایط و مقررات` همان نسخهٔ وام را با نگاشت تأییدشده در دادهٔ پایدار نگه دار و برای خواندن توسط adapter جزئیات آماده کن؛ ترتیب و متن شروط حفظ شود. مقدار خالی باید از نبود رکورد وام قابل تمایز باشد. اتصال واقعی adapter به parser امن در `T05B` انجام می‌شود.
4. audit پوشش دسته‌ها، وزن‌ها و ضرایب، شناسه‌های مفقود، مقادیر خارج از `[0,1]`، تکرارها، اختلاف منابع، تعداد وام‌های `rankedRecommendations` و `needsReview` و علت هر exclusion را از داده محاسبه کند. چهار متغیر محوریِ نامعلوم/متغیرِ دسته‌بندی‌نشده باید در `needsReview` بدون score/rank بمانند؛ سه ویژگی سپردهٔ نامعلوم طبق D-002 خنثی‌اند؛ ویژگی‌های نمایشی طبق D-004 در امتیاز وارد نمی‌شوند. اختلاف تأییدنشده در `docs/recommendation-data-decisions.md` با منبع، مقدارها، اثر و تصمیم لازم ثبت و از انتشار آن نسخه جلوگیری شود.
5. با fixtureهای golden مبتنی بر منبع و integration test روی PostgreSQL واقعی ثابت کن که پیکربندی تأییدشده، دسته‌های وام `PUBLISHED` و شروط همان loan version پایدار و با provenance قابل بازیابی‌اند؛ تکرار import، شکست میانی، rollback، نبود پیکربندی/نسخهٔ منتشرشده، دستهٔ ناقص و دادهٔ مبهم رفتار کنترل‌شده دارند. `npm run quality`، migration verification، secret/security و import-boundary checks و تست‌های مرتبط سبز باشند. قرارداد داده، ERD/data dictionary/pipeline/module map در صورت تغییر، `CHANGELOG.md` و checkpoint به‌روز شوند.

**معیار پذیرش:** داده و پیکربندی نسخه‌دار بر اساس منابع رسمی و وضعیت واقعی PostgreSQL آماده و با audit و golden test قابل بازتولید باشند؛ متن شرایط همان loan version پایدار باشد. مصرف این داده از طریق آداپتورهای سرور و اثبات خروجی use case متعلق به `T05B` است. این gate یک آزمون زیرساختی با دادهٔ رسمی است؛ endpoint عمومی، اتصال مسیر فعال فرانت، URL قابل‌آزمایش و E2E زنده همچنان متعلق به `US-09.T06` هستند. هیچ انتشار production یا تغییر Netlify در `T05A` انجام نشود.

### اتصال آداپتورهای پایدار به موتور و جزئیات — `US-09.T05B`

**هدف و وابستگی:** پس از gate سبز `T05A`، داده‌ها و پیکربندی موجود در PostgreSQL را از طریق portهای فعلی به `RecommendLoans` و `GetLoanDetails` وصل کن. موتور pure نباید مستقیم session، HTTP یا ORM را بخواند؛ این تفکیک معماری عمدی است. نگاشت session به ورودی canonical، endpoint `POST /api/v1/recommendations` و اتصال فرانت در `T06` است. `T05B` قانون امتیازدهی، وزن یا threshold جدید تعریف نمی‌کند.

1. آداپتور PostgreSQL برای `RecommendationSnapshotRepository.read_approved_snapshot()` بساز: در یک read سازگار، فقط active serving version و loan product versionهای `PUBLISHED`، category/state هر هشت متغیر و config `approved: true` را بخواند و به `LoanCandidate` و `RecommendationSnapshot` موجود تبدیل کند. هیچ selector از client یا دادهٔ draft/staging/superseded پذیرفته نشود؛ نبود نسخه، پیکربندی یا پوشش دستهٔ لازم خطای typed و fail-closed باشد. آداپتور حافظه‌ای فقط fixture/test باقی بماند.
2. آداپتور `SqlAlchemyServingLoanCatalogueRepository` را با ستون‌ها/روابط پایدارِ تأییدشده کامل کن: `conditions_source_text` باید از `شرایط و مقررات` همان loan version بیاید؛ سه ویژگی سپرده، نوع ضمانت، حساب سپرده و سایر facts مجاز فقط از دادهٔ serving بیایند. parser امن موجود متن شرایط را به bulletهای مرتب تبدیل کند؛ مقدار واقعاً خالی حالت «اطلاعات تکمیلی در دسترس نیست» باشد. `None` ثابت برای فیلد دارای داده و hard-code شرایط در UI ممنوع است.
3. مسیر `prepare_canonical_import.py` را با انتشار واقعی اشتباه نگیر: این فرمان فقط plan می‌سازد. آداپتور پایدار `ServingVersionRepository` و مسیر موردنیازِ approval/publish/active pointer را بر بستر رکوردهای بررسی‌شدهٔ `T05A` وصل و آزمون کن، فقط اگر audit نشان داد هنوز وجود ندارد؛ import تکراری یا تغییر رکورد تأییدشده ممنوع است. انتشار باید اتمیک، idempotent، provenanceدار و قابل rollback باشد. عملیات مدیریتی عمومی و RBAC مربوط به `US-10` را جلو نکش.
4. integration test با PostgreSQL واقعی برای خواندن snapshot نسخه‌دار، اجرا شدن `RecommendLoans` با ترجیحات canonical آزمایشیِ برگرفته از config، `rankedRecommendations` و score/reason قابل بازتولید، `needsReview` بدون score/rank، no-candidate، شروط واقعی جزئیات، مقدار خالی، نسخهٔ draft/superseded، قطع ارتباط/عدم پیکربندی و publication failure بنویس. ثابت کن trace/raw answers/session/config داخلی از پاسخ‌های عمومی جزئیات نشت نمی‌کند. `npm run quality`، migration verification، security/secret و boundary checks باید سبز باشند.
5. API/data contract، ERD/data dictionary، pipeline/runbook، module map، `CHANGELOG.md` و checkpoint را متناسب با تغییر واقعی به‌روز کن؛ commit و PR قابل‌بازبینی با SHA شش منبع و شواهد تست ثبت کن.

**معیار پذیرش:** use case موجود در سرور، با داده و پیکربندی تأییدشدهٔ پایدار و ورودی canonical آزمایشی، نتیجهٔ واقعی و قابل‌بازتولید بسازد و API موجودِ جزئیات همان شروط منتشرشده یا حالت خالی صریح را نشان دهد. session-to-preference adapter، endpoint توصیه و تجربهٔ واقعی پرسشنامه تا نتیجه در `T06` تکمیل می‌شود؛ تا آن زمان `US-09` Done نیست.

### تکمیل اجباری US-09 — `US-09.T06`

`US-09.T06` پس از gate سبز `US-09.T05A` و `US-09.T05B` اجرا می‌شود و صرفاً یک تست نمایشی یا mock نیست؛ حلقهٔ عملیاتیِ باقی‌مانده را کامل می‌کند. پایان `US-09` فقط وقتی معتبر است که مالک محصول بتواند روی یک URL قابل‌آزمایش:

1. پرسشنامهٔ canonical را تکمیل کند و پاسخ‌ها در session معتبرِ ۳۰ دقیقه‌ای همان مرورگر ادامه یابند.
2. صفحهٔ نتیجه، endpoint واقعی را فراخوانی کند و خروجی موتور سرور را بدون محاسبه یا دستکاری امتیاز در مرورگر نمایش دهد.
3. فقط وام‌های منتشرشده را با درصد تطابق محاسبه‌شده در سرور ببیند؛ موارد `needsReview` باید جدا و بدون درصد یا رتبه نمایش داده شوند.
4. فیلتر و sort دستی، حالت‌های loading/error/empty، RTL و دسترس‌پذیری را تجربه کند.
5. با انتخاب جزئیات هر وام، نام/اطلاعات وام و «شرایط و قوانین/مدارک مورد نیاز» را از دادهٔ serving و به‌صورت متن امن و bullet ببیند.

بدون endpoint متصل به session و use case `RecommendLoans`، خروجی واقعیِ API، مسیر جزئیات، E2E مرورگر و تأیید دستی روی URL قابل‌آزمایش، `US-09.T06` Done نیست. تکمیل کل US-09 علاوه بر آن به gate یکپارچگی UI `US-09.T06A` و gate استقرار `US-09.T07` وابسته است. این تسک نباید persistence/retention یا score را در client تکرار کند و نباید تولید یا انتشار production را ادعا کند؛ preview/staging قابل‌آزمایش کافی است مگر انتشار جداگانه‌ای تأیید شود.


### یکپارچگی UIهای توسعه‌یافته و فیلترهای واقعی — US-09.T06A

**هدف و وابستگی:** پس از gate سبز T06 و پیش از هر استقرار T07، ظاهر، RTL و مسیر تمام صفحه‌های وامِ توسعه‌یافته حفظ شود، اما هر داده، درصد، نام وام، شرایط، مقایسه، علت و روش اقدامِ قابل‌نمایش فقط از قراردادهای سرور و دادهٔ serving تأییدشده بیاید. این task هیچ دادهٔ ساختگی یا قاعدهٔ امتیازدهی جدیدی تولید نمی‌کند. تصمیم D-005 الزام‌آور است: فقط ضرایب جدول «تبدیل پاسخ‌ها به وزن‌های عددی» برای وزن پاسخ/پرسش معتبرند؛ ضرایب عددی ماتریس نگاشت در scoring یا نمایش نتیجه مصرف نمی‌شوند.

**قرارداد محصول:** «کمترین تطابق» خروجی واقعی اما غیرپیشنهادی است، نه needsReview. فقط وامی که برای هر چهار ویژگی محوری دستهٔ معتبر و score سروریِ قابل‌بازتولید دارد می‌تواند در یکی از دو حالت دارای درصد قرار گیرد. وامِ دارای ویژگی محوری unknown یا variable دسته‌بندی‌نشده فقط در «وضعیت متغیر/نیازمند بررسی» می‌آید و هرگز درصد، رتبه یا ادعای سازگاری نمی‌گیرد. اگر روش اقدام یا ثبت درخواستِ یک وام در serving data وجود ندارد، UI همان فقدان اطلاعات را شفاف نشان می‌دهد؛ ساختن پرداخت، ثبت درخواست، لینک بانک، تحلیل AI یا ادعای دریافت وام از روی حدس ممنوع است.

1. پیش از تغییر، همهٔ routeها و componentهای وامِ قابل‌دسترسی را inventory کن و برای هرکدام route، design موجود، منبع دادهٔ واقعی، action معتبر، حالت خالی/error و test مالک‌دار ثبت کن. loan-results، loan-details، انتخاب/مقایسهٔ وام، درخواست/روش اقدام و تحلیل/توضیح نتیجه باید جدا بررسی شوند. ظاهر تأییدشده و layout responsive/RTL حفظ شود؛ حذف، بازطراحی یا جایگزینی خاموش صفحه‌ها مجاز نیست.
2. هر literal یا fixture نمایشیِ قابل‌دسترسی در مسیر وام، از جمله نام وام، بانک، درصد، شرایط، مبلغ، قسط، سود، مدت، ضمانت، لینک و وضعیت درخواست، را از UI حذف و با view model/API سروریِ نسخه‌دار جایگزین کن. دادهٔ test fixture فقط در test باقی بماند. React نباید score، وزن، دسته، شروط یا روش اقدام را محاسبه یا حدس بزند.
3. قرارداد API نتایج را بدون تغییر فرمول scoring توسعه بده تا سه مجموعهٔ جدا و typed برگرداند:
   - **بیشترین تطابق:** rankedRecommendations با score معتبر، مرتب‌سازی پایدار compatibilityScore DESC سپس stableLoanId ASC و آستانهٔ پیش‌فرض مصوب.
   - **کمترین تطابق:** lowCompatibilityRecommendations شامل فقط وام‌های rankable با score معتبر اما زیر آستانه، مرتب‌سازی پایدار compatibilityScore ASC سپس stableLoanId ASC و برچسب روشن «تطابق پایین؛ پیشنهاد اصلی نیست». این نمایش فقط با انتخاب صریح فیلتر کاربر فعال است و scoring/threshold canonical را تغییر نمی‌دهد.
   - **وضعیت متغیر:** needsReview با rankingExcludedReasons، بدون score/rank. عنوان UI روشن می‌کند که مقایسهٔ دقیق به تکمیل/شفاف‌شدن دادهٔ وام نیاز دارد.
   هر سه مجموعه فقط از active approved snapshot و loan versionهای PUBLISHED خوانده شوند؛ client نباید selector snapshot، config، weight یا score بفرستد.
4. کنترل‌های موجودِ طراحی نتایج را به سه حالت بالا وصل کن و در هر حالت شمارش، empty state، دلیل/هشدار، ترتیب و لینک جزئیات واقعی را نشان بده. «صفر نتیجه پس از فیلتر» را از «هیچ وام قابل رتبه‌بندی نیست» و از خطای شبکه جدا کن. فیلتر باید قابل برگشت، keyboard-accessible و در mobile/desktop قابل استفاده باشد.
5. ورود مستقیم یا refresh در loan-results بدون session کاملِ همان تب نباید صفحهٔ نتیجهٔ خالی، خطای مبهم یا دادهٔ نمایشی نشان دهد؛ پیام امن فارسی، علت سطح‌بالا و مسیر بازگشت به شروع پرسشنامه بده. session/answer/trace در URL یا localStorage بلندمدت ذخیره نشود.
6. صفحهٔ جزئیات، انتخاب/مقایسه، روش اقدام/درخواست و تحلیل/توضیح را با view modelهای واقعی بساز: جزئیات و شرایط از همان loan versionِ انتخاب‌شده و parser امن موجود بیاید؛ مقایسه فقط میان loanIdهای واقعی و با facts واقعی همان loan version باشد؛ روش اقدام فقط از منبع تأییدشدهٔ همان وام نمایش داده شود؛ و تحلیل/توضیح فقط explanation و شرایط واقعیِ خروجی موتور را به زبان قابل‌فهم نشان دهد. عملیات بیرونیِ تأییدنشده (ثبت رسمی، پرداخت یا OTP واقعی) نباید شبیه‌سازی یا موفقیت اعلام شود.
7. برای قرارداد جدید، schema/typed error، presenter و repository/use caseهای لازم را در مرزهای موجود بساز؛ migration یا تغییر داده فقط در صورت ضرورت اثبات‌شده و با audit/approval/version/rollback انجام شود. فیلتر جدید یا route state نباید فرمول موتور، وزن‌های D-005، پاسخ canonical یا دادهٔ خام را تغییر دهد.
8. testهای اجباری: unit برای partition شدن قطعی ranked/low/needsReview و sort/tie/threshold؛ API integration با PostgreSQL برای PUBLISHED-only، snapshot missing و عدم نشت config/trace؛ UI test برای سه فیلتر، empty/error/loading، session-missing redirect و عدم نمایش literal ساختگی؛ E2E واقعی از پرسشنامه تا هر سه حالت، جزئیات، مقایسه و روش اقدام؛ visual review/screenshot در mobile و desktop با حفظ design. تست باید ثابت کند browser هیچ score تازه‌ای محاسبه نکرده و هر مقدار نمایش‌داده‌شده provenance دارد.
9. checkpoint، API/OpenAPI/module map و مستندات UI/route مرتبط، CHANGELOG و PR را به‌روز کن. سند تداوم docs/project-current-state.md فقط پس از پایان کل US-09 و عبور T07 به‌روزرسانی می‌شود، نه در پایان T06A.

**معیار پذیرش:** تمام صفحه‌ها و مسیرهای وام که کاربر می‌تواند به آن‌ها برسد، design تأییدشده را با داده و رفتار معتبرِ serving/API نمایش می‌دهند؛ هیچ نام وام، درصد، شرط، مقایسه، اقدام یا تحلیل ساختگی قابل‌نمایش نیست. کاربر می‌تواند پس از پرسشنامه، فیلتر «بیشترین تطابق»، «کمترین تطابق» یا «وضعیت متغیر» را انتخاب کند، داده و توضیح واقعی هر حالت را ببیند و تا جزئیات/مقایسه/روش اقدام معتبر پیش برود. این task استقرار، Netlify یا عملیاتی‌شدن providerهای خارجی را اثبات نمی‌کند؛ آن‌ها به‌ترتیب متعلق به T07 یا User Storyهای بعدی هستند.

### ماژولار‌سازی نتیجه و جزئیات وام — `US-09.T06B`

**هدف و وابستگی:** پس از `T06A` و پیش از `T07`، کدِ routeهای نتیجه و جزئیات وام از فایل monolith `src/home page.jsx` به componentهای feature مستقل منتقل شود، بی‌آنکه design تأییدشده، flow، قرارداد موتور یا دادهٔ serving تغییر کند. این task استقرار، تغییر فرمول یا ساخت دادهٔ جدید نیست.

1. `LoanResultsScreen`، کارت نتیجه و کنترل‌های فیلتر را در feature نتیجه نگه دار و route composition در home را سبک کن؛ `LoanDetailsScreen` نیز تنها owner نمایش جزئیات باشد. انتقال باید واقعی باشد، نه صرفاً comment یا code-map.
2. در mobile و desktop، header، actionها، دو کنترل فیلتر، کارت نتیجه، جدول facts، لینک جزئیات و کارت‌های گروهی جزئیات با layout مرجع RTL بررسی و با CSS موجود/حداقلی همسو شوند. بازطراحی خاموش یا جایگزینی صفحهٔ توسعه‌یافته ممنوع است.
3. نام بانک/وام، درصد، دلیل، مبلغ، قسط، نرخ، مدت، سپرده، ضمانت، حساب، شرایط و وضعیت فقط از response نسخهٔ `PUBLISHED` بیاید. اگر fact معتبری مانند «مجموع سود وام» در قرارداد serving وجود ندارد، UI باید آن را نسازد یا از نرخ/مدت استنتاج نکند.
4. URL لوگوی بانک فقط از فیلد public و validateشدهٔ `bankLogoReference` همان وام بیاید و به‌صورت تصویر SVG/وب امن render شود؛ frontend به PostgreSQL، source/provenance یا URL حدسی وصل نشود. مقدار نامعتبر یا غایب باید fallback بدون تصویر داشته باشد.
5. دو کنترل فیلتر باید دقیقاً سه partition server-owned «بیشترین تطابق»، «کمترین تطابق» و «وضعیت متغیر» و نام بانک را انتخاب کنند؛ client نباید score/threshold/order/مورد جدید بسازد. keyboard accessibility، loading/error/empty و ورود مستقیم بدون session حفظ شوند.
6. test schema/API برای URL لوگوی معتبر و نامعتبر، E2E برای سه فیلتر، logo، جزئیات و flow موجود و visual review mobile/desktop اجرا شود. API/OpenAPI، inventory route، CHANGELOG و PR به‌روز شوند؛ `docs/project-current-state.md` تا پایان کامل US-09/T07 تغییر نکند.

**معیار پذیرش:** source صفحه‌ها واقعاً ماژولار و قابل نگهداری است؛ UI مرجع با دادهٔ واقعی `PUBLISHED` کار می‌کند؛ لوگوی بانک از URL تأییدشدهٔ همان رکورد می‌آید؛ browser هیچ fact یا scoreای جعل نمی‌کند؛ PR همراه test و مرور تصویری قابل merge است. `T07` همچنان تنها gate استقرار واقعی، Netlify و URL عمومی است.

### اصلاح پایداری UI نتیجه، جزئیات و مقایسه — `US-09.T06C`

**هدف و وابستگی:** پس از `T06B` و پیش از `T07`، ایرادهای نمایشی و flow مشاهده‌شده در mobile/desktop را بدون تغییر موتور، snapshot، دادهٔ وام یا فرمول D-005 رفع کن. `T06B` در همین سند، درست پیش از این task، مرجع استخراج componentهاست.

1. لینک «مشاهده شرایط و مدارک مورد نیاز» در همه کارت‌های نتیجه وسط‌چین و آبی بماند. کارت‌های سه partition عرض، grid، ارتفاع و layout یکسان داشته باشند؛ تنها مقدار تطابق برای ranked/low درصد سروری و برای `needsReview` متن «نامشخص» است. reason/exclusion خام نباید card را گسترش دهد.
2. همه اعداد نمایشی با رقم فارسی و جداکنندهٔ `/` render شوند و نشانهٔ درصد پس از عدد باشد. ارقام ASCII داخل شروط/مدارک متن امن نیز به رقم فارسی تبدیل شوند، بدون تغییر متن یا ساختن fact.
3. فیلترهای نتایج در viewport موبایل overflow نکنند؛ outline سیاه، shadow و popup تیز ناشی از کنترل نباید ظاهر شود و keyboard accessibility حفظ شود.
4. لوگوی بانک فقط از `bankLogoReference` همان response `PUBLISHED` نمایش داده شود؛ client URL نامعتبر را رد و برای URL معتبر SVG/تصویر را با fallback امن فراخوانی کند. اتصال مستقیم UI به DB یا حدس URL ممنوع است.
5. صفحهٔ compare-loans باید با component feature-owned واقعی کار کند، حداقل دو وام واقعی را انتخاب و compare-result را از facts API باز کند. حذف runtime component هنگام refactor ممنوع است.
6. test مرورگر برای سه فیلتر، موبایل، logo URL امن، رقم فارسی، جزئیات و مسیر مقایسه؛ مستندات UI، CHANGELOG و PR به‌روز شوند. `docs/project-current-state.md` تا پایان T07 تغییر نکند.

**معیار پذیرش:** UI نتایج/جزئیات/مقایسه بدون overflow یا تفاوت ساختاری بین cardها کار می‌کند، هر مقدار از API می‌آید، و Playwright مسیر پرسشنامه تا مقایسه و جزئیات را می‌گذراند. این task استقرار یا provider خارجی نیست.

### تکمیل صحت نمایش UI و اعداد فارسی — `US-09.T06D`

**هدف و وابستگی:** پس از `T06C` و پیش از `T07`، همهٔ کارت‌های نتیجه و مقایسه دقیقاً با دادهٔ تأییدشدهٔ API/دیتابیس نمایش داده شوند. `T06B` (ماژولار‌سازی نتیجه و جزئیات) در همین سند پیش از `T06C` ثبت شده است و این task فقط اصلاح visual/UI آن componentهاست.

1. URL لوگوی بانک فقط از پاسخ تأییدشدهٔ جزئیات وام خوانده شود؛ URL معتبر HTTPS/HTTP یا مسیر SVG هم‌مبدأ بدون جعل fallback نمایش داده شود و کارت‌های نتیجه، جزئیات و مقایسه همان لوگو را رندر کنند.
2. سه حالت فیلتر نتیجه و کارت‌های مقایسه یک grid/عرض/شعاع واحد و responsive داشته باشند؛ کارت نباید از viewport موبایل بیرون بزند یا به‌سبب status توضیح متفاوتی بسازد.
3. کنترل‌های فیلتر custom، قابل‌دسترسی و بدون outline سیاه، سایه یا گوشهٔ تیز popup باشند؛ focus کیبورد همچنان نمایان و آبی باشد.
4. لینک شرایط و مدارک آبی و وسط‌چین باشد؛ همهٔ عددهای متن شرایط و پرسشنامه فارسی و علامت درصد پس از عدد باشد.
5. تست browser باید نمایش و بارگیری logo، سه حالت فیلتر، overflow موبایل، کارت مقایسه، اعداد فارسی و درصد trailing را اثبات کند. هیچ تغییر در داده، موتور، snapshot، migration یا D-005 مجاز نیست.

**معیار پذیرش:** UI در desktop/mobile بدون overflow می‌ماند؛ لوگو از منبع واقعی record می‌آید؛ داده/score در browser محاسبه یا جعل نمی‌شود؛ PR شامل تست و شواهد قابل بازبینی است. `docs/project-current-state.md` تا پایان کامل US-09/T07 تغییر نمی‌کند.

### رساندن لوگوی منتشرشده به همهٔ کارت‌ها — `US-09.T06E`

**هدف و وابستگی:** پس از `T06D` و پیش از `T07`، لوگوی بانک باید از همان رکورد `PUBLISHED` همراه پاسخ توصیه‌گر به کارت نتیجه و مقایسه برسد؛ درخواست جزئیات فقط fallback است، نه وابستگی لازم برای رندر logo.

1. API توصیه‌گر برای هر سه partition، فقط `bankLogoReference` تأییدشدهٔ همان serving-catalogue را بازمی‌گرداند. مرورگر URL یا SVG محلی جدید، نام بانک جایگزین یا logo ساختگی تولید نمی‌کند.
2. کارت‌های نتیجه و مقایسه ابتدا logo موجود در response توصیه‌گر را رندر می‌کنند و فقط در نبود آن، detail API را می‌خوانند.
3. کارت‌های high/low/variable در mobile/desktop عرض، box model و header responsive یکسان دارند؛ کارت یا عنوان آن از viewport بیرون نمی‌زند.
4. همه نمایش‌های درصد، از جمله «نرخ بهره اعلامی»، مقدار را با علامت درصد پس از عدد نشان می‌دهند.
5. unit/API/browser test باید propagation logo از serving row تا response و نمایش کارت‌های نتیجه/مقایسه را اثبات کند.

**خارج از scope:** تغییر snapshot، دادهٔ وام، فرمول D-005، migration، provider یا deploy نیست. `docs/project-current-state.md` تا پایان US-09/T07 تغییر نمی‌کند.

### تحویل پایدار دارایی‌های logo بانک — `US-09.T06F`

**هدف و وابستگی:** پس از `T06E` و پیش از `T07`، نمایش logo نباید به hotlink یا دسترس‌پذیری لحظه‌ای `rade.ir` وابسته باشد. ۲۹ فایل SVG تأییدشدهٔ تحویل‌داده‌شده باید دارایی نسخه‌دار خود پروژه باشند؛ URL اصلی فقط provenance باقی می‌ماند.

1. SVGها در مسیر public کنترل‌شدهٔ پروژه نگهداری شوند. manifest نسخه‌دار باید برای هر asset نام، کلید و SHA-256 و برای هر بانک canonical کلید مربوط را ثبت کند.
2. هنگام materialization، `loan_serving_facts` علاوه بر `bank_logo_reference` اصلی، `bank_logo_asset_key` و `bank_logo_asset_sha256` را ثبت کند. هر وام منتشرشده باید mapping تأییدشده داشته باشد؛ نبود آن fail-closed است. migration نیز رکوردهای PUBLISHED پیشین را با همین mapping backfill می‌کند.
3. کارت‌های نتیجه، تطابق کم، وضعیت متغیر، مقایسه و جزئیات از مسیر static خود سامانه logo را نمایش دهند، نه URL خارجی. layout یا source داده/امتیاز/شرط تغییر نمی‌کند.
4. آزمون browser باید مسیر کنترل‌شده، نمایش image و دریافت موفق SVG با MIME درست از همان سامانه را در کارت نتیجه و مقایسه اثبات کند. تست materialization نیز key/hash همه ۱۰۲ وام را بررسی می‌کند.
5. URL اصلی و hash asset در audit/provenance باقی می‌مانند. جایگزینی SVG فقط با فایل تأییدشده، تغییر manifest، hash جدید و PR مجاز است.

**خارج از scope:** deploy عمومی، object storage production، snapshot/migration عملیاتی روی سرور و Netlify واقعی همچنان جزء `T07` هستند. `docs/project-current-state.md` تا پایان کامل US-09/T07 تغییر نمی‌کند.

### نمایش قطعی asset و جهت‌بندی RTL — `US-09.T06G`

**هدف و وابستگی:** پس از T06F و پیش از T07، logoهای تأییدشده باید در مرورگر واقعاً دیده شوند؛ مسیر فایل نباید به نام فارسی یا decode خارجی وابسته باشد.

1. همان SVGهای تأییدشده با SHA-256 محاسبه‌شده از بایت فایل، بدون تغییر محتوا در مسیرهای ASCII و versioned نگهداری شوند؛ manifest و `bank_logo_asset_key` به همان مسیر URL-safe اشاره کنند. migration تکمیلی hashهای رکوردهای PUBLISHED پیشین را نیز تصحیح می‌کند.
2. همهٔ کارت‌های high/low/variable، مقایسه و جزئیات فقط از assetKey داخلی استفاده کنند. fallback خارجی برای logoهای بانکِ catalog مجاز نیست.
3. لینک «مشاهده شرایط و مدارک مورد نیاز» در هر سه فیلتر صریحاً آبی بماند، از جمله پس از visited شدن.
4. درصد در نتیجه، جزئیات و مقایسه با `bdi dir="ltr"` پس از عدد دیده شود؛ این قاعده «نرخ بهره اعلامی» را نیز پوشش می‌دهد.
5. E2E باید برای هر سه فیلتر، URL-safe logo و رنگ لینک را کنترل کند و پاسخ SVG را از خود برنامه بگیرد.

**خارج از scope:** دادهٔ وام، امتیازدهی، D-005، deploy و URL واقعی تغییر نمی‌کند. `docs/project-current-state.md` فقط در پایان US-09/T07 به‌روز می‌شود.

### ثابت‌سازی جای logo و هویت بانک — `US-09.T06H`

**هدف و وابستگی:** پس از T06G و پیش از T07، طول نام بانک نباید جای logo یا عنوان وام را در هیچ کارت قابل‌دسترسی تغییر دهد.

1. هویت بانک component مشترک با box ثابت logo و نام مستقلِ تک‌خطی و کامل باشد؛ نام بانک هرگز ellipsis، کوتاه یا دوخطی نشود، نام کوتاه یا بلند مختصات logo را تغییر ندهد و مقدار کامل API نمایش داده شود.
2. logo با فاصلهٔ ثابت از لبهٔ راست و بالای border کارت anchor و لبهٔ راست آن با نام بانک هم‌تراز شود. عنوان وام مستقل و تک‌خطی در مرکز کارت بماند و top bounding box آن در همهٔ کارت‌ها ۳۰px از border بالایی باشد؛ فضای آن حداقل عنوان چهارکلمه‌ای مرجع را کامل نشان دهد و فقط عنوان طولانی‌تر با ellipsis محدود شود، بدون حذف یا بازنویسی داده.
3. این قرارداد در نتایج high/low/variable، انتخاب مقایسه، نتیجهٔ مقایسه و جزئیات یکسان باشد و در mobile/desktop overflow ایجاد نکند. checkbox انتخاب مقایسه در راست کارت anchor شود و بدون تغییر جای/اندازه باقی بماند؛ ارتفاع کارت انتخاب با کارت نتیجهٔ مقایسه برابر باشد و مرکز ردیف «تطابق با وضعیت مشتری» تنها با تغییر layout خودِ متن، حداکثر با اختلاف ۱px با مرکز checkbox هم‌راستا شود. عدد و نماد درصد تطابق ۲۰٪ بزرگ‌تر از متن ردیف باشد و فهرست برای نوار ثابت اقدام فضای انتهایی کافی رزرو کند. بازگشت از نتیجهٔ مقایسه به انتخاب، همان loanIdهای انتخاب‌شده را فقط در حافظهٔ tab فعلی نگه دارد و checkboxهای آن‌ها سبز بمانند؛ ذخیره در URL یا web storage ممنوع است.
4. logo فقط از asset داخلی و تأییدشده خوانده شود؛ داده، API، migration، scoring و D-005 تغییر نکنند.
5. E2E با نام بانک/وام کوتاه و بلند، کامل‌بودن نام بانک، نمایش کامل عنوان چهارکلمه‌ای، ellipsis عنوان بلندتر، top=۳۰px عنوان، برابر بودن ارتفاع کارت انتخاب/نتیجهٔ مقایسه و هم‌راستایی عمودی متن تطابق/checkbox با تلرانس حداکثر ۱px، رشد ۱٫۲ برابری درصد تطابق و offset راست/بالای logo و راست checkbox را با geometry واقعی مرورگر اثبات کند؛ پنل فیلتر باید بالای کارت‌ها قابل مشاهده/کلیک باشد، کارت دهم بالای نوار ثابت مقایسه کاملاً قابل تعامل بماند، بازگشت از نتیجه checkboxهای انتخاب‌شدهٔ ۲ و ۱۰ وام را در desktop/mobile سبز نگه دارد و آخرین کارت نتیجهٔ مقایسه حداقل ۲۰px تا دکمهٔ ثابت فاصله داشته باشد.

**خارج از scope:** دادهٔ وام، موتور توصیه‌گر، provider خارجی و deploy واقعی تغییر نمی‌کند. `docs/project-current-state.md` تا پایان US-09/T07 تغییر نمی‌کند.

### بازگردانی جریان محلی اطلاعات شخصی و OTP نمایشی — `US-09.T06I`

**هدف و وابستگی:** پس از T06H و پیش از T07، صفحه‌های توسعه‌یافتهٔ اطلاعات شخصی، کد یکبارمصرف و پردازش محلی دوباره در flow کاربر قابل‌دسترسی باشند، بدون بازگرداندن دادهٔ ساختگی وام یا تضعیف قرارداد API توصیه‌گر.

1. مسیر `/personal-info` همان فرم RTL توسعه‌یافتهٔ نام، نام خانوادگی، شمارهٔ همراه، درآمد و شغل را نگه دارد. پیشنهادهای cache موجود برای اطلاعات پیش‌تر واردشده قابل انتخاب بمانند؛ پاسخ‌های پرسشنامه، session ID و trace هرگز در URL یا browser storage ذخیره نشوند.
2. پس از تأیید فرم، مسیر `/verify-code` همان UI شش‌رقمی و شمارش‌معکوس ۱۲۰ ثانیه‌ای/ارسال مجدد را نمایش دهد. در محیط توسعه فقط کد نمایشی ثابت `۱۲۳۴۵۶` جریان UI را جلو می‌برد؛ این رفتار نباید ورود واقعی، OTP واقعی، احراز هویت، ایجاد حساب سرور، ثبت درخواست یا تأیید وام نامیده یا شبیه‌سازی شود.
3. کد نمایشی نادرست خطای فارسی نشان دهد. کد نمایشی درست فقط پروفایل محلیِ نام/نام خانوادگی/شمارهٔ همراه را در همان browser برای نمایش نام در منوی همبرگری ثبت کند و سپس مسیر `/analysis` را باز کند.
4. صفحهٔ spinner توسعه‌یافته در `/analysis` از ۵ تا ۰، هر ثانیه یک‌بار، معکوس بشمارد و پس از پایان فقط به مسیر واقعی نتایج برود. موتور، API، ترتیب نتایج و قواعد fail-closed بدون تغییر می‌مانند؛ در نبود session معتبر صفحهٔ نتایج همچنان دادهٔ ساختگی نشان نمی‌دهد.
5. E2E باید فرم، انتخاب cache موجود، OTP صحیح/نادرست، شمارش ۱۲۰ ثانیه‌ای، شمارش ۵ ثانیه‌ای spinner، نام محلی در منوی همبرگری و حفظ جریان واقعیِ fail-closed نتیجه را کنترل کند.

**خارج از scope:** provider OTP، احراز هویت واقعی، persistence سمت سرورِ پروفایل، دادهٔ وام، snapshot، scoring، D-005، deployment و URL واقعی تغییر نمی‌کنند. `docs/project-current-state.md` تا پایان US-09/T07 تغییر نمی‌کند.

### صحت نمایش داده‌های واقعی در کارت وام — `US-09.T06J`

**هدف و وابستگی:** پس از T06I و پیش از T07، یک اصلاح نمایشیِ محدود انجام شود تا متن‌های قابل‌مشاهدهٔ وام رقم فارسی داشته باشند، رنگ کارت فقط معنای درصد تطابقِ از پیش محاسبه‌شدهٔ سرور را نشان دهد، دکمهٔ نتیجهٔ مقایسه نام درست داشته باشد و SVG تأییدشدهٔ بانک ملی واقعاً قابل‌رندر باشد.

1. هر متن قابل‌مشاهدهٔ حاصل از نام بانک/وام، شرایط و مشخصات وام در صفحه‌های نتیجه، جزئیات و مقایسه، رقم ASCII یا عربی-هندی را فقط در لایهٔ نمایش به رقم فارسی تبدیل کند؛ مقدار canonical، ID، URL، API و دادهٔ PostgreSQL تغییر نکند.
2. کارتِ دارای score با همان درصد گرد‌شده‌ای که به کاربر نشان داده می‌شود این نگاشت رنگ border و عدد/نماد درصد را داشته باشد: `۱۰۰–۸۰ → #0067ff`، `۷۹–۶۰ → #CFD238`، `۵۹–۴۰ → #F28943`، `۳۹–۲۰ → #FF2F00` و `۱۹–۰ → #FF0004`. مورد `needsReview` که score ندارد، رنگ یا درصد ساختگی نگیرد.
3. دکمهٔ پایین `/compare-result` دقیقاً «تحلیل با هوش مصنوعی» باشد؛ رفتار route فعلی و محدودیتِ نبود provider/تحلیل خارجی بدون تغییر بماند.
4. asset کنترل‌شدهٔ بانک ملی از همان SVG تأییدشده و با بایت‌های UTF-8 قابل‌رندر ساخته، با hash/content-address جدید در manifest ثبت و از مسیر داخلی برنامه خوانده شود؛ URL منشأ در دادهٔ serving برای provenance دست‌نخورده بماند.
5. unit test مرز هر پنج بازهٔ رنگ، تبدیل رقم و CSS را کنترل کند؛ E2E نام «میثاق 2» را به «میثاق ۲»، رنگ‌های واقعیِ مرزی، برچسب دکمه و complete/natural size بودن SVG بانک ملی را در مرورگر کنترل کند.

**خارج از scope:** مقدار score، threshold موتور، ترتیب/فیلتر توصیه، دادهٔ وام، migration، API، provider خارجی، deploy و D-005 تغییر نمی‌کنند. `docs/project-current-state.md` تا پایان US-09/T07 تغییر نمی‌کند.

### کنترل‌های صفحهٔ نتایج وام — `US-09.T06K`

**هدف و وابستگی:** پس از T06J و پیش از T07، چهار اصلاح محدودِ قابل مشاهده در `/loan-results` انجام شود؛ بدون تغییر دادن داده، قرارداد API یا منطق موتور توصیه‌گر.

1. منوی «نام بانک» فقط وقتی بیش از چهار نام بانک دارد، حداکثر چهار نام بانک به‌همراه گزینهٔ بازنشانی را هم‌زمان نمایش دهد و بقیهٔ گزینه‌ها با scroll عمودی، بدون بیرون‌زدن یا پنهان‌شدن زیر کارت‌ها، قابل انتخاب باشند.
2. در حالت «کمترین تطابق»، فقط اعضای همان partition کم‌تطابقِ تحویل‌شده از سرور، با همان score موجود، از درصد بالاتر به پایین‌تر نمایش داده شوند؛ در score برابر ترتیب ورودی حفظ شود. UI عضو جدیدی نمی‌سازد و score، threshold، membership یا دلیل را محاسبه/تغییر نمی‌دهد.
3. هر کارت یک کنترل bookmark «ذخیره وام» داشته باشد: حالت نخست outline و پس از کلیک fill است؛ پیام دقیق «وام مورد نظر با موفقیت ذخیره شد» با پس‌زمینهٔ `#BFFFE9` زیر همان کارت نشان داده و پس از دو ثانیه حذف شود. این فقط state نمایشیِ همان tab است؛ هیچ درخواست، claim ذخیرهٔ دائمی، دادهٔ وام یا provider خارجی ایجاد نمی‌شود.
4. عنوان CTA سبز header دقیقاً «بررسی آمادگی دریافت وام» باشد؛ disabled بودن و رفتار فعلی آن تا زمان وجود workflow تأییدشدهٔ درخواست وام تغییر نکند.
5. unit test ترتیب نزولی و پایدارِ partition کم‌تطابق را کنترل کند؛ E2E بازشدن/scroll فیلتر بانک، fill شدن bookmark، رنگ پیام و ناپدیدشدن پس از دو ثانیه، و عنوان CTA را در مرورگر کنترل کند.

**خارج از scope:** PostgreSQL، کاتالوگ PUBLISHED، API، score/threshold/ranking موتور، پاسخ پرسشنامه، جزئیات وام، مقایسه، provider خارجی، استقرار T07 و D-005 تغییر نمی‌کنند. `docs/project-current-state.md` تا پایان US-09/T07 تغییر نمی‌کند.

### پایداری جریان، ذخیره و هویت بصری وام — `US-09.T06L`

**هدف و وابستگی:** پس از T06K و پیش از T07، پنج اصلاح محدود و قابل‌آزمون روی flow موجود انجام شود؛ هیچ دادهٔ وام، score، قرارداد API یا تصمیم موتور تغییر نمی‌کند.

1. در `/loan-results` کنترل save از دو asset تأییدشدهٔ خود پروژه استفاده کند: حالت عادی outline و حالت ذخیره‌شده fill. کلیک نخست فقط state نمایشی همان tab را ذخیره کند و پیام دقیق «وام مورد نظر با موفقیت ذخیره شد» را **بالای همان کارت**، با پس‌زمینهٔ `#BFFFE9`، فقط به‌مدت دو ثانیه نشان دهد. کلیک دوباره state را لغو و فقط آیکن را به حالت عادی برگرداند؛ پیام دوم نمایش داده نشود.
2. برای هر وام در پایین `/loan-details` دکمهٔ سبز «تحلیل با هوش مصنوعی» با همان route موجود نمایش یابد. نبود provider خارجی و ممنوعیتِ تحلیل ساختگی تغییر نمی‌کند.
3. refresh در `/loan-details` و سپس Back باید به همان نتیجهٔ معتبرِ همان history navigation برگردد و کاربر را به تکمیل دوبارهٔ پرسشنامه یا پیام ساختگی هدایت نکند. پاسخ‌ها در URL یا local/session storage نوشته نمی‌شوند؛ فقط state فعالِ history همان browser برای بازسازی مسیر استفاده می‌شود.
4. بازگشت از `/compare-result` به `/compare-loans` انتخاب‌های همان جریان را حفظ کند. اما خروج از `/compare-loans` به `/loan-results` انتخاب‌ها را پاک کند تا ورود بعدی به مقایسه بدون انتخاب باشد.
5. asset کنترل‌شدهٔ بانک ملی روی کارت‌های نتیجه/جزئیات/مقایسه پس‌زمینهٔ مشکی نداشته باشد و رنگ‌های تأییدشدهٔ خود logo را بدون CSS filter یا جعل رنگ نمایش دهد. هر تغییر bytes با hash و manifest کنترل‌شده ثبت شود.

**تست اجباری:** unit/component رفتار toggle و پیام دوثانیه‌ای؛ E2E desktop/mobile برای asset عادی/fill، موقعیت پیام بالای کارت، refresh-detail→Back بدون پرسشنامه، دو قانون بازگشت مقایسه، CTA جزئیات و render طبیعی/شفاف بانک ملی. Build و quality gate نیز باید سبز باشند.

**خارج از scope:** PostgreSQL، داده/manifest وام به‌جز asset hash بانک ملی، API، scoring، threshold، ranking، پاسخ پرسشنامه، provider خارجی، deploy واقعی و D-005 تغییر نمی‌کنند. `docs/project-current-state.md` تا پایان US-09/T07 تغییر نمی‌کند.

### toolbar جزئیات و performance پاک — `US-09.T06N`

**هدف و وابستگی:** این task از baseline سالمِ `main` پس از T06L و بدون انتقال کد PR #68 اجرا می‌شود. هدف فقط حذف فاصلهٔ ناپایدار CTA و کار اضافهٔ قابل‌اثبات در client است.

1. toolbar «تحلیل با هوش مصنوعی» در `/loan-details` در desktop و mobile به لبهٔ پایین viewport متصل باشد؛ ارتفاع آن در داخل صفحه رزرو شود تا آخرین شرط وام پنهان نشود.
2. assetهای logo که فقط در spinner تحلیل نمایش دارند نباید در شروع routeهای دیگر بارگیری شوند.
3. درخواست recommendation در طول شمارش پنج‌ثانیه‌ای موجود شروع شود؛ برای هر session فقط یک درخواست هم‌زمان مجاز است و پس از خطا فقط «تلاش مجدد» کاربر درخواست جدید بسازد.
4. تغییر، دادهٔ PUBLISHED، API، score، threshold، session retention، refresh/back contract، compare، save، logoهای serving و D-005 را تغییر نمی‌دهد.

**تست اجباری:** E2E desktop/mobile برای اتصال toolbar به viewport و مشاهدهٔ آخرین شرط؛ آزمون recommendation کند/خطادار برای one-request و retry صریح؛ build و quality gate.

**خارج از scope:** migration، dependency، PostgreSQL، داده، engine، provider خارجی، deploy و سند تداوم تغییر نمی‌کنند؛ `docs/project-current-state.md` تا پایان US-09/T07 ثابت می‌ماند.

### بازیابی بی‌صدای session و dedupe جزئیات — `US-09.T06O`

**هدف و وابستگی:** پس از merge شدن T06N، تجربهٔ واقعی flow پرسشنامه و routeهای جزئیات را بدون انتقال PR #68 اصلاح کن.

1. پاسخ HTTP 410 برای session ناشناس نباید کارت خطا یا درخواست شروع مجدد به کاربر نمایش دهد؛ session تازه ساخته شود و پاسخ‌های canonical موجود در حافظه، به‌ترتیب replay شوند.
2. برای یک `loanId`، چند consumer هم‌زمان در یک tab فقط یک درخواست detail مشترک بسازند؛ پاسخ معتبر همان tab reuse شود و abort یک consumer درخواست مشترک را لغو نکند.
3. نوار CTA جزئیات قاب کامل نمونهٔ تأییدشده داشته باشد: ۳۵px فضای سفید بالا، دکمهٔ ۴۸px، و ۳۴px فضای سفید پایین؛ آخرین شرط همچنان قابل مشاهده باشد.
4. دادهٔ PUBLISHED، API schema، scoring، threshold، D-005، TTL سرور، session retention، provider و deploy تغییر نمی‌کنند.

**تست اجباری:** unit برای dedupe/cache؛ E2E برای 410 → session تازه/replay بدون نمایش کارت؛ desktop/mobile برای هندسهٔ قاب CTA و دسترسی آخرین شرط؛ quality و migration gate.

**خارج از scope:** مهاجرت، dependency، تغییر داده، engine، provider خارجی، deployment و سند تداوم تغییر نمی‌کنند؛ `docs/project-current-state.md` تا پایان US-09/T07 ثابت می‌ماند.

### حذف UI ساختگی و قاب قطعی CTA — `US-09.T06P`

**هدف:** پس از T06O، هیچ entry یا refresh نباید صفحهٔ mock قدیمی را نمایش دهد و CTA جزئیات باید دقیقاً قاب کامل نمونه را داشته باشد.

1. `src/App.jsx`، صفحهٔ mock وام خارج از runtime، حذف شود؛ entry واقعی فقط `src/home page.jsx` بماند.
2. قاب CTA جزئیات ارتفاع قطعی ۱۱۷px داشته باشد: ۳۵px بالا، دکمهٔ ۴۸px، ۳۴px پایین؛ E2E هر چهار مختصات را در desktop/mobile کنترل کند.
3. بررسی performance بر مبنای Network واقعی ادامه یابد؛ CI سبز جای اندازه‌گیری مرورگر را نمی‌گیرد.

**خارج از scope:** داده، API، scoring، session contract، provider، deployment و سند تداوم تغییر نمی‌کنند.

### حذف کامل fallback static در refresh — `US-09.T06Q`

**هدف:** صفحهٔ mock قدیمی حتی برای یک لحظه در شروع یا refresh نمایش داده نشود؛ ریشهٔ HTML فقط محل mount برنامهٔ واقعی باشد.

1. همهٔ markup ثابتِ صفحهٔ mock از `index.html` و تنها از همان فایل حذف شود؛ `#root` خالی بماند و فقط `src/main.jsx` برنامهٔ فعال را mount کند.
2. یک آزمون واحد، خالی‌بودن `#root` و نبود متن‌های شناسایی‌شدهٔ mock را در HTML ورودی کنترل کند.
3. یک E2E پس از `page.reload()` نبود همان متن‌ها را کنترل کند؛ این آزمون جای اندازه‌گیری performance یا استقرار واقعی نیست.

**خارج از scope:** UI فعال، داده، API، scoring، session contract، provider، deployment و سند تداوم تغییر نمی‌کنند.

### ارتقای وابستگی‌های امنیتی frontend — `US-09.T06R`

**هدف:** آسیب‌پذیری‌های شناخته‌شدهٔ زنجیرهٔ Vite در محیط توسعه، به‌ویژه Windows، بدون تغییر رفتار محصول رفع شوند.

1. Vite در `package.json` و `package-lock.json` روی نسخهٔ دقیقِ امن `8.3.3` pin شود؛ وابستگی‌های گذرای آن فقط از resolver npm و lockfile بازتولیدپذیر به نسخهٔ امن برسند.
2. `npm audit` روی lockfile نهایی هیچ آسیب‌پذیری high/critical یا مورد باقی‌مانده از زنجیرهٔ Vite/PostCSS/nanoid/source-map-js گزارش ندهد.
3. build و testهای موجود در CI روی lockfile جدید اجرا شوند؛ شکست‌های نامرتبط از asset یا محیط محلی به‌عنوان موفقیت گزارش نشوند.
4. هیچ dependency یا API/runtime محصولی جز آنچه resolver برای همین زنجیره لازم دارد تغییر نکند.

**خارج از scope:** UI، data/API، scoring، migration، session، provider، deployment و سند تداوم تغییر نمی‌کنند.

### نمایش سریع نتیجهٔ واقعی بدون fan-out جزئیات — `US-09.T06S`

**هدف:** پس از spinner پنج‌ثانیه‌ای، صفحهٔ نتیجه با دادهٔ واقعیِ منتشرشده فوراً قابل‌نمایش باشد؛ بدون ساختن داده، امتیاز یا شرط در مرورگر.

1. endpoint توصیه در هر درخواست فقط یک snapshot تأییدشده را می‌خواند و همان snapshot برای impacts و scoring به کار می‌رود؛ مدل، ضرایب، threshold، partition و fail-closed تغییر نمی‌کنند.
2. همان پاسخِ server-owned، چهار fact نمایشیِ هر وام PUBLISHED را از serving catalogue هم‌نسخه می‌آورد: مبلغ، قسط، مدت و نرخ بهره. شروط کامل فقط همچنان از endpoint جزئیات در زمان ورود کاربر خوانده می‌شوند.
3. کارت نتیجه وقتی `loanSummary` معتبر دارد، هیچ درخواست جزئیات اضافی نمی‌فرستد؛ برای پاسخ‌های قدیمی/ناقص فقط fallback امن endpoint جزئیات باقی می‌ماند. مرورگر هیچ fact یا score جدیدی محاسبه نمی‌کند.
4. آزمون backend دقیقاً یک خواندن snapshot و تطابق loanSummary با endpoint جزئیات را ثابت کند. آزمون E2E ثابت کند کارت‌های آماده بلافاصله پس از route نتیجه دیده می‌شوند و قبل از ورود به جزئیات، موج N+1 درخواست detail رخ نمی‌دهد.

**خارج از scope:** دادهٔ منبع، migration، session/OTP، سیاست نگهداری، قواعد D-005، API جزئیات، UI ظاهری، provider خارجی، استقرار و سند تداوم تغییر نمی‌کنند.

### استفادهٔ پایدار از connection pool در API محلی — `US-09.T06T`

**هدف:** تأخیر ناشی از ساخت و dispose کردن engine SQLAlchemy در هر درخواست محلی حذف شود، بدون تغییر دادن قرارداد عمومی API، دادهٔ PUBLISHED، retention، Redis fallback یا منطق توصیه.

1. FastAPI در lifespan خود فقط یک database engine و session factory می‌سازد، آن‌ها را در `app.state` نگه می‌دارد و فقط در shutdown همان engine را dispose می‌کند.
2. dependencyهای questionnaire، جزئیات و recommendation در هر HTTP request از همان factory یک `Session` تازه می‌گیرند و فقط همان Session را در پایان request می‌بندند؛ هیچ Session میان requestها share نمی‌شود.
3. در محیط local/test فقط برای ساخت session، ثبت پاسخ و recommendation، log ساخت‌یافته با نام ثابت endpoint، status و `duration_ms` ثبت می‌شود. session ID، answer، payload، database URL و secret نباید در log بیایند؛ production timing development را منتشر نمی‌کند.
4. تست‌ها باید creation یک‌بارهٔ engine در lifecycle، dispose در shutdown، استقلال/بسته‌شدن Sessionها، timing redacted و مسیر کامل session → answer → recommendation را ثابت کنند. اندازه‌گیری واقعی localhost پیش و پس از تغییر، جدا از CI ثبت شود.

**خارج از scope:** PostgreSQL schema/migration، Redis fallback، retention، داده وام PUBLISHED، D-005، scoring، API response، UI، provider خارجی، deploy و سند تداوم تغییر نمی‌کنند.


### بهینه‌سازی queryهای پرسشنامه و جزئیات وام — US-09.T06U

**هدف:** حذف queryهای تکراری در ثبت پاسخ و جلوگیری از خواندن کل کاتالوگ برای جزئیات یک وام، بدون تغییر قرارداد API، دادهٔ PUBLISHED، retention، Redis fallback، D-005 یا scoring.

1. شناسه‌های مرجع پرسشنامه فقط یک‌بار در lifecycle برنامه از کاتالوگ تأییدشده آماده می‌شوند؛ هر request آن‌ها را reuse می‌کند و دیگر catalog-check/commit تکراری ندارد.
2. هر درخواست همچنان Session مستقل خود را دارد؛ Session یا transaction بین requestها share نمی‌شود.
3. جزئیات وام فقط با شناسهٔ opaque همان وام و تمام predicateهای publication موجود query می‌شود؛ خواندن و scan همهٔ ردیف‌های serving catalogue ممنوع است.
4. معیار پذیرش local warm: p95 ثبت پاسخ در مرورگر کمتر از ۵۰ms و مسیر جزئیات با یک request برای یک loanId، همراه با ثبت زمان مرحله‌ایِ redacted برای تشخیص گلوگاه.
5. تست regression باید reuse reference catalogue، بسته‌شدن Session، فیلتر PUBLISHED و lookup تک‌وام را پوشش دهد؛ اندازه‌گیری واقعی مرورگر از CI جدا گزارش می‌شود.

**خارج از scope:** migration/schema، دادهٔ وام، Redis fallback، retention، UI، URL، scoring، D-005، provider خارجی، deploy و سند تداوم تغییر نمی‌کنند.

### استاندارد skeleton و تعامل مقایسه — `US-09.T06V`

**هدف:** پس از ۵۰ms انتظار برای دادهٔ واقعی، Skeleton همان ناحیهٔ محصول نمایش داده شود؛ پیام loading یا صفحهٔ خالی به کاربر نشان داده نشود. این استاندارد برای همهٔ صفحه‌ها و تغییرهای بعدی لازم‌الاجرا است؛ spinner پنج‌ثانیه‌ای تحلیل تنها استثنای صریح است.

1. Skeleton فقط نمایشی است، داده، score، source یا نتیجهٔ ساختگی تولید نمی‌کند.
2. جزئیات مقدار null با واحد پول یا واحد زمانی ترکیب نمی‌شود.
3. کارت وام در compare-loans و compare-result با click/keyboard به جزئیات همان loanId می‌رود؛ کنترل checkbox از navigation مستقل می‌ماند.
4. دکمهٔ مقایسه با کمتر از دو انتخاب disabled است و ترتیب compare-loans نزولی بر اساس score server-owned با tie-break loanId است.
5. E2E باید delayed Skeleton، نبود متن loading قدیمی، navigation کارت و disable/enable مقایسه را کنترل کند.

**خارج از scope:** API، دادهٔ PUBLISHED، D-005، scoring، migration، provider خارجی، deploy و سند تداوم تغییر نمی‌کنند.

### پوشش نخستین paint و انتظار پاسخ پرسشنامه — `US-09.T06W`

**هدف:** پس از `T06V`، نخستین ورود/refresh به home و navigation پرسشنامه نباید صفحهٔ سفید یا متن loading داشته باشد. مسیرهای سبک باید بدون انتظار غیرضروری render شوند و اگر آماده‌شدن برنامه یا ثبت پاسخ canonical بیش از ۵۰ms طول کشید، فقط Skeleton همان ناحیه نمایش داده شود. این task سرعت شبکه یا API را جعل نمی‌کند؛ budget واقعی با Network اندازه‌گیری می‌شود.

1. `#root` در HTML اولیه خالی می‌ماند. fallback مستقلِ document-level فقط پس از ۵۰ms ظاهر می‌شود و پس از paint اپ واقعی حذف می‌شود؛ صفحهٔ mock یا متن ساختگی ممنوع است.
2. هنگام ثبت پاسخ پرسشنامه، تا ۵۰ms UI فعلی پایدار می‌ماند و پس از آن Skeleton ناحیهٔ پرسشنامه جای آن را می‌پوشاند؛ پاسخ، session، score و route از Skeleton ساخته یا تغییر داده نمی‌شوند.
3. دکمهٔ «مقایسه کن» با تنها یک انتخاب علاوه بر `disabled` بودن، حالت خاکستری و cursor غیرقابل‌کلیک دارد؛ با دو انتخاب به سبک فعال موجود برمی‌گردد.
4. E2E باید threshold Skeleton پرسشنامه، حذف fallback پس از paint و disabled/enable/رنگ دکمه را کنترل کند. اندازه‌گیری p95 Network مسیرهای local warm جدا از CI ثبت می‌شود؛ هر مسیر بالای ۵۰ms باید علت یا Skeleton داشته باشد.
5. `D-005`، دادهٔ `PUBLISHED`، API، scoring، migration، provider، deploy و سند تداوم تغییر نمی‌کنند.

**معیار پذیرش:** کاربر هنگام آغاز یا refresh طولانی، Skeleton می‌بیند نه صفحهٔ سفید/پیام loading؛ ثبت پاسخ کند نیز همین رفتار را دارد و دکمهٔ مقایسهٔ یک وام ظاهراً و عملاً غیرفعال است.

### بهینه‌سازی نخستین paint و Skeleton هم‌شکل مسیر — `US-09.T06X`

**هدف:** پس از `T06W`، انتظار بیش از ۵۰ms باید Skeleton هم‌شکل همان صفحه نشان دهد، نه الگوی چندخطی ثابت. نخستین paint نیز نباید به stylesheet فونت خارجی وابسته بماند. این task معیار قطعی «همهٔ مسیرها زیر ۵۰ms» را جعل نمی‌کند: بودجه باید با اندازه‌گیری warm/cold واقعی هر محیط سنجیده شود؛ هر انتظار بالاتر از آستانه با Skeleton مسیر پوشیده می‌شود.

1. stylesheet فونت فقط برای بهبود ظاهر است و نباید نخستین paint را render-block کند؛ fallback سیستم و `font-display: swap` برای مشاهدهٔ فوری مجاز است.
2. fallback پیش از mount بر اساس path چهار فرم دارد: home (هدر/hero/control/action)، پرسشنامه (stage/title/options/action)، فهرست/مقایسه (heading/filter/cards)، و جزئیات (heading/summary/groups/action). هیچ‌یک نام، مبلغ، score، شرط یا نتیجهٔ ساختگی ندارد.
3. `DeferredPageSkeleton` نیز برای loading درون React، variantهای cards/detail/questionnaire با هندسهٔ همان مسیر دارد. ظاهر موجود تنها پس از آماده‌شدن دادهٔ واقعی جای آن را می‌گیرد.
4. تصویرهای غیرضروریِ پایین صفحهٔ home lazy/async decode می‌شوند تا با شروع مسیر رقابت نکنند. تغییر داده، API، session، scoring، D-005، migration و deploy ممنوع است.
5. E2E باید آستانهٔ ۵۰ms و نمایش فرم درست برای home، questionnaire و detail را کنترل کند. گزارش performance فقط زمان‌های واقعاً اندازه‌گیری‌شده را بیان می‌کند.

**معیار پذیرش:** در انتظار طولانی، کاربر صفحهٔ سفید یا پیام loading نمی‌بیند و شکل Skeleton با مسیر فعلی سازگار است؛ paint اولیه به دانلود stylesheet فونت وابسته نیست. **خارج از scope:** تضمین عدد ۵۰ms برای cold-start/Docker/شبکه و سند تداوم؛ تحلیل علت‌های باقی‌مانده در task محدودِ بعدی انجام می‌شود.

### Runbook استقرار محیط پایدار — `US-09.T06Y`

**هدف:** پیش از provision واقعی T07، مسیر عملیاتیِ قابل‌اجرا و بازبینی‌پذیر برای PostgreSQL دائمی، FastAPI HTTPS، Netlify، publication داده، آزمون URL واقعی و rollback ثبت شود. این task صرفاً مستندات است و هیچ سرور، secret، داده یا deploy واقعی ایجاد نمی‌کند.

1. runbook باید معماری هدف، مالک/دامنه/secretهای لازم، backup/restore، migration، audit و publication رسمی، اتصال Netlify، آزمون end-to-end و restart را به ترتیب امن بیان کند.
2. دستور publication فقط از مسیر موجودِ audit/approval استفاده کند؛ هیچ داده یا ضریب فرضی، اصلاح مستقیم دیتابیس یا fallback توصیه‌گر مجاز نیست.
3. صحت‌سنجی T07 باید صریحاً PostgreSQL پایدار، API HTTPS، اتصال Netlify، URL واقعی، mobile/desktop و restart را جدا از CI اعلام کند.
4. rollback کد، migration و داده از هم تفکیک و secretها از Git/فرانت/گزارش حذف شوند.
5. سند در `docs/runbook/` قرار گیرد و از docs عملیات پیوند داشته باشد. سند تداوم فقط در پایان کامل US-09 تغییر می‌کند.

**معیار پذیرش:** مالک پروژه یک راهنمای مستقل، مرحله‌به‌مرحله و بدون credential در Git دارد که مشخص می‌کند چگونه محیط واقعی را بسازد و چگونه اثبات کند ساخته شده است. **خارج از scope:** اجرای T07، provision سرور، DNS/TLS، انتشار production یا تغییر runtime.

### منوی مهمان/کاربر و ورود OTP نمایشی — `US-09.T06Z`

**هدف:** منوی همبرگری باید فقط بر اساس وضعیت ورودِ محلی، دو حالت روشن و کوچک داشته باشد: مهمان فقط «ورود کاربر» و «درباره ما» را می‌بیند؛ پس از تکمیل OTP نمایشی، نام کاربر، «پروفایل کاربر»، «سوابق درخواست وام»، «وام‌های نشان شده»، «درباره ما» و خروج نمایش داده می‌شوند.

1. دکمهٔ ورود از نوار ناوبری home حذف می‌شود و شروع ورود فقط از منوی مهمان است.
2. تکمیل شش رقم در flow نمایشی، فقط profile محلی UI را می‌سازد؛ این رفتار نباید به‌عنوان احراز هویت سروری یا تأیید هویت واقعی معرفی شود.
3. خروج فقط وضعیت محلی profile را پاک می‌کند و منوی مهمان را بازمی‌گرداند؛ API، session پرسشنامه، داده، scoring، D-005 و migration تغییری نمی‌کنند.
4. آیکن‌های menu سیاه‌اند؛ متن خروج می‌تواند برای تمایز قرمز باشد. آزمون E2E باید حذف ورود از home، دو آیتم مهمان، ورود OTP، آیتم‌های کاربر واردشده و بازگشت به مهمان پس از خروج را کنترل کند.

**خارج از scope:** provider OTP، ورود/هویت واقعی، role/access control، API جدید، حساب کاربری پایدار سمت سرور، دادهٔ وام و سند تداوم.

### استقرار و راستی‌آزمایی محیط پایدار — `US-09.T07`

**هدف و وابستگی:** پس از T06A، یک محیط staging با PostgreSQL دائمی و بک‌اند مستقر بساز؛ سایت Netlify را به همان API وصل کن و مسیر واقعی را روی URL در دسترس مالک محصول اثبات کن. این تسک بخشی از تحویل US-09 است؛ سبز بودن CI یا دیتابیس موقت GitHub Actions جای آن را نمی‌گیرد. انتشار production نهایی، امنیت و release gate همچنان در US-11/US-12 انجام می‌شوند.

1. میزبان API و PostgreSQL پایدار، مالک حساب، ناحیه، محدودیت هزینه/دسترسی و backup/restore را پیش از provisioning ثبت کن. secret/connection string در Git، PR و log قرار نگیرد؛ DB فقط از API/job مدیریتی مجاز قابل دسترسی باشد.
2. image/runtime را برای اجرای FastAPI، migration و job ورود دادهٔ رسمی آماده کن؛ بایت شش منبع را ثابت نگه دار. ابتدا migration سازگار، سپس audit فقط‌خواندنی دیتابیس انتخاب‌شده، و فقط بعد از approval صریح، ورود/انتشار idempotent و با provenance را روی **همان** DB انجام بده. تعداد، هشت category/state، شرایط و active pointer را از DB مستقر دوباره بخوان.
3. Netlify را با API همان محیط از مسیر same-origin یا origin allowlist امن وصل کن؛ ترتیب rewrite پیش از SPA fallback، TLS، env و health/readiness را آزمون کن. هیچ credential دیتابیس به مرورگر منتقل نشود.
4. روی URL واقعی، پرسشنامه تا نتیجهٔ محاسبه‌شده در سرور، ۸۸ مورد بالقوهٔ rankable/۱۴ نیازمند بررسی بر اساس منبع در سناریوهای مناسب، شروط همان وام، empty/error، mobile/desktop، restart و پایداری داده را با شواهد قابل بازبینی تست کن. شمارش نتیجهٔ یک پرسشنامه ممکن است به فیلتر و ورودی وابسته باشد؛ صرف شمارش منبع به‌جای آزمون مسیر واقعی پذیرفته نیست.
5. runbook استقرار، نسخهٔ داده/config، زمان و نتیجهٔ migration/import، URL، هزینه و محل backup، rollback و محدودیت‌های شناخته‌شده را در PR/checkpoint ثبت کن. فقط بعد از آزمون روی سرویس مستقر T07 Done و کل US-09 قابل پایان است؛ سند تداوم در همین پایان داستان به‌روزرسانی شود.

**معیار پذیرش:** PostgreSQL دائمی staging واقعاً وجود دارد و نسخهٔ تأییدشدهٔ وام‌ها/شروط در آن ثبت و از API خوانده می‌شود؛ سایت Netlify به همان API وصل است؛ مالک محصول مسیر پرسشنامه تا نتیجه و جزئیات را روی URL واقعی طی می‌کند؛ E2E و آزمون دستی URL و بازیابی پس از restart سبزند. CI به‌تنهایی معیار پذیرش نیست.

قانون عبور: تا زمانی که یک شناسهٔ `T` commit، checkpoint، test output و سندِ مربوط را ندارد، «Done» نیست و شناسهٔ بعدی آغاز نمی‌شود. اگر یک تغییر به چند شناسه نیاز دارد، آن را به چند commit مستقل تقسیم کن؛ هیچ commit نباید وابستگی‌های آینده را زودتر پیاده‌سازی کند. وضعیت جاری فقط در `docs/project-current-state.md` ثبت می‌شود و باید شامل `activeTaskId`، commit، testهای اجراشده، blocker، تصمیم باز و قدم بعد باشد.

### پروتکل ثابت اجرای هر تسک

برای هر تسک و زیرتسک، Codex باید به‌ترتیب: (۱) بخش مرتبط همین guide و ADR/data decision را بخواند؛ (۲) acceptance criterion و test را پیش از کدنویسی بنویسد؛ (۳) کوچک‌ترین تغییر سازگار را پیاده کند؛ (۴) lint/type/unit/integration یا E2E مرتبط را اجرا کند؛ (۵) code review محلی شامل امنیت، performance، duplication، boundary و comment/docstring انجام دهد؛ (۶) فقط در صورت نیاز refactor محدود با test characterization انجام دهد؛ (۷) docs، ERD/OpenAPI/pipeline/runbook یا module map مربوط را به‌روزرسانی کند؛ (۸) `CHANGELOG.md` و PR را به‌روز کند. شکست هر مرحله مانع شروع تسک بعدی است.

### CHANGELOG و ثبت تغییرات

یک `CHANGELOG.md` در ریشهٔ مخزن با قالب Keep a Changelog ایجاد و نگهداری کن. هر change باید زیر `Unreleased` و یکی از دسته‌های `Added`, `Changed`, `Fixed`, `Security`, `Deprecated`, `Removed` ثبت شود؛ entry شامل شناسهٔ user story/task، خلاصهٔ قابل‌فهم، اثر داده/API/migration، نسخهٔ config/schema در صورت مرتبط‌بودن و لینک PR/ADR باشد. تغییر migration، data decision، قانون scoring، امنیت، dependency، رفتار UI یا bug fix بدون CHANGELOG entry قابل قبول نیست. در release، `Unreleased` به نسخه و تاریخ تبدیل شود؛ تاریخچهٔ قبلی بازنویسی نشود.

## پروتکل توسعهٔ مرحله‌ای، تداوم کار و مصرف بهینهٔ توکن

پروژه باید در چند مرحلهٔ کوچک، مستقل و قابل تحویل توسعه یابد؛ هیچ نشست یا پاسخ واحدی نباید مسئول توسعهٔ کل backend، دیتابیس، UI و deploy باشد. هدف از این روش، حذف دوباره‌کاری، حفظ زمینهٔ لازم در Git و اسناد، و مصرف حداقلیِ مؤثرِ توکن است؛ نه کوتاه‌کردن بررسی‌های ضروری امنیت، تست یا کیفیت.

### قانون قطعی بودجهٔ توسعه و توکن

Codex نباید کار را با این فرض آغاز کند که در همان نشست برای کل User Story یا کل پروژه بودجهٔ توکن دارد. پیش از شروع هر `US-xx.T-yy` باید یک **برآورد محافظه‌کارانهٔ ظرفیت** انجام دهد: خواندن حداقلیِ زمینه، پیاده‌سازی، اجرای تست نزدیک، رفع خطای محتمل، مستندسازی، checkpoint و commit. فقط وقتی task شروع می‌شود که ظرفیت باقی‌مانده برای بستن کامل همین چرخه کافی باشد. اندازهٔ task باید با ظرفیت واقعی باقی‌مانده هماهنگ شود، نه با آرزوی تمام‌کردن یک قابلیت بزرگ.

اگر ظرفیت برای چرخهٔ کامل کافی نیست یا در طول کار کاهش می‌یابد، Codex باید **پیش از تغییر نیمه‌تمام** یکی از این کارها را انجام دهد: (۱) task را به زیرتسک‌های مستقل و مرتب‌تر تقسیم کند؛ یا (۲) فقط یک checkpoint مستند و بدون تغییر کد بسازد. شروع تغییر کد، migration، deploy یا refactor وقتی احتمال معقولی وجود دارد که test/document/commit آن در همان چرخه تمام نشود ممنوع است. هیچ قابلیت نباید در وضعیت «کد نوشته شده ولی تست، مستندات یا commit ندارد» رها شود.

هر checkpoint آغاز باید `estimatedWorkScope` و `completionBudget` را ثبت کند؛ checkpoint پایان باید `actualScope`، وضعیت کامل/ناتمام و دقیق‌ترین `nextTaskId` را داشته باشد. در صورت قطع اجباری نشست، تنها وضعیت معتبر، آخرین commit موفق و `docs/project-current-state.md` است؛ نشست بعدی از همان checkpoint ادامه می‌دهد و بدون تکرارِ کاوش یا دستکاریِ قبلی کار را می‌بندد. هدف عملی این پروتکل کاهش چشمگیر احتمال توقف وسط توسعه است؛ هیچ ادعای غیرواقعی دربارهٔ مقدار دقیق توکن یا تضمین فنیِ ناممکن جای این gate را نمی‌گیرد.

### ۱. واحد توسعهٔ اجباری

هر واحد توسعه دقیقاً یک task یا زیرتسک از User Story فعال است و باید آن‌قدر کوچک باشد که بتوان آن را در یک PR/commit روشن بازبینی کرد. پس از بازخوانی کامل و اجباری همین guide، Codex فقط این موارد را از سایر منابع پروژه بخواند: ADR/data decision مرتبط، module map همان feature، قرارداد public و testهای همان محدوده. خواندن دوبارهٔ کل مخزن، تکرار محتوای بلند اسناد یا بازنویسی فایل‌های نامرتبط ممنوع است.

برای هر واحد، این ترتیب ثابت است:

1. **Checkpoint آغاز:** شناسهٔ `US-xx / T-xx`، هدف، فایل‌های هدف، acceptance criterion، خطر، وابستگی و test plan در PR/issue یا `docs/progress/` ثبت شود.
2. **بررسی محدود:** فقط `rg`/فهرست فایل و قطعه‌های مرتبط خوانده شوند؛ محتوا یا خروجی‌های بلند دوباره در گفتگو کپی نشوند.
3. **تغییر حداقلی:** فقط فایل‌های متعلق به همان boundary تغییر کنند. اگر تغییر به boundary دیگر نیاز دارد، contract/ADR جداگانه بساز و task را بشکن.
4. **تست نزدیک:** ابتدا سریع‌ترین test واحد/fixture، سپس integration مرتبط اجرا شود. refactor فقط پس از سبزشدن behavior فعلی و همراه test انجام شود.
5. **ثبت پایدار:** code comment/docstring، سند مرتبط، `CHANGELOG.md` و progress checkpoint به‌روز شوند؛ سپس یک commit کوچک با پیام conventional و شناسهٔ task ثبت شود.
6. **Checkpoint پایان:** فایل‌های تغییرکرده، فرمان‌های test و نتیجه، migration/config/data version، ریسک باقی‌مانده و task بعدی در `docs/progress/current-state.md` ثبت شود.

هر زمان ادامهٔ کار به نشست/گفتگوی بعدی منتقل شد، Codex باید تنها با خواندن `docs/progress/current-state.md`، `CHANGELOG.md`، PR/commit قبلی و فایل‌های feature فعال ادامه دهد. از حدس‌زدن وضعیت یا انجام دوبارهٔ کار قبلی پرهیز کند. اگر checkpoint ناقص است، ابتدا آن را بازسازی کند و feature جدید شروع نکند.

### ۲. سیاست بهینه‌سازی توکن و زمینه

- از برنامهٔ User Story به‌عنوان صف قطعی کار استفاده کن؛ یک task فعال در هر زمان.
- قبل از تولید کد جدید، contract، test fixture و موجودیت مشابه را جست‌وجو کن تا کد تکراری یا abstraction جدید بی‌دلیل ساخته نشود.
- patchهای کوچک، خروجی test خلاصه و link به فایل/commit را ترجیح بده؛ log کامل یا source بزرگ فقط وقتی failure به آن وابسته است بررسی شود.
- اسناد مرجع بزرگ (`.unitext`) را یک‌بار inventory/audit کن و نتیجهٔ ساختاریافته را در `docs/source-inventory.md` و `docs/recommendation-data-decisions.md` نگه دار؛ در taskهای بعدی فقط source/section لازم را بخوان.
- testهای کم‌هزینه را نزدیک تغییر اجرا کن؛ full suite و E2E/security/performance را در gateهای داستان و release اجرا کن. شکست test دقیقاً همان لایه را اصلاح کند.
- «صرفه‌جویی توکن» هرگز مجوز حذف migration، تست، threat model، backup verification، مستندات یا review نیست.
- اگر یک task بیش از حد بزرگ شد، توقف کن، آن را به taskهای کوچک‌تر با dependency روشن تقسیم کن و checkpoint ثبت کن؛ ادامهٔ کورکورانه ممنوع است.

### ۳. Git، commit و مستندسازی مرحله‌ای

از شاخهٔ feature برای هر user story یا مجموعهٔ کوچکِ سازگار استفاده کن. هر commit باید buildable یا دست‌کم در یک حالت قابل توضیح باشد و پیامش شامل نوع و شناسهٔ task باشد؛ مثال: `feat(US-04/T-03): add versioned loan-term schema`. commitهای مجاز: `docs`, `test`, `feat`, `fix`, `refactor`, `chore`, `security`, `perf`.

ترتیب پیشنهادی برای یک story: `docs/test` → `domain/config` → `infrastructure/migration` → `application/API` → `presentation` → `refactor/docs/release-gate`. در یک commit، migration، تغییر رفتار و refactor گسترده را مخلوط نکن. هر PR باید summary، محدودهٔ User Story/Task، ریسک، test output خلاصه، تغییر داده/API/migration، تصمیم امنیتی و rollback را داشته باشد.

### ۴. محیط محلی استاندارد و Docker

برای جلوگیری از تفاوت سیستم‌ها، محیط اصلی توسعه با Docker Compose اجرا می‌شود. روی Windows، **Docker Desktop با WSL 2**؛ روی macOS/Linux، Docker Desktop یا Docker Engine به‌همراه Docker Compose v2 لازم است. نصب جداگانهٔ PostgreSQL برای توسعه ضروری نیست؛ دیتابیس در container اجرا می‌شود. ابزارهای محلی لازم:

| ابزار | نسخه/کاربرد | الزام |
| --- | --- | --- |
| Git | نسخهٔ پایدار | clone، branch، commit و PR |
| Docker + Compose v2 | نسخهٔ پایدار | frontend، FastAPI، PostgreSQL و ابزارهای وابسته |
| Node.js LTS + npm | نسخهٔ LTS ثابت در `.nvmrc`/`package.json` | React/Vite، lint و test frontend |
| Python 3.12+ | نسخهٔ ثابت در `pyproject.toml` | FastAPI، scripts و test backend |
| `uv` یا ابزار محیط پایتون مصوب | lockfile قطعی | نصب سریع و reproducible dependencyهای Python |
| مرورگر Chromium/Playwright | نسخهٔ قفل‌شده در project | E2E محلی و CI |

در مخزن باید این فایل‌ها وجود داشته باشند و هم‌زمان با توسعه به‌روز شوند:

```text
compose.yaml                         # سرویس‌های frontend, api, postgres و profileهای test/tool
.env.example                         # فقط نام متغیرها و مقدارهای غیرحساس نمونه
backend/Dockerfile                   # build چندمرحله‌ای FastAPI و non-root user
frontend/Dockerfile                  # build/serve frontend و non-root user
backend/pyproject.toml + lockfile    # dependencyهای Python قفل‌شده
package.json + package-lock.json     # dependencyهای Node قفل‌شده
docs/local-development.md            # نصب، فرمان‌ها، portها و troubleshooting
docs/operations/docker-runbook.md    # reset امن، backup/restore محلی و health checks
```

Compose باید شبکهٔ داخلی، named volume PostgreSQL، health check، متغیر محیطی از `.env` محلی، dependency readiness و profileهای جدا برای test را داشته باشد. password/secret پیش‌فرض فقط برای local باشد، در `.env` قرار گیرد و هرگز commit نشود. production compose و development compose را یکی فرض نکن؛ deploy production از configuration/secret manager و pipeline جدا استفاده کند.

### ۵. مراحل نصب و راه‌اندازی محلی

Codex باید این راهنما را در `docs/local-development.md` تولید و با اجرای واقعی تأیید کند؛ فرمان دقیق ممکن است با OS تغییر کند، اما این توالی ثابت است:

1. نصب Git، Docker Desktop/Engine با Compose v2، Node LTS و Python 3.12+؛ با فرمان version هرکدام را بررسی کن.
2. clone مخزن، ورود به شاخهٔ درست و کپی `.env.example` به `.env`؛ فقط مقادیر local را پر کن.
3. یک‌بار dependencyهای frontend و backend را از lockfile نصب کن؛ dependency جدید فقط با PR، lockfile و scan اضافه می‌شود.
4. `docker compose up --build` را اجرا کن؛ readiness database، migration و health endpoint API را بررسی کن.
5. pipeline seed/import آزمایشی را روی دادهٔ غیرحساس اجرا و audit را بررسی کن؛ هرگز با reset بی‌هدف volume داده را حذف نکن.
6. frontend، OpenAPI/health API و مسیر پرسشنامه را باز کن؛ سپس unit/integration/E2E کوتاهِ smoke اجرا کن.
7. برای توقف از down بدون حذف volume استفاده کن؛ reset یا حذف volume فقط طبق runbook و با تأیید هدف/محیط انجام شود.

README نباید صرفاً فرمان‌ها را فهرست کند؛ باید پیش‌نیازها، علت هر سرویس، portها، health check، مسیر troubleshoot، seed data، نحوهٔ اجرای testها و تفاوت local/staging/production را توضیح دهد. هر تغییر در stack، port، env، dependency، migration یا فرمان اجرا، در همان PR به `docs/local-development.md`, `docs/operations/docker-runbook.md` و CHANGELOG اضافه شود.

### ۶. شرط آغاز مرحلهٔ بعد و شرط پایان کل توسعه

شروع task بعدی فقط وقتی مجاز است که checkpoint پایان task فعلی کامل، commit ثبت، test نزدیک سبز و تغییرات مستند شده باشند. شروع User Story بعدی فقط با gate سبز، PR قابل بازبینی و عدم وجود blocker باز از story قبلی ممکن است. پایان کل پروژه زمانی است که US-12 کامل، تمام containerها در محیط local با راهنمای مستند بالا می‌آیند، full release gate سبز است، deploy preview و rollback تست شده و آخرین checkpoint و CHANGELOG وضعیت دقیق نسخه را نشان می‌دهند.

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


## اصلاح برنامه — US-01.T03a: بازگردانی بایت‌های منابع canonical

این تسک اصلاحیِ الزامی پس از US-01.T03 و پیش از US-01.T04 اجرا می‌شود. علت آن، ناسازگاری بایت‌های فایل‌های UTF-16 LE پس از انتقال متنی قبلی است؛ این تسک هیچ تغییر محصولی، داده‌ای، تفسیری یا الگوریتمی ایجاد نمی‌کند.

### خروجی و gate

1. هر شش فایل .agents/documents/*.unitext فقط با عملیات باینری/base64 جایگزین شوند؛ تبدیل UTF-16 به UTF-8 یا normalize کردن line ending ممنوع است.
2. هش Git blob محاسبه‌شده از بایت اصلی باید با هش blob بازگردانده‌شده از Git برابر باشد؛ SHA-256 و byte count هر شش فایل نیز ثبت شوند.
3. نتیجه در docs/source-inventory.md، docs/source-integrity-verification.md، docs/progress/current-state.md و CHANGELOG.md ثبت شود.
4. اگر حتی یک فایل برابر نبود، blocker باز می‌ماند و ورود به US-02 ممنوع است. اگر همه برابرند، فقط blocker یکپارچگی منبع رفع می‌شود؛ تکمیل بقیهٔ US-01 همچنان پیش‌نیاز US-02 است.


## US-09.T071 — Account UI

Saved loans persist only in browser localStorage and use server-supplied recommendation display data. The saved-loan view excludes readiness and comparison actions. Profile phone is read-only; other local fields are editable. Profile uploads are selected locally and reject files over 100 KB. PR #85 also added profile API persistence and migration d1a9e71b4c3f for user_profiles. Saved loans remain browser-local. The unrestricted API is corrected by T072 below; scoring, PUBLISHED data and anonymous session policy are unchanged.


## US-09.T072 — Profile access and persistence repair after PR #85

Within the owner's repair request, protect existing profile persistence, connect personal-info after server development OTP verification, expose storage errors and preserve complete phone identities. Reuse user_profiles and its existing migration; no new migration, loan data, D-005, questionnaire TTL, design, About text or story continuity changes.

1. Reads use /profiles/me; writes require the server-owned phone. Client phone and browser cache alone never authorize.
2. OTP remains an explicitly enabled local/test mock with expiry, attempts, quotas and revocable memory-only bearer capability. Staging/production always reject this mock. Real SMS/Kavenegar still requires separate owner approval/configuration and is not delivered here.
3. Server verification plus DB persistence precede analysis navigation. Failed storage remains retryable on the current screen. Confirmed profile caches update only after success; full phones are not truncated.
4. API/security/client/browser and real PostgreSQL checks must pass. API, ADR, profile threat model, module map, database docs, local/Docker runbooks, CHANGELOG and checkpoint are updated.
5. Supersedes profile local-only limitations of T06I/T06Z solely for development persistence/access. This does not claim real phone ownership, production login or full US-09 completion. Continuity remains unchanged until its story-level gate.

See docs/architecture/0010-profile-access-and-persistence.md for contract and rollback.

## Verified first-login profile creation — 2026-10-09

Owner clarification: after entering a phone and successfully verifying mock OTP `123456`, the API creates the actor's `user_profiles` record before issuing access. Requesting a code or submitting an invalid code does not create a profile. Repeated login reuses the record without erasing name, income, job, gender or avatar. Personal-info then updates that same database profile before analysis. Creation failure returns 503 without issuing access; resend a code to retry. Existing migration is reused. Real SMS provider remains deferred until the owner supplies its API key; mock remains explicitly local/test. API tests and a real PostgreSQL HTTP integration test cover creation, persistence and repeat login. Follow-up CI must pass before merge.

## US-09.T073 — Local OTP request repair (2026-10-09)

Owner reported failures in both login and personal-info on local Docker. Reproduced local API 503 with the new mock flag absent (old-container environment). Local/test now default to fake OTP 123456; explicit false still disables it, and staging/production remain fail-closed. This supersedes T072's opt-in-only local default without enabling real SMS or production authentication. The profile client honors VITE_SHAHAB_API_BASE_URL for every request. Existing schema, design, icons, About text, D-005 and published source data remain unchanged. New CI browser integration runs against real FastAPI/PostgreSQL through Vite, not API route fixtures. See Docker runbook for non-destructive container recreation.

## US-09.T074 � Home hero-only composition (2026-10-09)

Owner requested the home route to contain only the supplied initial mobile composition: existing header/menu and the loan-request hero. The statistics marquee, feature grid, secondary CTA and footer are no longer rendered on home. This is a presentation-only composition change; questionnaire routing, OTP/profile access, API, PostgreSQL, PUBLISHED loan data, D-005, scoring and deployment behavior are unchanged. The continuity document remains unchanged.

## US-09.T075 — Saved-loans empty state and navigation (2026-10-09)

Saved loans retain their browser-local storage contract and their own /saved-loans route. With zero saved loans, the view uses the owner-supplied empty-state artwork; filters are hidden when zero or one saved loan exists because they cannot change the results. Detail navigation marks only the return route, so the detail back arrow returns to /saved-loans. The shared serving-loan card now includes its document icon in both result and saved-loan views, and the saved header receives the same horizontal inset as profile and About. This is UI/navigation-only; PostgreSQL, API, PUBLISHED data, D-005, scoring, retention and the continuity document remain unchanged.
