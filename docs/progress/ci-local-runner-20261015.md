# اجرای CI روی اجراکنندهٔ محلی شهاب

## محدوده و معیار پذیرش

تسک مستقل زیرساختی `CI-LOCAL-20261015` از `main=f5711e78df58366b65c7f00e29fa484ea5fb0b85`.
علت: سقف مصرف اجراکننده‌های میزبانی‌شده مانع شروع jobها شده است. مطلوب: همان شش job در سه workflow، با نام چک و فرمان آزمون قبلی، روی اجراکنندهٔ دارای برچسب `shahab-local` اجرا شوند. این کار هیچ زیرتسک US-13 را Done نمی‌کند.

سه قانون طلایی رعایت می‌شوند: تغییر کوچک زیرساختی؛ راهنمای جامع با blob `9d4e740ce4908d57ce33522603c4d83cf8df06fc` و پروتکل با blob `7a2e369ee6bef86601cb79b3b02cbe82c9e15d96` در همین جریان کار بازخوانی شده‌اند؛ پایان فقط با شاهد CI روی revision نهایی. منابع دادهٔ unitext موضوع این تغییر نیستند؛ UI، API، schema، scoring و داده دست‌نخورده‌اند.

## محیط و حفاظت از داده

- اجراکننده: WSL/Linux/X64، Docker Desktop، Git روی میزبان و برچسب اضافی `shahab-local`.
- نسخهٔ اصلاح‌شده از ایمیج ازپیش‌ساختهٔ محلی `shahab-ci:local-v1` استفاده می‌کند. عمداً `jobs.container` نیست: runner پیش از job برای image pull تلاش می‌کند؛ wrapper با `docker run --pull=never` از دانلود ایمیج آزمون و PostgreSQL جلوگیری می‌کند. نبود ایمیج خطای روشن است؛ fallback به image/DB دیگری نداریم.
- نود 22.23.3، Python 3.12 و Playwright 1.63.0 در شروع بررسی می‌شوند. دستور ساخت در `ci/local-image/Dockerfile` ثبت شده؛ دو archive ورودی فقط محلی و ignored هستند. نود با SHA256 رسمی بررسی شده؛ zip مرورگر از URL رسمی همان نسخهٔ اعلام‌شده توسط Playwright (Chrome for Testing 153.0.8010.12) دریافت و سلامت archive بررسی می‌شود. بررسی zip معادل تأیید رمزنگاری‌شدهٔ منشأ آن نیست.
- مرورگر آماده در `/opt/chrome/chrome-linux64/chrome` قرار دارد. config عمومی قبلاً متغیر `SHAHAB_E2E_BROWSER_PATH` داشت؛ config پروفایل و چهار launch مستقیمِ دو آزمون baseline هم همان متغیر را مصرف می‌کنند. در نبود متغیر، رفتار قبلی حفظ می‌شود؛ assertionها، viewportها، CSS، baseline SHA و شرط صفرپیکسل تغییر نمی‌کنند. این مرورگر کامل است؛ شواهد جدید باید با همین نسخه واقعاً تأیید شوند.
- هر job کانتینر موقت غیرroot با UID/GID اجراکننده دارد تا فایل‌های checkout/artifact root-owned نشوند. venv تازه در /tmp ساخته می‌شود؛ کتابخانه‌های پروژه هنوز از lockfile/pyproject نصب می‌شوند. cacheهای دانلود npm/pip در پوشهٔ اختصاصی runner نگه داشته می‌شوند؛ هیچ venv یا node_modules قدیمی جایگزین نصب معتبر نمی‌شود.
- PostgreSQL آزمایشی فقط از ایمیج محلی `postgres:16-alpine`، در شبکهٔ تصادفی همان job و با نام داخلی `postgres` ساخته می‌شود. تنها دو نام `shahab_test` و `shahab_profile_test` مجازند. هیچ پورت میزبان publish نمی‌شود و هیچ volume موجود mount نمی‌شود.
- cleanup فقط نام‌های تصادفی همان invocation را حذف می‌کند و anonymous volume خود PostgreSQL آزمایشی را پاک می‌کند. docker compose، global prune، reset و دسترسی به `shahab-demo_postgres_data` وجود ندارد. شکست تست همان کد خروجی شکست را نگه می‌دارد؛ readiness ناموفق DB مانع اجرای suite می‌شود.
- فقط checkout جاری، فایل فرمان read-only و cache دانلود mount می‌شوند؛ docker socket و env محلی برنامه به کانتینر داده نمی‌شوند. مسیرهای baseline /tmp در کانتینر موقت‌اند. artifactها از checkout runner با همان نام و retention قبلی upload می‌شوند.
- این روش به دانلود بسته‌های پروژه، fetch baseline، audit امنیتی و upload artifact هنوز نیاز دارد؛ «CI کاملاً آفلاین» ادعا نمی‌شود. کانتینر مرز امنیتی کافی برای کد مخرب نیست؛ runner به Docker میزبان دسترسی دارد و فقط برای مخزن خصوصی و کد مورد اعتماد است.

## روش استفاده

در Ubuntu و پوشهٔ `~/actions-runner` اجراکننده باید با `./run.sh` روشن و در حالت Listening for Jobs باشد؛ لپ‌تاپ، Ubuntu و Docker Desktop روشن بمانند. با Ctrl+C اجراکننده متوقف می‌شود؛ دادهٔ برنامه حذف نمی‌شود.

همهٔ jobها هر چهار برچسب `self-hosted, Linux, X64, shahab-local` را لازم دارند. اگر job در صف ماند، وضعیت Online و همین برچسب‌ها را در Settings → Actions → Runners بررسی کن. این اتصال ابزار به endpoint مدیریتی runner دسترسی ندارد؛ دریافت واقعی job شاهد مستقل اتصال است.

ابتدا PR همین زیرساخت باید با شش چک واقعی بررسی شود. پس از تأیید و مرج مالک، شاخهٔ PR #131 باید تغییرات جدید main را دریافت کند و روی SHA تازه آزمون شود. صرف rerun اجرای قدیمی، فایل workflow قدیمی را به نسخهٔ جدید تبدیل نمی‌کند. هیچ bypass یا وضعیت موفق دستی جایگزین آزمون نیست.

## اعتبارسنجی و محدودیت

قبل از push: YAML سه workflow، نحو bash wrapper و فرمان‌ها، syntax سه فایل مرورگر، حفظ نام jobها/triggerها/timeoutها/فرمان‌های آزمون/baseline/artifact بررسی شد. پنج آزمون wrapper با Docker شبیه‌سازی‌شده، عدم pull و انتشار پورت، محدودبودن cleanup، رد DB غیرآزمایشی، انتقال شکست تست و readiness ناموفق را اثبات کردند. این آزمون‌ها جای اجرای واقعی Docker نیستند. در محیط Codex فعلی Docker نصب نیست؛ اجرای کانتینر، نصب وابستگی و suiteها فقط روی runner لپ‌تاپ قابل اثبات است. موفقیت بررسی ایستا معادل موفقیت CI نیست.

برای شکست، SHA، job، step و اولین خطای همان attempt بررسی می‌شود. سقف زمان آزمون صرفاً برای سبزشدن افزایش نمی‌یابد. برگشت با revert همین تغییر زیرساخت و بازگشت workflowها به اجراکنندهٔ میزبانی‌شده ممکن است؛ داده یا migration برای برگشت لازم نیست.

## ثبت زمان

شروع بخش ثبت‌شده: 2026-10-15T20:42:30.487Z (UTC). مراحل نصب و راهنمایی پیش از این زمان ثبت دقیق نداشته‌اند.
خواندن/بررسی، آماده‌سازی patch، بررسی ایستا و انتشار در همین تسک ثبت می‌شوند؛ انتظار اجرای لپ‌تاپ جدا از زمان فعالیت است. نتیجهٔ واقعی jobها از صفحهٔ Actions در SHA نهایی خوانده می‌شود، نه از زمان commit.

## علت اصلاح پس از اجرای اول

روی `d9089b7`: job امنیتی `116661336337` در pull اوبونتو 403 گرفت؛ baseline `116661336331` پس از حدود هفت دقیقه دانلود Node لغو شد. تکرار نصب میزبان تازه علت اصلی اتلاف بود. ساخت اولیهٔ image نیز به دلیل منع مکانی CDN مرورگر شکست خورد؛ مالک archive رسمی را با مرورگر دریافت کرد، image را ساخت و موفقیت smoke اجرای صفحه و مرورگر را اعلام کرد. این گزارش مالک جایگزین suiteهای CI نیست.

ادامهٔ ثبت‌شدهٔ اصلاح: 2026-10-15T23:09:37.847Z (UTC). مدت فعالیت راهنمایی و انتظار دانلود/ساخت در فاصلهٔ گفت‌وگو به‌صورت دقیق ثبت نشده و از فاصلهٔ پیام‌ها حدس زده نمی‌شود. بررسی محلی wrapper پنج آزمون موفق داشت؛ نتیجهٔ شش job نهایی فقط پس از اجرای همین revision معتبر است. سه قانون طلایی و نبود merge/deploy/تغییر داده همچنان برقرارند؛ سند تداوم تا پایان داستان تغییر نمی‌کند.

## اصلاح بر پایهٔ شواهد attemptهای بعدی — ۲۰۲۶-۱۰-۱۶

- هر شش job در attempt اول 9a41173 پیش از suite به EACCES پوشهٔ checkout قدیمی خوردند. مالک با chown محدود به checkout اجراکننده مالکیت را اصلاح کرد؛ attempt بعدی checkout را با موفقیت گذراند. wrapper جدید با UID/GID میزبان ادامه می‌دهد؛ نیازی به اجرای runner با root نیست.
- job امنیتی 116726131687: SAST پاس؛ pip-audit شش advisory فقط برای pip 24.0 گزارش کرد، با حداقل fix مشترک 26.2. venv اوبونتو برخلاف setup-python قبلی pip قدیمی دارد. قبل از نصب وابستگی در job امنیتی، `python -m pip install --upgrade "pip>=26.2"` اضافه شد؛ audit و سیاست رد آسیب‌پذیری حفظ شدند. انتشار 26.2 و latest 26.2.1 از JSON رسمی PyPI بررسی شد.
- job تصویری 116726107872: trace در launch مرورگر به سقف 30 ثانیه رسید؛ smoke هم‌شرایط مالک launch=647ms و exit=0 داشت. یک rerun با همین شاهد محیطی مجاز شد. job 116729242074 دیگر timeout نداشت: home/about390 دقیقاً صفر پیکسل اختلاف، اما login390 با bbox(24,33,366,368) و 73972 پیکسل متفاوت شکست خورد؛ PNG مرجع فرم واقعی و candidate اسکلت بارگذاری بود. بنابراین علتِ این failure زمان‌بندی fixture است، نه شاهد تغییر طراحی.
- پیش از screenshot هر دو origin در login، visible بودن `.hp-login-form` و hidden بودن `.hp-deferred-skeleton` به fixture افزوده شد. selector قبلیِ اندازه‌گیری nav، تمام viewportها، تصاویر مستقل baseline/candidate، SHA ثابت و assertion صفرپیکسل حفظ شدند؛ sleep، mask، threshold، تغییر محصول یا افزایش timeout نداریم.
- syntax JavaScript/YAML/bash فرمان اصلاح‌شده پاس شد. suite تصویری و audit واقعی فقط CI همین commit می‌توانند تأیید کنند؛ موفقیت از بررسی ایستا یا تصاویر subset نتیجه‌گیری نمی‌شود. زمان دقیق فعالیت این بخش مستقل ثبت نشده؛ هیچ زمان حدسی از فاصلهٔ پیام‌ها گزارش نمی‌شود.


## ادامهٔ اصلاح لغو و سنجش محدود — ۲۰۲۶-۱۰-۱۶

Checkpoint پیش از تغییر: wrapper هنگام docker run پیش‌زمینه می‌تواند اجرای trap را تا پایان child عقب بیندازد؛ نتیجه مطلوب، خروج با status شکست/لغو و حذف فقط منابع همان invocation است. محدوده فقط CI/scripts/tests/docs است؛ UI/API/schema/data/scoring تغییر نمی‌کند. وابستگی‌ها: شش job سه workflow و wrapper مشترک. اثبات نزدیک: هفت تست mock شامل TERM و فیلتر مالکیت؛ اثبات واقعی روی Docker لپ‌تاپ جدا لازم است.

- docker run در background با wait قابل قطع اجرا می‌شود؛ container/network برچسب run-attempt-job دارند. هر شش job مرحله always برای پاک‌سازی فقط همان برچسب دارند. این کنترل cooperative cancellation است؛ خاموشی میزبان/daemon یا SIGKILL همهٔ پردازش‌ها تضمین cleanup فوری ندارد.
- scripts/ci/diagnose-local-postgres.sh فقط در checkout مستقل اجرا شود. در حضور container آزمون دیگر متوقف می‌شود؛ ابتدا sleep واقعی داخل container را با TERM قطع و نبود container/network همان probe را بررسی می‌کند (۲۰ ثانیه + حداکثر ۱۰ ثانیه kill grace). سپس تنها test_upgrade_fixture_and_downgrade را روی DB آزمایشی wrapper اجرا می‌کند (کل مرحله ۲۴۰ ثانیه + grace)؛ نصب، import، ۲۰ تراکنش موقت و هر subprocess migration زمان مستقل دارند. هیچ fsync/synchronous_commit/full_page_writes تغییر نمی‌کند. suite کامل، مرورگر، npm و workflow جدید اجرا نمی‌شود.
- بررسی منبع نشان داد fixtureها migration را در subprocess و در setup/teardown تکرار می‌کنند؛ این فقط فرضیه اندازه‌گیری است، نه علت قطعی کندی لپ‌تاپ. سقف‌ها و فرمان‌های gateهای موجود حفظ شده‌اند.
- بررسی هدفمند نهایی: ۷/۷ آزمون Node mock، bash -n سه script، Python compile و parse YAML موفق. Docker در محیط Codex موجود نیست؛ سنجش واقعی لغو و PostgreSQL هنوز اجرا نشده است. نتیجه واقعی باید از لپ‌تاپ دریافت شود؛ PR همچنان draft است.
- commit با [skip ci] منتشر می‌شود تا طبق دستور مالک شش gate دوباره وارد صف نشوند؛ این commit اثبات CI موفق یا مجوز merge نیست. پس از بررسی محدود و رفع علت، نسخه نهایی باید gateهای لازم را واقعاً بگذراند.
- ثبت زمان: بررسی اولیه این نوبت پیش از 2026-10-16T07:55:54Z دقیق ثبت نشده؛ اولین checkpoint ساعت 07:55:54Z UTC است. زمان فعالیت بخش‌های پیشین حدس زده نمی‌شود. build/full suite تکرار نشده؛ انتظار ضروری باقی‌مانده اجرای probe روی Docker مالک است.

## حذف نصب تکراری پایتون — ۲۰۲۶-۱۰-۱۶

Checkpoint این نوبت: در خروجی مالک روی f5fba822، نصب ۷۹ ثانیه، import برابر ۰٫۶۴۸، ۲۰ تراکنش ۲٫۵۳۶ و یک migration test برابر ۲۲٫۷۶۵ ثانیه بود؛ upgrade head به‌تنهایی ۱۷٫۶۷۹ ثانیه. عبور برنامه به DB به معنی عبور probe اولیه لغو است. این فقط یک test است و علت زمان تمام suite را اثبات نمی‌کند.

محدوده مصوب: setup پایتون و زمان‌سنجی CI؛ نه تغییر fixture یا assertionهای migration، UI، API، dependency versions، schema، scoring یا داده کاربر. وابستگی‌ها چهار job پایتون، wrapper مشترک و probe محدودند. fixtureهای migration فعلاً حفظ می‌شوند؛ هزینه آن‌ها هنوز در کل suite اندازه‌گیری نشده است.

### رفتار جدید
- prepare-python-environment.py محیط نصب‌شده را در snapshot محلی نگه می‌دارد؛ برای هر container در همان مسیر /tmp/shahab-job-python یک کپی خصوصی بازسازی می‌شود. مسیر editable کد همچنان /workspace جاری است؛ کد PR قبلی از snapshot اجرا نمی‌شود. cache شامل کد منبع برنامه یا HOME/credential نیست.
- کلید شامل pyproject.toml کامل، خود helper، Python/ABI/platform/architecture، profile و شناسه immutable ایمیج آماده است. عمر reuse حداکثر ۲۴ ساعت است چون وابستگی‌های Python range هستند. تغییر این ورودی‌ها یا انقضا باعث نصب تازه می‌شود. profile امنیتی مستقل، pip>=26.2 و bandit/pip-audit با نسخه‌های قبلی دارد؛ audit هر بار اجرا می‌شود.
- cache hit هیچ pip install ندارد؛ فقط استخراج کپی مستقل و pip check انجام می‌شود. cache خراب/ناسازگار بازسازی می‌شود؛ نصب ناموفق snapshot جدید منتشر نمی‌کند. انتشار atomic و lock بین آماده‌سازی‌های هم‌کلید است. استخراج با data filter و بدون symlink مطلق است. interpreterهای venv در snapshot کپی‌اند و lib64 نسبی حفظ می‌شود. cache برای کد مورد اعتماد runner است، نه مرز امنیتی بین PR خصمانه.
- فرمان‌های نصب workflow به bootstrap منتقل شده‌اند، نه اینکه وابستگی‌ها حذف شوند. سه job عمومی پایتون profile project مشترک و job امنیتی profile security دارد. نصب Node و تمام فرمان‌های آزمون/امنیت/browser/baseline و سقف gateها حفظ شده‌اند. هر ۹ مجموعه unittest PostgreSQL با time مدت مستقل می‌دهند.
- probe جدید با --cache ابتدا لغو wrapper را می‌سنجد، سپس یک container برای ساخت/اعتبارسنجی snapshot و container دوم برای cache hit و همان یک migration test اجرا می‌کند. سقف‌ها ۲۰/۱۸۰/۱۲۰ ثانیه و هرکدام حداکثر ۱۰ ثانیه grace هستند؛ آزمون کامل را dispatch نمی‌کند. Docker در Codex موجود نیست؛ زمان بهبود روی لپ‌تاپ هنوز اثبات نشده است.
- linked worktree داخل Docker به .git میزبان خارج از mount اشاره می‌کند؛ probe اکنون آن را پیش از اجرا با خطای روشن رد می‌کند. clone مستقل لازم است. کپی از shallow runner موجب انتقال ناقص commit شد؛ دستور بعدی clone مستقیم تک‌شاخه از GitHub است. این رفت‌وبرگشت‌ها نقص دستور قبلی بود، نه failure محصول.

### بررسی نزدیک و محدودیت
۱۰ آزمون Node شامل لغو/مالکیت، profile/image و ترتیب probe، و ۹ آزمون Python cache موفق‌اند. cache hit بدون نصب، ایزوله‌بودن کپی، invalidation، انقضا، شکست نصب، snapshot خراب و traversal پوشش دارند. یکی از آزمون‌ها venv واقعی و pip/console-script واقعی را بدون دانلود می‌سازد و پس از restore اجرا می‌کند؛ این fixture وابستگی‌های کامل پروژه را ندارد و زمانش به لپ‌تاپ تعمیم داده نمی‌شود. Ruff lint/format، Bandit با همان -ll -ii پروژه، bash syntax، diff check و بررسی YAML/حفظ gateها انجام شده‌اند. خطای import-order فایل probe قبلی نیز با importlib اصلاح شد تا gate formatter/linter را نشکند.

نتیجه واقعی cold/warm در Docker لپ‌تاپ، pip-audit محیط cached و شش gate نسخه نهایی باقی‌اند. commit با [skip ci] منتشر می‌شود؛ PR draft می‌ماند و merge/deploy انجام نمی‌شود. snapshotهای کلیدهای قدیمی روی دیسک cache باقی می‌مانند؛ rebuild به معنای حذف cacheهای نامرتبط یا داده برنامه نیست. rollback با revert همین تغییر cache و برگشت نصب داخل job ممکن است؛ DB/data migration لازم نیست.

### ثبت زمان
اولین timestamp ثبت‌شده این نوبت 2026-10-16T08:37:03Z UTC؛ فعالیت پیش از آن دقیق ثبت نشده است. تا 08:44:04Z بررسی، پیاده‌سازی و آزمون نزدیک انجام شد (۷ دقیقه و ۱ ثانیه دیواری؛ مدت فعال هر بخش جدا ثبت نشده، فعالیت و انتظار با هم جمع نمی‌شوند). آزمون‌های نزدیک پس از تغییرات مرتبط دوباره اجرا شدند؛ full suite یا شش workflow تکرار نشد. عوامل اتلاف هدف‌گرفته‌شده: نصب تکراری → snapshot مستقل؛ دستور worktree/shallow نامناسب → clone مستقیم؛ زمان نامشخص suite → زمان‌سنجی هر module. انتظار باقی‌مانده دریافت سنجش واقعی Docker است.

## سنجش واقعی cache و آغاز gateها — ۲۰۲۶-۱۰-۱۶

مالک خروج موفق probe نسخه bd54d7f1 و exit=0 را گزارش کرد: نصب project=41.134s، ساخت کامل snapshot=63.450s، بازیابی در container مستقل=17.738s (pip check=1.971s)، imports=0.411s و ۲۰ تراکنش=1.805s. migration test موجود با 22.149s موفق شد؛ upgrade head=15.015s. fsync/synchronous_commit/full_page_writes همچنان on بودند. عبور probe اولیه لغو پیش‌شرط ورود به این مراحل بود. این اندازه‌گیری شاهد cache واقعی است، نه نتیجه کل suite یا security profile.

طبق قرار مالک، پس از موفقیت probe، ثبت این شواهد بدون تغییر کد اجرایی و بدون skip-ci منتشر می‌شود تا شش gate موجود روی revision نهایی اجرا شوند. cache helper و pyproject/image/profile ثابت‌اند؛ کلید cache project با تغییر مستندات عوض نمی‌شود. profile امنیتی ممکن است اولین بار نیاز به آماده‌سازی مستقل داشته باشد. PR تا موفقیت واقعی تمام gateها draft می‌ماند؛ merge/deploy انجام نمی‌شود. سقف gateها و assertionها تغییر نمی‌کنند.

## timeout پروفایل و آزمون فرضیهٔ I/O — ۲۰۲۶-۱۰-۱۶

معیار مالک حداکثر پنج دقیقه برای کل شش gate است؛ هنوز اثبات نشده است. برآورد ۲۰–۳۰ دقیقه معیار پذیرش نیست. شروع این بررسی: پس از گزارش مالک ساعت 12:46:44 Asia/Tehran؛ timestamp پایان بررسی/پیاده‌سازی محلی 2026-10-16T09:24:01Z UTC ثبت شد، تفکیک دقیق فعالیت/انتظار پیش از آن ثبت نشده است.

شاهد اجرای f9ff720f: job پروفایل 116895000040 در ۳۰ ثانیهٔ هر test سه failure داشت (Swagger، navigation دستگاه دوم bookmarks، ورود مجدد OTP)، ۸ test موفق و مدت suite برابر ۶٫۷ دقیقه بود؛ سپس job cancelled شد. cache hit=15.704s در همین اجرا موفق بود و security job 116894999731 نیز موفق شد. بنابراین cache اصلاح نصب است، نه حل سرعت کل محیط.

مقایسه با jobهای موفق commit 3d340f11 در run 38448672499: migration اولیه ۱ ثانیه، profile browser suite=75s، ۱۱/۱۱ موفق؛ PostgreSQL job حدود ۳:۴۵ و کل Quality حدود ۳:۵۰ بود. این سابقه ادعای ۱–۲ دقیقه برای تمام شش gate را تأیید نمی‌کند، اما افت فعلی را روشن می‌کند: migration اولیه فعلی حدود ۱۷ ثانیه و profile suite حدود ۶٫۷ دقیقه است. زمان مجموع صف و زمان هر job از هم جدا هستند.

trace واقعی دریافت شد: Swagger DOM تمام ۱۹ operation و selector health را دارد؛ goto حدود ۱۳٫۲ ثانیه و resourceهای CDN حدود ۳٫۴–۳٫۶ ثانیه صرف کرده‌اند. هنوز شاهدی برای تغییر selector یا افزایش timeout نداریم. OTP trace نیز جایگزینی دکمه مهمان پس از restore نشست را نشان می‌دهد؛ assertion یا محصول برای عبور تغییر نمی‌کند. فرضیهٔ محدود فعلی: I/O فایل‌های bindشدهٔ Docker Desktop و دیسک DB موقت، با شواهد کندی migration/npm/import؛ CPU، RAM و شبکه نیز هنوز علت‌های ردشده نیستند.

patch آزمایشی، نه ادعای علت قطعی:
- /workspace یک tmpfs خصوصی با cap=512MiB و UID/GID همان runner است. checkout دقیق به‌همراه .git از /ci-source فقط‌خواندنی کپی می‌شود؛ node_modules، dist و test-results قدیمی و metadata worktreeهای خارجی وارد آن نمی‌شوند. مسیر /workspace عوض نشده؛ cache key و editable source قبلی معتبر می‌مانند.
- /tmp مربوط به job tmpfs با cap=1GiB دارد؛ venv و فایل‌های موقت روی RAM بازسازی می‌شوند. PostgreSQL فقط DB آزمایشی wrapper و tmpfs اختصاصی data با cap=512MiB دارد. این capها رزرو پیشاپیش حافظه نیستند؛ مصرف واقعی باید روی لپ‌تاپ سنجیده شود. هیچ volume یا DB برنامه تغییر نمی‌کند.
- fsync، synchronous_commit و full_page_writes خاموش نشده‌اند؛ transaction، ownership، migration و همه assertionها ثابت‌اند. tmpfs این DB صرفاً برای fixture یک job است و شاهد ماندگاری پس از خاموشی/container restart نیست؛ همانند قبل هیچ ادعای durability دادهٔ تولیدی از آن نمی‌شود.
- پیش از خروج عادی یا شکست، EXIT trap تصاویر و trace را به bind اختصاصی /ci-evidence می‌فرستد؛ پیش از حذف container هنگام لغو نیز تلاش به copy شواهد موجود می‌شود. خاموشی اجباری می‌تواند evidence ناتمام داشته باشد؛ cleanup برچسب‌دار موجود حفظ شده است.
- ۱۲ آزمون Node موفق؛ دو مورد جدید copy واقعی tar با حفظ byteهای source و جدایی ورودی/خروجی و انتقال evidence هنگام exit=23، و محدودبودن tmpfsها به containerهای آزمایشی را می‌سنجند. bash syntax و diff check موفق‌اند. ۹ آزمون cacheِ revision قبلی تحت تغییر نیستند و بی‌دلیل تکرار نشده‌اند.
- در این محیط Docker نیست؛ cap حافظه، اثر واقعی tmpfs، artifact کامل در Docker، و کاهش زمان به پنج دقیقه هنوز باید روی لپ‌تاپ ثابت شوند. نسخه با [skip ci] منتشر می‌شود؛ تا probe موفق، شش gate جدید dispatch نمی‌شوند. هیچ timeout/test/selector/security check تغییر نکرده؛ اصلاح fixture یا runner موازی بدون شاهد به این patch اضافه نمی‌شود.

## اصلاح قابلیت اجرای tmpfs — ۲۰۲۶-۱۰-۱۶

مالک ImportError در بارگذاری SQLAlchemy .so با failed to map segment گزارش کرد. این نشانه با mount دارای noexec سازگار است؛ flags واقعی میزبان هنوز دریافت نشده‌اند. دو tmpfs اجرا (/tmp و /workspace) اکنون exec را صریح دارند؛ nosuid/nodev و capها حفظ می‌شوند و PGDATA همچنان نیاز به exec ندارد. تغییر فقط دو گزینه mount و انتظار تست مربوط است؛ package/image/cache key و assertion/timeout تغییر نمی‌کند. ۱۲ آزمون نزدیک Node، syntax bash و diff check موفق‌اند؛ Docker محلی موجود نیست و اثبات بارگذاری native module و سنجش زمان با probe واقعی لپ‌تاپ باقی است. تکیه به آزمون mock برای flag پیش‌فرض mount نقص بررسی قبلی بود. راهنمای رسمی Docker: https://docs.docker.com/engine/storage/tmpfs/ . نسخه با skip-ci منتشر می‌شود؛ full gate جدیدی dispatch نمی‌شود.

## سنجش واقعی tmpfs و اجرای gateها — ۲۰۲۶-۱۰-۱۶

مالک خروج موفق probe نسخه 75588b40 را فرستاد: cancellation و نبود container/network باقی‌مانده موفق؛ checkout copy در دقت ثانیه=0؛ cache hit در دو container مستقل=2.439s و 2.293s؛ imports=0.257s؛ بیست تراکنش=0.078s؛ migration test=5.816s با upgrade head=1.512s. fsync/synchronous_commit/full_page_writes همچنان on بودند. نسبت به probe قبلی، cache از17.738s و test از22.149s کاهش یافت؛ این مقایسه کل suite یا علت انحصاری کندی را ثابت نمی‌کند.

پس از این شاهد، فقط ثبت شواهد بدون skip-ci منتشر می‌شود تا شش gate موجود اجرا شوند. هدف حداکثر پنج دقیقه برای کل مسیر هنوز باید در full run اندازه‌گیری شود؛ سه failure مرورگر پروفایل اجرای قبل هم باید واقعاً حل شده باشند. assertion، fixture، timeout، image و cache key تغییر نمی‌کنند؛ PR تا موفقیت تمام gateها draft می‌ماند. زمان کل CI و نتیجهٔ شش job فقط از همین revision معتبر است؛ merge/deploy انجام نمی‌شود.


## تشخیص هدفمند شکست مرورگر — ۲۰۲۶-۱۰-۱۶

روی SHA `6117ebf93f70aac201dd16aa22e54d253f0973db` سه چک Quality، PostgreSQL و Security موفق و سه چک مرورگر ناموفق بودند. بررسی روی شاخهٔ جداگانهٔ `ci/browser-fixture-diagnostic-20261016-1023` و بدون PR انجام شد؛ شش gate کامل برای هر فرضیه تکرار نشدند.

- اجرای `38887339042` فشار واقعی CPU و حافظه را ثبت کرد: memory PSI full avg10 در مرحلهٔ baseline حدود ۴۴٪ شد؛ OOM یا محدودسازی سهم CPU در cgroup ثبت نشد. عکس حافظه در حالت کم‌بار اثبات وضعیت زمان آزمون نبود.
- مقایسهٔ `38888465816` همان Swagger واقعی را بدون trace در ۱۳٫۶ ثانیه و با trace قبلی در ۱۷٫۱ ثانیه موفق اجرا کرد. بنابراین trace حذف نشد و علت اصلی فرض نشد.
- اجرای تک‌worker `38888852183` هر دو تصویر empty artwork، هر دو آزمون document fallback و هر دو مسیر طولانی دسکتاپ/موبایل را موفق اجرا کرد. image.decode پیش‌نیاز تصویر کامل است؛ barrier ورودی تا پایان مشاهدهٔ skeleton نگه داشته و سپس load واقعی انتظار کشیده می‌شود. شرط پیکسلی و هندسه تضعیف نشده است.
- سه شکست باقی‌مانده جدا بررسی شدند: reload واقعی برنامه از dev server حدود ۱۳ ثانیه طول کشید؛ آزمون route-map ده بار راه‌اندازی مستقیم را در یک تست جمع کرده بود؛ اختلاف About فقط محدودهٔ عکس بود و candidate پیش از decode عکس ثبت شده بود.
- اصلاح تأییدشده در اجرای `38889800995` روی `b8922c2a604b7daf525bacaa166d3158838fe706`: suite واقعی API خروجی build همان revision را با preview و proxy قبلی به همان FastAPI/PostgreSQL موقت مصرف می‌کند؛ mock API به آن اضافه نشده است. route-map برای هر یک از ده مسیر تست مستقل با همان URL/متن دارد. collector برای هر viewport تست مستقل دارد و هر نه ترکیب route/viewport همچنان مقایسهٔ صفرپیکسل کامل با SHA منجمد قبلی و همان flagها را اجرا می‌کنند؛ عکس‌های قابل‌دیدن پیش از ثبت decode می‌شوند. هیچ timeout، tolerance، baseline، شرط مالکیت یا داده‌ای تغییر نکرده است.

- نتیجهٔ همان اجرای هدفمند: Swagger و آزمون چنددستگاهی هر دو موفق (۳۵٫۶ ثانیه با startup suite)؛ ده مسیر مستقل موفق (۲۹٫۶ ثانیه)؛ سه viewport با هر نه مقایسهٔ صفرپیکسل موفق (۳۷٫۶ ثانیه). مجموعاً ۱۵ تست موفق؛ شش مورد دیگر قبلاً روی patch مربوط خود موفق شده بودند. نبود backend در suite صرفاً قراردادی route-map/collector همان محدودیت پیشین است و اثبات واقعی API فقط در profile-live انجام شد.

سند تداوم و وضعیت داستان‌های محصول تغییر نکرده‌اند. موفقیت بررسی هدفمند جای نتیجهٔ نهایی شش gate روی head نهایی نیست؛ سقف مجموع پنج دقیقه هنوز اثبات نشده است. زمان دقیق فعالیت‌های قبل از اولین اجرای هدفمند ثبت نشده؛ زمان انتظار و مدت jobها از خود Actions قابل بازبینی است.

## اصلاح ادامهٔ CI با شواهد مستقل — ۲۰۲۶-۱۰-۱۶

- آغاز ثبت این ادامه: 2026-10-16T15:31:16Z (۱۹:۰۱:۱۶ تهران). head محصول `cf881c4`؛ Quality/Security موفق، سه مرورگر ناموفق و PostgreSQL در سقف ده دقیقه لغوشده بودند. چهار سند برنامه تنها تفاوت محصول با `5ecf436` بودند؛ این شاهد برای تفکیک ناپایداری اجرا از تغییر عمدی محصول است، نه اثبات علت واحد تمام شکست‌ها.
- محدوده: فقط CI، تست/harness، دو helper و آزمون‌های ایمنی آن‌ها، checkpoint و CHANGELOG؛ source محصول، asset، CSS، API، schema، raw source، scoring، baseline SHA و سند تداوم تغییر نمی‌کنند. اصلاح به درخواست مالک در همان PR132 باقی می‌ماند. کار در checkout مستقل و شاخهٔ تشخیصی Codex انجام شد؛ وضعیت IDE مالک از اتصال GitHub قابل مشاهده نیست.
- baseline و candidate هر دو پیش از آزمون تصویری build می‌شوند و با preview همان revision اجرا می‌شوند. SHA منجمد اصلی و هر نه مقایسهٔ صفرپیکسل حفظ شده‌اند. مرورگر عمومی در دو مرحلهٔ build و dev اجرا می‌شود؛ فقط فایل‌های دارای interception روی src/main.jsx و HTML harness در مرحلهٔ dev هستند. helper discovery مجموعهٔ کامل قدیمی را با اجتماع دو مرحله و نبود اشتراک مقایسه می‌کند؛ حذف یا تکرار هر تست gate را می‌شکند.
- refresh روی آماده‌شدن .hp-nav بعد از navigation/reload واقعی منتظر می‌ماند؛ درخواست‌های غیرمرتبط فونت/تصویر معیار این regression نیستند. تمام متن‌های legacy همچنان باید غایب باشند. سه مسئولیت Swagger مستقل شدند: فهرست ۱۹ operation/قرارداد امنیت، health واقعی 200 و پروفایل واقعی بدون مجوز 401. پاسخ HTTP واقعی صریح انتظار کشیده و status آن نیز assert می‌شود؛ هیچ API mock اضافه نشده است.
- trace در فایل Swagger همچنان action/network/screenshot/source را نگه می‌دارد، ولی کپی DOM کامل در تک‌تک actionها غیرفعال است؛ DOM نهایی error-context هنگام شکست همچنان موجود است. trace کامل سایر suiteها، معیار بصری و تمام timeoutها تغییر نمی‌کنند. محدودیت: در trace Swagger بازسازی DOM تک‌تک actionها دیگر موجود نیست.
- PostgreSQL: هر ۹ module قبلی با subprocess مستقل و دیتابیس تازهٔ مخصوص همان module اجرا می‌شوند. migrations، downgrade/upgrade، race، مالکیت و least-privilege همان تست‌های قبلی‌اند. عملیات CREATE/DROP فقط نام تصادفی کنترل‌شدهٔ همان اجرای موقت را می‌گیرد؛ URL به سرویس postgres متعلق به CI و نام دیتابیس parent مقید است. شکست provision/cleanup/process یا zero-test/skip موجب شکست gate است. شناسهٔ دیتابیس موقت از harness به container منتقل می‌شود. هیچ داده یا volume کاربر mount/reset نمی‌شود.
- پذیرش نزدیک: syntax Node/Bash/Python و YAML، ۱۲ آزمون harness، سه آزمون جلوگیری از حذف/تکرار discovery و پنج آزمون ایمنی scheduler؛ سپس اجرای واقعی همهٔ moduleها، همهٔ تست‌های مرورگر در هر دو مرحله و شش check روی head نهایی. واحدها جای شواهد واقعی PostgreSQL و browser را نمی‌گیرند.

### شواهد ثبت‌شده پیش از انتشار patch

| بررسی | نسخه/اجرا و نتیجه |
| --- | --- |
| baseline مستقل روی build | 4ac8b98 / 38925069273: پنج تست در دو تکرار، هر ۱۰ اجرا و تمام مقایسه‌های صفرپیکسل موفق؛ ۱٫۳ دقیقه با startup آزمون |
| refresh با readiness واقعی | همان اجرا: هر دو تکرار موفق؛ ۲۵٫۳ ثانیه با startup |
| Swagger اولیهٔ تقسیم‌شده | همان اجرا: پنج موفق و یک انتظار جدول ناموفق؛ پاسخ health واقعی 111ms و جدول 200 در error-context موجود بود؛ این نسخه موفق اعلام نشد |
| رفع خطای fixture ایمنی | یک خطای Ruff در mock SQL و نبود شناسهٔ parent داخل container، پیش از اجرای مجموعه‌های واقعی اصلاح شدند؛ خطای محافظت با حذف guard دور زده نشد |
| PostgreSQL با دو worker | ee5fb284 / 38926913368: هر ۹ مجموعه و ۴۷ تست موفق، بدون skip؛ زمان suites=267.448s؛ peak کانتینر حدود529MiB، کمترین حافظهٔ در دسترس VM حدود2099MiB، memory PSI=0 |
| Swagger نهایی با API واقعی | همان اجرا: هر سه بررسی در دو تکرار، ۶/۶ موفق، 39.1s با startup |
| مرورگر عمومی کامل | 2bfb03bf / 38927050210: discovery=73، partition=66 build +7 dev؛ 60 آزمون build و7 dev موفق؛ همان6 skip قبلی، بدون skip جدید؛ مرحله build حدود3.5m وdev37.1s |
| سقف هم‌زمانی پذیرفته‌شده | 9c33f2b5 / 38928157560: لاگ هر47 تست با4 worker موفق ولی507.129s؛ نتیجهٔ کل run لغوشده است، نه موفق؛ تقریباً دو برابر نسخه2worker. نسخهٔ نهایی سقف ثابت2 را نگه می‌دارد؛ این انتخاب بر مبنای benchmark است، نه فرض کمبود RAM |
| تعداد صحیح PostgreSQL | خروجی نسخهٔ موفق قبلی 5ecf436 نیز جمعاً ۴۷ تست دارد؛ عدد ۴۵ در گزارش قبلی خطای شمارش بود و در این گزارش تصحیح می‌شود |

سقف نهایی worker و نتیجهٔ اجرای کامل مرورگر/شش check فقط با شواهد همان نسخه در شرح PR ثبت می‌شود. موفقیت بالا جای نتیجهٔ نهایی head PR نیست. هدف مجموع پنج دقیقه هنوز اثبات نشده است؛ مرج و deploy انجام نمی‌شود.

