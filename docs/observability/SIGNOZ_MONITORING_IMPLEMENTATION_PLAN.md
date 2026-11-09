# طرح اولیهٔ پیاده‌سازی مانیتورینگ شهاب با SigNoz

> **وضعیت سند:** پیش‌نویس برای بازبینی مالک؛ این سند به‌تنهایی مجوز نصب، خرید ماشین یا تغییر production نیست.  
> **تاریخ تهیه:** ۲۰۲۶-۱۱-۰۹  
> **دامنه:** پایش فنی و عملکردی شهاب؛ جدا از تحلیل رفتار مشتری در Microsoft Clarity.  
> **شناسه‌ها:** شناسه‌های `MON.Txx` در این سند پیشنهادی‌اند و تا تصویب و ثبت در سند جامع، شناسهٔ رسمی تسک پروژه نیستند.

## ۱. هدف و دامنه

هدف، ایجاد سامانه‌ای است که بتواند کندی صفحه را از کندی مرورگر، API، پایگاه داده یا زیرساخت تفکیک کند و لاگ فنی امن را در داشبورد قابل جست‌وجو گرد آورد.

سامانهٔ هدف باید در مرحلهٔ اول این سیگنال‌ها را پوشش دهد:

- **فرانت‌اند:** زمان navigation و بارگذاری، Core Web Vitals، تغییر route در React و خطاهای JavaScript.
- **بک‌اند:** زمان پاسخ و نرخ خطا به تفکیک route template، trace محدود درخواست‌ها و رخدادهای خطای ساختاریافته.
- **زیرساخت:** CPU، حافظه، دیسک، شبکه، وضعیت میزبان و کانتینرهای Docker.
- **داده‌پایه:** سلامت و ظرفیت PostgreSQL و Redis و در مرحلهٔ بعد زمان‌گیری queryها.
- **پروکسی:** زمان کل درخواست و زمان upstream بدون ثبت query string یا شناسه‌های حساس در مسیر.

این طرح برای ضبط نشست، مشاهدهٔ کلیک‌ها، ذخیرهٔ پاسخ پرسشنامه یا ایجاد پروفایل رفتاری مشتری نیست. Clarity مسئول تحلیل رفتار محصول می‌ماند.

## ۲. وضعیت فعلی و نتیجهٔ ظرفیت‌سنجی اولیه

خروجی مالک از VM production در ۲۰۲۶-۱۱-۰۹ چنین بوده است:

| شاخص | مقدار مشاهده‌شده |
|---|---:|
| vCPU | ۲ |
| RAM کل | ۳٫۸ GiB |
| RAM available هنگام اجرا | ۳٫۱ GiB |
| Swap | صفر |
| دیسک ریشه | ۲۳ GB کل، ۱۸ GB آزاد |
| کانتینرهای فعلی | frontend، API، PostgreSQL، Redis |

خروجی `docker stats` در همان لحظه حدود ۴٫۴ MiB برای frontend، ۷۹ MiB برای API، ۵۵ MiB برای PostgreSQL و ۷٫۳ MiB برای Redis نشان داده است. این فقط یک snapshot کم‌ترافیک است و مصرف peak یا رشد بعدی برنامه را نشان نمی‌دهد.

مستند SigNoz برای نصب آزمایشی Docker Compose دست‌کم ۴ GB حافظهٔ اختصاص‌یافته به Docker را می‌خواهد و اجزای خود را روی همان ماشین اجرا می‌کند. بنابراین RAM کل VM فعلی از حداقل آزمایشی اعلام‌شده هم کمتر است؛ SigNoz نباید کنار production فعلی نصب شود. فضای آزاد ۱۸ GB نیز بدون اندازه‌گیری ingest و retention برای ClickHouse قابل تأیید نیست. نتیجهٔ اجرایی این سند، **ماشین مجزای مانیتورینگ** است.

کد بک‌اند هم اکنون متریک‌های process-local محدودی در `backend/app/api/observability.py` دارد؛ این اعداد ماندگار نیستند و در داشبورد مرکزی دیده نمی‌شوند. لاگ فعلی Nginx عمداً فقط روش درخواست و status را ثبت می‌کند و زمان پاسخ را ندارد. این دو مورد باید با سیاست حفظ حریم خصوصی هماهنگ و سپس به سامانهٔ مرکزی متصل شوند.

## ۳. مشخصات پیشنهادی ماشین

اعداد زیر برآورد اولیه برای یک نصب تک‌گرهی کم‌تا‌متوسط‌حجم هستند، نه حداقل یا تضمین رسمی SigNoz. تا زمانی که حجم واقعی telemetry، میزان رشد و retention معلوم نشود، خرید بر اساس عدد ثابت ۲ تا ۳ ساله دقیق نیست.

| مرحله | vCPU | RAM | دیسک دادهٔ پایدار | کاربرد |
|---|---:|---:|---:|---|
| آزمایش و پایلوت محدود | ۴ | ۸ GiB | ۱۰۰ GB SSD/NVMe | نصب، ابزارگذاری staging و سنجش ingest |
| هدف پیشنهادی شروع production | ۴ | ۱۶ GiB | ۲۰۰ GB SSD/NVMe | شروع مجزا از production با حاشیهٔ حافظه و دیسک |
| مسیر رشد ۲ تا ۳ ساله | قابل ارتقا تا ۸ | قابل ارتقا تا ۳۲ GiB | قابل توسعه تا ۵۰۰ GB یا object storage | افزایش پس از سنجش واقعی، نه خرید قطعی امروز |

**توصیهٔ فعلی برای ماشین جدید:** اگر قرار است self-hosted SigNoz در production ارزیابی شود، هدف اولیه ۴ vCPU، ۱۶ GiB RAM و ۲۰۰ GB SSD/NVMe در نظر گرفته شود و امکان ارتقا/افزایش حجم دیسک از ابتدا بررسی شود. این برآورد باید پیش از خرید با بودجه، traffic واقعی، حجم telemetry و بازهٔ نگهداری بازبینی شود.

مستند رسمی ۴ GB را فقط prerequisite نصب Docker معرفی می‌کند؛ آن عدد را نباید ظرفیت مناسب production تلقی کرد. راهنمای برنامه‌ریزی منابع SigNoz نیز sizing را تابع تعداد داده، collectorها، ClickHouse و retention می‌داند و اعداد مقیاس بزرگ آن مستقیماً برای شهاب قابل تعمیم نیستند.

فضای دیسک نهایی باید با نمونه‌برداری از حجم روزانه پس از ابزارگذاری تعیین شود:  
`فضای داده ≈ حجم ingest روزانه × روزهای retention × ضریب واقعی ذخیره‌سازی`  
سپس باید فضای عملیاتی آزاد برای compaction، به‌روزرسانی و رشد در نظر گرفته شود؛ عدد ضریب را با benchmark واقعی ClickHouse تعیین می‌کنیم.

**افق ۲ تا ۳ سال** در این سند به معنی مسیر ارتقا و بازبینی دوره‌ای است، نه نگهداری همهٔ telemetry برای ۲ تا ۳ سال. تا تصویب مالک، retention فقط پیشنهاد اولیه است: metrics تا ۳۰ روز، logs تا ۱۴ روز و traces تا ۷ روز. این مقادیر باید با هزینه، نیاز عیب‌یابی و سیاست داده تأیید شوند.

## ۴. معماری پیشنهادی

شهاب از SigNoz self-hosted روی VM جدا استفاده می‌کند. اجزای آن شامل رابط SigNoz، OpenTelemetry Collector و ClickHouse است؛ SigNoz همچنین راهکار self-hosted مبتنی بر Docker Compose را مستند کرده است. در زمان اجرا باید نسخهٔ مستندات و installer رسمی دوباره بررسی و نسخه‌ها pin شوند؛ راهنمای فعلی، مسیر Foundry را پشتیبانی می‌کند و نصب‌نامه/Compose قدیمی را deprecated اعلام کرده است.

API و agentهای VM داده را از مسیر خصوصی به collector می‌فرستند. فرانت‌اند برای ارسال Web Vitals به یک endpoint HTTPS نیاز دارد؛ endpoint ingest باید محدود و محافظت‌شده باشد. رابط مدیریت SigNoz عمومی نشود و فقط از VPN یا IPهای مجاز در دسترس باشد. پورت‌های OTLP، یعنی ۴۳۱۷ و ۴۳۱۸، به اینترنت عمومی باز نشوند. در صورت نیاز به RUM از مرورگر، فقط مسیر ingest امن با TLS، محدودیت اندازه و نرخ درخواست و CORS مشخص منتشر شود؛ رابط ادمین روی همان مسیر منتشر نشود.

**توجه به پورت‌ها:** خروجی قبلی production پورت‌های ۸۰۸۰ و ۸۴۴۳ فرانت‌اند را نشان می‌داد. SigNoz هم به‌طور پیش‌فرض UI را روی ۸۰۸۰ ارائه می‌کند؛ استقرار روی ماشین جدا این برخورد را حذف می‌کند.

## ۵. قرارداد داده و حریم خصوصی

پیش از فعال‌کردن هر exporter یا SDK، موارد زیر باید به‌صورت خودکار یا با آزمون ثابت شوند:

- **عدم ارسال دادهٔ مالی یا هویتی:** متن پاسخ‌ها، نام، شماره تلفن، OTP، درآمد، جنسیت، شغل، session token، cookie، authorization، بدنهٔ درخواست/پاسخ و شناسهٔ کاربر وارد log، metric، attribute یا trace نشوند.
- **محدودکردن مسیرها:** به‌جای URL خام از route template مانند `/api/v1/recommendations/{id}` استفاده شود؛ query string و شناسهٔ واقعی از telemetry حذف شود.
- **محدودکردن labels:** هیچ label متریک شامل user/session/request ID، مقدار آزاد یا دادهٔ با cardinality بالا نباشد.
- **ارسال امن:** telemetry ساختاریافته، با سطح دسترسی محدود، نرخ/اندازهٔ کنترل‌شده و retention مصوب باشد.
- **ردیابی امن:** correlation/trace ID تصادفی فقط برای پیوند فنی log و span استفاده شود؛ به شناسهٔ مشتری یا دادهٔ کسب‌وکاری تبدیل نشود.

## ۶. فهرست تسک‌های پیشنهادی به ترتیب

هر شناسه در این جدول موقت است. پیش از اجرا باید آن را با سند جامع، وضعیت جاری، قواعد طلایی و پروتکل اجرای تسک تطبیق داد؛ مالکیت، وابستگی‌ها و معیار پذیرش نهایی با تصویب مالک تثبیت می‌شود.

| ترتیب | شناسهٔ پیشنهادی | تسک و خروجی | معیار پذیرش |
|---:|---|---|---|
| ۱ | `MON.T01` | **تثبیت نیاز و سیاست داده:** تعریف مخاطبان داشبورد، شاخص‌های صفحه/API، alertها، retention، نرخ sampling، سطح دسترسی و کانال اعلان. | تصمیم‌های باز ثبت و موارد ممنوع telemetry به checklist قابل آزمون تبدیل شده باشند. |
| ۲ | `MON.T02` | **تعیین حجم و sizing:** ثبت baseline درخواست/روز، بازدید/صفحه، خطا، حجم log، نرخ trace نمونه‌ای و رشد مورد انتظار؛ برآورد storage با retention مصوب. | ماشین پیشنهادی، ارتقا و هزینه بر اساس اندازه‌گیری یا فرض‌های صریح بازبینی‌شده باشد؛ محدودیت ماشین فعلی مستند بماند. |
| ۳ | `MON.T03` | **آماده‌سازی VM مجزا:** انتخاب Linux پشتیبانی‌شده، CPU/RAM/disk، volume پایدار، DNS، firewall، به‌روزرسانی و دسترسی ادمین خصوصی. | UI عمومی نباشد؛ OTLP ingress عمومی نباشد؛ دیسک داده و backup از root/app جدا و قابل بازیابی باشد. |
| ۴ | `MON.T04` | **نصب SigNoz:** استفاده از روش رسمی پشتیبانی‌شده و نسخه‌های pin‌شده؛ تنظیم ClickHouse، metastore، Collector، storage و health check. | نصب تکرارپذیر باشد، همهٔ اجزا healthy باشند، داده پس از restart باقی بماند و روش upgrade/rollback ثبت شود. |
| ۵ | `MON.T05` | **پایش میزبان و Docker:** دریافت host metrics و لاگ‌های انتخاب‌شدهٔ frontend/API/PostgreSQL/Redis؛ محدودسازی سطح و حجم لاگ. | CPU/RAM/disk/network و وضعیت سرویس‌ها در dashboard دیده شود؛ logهای حساس با fixture آزمایشی رد یا redact شوند. |
| ۶ | `MON.T06` | **ابزارگذاری API:** تنظیم OpenTelemetry در FastAPI برای latency/error/trace؛ اتصال محدود و امن به SQLAlchemy/PostgreSQL و Redis؛ correlation با logهای موجود. | route template، status، duration و spanهای وابستگی دیده شوند؛ body، query parameters، SQL bind values و هویت کاربر ثبت نشوند. |
| ۷ | `MON.T07` | **ابزارگذاری React/RUM:** ثبت document load، navigationهای SPA، Core Web Vitals و خطاهای JavaScript؛ بدون click tracking و session replay. | page-load و Web Vitals بر اساس route امن و release version قابل مشاهده باشند؛ هیچ دادهٔ فرم/هویت/URL حساس ارسال نشود. |
| ۸ | `MON.T08` | **زمان‌گیری Nginx و وابستگی‌ها:** افزودن request/upstream duration به log ساختاریافتهٔ Nginx بدون URL خام؛ تکمیل شاخص‌های PostgreSQL و Redis در صورت نیاز. | بتوان latency مرورگر، proxy، API و DB را از هم تفکیک کرد؛ log هیچ query string یا شناسهٔ حساس نداشته باشد. |
| ۹ | `MON.T09` | **ساخت داشبورد و alert:** نمای کلی availability، کندی صفحه، API p50/p95/p99، error rate، منابع host، DB/Redis و log/trace مرتبط. | alertها آزمون شوند و به کانال مصوب برسند؛ آستانه‌ها از baseline و SLO مصوب استخراج شوند، نه حدس ثابت. |
| ۱۰ | `MON.T10` | **کنترل sampling و storage:** تنظیم sampling trace، retention، quota و اخطار پرشدن دیسک؛ حفظ همهٔ metricهای کم‌cardinality و ارسال log با سطح‌بندی. | حجم ingest و مصرف RAM/CPU/disk در بار staging اندازه‌گیری شود؛ رشد قابل پیش‌بینی و retention اعمال‌شده باشد. |
| ۱۱ | `MON.T11` | **آزمون staging و امنیت:** تولید خطا و درخواست کند کنترل‌شده، سنجش page load، بررسی redaction، auth، TLS، firewall، backup و restore. | trace قابل دنبال‌کردن باشد؛ هیچ canary حساس در backend telemetry پیدا نشود؛ restore و alert آزمایش‌شده باشند. |
| ۱۲ | `MON.T12` | **انتقال مرحله‌ای production و runbook:** ارسال محدود و قابل rollback، پایش اثر بر latency برنامه، ثبت نگهداری/upgrade/backup/incident. | داشبورد و alert در production با بار واقعی کار کنند؛ مصرف منابع در حد مصوب باشد؛ خاموش‌سازی instrumentation بدون تغییر محصول ممکن باشد. |

### وابستگی تسک‌ها

ترتیب اصلی `MON.T01 → MON.T02 → MON.T03 → MON.T04` است. سپس `MON.T05` تا `MON.T08` پس از آماده‌شدن receiver و قرارداد داده اجرا می‌شوند؛ `MON.T09` و `MON.T10` به دادهٔ واقعی staging نیاز دارند؛ `MON.T11` پیش‌نیاز `MON.T12` است. اجرای instrumentation در production پیش از تصویب امنیت/حریم خصوصی و آماده‌شدن داشبورد/alert مجاز نیست.

## ۷. شاخص‌های اولیهٔ داشبورد

- **صفحه:** LCP، INP، CLS، document load و زمان navigation؛ بر حسب route template، مرورگر/نوع دستگاه و release، بدون شناسهٔ کاربر.
- **API:** تعداد درخواست، status class، latency histogram و p50/p95/p99 برای route template.
- **وابستگی‌ها:** زمان و خطای PostgreSQL و Redis، تعداد اتصال/اشباع pool در حد امن.
- **زیرساخت:** CPU، memory، disk free، disk I/O، network، restart و health کانتینرها.
- **خطا:** تعداد و نوع exception، trace/correlation ID، نام سرویس و release؛ بدون متن حساس ورودی.
- **اعلان:** availability، افزایش 5xx، p95 بالاتر از SLO مصوب، افت disk free، فشار حافظه یا unhealthy شدن سرویس.

SLO و آستانه‌های alert هنوز تصمیم‌گیری نشده‌اند؛ برایشان عدد فرضی در این سند ثبت نشده است.

## ۸. تصمیم‌های باز برای بازبینی پیش از اجرا

- **بودجه و محل ماشین:** خرید/اجارهٔ VM اختصاصی و مقدار ارتقای قابل‌دسترس.
- **Retention:** مدت نگهداری log، metric و trace و نیاز احتمالی به archive.
- **حجم traffic:** تعداد page view، API request و log در روز و رشد سالانه.
- **دسترسی:** VPN یا allowlist برای UI و روش امن ارسال RUM از مرورگر.
- **sampling:** نرخ اولیهٔ trace و سیاست نگهداری traceهای error/slow، بر اساس منابع Collector.
- **اعلان:** کانال و مالک دریافت هشدار.
- **تثبیت در اسناد:** پس از تأیید، شناسه‌ها و وابستگی‌ها به سند جامع منتقل شوند؛ این پیش‌نویس به‌تنهایی آن سند را جایگزین نمی‌کند.

## ۹. منابع رسمی

- [SigNoz — نصب self-hosted با Docker](https://signoz.io/docs/install/docker/)
- [SigNoz — برنامه‌ریزی منابع](https://signoz.io/docs/setup/capacity-planning/community/resources-planning/)
- [SigNoz — معماری فنی](https://signoz.io/docs/architecture/)
- [SigNoz — جمع‌آوری متریک میزبان](https://signoz.io/docs/infrastructure-monitoring/user-guides/hostmetrics/)
- [SigNoz — جمع‌آوری logهای Docker](https://signoz.io/docs/userguide/collect_docker_logs/)
- [SigNoz — ابزارگذاری Python/FastAPI](https://signoz.io/docs/instrumentation/python/fastapi-native-opentelemetry/)
- [SigNoz — پایش Frontend و Web Vitals](https://signoz.io/docs/frontend-monitoring/)
- [SigNoz — پایش بارگذاری سند](https://signoz.io/docs/frontend-monitoring/document-load/)

## ۱۰. اسناد شهاب که باید هنگام شروع هر تسک دوباره خوانده شوند

- `docs/SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md` — مرجع قواعد محصول، امنیت، توسعه و تسک‌های رسمی.
- `docs/TASK_EXECUTION_PROTOCOL.md` — روش اجرای تسک، تست متناسب و ثبت شواهد.
- `docs/PROJECT_CONTINUITY_DOCUMENT_SHAHAB_FINANCE_DEMO.md` و `docs/project-current-state.md` — وضعیت و handoff جاری؛ نسخهٔ سند و main باید روز شروع دوباره تأیید شوند.
- `docs/deployment/arvan-vm-deployment.md` و `docker-compose.prod.yml` — توپولوژی و مرزهای عملیاتی فعلی؛ هیچ تنظیم production از روی این پیش‌نویس تغییر نکند.
