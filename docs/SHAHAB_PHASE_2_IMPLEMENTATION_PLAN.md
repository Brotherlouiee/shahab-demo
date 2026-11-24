# برنامه یکپارچه پیاده‌سازی فاز دوم شهاب

> **سند اجرایی واحد و تدریجی — نسخه یکپارچه C01–C14، R01–R10 و A01–A08.** این فایل برنامهٔ پذیرفته‌شدهٔ C01–C14، R01–R10 و A01–A08 و بسته‌های باقی‌ماندهٔ NOT_STARTED را در یک سند نگهداری می‌کند. این سند، برنامه است و نشانه پیاده‌سازی یا اجرای محصول نیست.

## ۰. حاکمیت سند، وضعیت واقعی و قواعد به‌روزرسانی

این فایل **تنها سند روایی و اجرایی مرجع برای ۳۶ بسته** است. داده‌های رجیستری/Fixture/Validator اسناد پشتیبان و شواهد ماشین‌خوان هستند؛ هیچ بسته‌ای نباید سند اجرایی مستقل یا PR مستقل برای افزودن برنامه به این فایل بسازد. بعد از هر بسته، فصل همان بسته در **همین سند و همین PR تجمیعی** کامل می‌شود. وضعیت پذیرش هر بسته مجزا می‌ماند و هیچ گیت بسته‌ای از گیت دیگر نتیجه‌گیری نمی‌شود.

قواعد: ۱) اصلاح در جای مربوط و بدون الحاقیه پراکنده؛ ۲) عدم تکرار Requirement/Task مشترک و ارجاع به مالک واقعی؛ ۳) ردیابی Source → Requirement → Story/Enabler → Task/Subtask → AC → Test → Dependency/Contract؛ ۴) تفکیک RA/IPA برنامه‌ریزی از Product Tests و استقرار؛ ۵) تصمیم‌های باز بدون جعل تصویب؛ ۶) عدم بازنویسی مبنای تأیید‌شده بدون شاهد نقض مشخص؛ ۷) این PR تا تکمیل تدریجی بسته‌ها باز می‌ماند؛ ۸) سند منسوخ و PR #247 مبنا نیست و محتوای آن بازیافت نشده است.

### منابع قطعی و منشأ اطلاعات
| منبع | شناسه / SHA | کاربرد |
| --- | --- | --- |
| Blueprint V1.6 | SHA-256 `0709c84fe9e47e1d9218c6d0f93a82c89a62d6b234565e9b0ca2d4158759f266` | احکام طراحی و اصول مصوب؛ تطبیق با Graph Report |
| Digital Wallet V0.20 | SHA-256 `8b8d139b64f25f8f9592f936c070ece37b3e97df55d4e6b1d0cf305933960b74` | قواعد کیف پول؛ تطبیق با Graph Report |
| G1 / C01 / C02 | `docs/phase2/core/CORE_REGISTRY.jsonl` در main پس از PR #250 | شواهد پذیرفته‌شده C01 و C02 |
| C03 IPA | Bundle `shahab-c03-ipa-final.bundle`؛ SHA-256 `6d3af04fd4cb9a20d787b5643e463251359a9efc06ae495c143bc7ad8485c0c4`؛ Commit ممیزی `44d2d63b25c5e7d491b8bc6bd0be3a0103790c33` | شواهد پذیرفته‌شده C03؛ انتشار مستقلی در main ندارد |

### تصویر کل برنامه
| دامنه | بسته‌ها | تعداد | وضعیت |
| --- | --- | --- | --- |
| Core / Wallet | C01، C02، C03، C04، C05a، C05b، C06، C07، C08، C09، C10، C11a، C11b، C12a، C12b، C13a، C13b، C14 | 18 | ۱۸ بسته برنامه‌ریزی پذیرفته‌شده |
| RAG / Adviser | R01–R10 | 10 | R01–R10 پذیرفته‌شدهٔ برنامه‌ریزی؛ محصول اجرا نشده |
| Assistant | A01–A08 | 8 | A01–A08 پذیرفتهٔ برنامه‌ریزی؛ محصول اجرا نشده |
| کل | ۳۶ بسته | 36 | ۳۶ پذیرفته‌شدهٔ برنامه‌ریزی؛ محصول اجرا نشده |

### جدول وضعیت واحد بسته‌ها
| بسته | عنوان/دامنه | RA | IPA | اجرای محصول |
| --- | --- | --- | --- | --- |
| C01 | معماری و مبانی مشترک Core | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C02 | هویت، سازمان‌ها و مجوزها | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C03 | قراردادها، داده و زیرساخت مشترک | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C04 | اشتراک، پلن و Billing | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C05a | کاتالوگ خدمات شهاب | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C05b | کاتالوگ محصولات مالی و توصیه‌گر | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C06 | پوسته سوپراپ و UI مشترک | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C07 | مالکیت وجوه و مدل اعتبار | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C08 | شارژ، هدیه و تخفیف | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C09 | مصرف و رزرو | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C10 | انتقال و برداشت | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C11a | استرداد و اصلاحات مالی | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C11b | عملیات دوره‌ای و محدودیت‌ها | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C12a | دفترکل و یکپارچگی مالی | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C12b | تطبیق و بازیابی مالی | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C13a | قیمت‌گذاری، تسویه و حسابداری | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C13b | تجربه و پشتیبانی کیف پول | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| C14 | سوابق پیام‌ها، اعلان‌ها و Monitoring مشترک | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| R01 | پذیرش خدمت، فهم پرسش و مسیریابی بازیابی ریسک‌محور | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| R02 | دسترسی کنترل‌شده به منابع و ورود تقاضامحور دانش | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| R03 | مخزن دانش، هویت و نسخه، Lineage و انتشار Snapshot | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| R04 | کشف منبع و کاتالوگ فراداده | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| R05 | بازیابی چندمرحله‌ای و سنجش کفایت شواهد | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| R06 | تجمیع پاسخ، Citation Guard و ارزیابی کیفیت Adviser | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| R07 | کشف و ارزیابی رابطهٔ اسناد و ورود انتخابی | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| R08 | بازاعتبارسنجی سند و هماهنگی اثر تغییر | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| R09 | زمینهٔ ساختاریافتهٔ گفت‌وگو و تداوم Adviser | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| R10 | محاسبهٔ قطعی و قرارداد Adviser–Core | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| A01 | تفسیر درخواست و پیشنهاد ابزار دستیار | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| A02 | گردش‌کار پایدار دستیار و هماهنگی زیرکار | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| A03 | تحلیل رویدادمحور، Feedback و Feedforward دستیار | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| A04 | انتخاب و اجرای مسیر Computer Use در وب و اپ | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| A05 | سه جریان مالی آغازین دستیار: موجودی، قبض و انتقال فردبه‌فرد | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| A06 | دانش رابط بانکی، آزمون و پایش تغییرات UI | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| A07 | مرزهای زمینه، حافظه و انتقال داده در دستیار | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |
| A08 | قراردادهای API و پیکربندی امن سرویس دستیار | PASS | PASS | PLANNING_ACCEPTED / PRODUCT_NOT_EXECUTED |

### اصول مصوب پیاده‌سازی (از Blueprint، برای همه بسته‌ها)
- `POL:BLUEPRINT:5.2.1:01` (B:1966): ۱. **انتشار هفتگی ارزش واقعی:** هر چرخه حداکثر هفت روز تقویمی دارد و هدف آن تحویل نسخه‌ای قابل‌استقرار، یکپارچه و واقعاً قابل‌استفاده برای کاربر یا بهره‌بردار مجاز است. پایان Task، ادغام PR، API بدون مصرف‌کننده یا PoC داخلی به‌تنهایی تحویل محصول نیست. استقرار واقعی به عبور از گیت‌های مصوب وابسته است؛ اگر انتشار به‌علت مانع معتبر ایمنی یا کیفیت متوقف شود، نباید موفقیت انتشار اعلام شود.
- `POL:BLUEPRINT:5.2.1:02` (B:1968): ۲. **افزایش پیوسته محصول:** هر انتشار باید بر نسخه کارای قبلی بنا شود و قابلیت‌های منتشرشده را حفظ کند؛ یکپارچگی، سازگاری قراردادها، آزمون رگرسیون و مسیر بازگشت بخشی از تحویل‌اند. انتشار جزیره‌ای و اجزای غیرقابل‌استفاده خروجی معمول چرخه نیستند.
- `POL:BLUEPRINT:5.2.1:03` (B:1970): ۳. **استثنای محدود و اثبات‌پذیر:** عبور یک قابلیت از مرز هفت روز فقط وقتی مجاز است که تقسیم آن به برش‌های مستقل و ایمنِ دارای ارزش واقعی، به دلیل مستند فنی، کارکردی یا امنیتی ممکن یا منطقی نباشد. دلیل، گزینه‌های تقسیم بررسی‌شده، وابستگی‌ها، سقف زمان/هزینه، خروجی میانی قابل‌آزمون و تاریخ بازبینی باید در برنامه ثبت شوند؛ خروجی میانی جای انتشار محصول را نمی‌گیرد.
- `POL:BLUEPRINT:5.2.1:04` (B:1974): ۴. **اولویت با آسان‌ترین قابلیت ارزشمند:** شروع با برش‌های کوچک، کم‌ریسک، سریع و کم‌هزینه‌ای است که مسئله واقعی کاربر را حل می‌کنند؛ سادگیِ فاقد ارزش یا ارزشِ بدون امکان تحویل ملاک اولویت نیست.
- `POL:BLUEPRINT:5.2.1:05` (B:1976): ۵. **تقدم وابستگی‌های واقعی:** قبل از ترتیب انتشار، نقشه وابستگی قابلیت‌ها، قراردادها، داده‌ها، مجوزها و زیرساخت‌ها تهیه می‌شود؛ قابلیت پایه مشترک در نخستین نقطه نیاز و با مصرف‌کننده واقعی ساخته می‌شود تا دوباره‌کاری ایجاد نشود.
- `POL:BLUEPRINT:5.2.1:06` (B:1978): ۶. **زیرساخت به‌اندازه نیاز، با مرز توسعه‌پذیر:** زیرساخت فقط تا سطح لازم برای انتشارهای نزدیک ساخته می‌شود، بدون نقض معماری مصوب Core ماژولار، Adviser مستقل و Assistant مستقل هدف؛ توسعه پیش‌دستانه کامل سامانه‌های فاقد مصرف‌کننده ممنوع است مگر وابستگی/ریسک آن اثبات شود.
- `POL:BLUEPRINT:5.2.1:07` (B:1980): ۷. **یکپارچگی تجربه و داده:** ورود کاربر، هویت، انتخاب حوزه، وضعیت عملیات، قراردادهای نسخه‌دار، مالکیت داده و رابط کاربری باید در همه انتشارها سازگار بمانند؛ راه‌حل موقت نباید مسیر موازی ناسازگار ایجاد کند.
- `POL:BLUEPRINT:5.2.1:08` (B:1984): ۸. **دو جریان هماهنگ و متناوب:** کار بر مشاور و دستیار با تقدم وابستگی‌ها و به‌صورت برش‌های مرتبط و متناوب پیش می‌رود؛ تحقیق و آماده‌سازی مستقل دستیار می‌تواند پیش از پایان تمام توسعه مشاور شروع شود، اما فعال‌سازی و Delivery عملیاتی دستیار تابع گیت G1، توالی سیاستی مصوب و مجوز انتشار است. این اصل مرحله‌بندی سه‌گانه را حذف نمی‌کند.
- `POL:BLUEPRINT:5.2.1:09` (B:1986): ۹. **استفاده مجدد کنترل‌شده:** هویت، مجوز، مشاهده‌پذیری، قرارداد و زیرساخت مشترک در مالک مناسب توسعه می‌یابند؛ منطق تخصصی RAG/Adviser و اجرای Assistant، داده‌ها و مجوزهای حوزه‌ای مستقل می‌مانند. استفاده مجدد به معنی موتور واحد اجباری یا دسترسی مستقیم Adviser به داده Core نیست.
- `POL:BLUEPRINT:5.2.1:10` (B:1988): ۱۰. **آزمون زودهنگام عدم‌قطعیت‌های دشوار:** امکان‌سنجی محدود و زمان‌بندی‌شده Computer Use، کشف فلو، تغییر رابط، OTP، محدودیت وب/Android/iOS و بازیابی عملیات می‌تواند هم‌زمان با انتشار قابلیت‌های آسان انجام شود؛ PoC و Discovery جایگزین انتشار هفتگی قابل‌استفاده نیستند.
- `POL:BLUEPRINT:5.2.1:11` (B:1992): ۱۱. **برآورد پیش از تعهد:** هر برش قبل از ورود به چرخه، دارای دامنه، تعداد/پیچیدگی Task، وابستگی، نفرساعت، هفته تقویمی، ظرفیت واقعی، ریسک، حاشیه عدم‌قطعیت، هزینه و برآورد توکن است؛ اعداد بدون داده به‌عنوان تعهد قطعی ثبت نمی‌شوند.
- `POL:BLUEPRINT:5.2.1:12` (B:1994): ۱۲. **تفکیک هزینه ساخت و استفاده:** هزینه توسعه (انسان، ایجنت کدنویسی، توکن تحلیل/کد/تست/اصلاح، ابزار و آزمون) از هزینه بهره‌برداری (توکن هر درخواست، API/بانکداری باز، زیرساخت، پایش، نگهداری و هزینه هر عملیات موفق) مستقل برآورد و پایش می‌شود. MCPهای اتصال به منابع و خدمات تحت مالکیت و کنترل شهاب توسعه می‌یابند؛ استفاده از APIهای مجاز بانکداری باز بر اساس دسترسی، قرارداد، امنیت و هزینه بررسی می‌شود و اتصال MCP به‌خودی‌خود مزیت رقابتی فرض نمی‌شود.
- `POL:BLUEPRINT:5.2.1:13` (B:1996): ۱۳. **ظرفیت واقعی و حفظ تحقیق:** تعهد هفتگی بر اساس ظرفیت واقعی توسعه، تست و استقرار تعیین می‌شود؛ تخصیص Discovery/Delivery مطابق نسبت‌های مصوب O5-09 و شرایط تغییر آن است، نه تقسیم مصنوعی و ثابت میان دو سرویس.
- `POL:BLUEPRINT:5.2.1:14` (B:1998): ۱۴. **اصلاح تخمین با شواهد:** در پایان هر چرخه، زمان، نفرساعت، توکن، هزینه و خطاهای پیش‌بینی‌شده با مقدار واقعی مقایسه و مبنای تخمین چرخه‌های بعد به‌روزرسانی می‌شود؛ علت اختلاف و هزینه دوباره‌کاری ثبت می‌شود.
- `POL:BLUEPRINT:5.2.1:15` (B:2002): ۱۵. **تعریف پایان مبتنی بر کارکرد:** قابلیت فقط با تکمیل اتصال سرتاسری، تجربه کاربری، آزمون‌های لازم، معیار پذیرش، پایش متناسب، مستندات ضروری و اثبات عملکرد در محیط هدف «انجام‌شده» است؛ سبزشدن تست واحد یا Merge به‌تنهایی کافی نیست.
- `POL:BLUEPRINT:5.2.1:16` (B:2004): ۱۶. **انتشار ایمن و قابل‌بازگشت:** هر نسخه باید گیت‌های ریسک R1–R4، RG/REL و F06 متناسب با دامنه را بگذراند؛ انتشار آزمایشی برای کاربران مجاز، استقرار و انتشار عمومی یکسان نیستند. Rollback/Restore و توقف اضطراری پیش از فعال‌سازی بررسی می‌شوند.
- `POL:BLUEPRINT:5.2.1:17` (B:2006): ۱۷. **یادگیری زیر بار واقعی:** انتشارهای مجاز در اولین فرصت به کاربران واقعی یا گروه پایلوت می‌رسند؛ موفقیت، شکست، زمان، هزینه، خطا و بازخورد با حداقل داده لازم و رعایت حریم خصوصی سنجیده می‌شود؛ RUM به داده‌های عملکردی محدود می‌ماند و به معنی ضبط نشست/فرم نیست.
- `POL:BLUEPRINT:5.2.1:18` (B:2008): ۱۸. **اثبات تدریجی تمایز:** RAG معتبر، کشف فلو، Computer Use سازگارشونده، مدیریت وابستگی خدمت و Feedback/Feedforward با سناریو و شاخص واقعی (صحت، نرخ موفقیت، مداخله انسانی، زمان و هزینه هر عملیات موفق) ارزیابی می‌شوند؛ نمایش فنی یا تعداد MCP/API شاخص مزیت رقابتی نیست.
- `POL:BLUEPRINT:5.2.1:19` (B:2012): ۱۹. **تفکیک مرجع سیاست از برنامه اجرا:** سند جامع فاز دوم و اسناد مصوب مرتبط از جمله سند کیف پول، مرجع الزامات باقی می‌مانند؛ «سند برنامه پیاده‌سازی فاز دوم شهاب» فقط ترتیب، برش انتشار، وابستگی، منابع، هزینه، توکن و معیار پذیرش را تعیین می‌کند و بدون تصمیم مستقل، مصوبه‌ای را تغییر نمی‌دهد.
- `POL:BLUEPRINT:5.2.1:20` (B:2014): ۲۰. **ردیابی دوسویه الزامات:** برای هر برش و Task باید شناسه الزام/مصوبه، مالک، وابستگی، نسخه انتشار، آزمون و شاهد پذیرش مشخص باشد؛ ماتریس پوشش باید الزامات اجراشده، برنامه‌ریزی‌شده و باقی‌مانده را نشان دهد تا ساده‌سازی به حذف خاموش دامنه نینجامد.
- `POL:BLUEPRINT:5.2.1:21` (B:2016): ۲۱. **کنترل تغییر و جلوگیری از تکرار:** قبل از ساخت، کد و قابلیت‌های موجود Core/Adviser/زیرساخت بررسی می‌شوند؛ تغییر قرارداد، داده، UI یا وابستگی با تحلیل اثر، سازگاری با پروتکل اجرای تسک و آزمون رگرسیون انجام می‌شود؛ اصلاح متن و کد موجود بر ایجاد مسیر موازی ترجیح دارد.
- `POL:BLUEPRINT:5.2.1:22` (B:2018): ۲۲. **اولویت‌بندی پویا بدون تغییر خاموش دامنه:** ترتیب برش‌ها بر اساس ارزش، وابستگی، ظرفیت، هزینه، ریسک و یادگیری واقعی بازتنظیم می‌شود؛ حذف الزام، تغییر معماری، جابه‌جایی گیت یا فعال‌سازی قابلیت مالی بدون تصویب مستقل مجاز نیست.

---

## ۱. برنامه Core / Wallet — ۱۸ بسته

### C01 — معماری و مبانی مشترک Core

**وضعیت:** `RA=PASS` / `IPA=PASS` در رجیستری پذیرفته‌شده؛ 40 Requirement؛ 4 Enabler/Story؛ 13 Task؛ 39 Subtask؛ 40 AC؛ 40 Test definition. اجرای محصول: **صفر**.

#### داستان‌ها / Enablerهای پذیرفته‌شده
**`TE:CORE:001` — Baseline and modular Core architecture**
- **هدف:** Baseline and modular Core architecture
- **ارزش:** Source-locked implementable boundary and validation specification; no standalone user release claimed
- **دامنه:** C01 architecture/phase-one compatibility design only
- **Taskهای عضو:** `TASK:CORE:001`، `TASK:CORE:002`، `TASK:CORE:003`

**`TE:CORE:002` — Core/Adviser contracts, snapshots and job/event boundaries**
- **هدف:** Core/Adviser contracts, snapshots and job/event boundaries
- **ارزش:** Source-locked implementable boundary and validation specification; no standalone user release claimed
- **دامنه:** C01 architecture/phase-one compatibility design only
- **Taskهای عضو:** `TASK:CORE:004`، `TASK:CORE:005`، `TASK:CORE:006`، `TASK:CORE:008`

**`TE:CORE:003` — Resilience, configuration and privacy-aware telemetry**
- **هدف:** Resilience, configuration and privacy-aware telemetry
- **ارزش:** Source-locked implementable boundary and validation specification; no standalone user release claimed
- **دامنه:** C01 architecture/phase-one compatibility design only
- **Taskهای عضو:** `TASK:CORE:007`، `TASK:CORE:009`، `TASK:CORE:010`

**`TE:CORE:004` — Incremental rollout, capacity and finance boundary protection**
- **هدف:** Incremental rollout, capacity and finance boundary protection
- **ارزش:** Source-locked implementable boundary and validation specification; no standalone user release claimed
- **دامنه:** C01 architecture/phase-one compatibility design only
- **Taskهای عضو:** `TASK:CORE:011`، `TASK:CORE:012`، `TASK:CORE:013`

#### Taskها و Subtaskهای اجرایی
##### `TASK:CORE:001` — Verify phase-one code/data/migration and regression baseline without assuming production state
- **مالک برنامه‌ریزی / اجرا:** C01 / C01
- **نوع کار / وضعیت کد:** VALIDATION / EXISTING_PARTIAL
- **مولفه‌ها:** FastAPI router; account; questionnaire; canonical scorer; serving publication; Alembic; Docker
- **شرط ورود:** locked main and safe read-only code inventory
- **خروجی اجرایی:** source-locked current-vs-target capability and migration baseline
- **Requirement:** `REQ:CORE:022`، `REQ:CORE:023`
- **وابستگی/قرارداد/پیش‌نیاز:** —
- **`TASK:CORE:001.S01`:** Map real routes/schemas/dependencies and preserved behavior؛ Requirement: `REQ:CORE:022`، `REQ:CORE:023`؛ AC: `AC:CORE:C01:022`، `AC:CORE:C01:023`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:001.S02`:** Verify Alembic heads/history against actual PostgreSQL test environment؛ Requirement: `REQ:CORE:022`، `REQ:CORE:023`؛ AC: `AC:CORE:C01:022`، `AC:CORE:C01:023`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:001.S03`:** Record tag/release digest and E2E evidence; mark unknown if runtime inaccessible؛ Requirement: `REQ:CORE:022`، `REQ:CORE:023`؛ AC: `AC:CORE:C01:022`، `AC:CORE:C01:023`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:002` — Define and test modular Core boundaries and independent service data ownership
- **مالک برنامه‌ریزی / اجرا:** C01 / C01
- **نوع کار / وضعیت کد:** ARCHITECTURE_HARDENING / EXISTING_PARTIAL
- **مولفه‌ها:** backend/app/*; SQLAlchemy; architecture import checks
- **شرط ورود:** T001 baseline
- **خروجی اجرایی:** module ownership map, architecture policy test specification and service data authority matrix
- **Requirement:** `REQ:CORE:001`، `REQ:CORE:005`، `REQ:CORE:007`، `REQ:CORE:013`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:001', 'type': 'HARD'}
- **`TASK:CORE:002.S01`:** Map module ownership and public ports؛ Requirement: `REQ:CORE:001`، `REQ:CORE:005`، `REQ:CORE:007`، `REQ:CORE:013`؛ AC: `AC:CORE:C01:001`، `AC:CORE:C01:005`، `AC:CORE:C01:007`، `AC:CORE:C01:013`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:002.S02`:** Specify forbidden private ORM/table access and dependency DAG؛ Requirement: `REQ:CORE:001`، `REQ:CORE:005`، `REQ:CORE:007`، `REQ:CORE:013`؛ AC: `AC:CORE:C01:001`، `AC:CORE:C01:005`، `AC:CORE:C01:007`، `AC:CORE:C01:013`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:002.S03`:** Specify local transaction boundaries and regression safety؛ Requirement: `REQ:CORE:001`، `REQ:CORE:005`، `REQ:CORE:007`، `REQ:CORE:013`؛ AC: `AC:CORE:C01:001`، `AC:CORE:C01:005`، `AC:CORE:C01:007`، `AC:CORE:C01:013`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:003` — Specify R1 Core/Adviser deployment and future Assistant boundary on existing infrastructure
- **مالک برنامه‌ریزی / اجرا:** C01 / C01
- **نوع کار / وضعیت کد:** CONTRACT_DESIGN / NEW
- **مولفه‌ها:** Docker Compose; Core API; Adviser deployment contract; PostgreSQL/Redis ownership
- **شرط ورود:** T002 authority map and R1 scope approval
- **خروجی اجرایی:** R1 topology and independent release-boundary acceptance contract without deployment
- **Requirement:** `REQ:CORE:002`، `REQ:CORE:003`، `REQ:CORE:004`، `REQ:CORE:049`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:002', 'type': 'HARD'}
- **`TASK:CORE:003.S01`:** Define two R1 deployment units, Assistant interface only؛ Requirement: `REQ:CORE:002`، `REQ:CORE:003`، `REQ:CORE:004`، `REQ:CORE:049`؛ AC: `AC:CORE:C01:002`، `AC:CORE:C01:003`، `AC:CORE:C01:004`، `AC:CORE:C01:049`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:003.S02`:** Define shared-host resource and logical tenant/schema separation؛ Requirement: `REQ:CORE:002`، `REQ:CORE:003`، `REQ:CORE:004`، `REQ:CORE:049`؛ AC: `AC:CORE:C01:002`، `AC:CORE:C01:003`، `AC:CORE:C01:004`، `AC:CORE:C01:049`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:003.S03`:** Specify R1 boot/integration and no-Wallet dependency checks؛ Requirement: `REQ:CORE:002`، `REQ:CORE:003`، `REQ:CORE:004`، `REQ:CORE:049`؛ AC: `AC:CORE:C01:002`، `AC:CORE:C01:003`، `AC:CORE:C01:004`، `AC:CORE:C01:049`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:004` — Preserve deterministic loan recommendation under one published snapshot and expose versioned contract
- **مالک برنامه‌ریزی / اجرا:** C01 / C05b
- **نوع کار / وضعیت کد:** CONTRACT_ADAPTATION / REUSE
- **مولفه‌ها:** recommendation/application/use_cases.py; canonical_scoring.py; data_pipeline/publish_serving_version.py; API
- **شرط ورود:** T001 baseline, T008 contract design
- **خروجی اجرایی:** Core recommendation consumer contract and golden/nonregression test plan
- **Requirement:** `REQ:CORE:008`، `REQ:CORE:009`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:001', 'type': 'HARD'}؛ {'task': 'TASK:CORE:008', 'type': 'CONTRACT'}
- **`TASK:CORE:004.S01`:** Freeze existing golden semantics and published snapshot authority؛ Requirement: `REQ:CORE:008`، `REQ:CORE:009`؛ AC: `AC:CORE:C01:008`، `AC:CORE:C01:009`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:004.S02`:** Specify synchronous recommendation result schema, version and provenance؛ Requirement: `REQ:CORE:008`، `REQ:CORE:009`؛ AC: `AC:CORE:C01:008`، `AC:CORE:C01:009`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:004.S03`:** Specify failure/invalid-snapshot handling without fabricated match؛ Requirement: `REQ:CORE:008`، `REQ:CORE:009`؛ AC: `AC:CORE:C01:008`، `AC:CORE:C01:009`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:005` — Design service-owned durable job pattern without imposing one universal workflow engine
- **مالک برنامه‌ریزی / اجرا:** C01 / C03
- **نوع کار / وضعیت کد:** ARCHITECTURE_DESIGN / NEW
- **مولفه‌ها:** PostgreSQL job state; Port/Adapter; service-owned worker
- **شرط ورود:** T002 service ownership; owner-specific long-running use case
- **خروجی اجرایی:** versioned job pattern and worker-crash/migration test contract
- **Requirement:** `REQ:CORE:010`، `REQ:CORE:011`، `REQ:CORE:041`، `REQ:CORE:042`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:002', 'type': 'HARD'}
- **`TASK:CORE:005.S01`:** Separate short synchronous calls from actual long jobs؛ Requirement: `REQ:CORE:010`، `REQ:CORE:011`، `REQ:CORE:041`، `REQ:CORE:042`؛ AC: `AC:CORE:C01:010`، `AC:CORE:C01:011`، `AC:CORE:C01:041`، `AC:CORE:C01:042`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:005.S02`:** Specify persistent job state/version and safe recovery؛ Requirement: `REQ:CORE:010`، `REQ:CORE:011`، `REQ:CORE:041`، `REQ:CORE:042`؛ AC: `AC:CORE:C01:010`، `AC:CORE:C01:011`، `AC:CORE:C01:041`، `AC:CORE:C01:042`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:005.S03`:** Define old-job completion vs new-engine routing criteria؛ Requirement: `REQ:CORE:010`، `REQ:CORE:011`، `REQ:CORE:041`، `REQ:CORE:042`؛ AC: `AC:CORE:C01:010`، `AC:CORE:C01:011`، `AC:CORE:C01:041`، `AC:CORE:C01:042`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:006` — Specify transactional outbox and idempotent event consumption only for proven asynchronous flows
- **مالک برنامه‌ریزی / اجرا:** C01 / C03
- **نوع کار / وضعیت کد:** CONDITIONAL_DESIGN / NEW
- **مولفه‌ها:** Owner transaction; outbox; event schema; subscribers
- **شرط ورود:** T002 data ownership; demonstrable event consumer/use case
- **خروجی اجرایی:** minimal event/outbox protocol with fault-injection acceptance
- **Requirement:** `REQ:CORE:012`، `REQ:CORE:043`، `REQ:CORE:044`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:002', 'type': 'HARD'}؛ {'task': 'TASK:CORE:005', 'type': 'CONTRACT'}
- **`TASK:CORE:006.S01`:** Identify truly necessary reliable events؛ Requirement: `REQ:CORE:012`، `REQ:CORE:043`، `REQ:CORE:044`؛ AC: `AC:CORE:C01:012`، `AC:CORE:C01:043`، `AC:CORE:C01:044`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:006.S02`:** Specify atomic local writes and publisher recovery؛ Requirement: `REQ:CORE:012`، `REQ:CORE:043`، `REQ:CORE:044`؛ AC: `AC:CORE:C01:012`، `AC:CORE:C01:043`، `AC:CORE:C01:044`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:006.S03`:** Specify duplicate/out-of-order/unknown-schema consumer behavior؛ Requirement: `REQ:CORE:012`، `REQ:CORE:043`، `REQ:CORE:044`؛ AC: `AC:CORE:C01:012`، `AC:CORE:C01:043`، `AC:CORE:C01:044`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:007` — Specify bounded cross-service resilience and interactive/background isolation
- **مالک برنامه‌ریزی / اجرا:** C01 / C03
- **نوع کار / وضعیت کد:** CONTRACT_HARDENING / NEW
- **مولفه‌ها:** HTTP client; job queue; rate/timeout/circuit policy
- **شرط ورود:** T003 and T008 service-contract interfaces
- **خروجی اجرایی:** fault matrix and testable resilience contract, numeric thresholds ESTIMATION_REQUIRED
- **Requirement:** `REQ:CORE:037`، `REQ:CORE:038`، `REQ:CORE:039`، `REQ:CORE:040`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:003', 'type': 'CONTRACT'}؛ {'task': 'TASK:CORE:008', 'type': 'CONTRACT'}
- **`TASK:CORE:007.S01`:** Set timeout budget from tested path baseline؛ Requirement: `REQ:CORE:037`، `REQ:CORE:038`، `REQ:CORE:039`، `REQ:CORE:040`؛ AC: `AC:CORE:C01:037`، `AC:CORE:C01:038`، `AC:CORE:C01:039`، `AC:CORE:C01:040`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:007.S02`:** Bound transient retry and circuit state transitions؛ Requirement: `REQ:CORE:037`، `REQ:CORE:038`، `REQ:CORE:039`، `REQ:CORE:040`؛ AC: `AC:CORE:C01:037`، `AC:CORE:C01:038`، `AC:CORE:C01:039`، `AC:CORE:C01:040`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:007.S03`:** Separate concurrency pools and graceful degradation؛ Requirement: `REQ:CORE:037`، `REQ:CORE:038`، `REQ:CORE:039`، `REQ:CORE:040`؛ AC: `AC:CORE:C01:037`، `AC:CORE:C01:038`، `AC:CORE:C01:039`، `AC:CORE:C01:040`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:008` — Design Core API versioning and semantic provider/consumer compatibility verification
- **مالک برنامه‌ریزی / اجرا:** C01 / C03
- **نوع کار / وضعیت کد:** CONTRACT_CHANGE / EXISTING_PARTIAL
- **مولفه‌ها:** FastAPI OpenAPI; API v1 router; schema fixtures; CI
- **شرط ورود:** T002 authority matrix and existing API schema
- **خروجی اجرایی:** contract matrix and migration-safe OpenAPI evolution plan
- **Requirement:** `REQ:CORE:006`، `REQ:CORE:015`، `REQ:CORE:016`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:002', 'type': 'HARD'}
- **`TASK:CORE:008.S01`:** Inventory existing versioned API and consumers؛ Requirement: `REQ:CORE:006`، `REQ:CORE:015`، `REQ:CORE:016`؛ AC: `AC:CORE:C01:006`، `AC:CORE:C01:015`، `AC:CORE:C01:016`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:008.S02`:** Specify schema-first compatible and breaking change protocol؛ Requirement: `REQ:CORE:006`، `REQ:CORE:015`، `REQ:CORE:016`؛ AC: `AC:CORE:C01:006`، `AC:CORE:C01:015`، `AC:CORE:C01:016`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:008.S03`:** Define consumer contract, semantic field and error tests؛ Requirement: `REQ:CORE:006`، `REQ:CORE:015`، `REQ:CORE:016`؛ AC: `AC:CORE:C01:006`، `AC:CORE:C01:015`، `AC:CORE:C01:016`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:009` — Separate typed runtime config, secrets, feature flags and protected financial business policy
- **مالک برنامه‌ریزی / اجرا:** C01 / C03
- **نوع کار / وضعیت کد:** POLICY_AND_CONFIG_DESIGN / EXISTING_PARTIAL
- **مولفه‌ها:** core/config.py; CI security; configuration deployment
- **شرط ورود:** T001 baseline and known policy owners
- **خروجی اجرایی:** four-category config contract and validation/rollback tests
- **Requirement:** `REQ:CORE:017`، `REQ:CORE:018`، `REQ:CORE:045`، `REQ:CORE:046`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:001', 'type': 'HARD'}؛ {'task': 'TASK:CORE:008', 'type': 'CONTRACT'}
- **`TASK:CORE:009.S01`:** Inventory present Settings and secret paths؛ Requirement: `REQ:CORE:017`، `REQ:CORE:018`، `REQ:CORE:045`، `REQ:CORE:046`؛ AC: `AC:CORE:C01:017`، `AC:CORE:C01:018`، `AC:CORE:C01:045`، `AC:CORE:C01:046`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:009.S02`:** Define schema, policy authorization, flag dependency and change audit؛ Requirement: `REQ:CORE:017`، `REQ:CORE:018`، `REQ:CORE:045`، `REQ:CORE:046`؛ AC: `AC:CORE:C01:017`، `AC:CORE:C01:018`، `AC:CORE:C01:045`، `AC:CORE:C01:046`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:009.S03`:** Design compatible config rollback and negative gate cases؛ Requirement: `REQ:CORE:017`، `REQ:CORE:018`، `REQ:CORE:045`، `REQ:CORE:046`؛ AC: `AC:CORE:C01:017`، `AC:CORE:C01:018`، `AC:CORE:C01:045`، `AC:CORE:C01:046`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:010` — Plan privacy-preserving OpenTelemetry and measured SLO/incident evidence
- **مالک برنامه‌ریزی / اجرا:** C01 / C03
- **نوع کار / وضعیت کد:** OBSERVABILITY_DESIGN / EXISTING_PARTIAL
- **مولفه‌ها:** api/observability.py; metrics/logging; tracing; CI and runbooks
- **شرط ورود:** T001 operational footprint and realistic workload
- **خروجی اجرایی:** telemetry data-classification and SLO measurement/runbook acceptance contract
- **Requirement:** `REQ:CORE:019`، `REQ:CORE:020`، `REQ:CORE:021`، `REQ:CORE:047`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:001', 'type': 'HARD'}؛ {'task': 'TASK:CORE:007', 'type': 'PREFERENCE'}
- **`TASK:CORE:010.S01`:** Map existing low-cardinality API observability؛ Requirement: `REQ:CORE:019`، `REQ:CORE:020`، `REQ:CORE:021`، `REQ:CORE:047`؛ AC: `AC:CORE:C01:019`، `AC:CORE:C01:020`، `AC:CORE:C01:021`، `AC:CORE:C01:047`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:010.S02`:** Specify trace context propagation without PII/OTP؛ Requirement: `REQ:CORE:019`، `REQ:CORE:020`، `REQ:CORE:021`، `REQ:CORE:047`؛ AC: `AC:CORE:C01:019`، `AC:CORE:C01:020`، `AC:CORE:C01:021`، `AC:CORE:C01:047`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:010.S03`:** Define measurement experiment and SigNoz decision gate؛ Requirement: `REQ:CORE:019`، `REQ:CORE:020`، `REQ:CORE:021`، `REQ:CORE:047`؛ AC: `AC:CORE:C01:019`، `AC:CORE:C01:020`، `AC:CORE:C01:021`، `AC:CORE:C01:047`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:011` — Implement planning-level stage/release separation and RG/REL/F06/COV evidence mapping
- **مالک برنامه‌ریزی / اجرا:** C01 / C01
- **نوع کار / وضعیت کد:** RELEASE_GOVERNANCE_DESIGN / REUSE
- **مولفه‌ها:** quality/security workflows; release policy; documentation checkpoint
- **شرط ورود:** source-locked 22 principles and approved governance decision texts
- **خروجی اجرایی:** go/no-go and scope-completeness release evidence schema; no release authorized
- **Requirement:** `REQ:CORE:024`، `REQ:CORE:026`، `REQ:CORE:027`، `REQ:CORE:048`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:001', 'type': 'CONTRACT'}؛ {'task': 'TASK:CORE:004', 'type': 'CONTRACT'}؛ {'task': 'TASK:CORE:009', 'type': 'POLICY'}؛ {'task': 'TASK:CORE:010', 'type': 'POLICY'}
- **`TASK:CORE:011.S01`:** Map risk and RG/REL/F06 controls without replacing them؛ Requirement: `REQ:CORE:024`، `REQ:CORE:026`، `REQ:CORE:027`، `REQ:CORE:048`؛ AC: `AC:CORE:C01:024`، `AC:CORE:C01:026`، `AC:CORE:C01:027`، `AC:CORE:C01:048`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:011.S02`:** Define stage completion vs incremental readiness evidence and record the O5-09 capacity allocation class and actual Discovery/Delivery split؛ baseline 80/20، critical work 90/10، uncertain work 70/30 with an explicit timebox؛ Requirement: `REQ:CORE:024`، `REQ:CORE:026`، `REQ:CORE:027`، `REQ:CORE:048`؛ AC: `AC:CORE:C01:024`، `AC:CORE:C01:026`، `AC:CORE:C01:027`، `AC:CORE:C01:048`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:011.S03`:** Define independent high-risk reviewer, conditional go and rollback records؛ Requirement: `REQ:CORE:024`، `REQ:CORE:026`، `REQ:CORE:027`، `REQ:CORE:048`؛ AC: `AC:CORE:C01:024`، `AC:CORE:C01:026`، `AC:CORE:C01:027`، `AC:CORE:C01:048`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:012` — Protect modular Wallet/Ledger boundary and future service/contract integration without early financial activation
- **مالک برنامه‌ریزی / اجرا:** C01 / C07
- **نوع کار / وضعیت کد:** BOUNDARY_DESIGN / NEW
- **مولفه‌ها:** Future wallet module interface; Core financial authority
- **شرط ورود:** W V0.20 and B A01/O5-13; finance-specific packages later
- **خروجی اجرایی:** wallet module boundary and finance handoff contract
- **Requirement:** `REQ:CORE:033`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:002', 'type': 'CONTRACT'}؛ {'task': 'TASK:CORE:011', 'type': 'POLICY'}
- **`TASK:CORE:012.S01`:** Document closed-loop scope and Core module ownership؛ Requirement: `REQ:CORE:033`؛ AC: `AC:CORE:C01:033`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:012.S02`:** Prohibit external-merchant acceptance and early paid-flow assumption؛ Requirement: `REQ:CORE:033`؛ AC: `AC:CORE:C01:033`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:012.S03`:** Handoff ledger/credit policies to C07-C13 without duplicate implementation؛ Requirement: `REQ:CORE:033`؛ AC: `AC:CORE:C01:033`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

##### `TASK:CORE:013` — Benchmark real phase-two service capacity and justify any physical split or VM/telemetry deployment
- **مالک برنامه‌ریزی / اجرا:** C01 / C01
- **نوع کار / وضعیت کد:** MEASUREMENT_AND_DECISION / BLOCKED
- **مولفه‌ها:** docker-compose.prod.yml; VM and runtime metrics; load fixtures
- **شرط ورود:** authorized performance environment and safe workload; numeric budget gate pending
- **خروجی اجرایی:** evidence-based capacity decision; no arbitrary VM/SigNoz deployment
- **Requirement:** `REQ:CORE:032`
- **وابستگی/قرارداد/پیش‌نیاز:** {'task': 'TASK:CORE:003', 'type': 'CONTRACT'}؛ {'task': 'TASK:CORE:007', 'type': 'CONTRACT'}؛ {'task': 'TASK:CORE:010', 'type': 'CONTRACT'}
- **`TASK:CORE:013.S01`:** Collect existing production/runtime resource baseline when authorized؛ Requirement: `REQ:CORE:032`؛ AC: `AC:CORE:C01:032`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:013.S02`:** Measure equal workloads and failure isolation؛ Requirement: `REQ:CORE:032`؛ AC: `AC:CORE:C01:032`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:013.S03`:** Compare cost and define explicit physical-extraction decision record؛ Requirement: `REQ:CORE:032`؛ AC: `AC:CORE:C01:032`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`
- **`TASK:CORE:013.S04`:** Separate development from operating cost, use measured team capacity/uncertainty, and compare actual time/person-hours/tokens/cost/rework with the estimate after each cycle؛ Requirement: `REQ:CORE:032`؛ AC: `AC:CORE:C01:032`؛ وضعیت اجرای محصول: `NOT_IMPLEMENTED`

#### ردیابی اتمی Requirement → AC → Test
هر ردیف زیر حکم منبع را به معیار پذیرش و آزمون طراحی متصل می‌کند. سناریوهای تست طراحی‌اند؛ `NOT_EXECUTED` به معنای تأیید عملکرد واقعی نیست.

##### `REQ:CORE:001` — Core is a modular monolith with explicit internal module boundaries; no forced service-per-module split.
- **مرجع:** B:20;B:1956
- **Source Unit:** `SU-B-00009`، `SU-B-00884`
- **مالک:** CoreArchitecture
- **وضعیت حکم:** APPROVED_EXPLICIT
- **شرط/استثنا:** All Core modules / No service-per-module mandate
- **رفتارهای اتمی:** `REQ:CORE:001.B01` Core remains a modular monolith؛ `REQ:CORE:001.B02` Module public boundaries and data authority are explicit
- **Taskهای ردیابی‌شده:** `TASK:CORE:002`
- **AC `AC:CORE:C01:001`**؛ Task: `TASK:CORE:002`؛ Given: All Core modules؛ When: Compose Core with declared modules and public ports: deployment is one modular Core with a single owner per module؛ Then: Core remains a modular monolith؛ Module public boundaries and data authority are explicit؛ Negative: Propose one standalone service per module without evidence: architecture review rejects it؛ Boundary: Add a module calling a private neighbour: boundary checker flags the edge rather than silently expanding public authority
- **Test `TEST:CORE:C01:001`**؛ Environment: Static topology/module review plus architecture-policy fixture؛ Oracle: Check every linked atomic behaviour and exception against the source-locked contract; all positive assertions must hold and the injected violation must be rejected. A passing API/file-existence check is insufficient.؛ وضعیت: `NOT_EXECUTED`
  - `TEST:CORE:C01:001.P` (POSITIVE): Compose Core with declared modules and public ports: deployment is one modular Core with a single owner per module
  - `TEST:CORE:C01:001.N` (NEGATIVE): Propose one standalone service per module without evidence: architecture review rejects it
  - `TEST:CORE:C01:001.B` (BOUNDARY_OR_CONCURRENCY): Add a module calling a private neighbour: boundary checker flags the edge rather than silently expanding public authority

##### `REQ:CORE:002` — Adviser/RAG has independent deployment and independent data ownership from Core.
- **مرجع:** B:21;B:788;B:2063
- **Source Unit:** `SU-B-00010`، `SU-B-00418`، `SU-B-00934`
- **مالک:** CoreArchitecture
- **وضعیت حکم:** APPROVED_EXPLICIT
- **شرط/استثنا:** Core and Adviser integration / A shared host is permitted, shared private-table authority is not
- **رفتارهای اتمی:** `REQ:CORE:002.B01` Adviser is independently deployable from Core؛ `REQ:CORE:002.B02` Adviser owns its knowledge data and accesses Core only through authorized contracts
- **Taskهای ردیابی‌شده:** `TASK:CORE:003`
- **AC `AC:CORE:C01:002`**؛ Task: `TASK:CORE:003`؛ Given: Core and Adviser integration؛ When: Deploy a compatible Adviser revision independently while Core version stays fixed: authorized API calls remain valid؛ Then: Adviser is independently deployable from Core؛ Adviser owns its knowledge data and accesses Core only through authorized contracts؛ Negative: Configure Adviser credentials to SELECT/UPDATE a Core-private table: DB access denied and no data leaked؛ Boundary: Shared PostgreSQL instance with separate roles: own schema works while cross-schema grants remain absent
- **Test `TEST:CORE:C01:002`**؛ Environment: Isolated Core/Adviser integration with PostgreSQL16 separate roles and versioned contract harness؛ Oracle: Check every linked atomic behaviour and exception against the source-locked contract; all positive assertions must hold and the injected violation must be rejected. A passing API/file-existence check is insufficient.؛ وضعیت: `NOT_EXECUTED`
  - `TEST:CORE:C01:002.P` (POSITIVE): Deploy a compatible Adviser revision independently while Core version stays fixed: authorized API calls remain valid
  - `TEST:CORE:C01:002.N` (NEGATIVE): Configure Adviser credentials to SELECT/UPDATE a Core-private table: DB access denied and no data leaked
  - `TEST:CORE:C01:002.B` (BOUNDARY_OR_CONCURRENCY): Shared PostgreSQL instance with separate roles: own schema works while cross-schema grants remain absent

##### `REQ:CORE:003` — Assistant is an independent target service; R1 permits only its boundary/contracts, not running deployment.
- **مرجع:** B:22-23;B:2063
- **Source Unit:** `SU-B-00011`، `SU-B-00012`، `SU-B-00934`
- **مالک:** CoreArchitecture
- **وضعیت حکم:** APPROVED_EXPLICIT
- **شرط/استثنا:** RAG R1 / Future Assistant deployment needs its own approved release
- **رفتارهای اتمی:** `REQ:CORE:003.B01` R1 defines Assistant boundaries and versioned interfaces؛ `REQ:CORE:003.B02` R1 contains no running Assistant deployment or operational banking execution
- **Taskهای ردیابی‌شده:** `TASK:CORE:003`
- **AC `AC:CORE:C01:003`**؛ Task: `TASK:CORE:003`؛ Given: RAG R1؛ When: Review R1 manifest and interfaces: only Core/Adviser run; Assistant contract is recorded without worker or banking action؛ Then: R1 defines Assistant boundaries and versioned interfaces؛ R1 contains no running Assistant deployment or operational banking execution؛ Negative: Enable Assistant worker or transactional route through a flag in R1: release gate blocks activation؛ Boundary: A UI Coming Soon tab is allowed but cannot invoke an operational tool
- **Test `TEST:CORE:C01:003`**؛ Environment: R1 Compose/activation-manifest fixture; no production execution؛ Oracle: Check every linked atomic behaviour and exception against the source-locked contract; all positive assertions must hold and the injected violation must be rejected. A passing API/file-existence check is insufficient.؛ وضعیت: `NOT_EXECUTED`
  - `TEST:CORE:C01:003.P` (POSITIVE): Review R1 manifest and interfaces: only Core/Adviser run; Assistant contract is recorded without worker or banking action
  - `TEST:CORE:C01:003.N` (NEGATIVE): Enable Assistant worker or transactional route through a flag in R1: release gate blocks activation
  - `TEST:CORE:C01:003.B` (BOUNDARY_OR_CONCURRENCY): A UI Coming Soon tab is allowed but cannot invoke an operational tool

##### `REQ:CORE:004` — R1 may reuse current VM, PostgreSQL and Redis, subject to validation; logical ownership remains separate.
- **مرجع:** B:24;B:2063;B:2071
- **Source Unit:** `SU-B-00013`، `SU-B-00934`، `SU-B-00940`
- **مالک:** CoreArchitecture
- **وضعیت حکم:** APPROVED_EXPLICIT
- **شرط/استثنا:** Initial deployment planning / Physical separation requires security/capacity/resilience evidence and separate approval
- **رفتارهای اتمی:** `REQ:CORE:004.B01` Use current VM and PostgreSQL/Redis as a starting hypothesis, not proven capacity؛ `REQ:CORE:004.B02` Preserve logical service ownership on shared infrastructure؛ `REQ:CORE:004.B03` Do not infer three VMs or three database instances from three target services
- **Taskهای ردیابی‌شده:** `TASK:CORE:003`
- **AC `AC:CORE:C01:004`**؛ Task: `TASK:CORE:003`؛ Given: Initial deployment planning؛ When: Evaluate existing-host Core/Adviser topology with measured limits and separate logical data roles؛ Then: Use current VM and PostgreSQL/Redis as a starting hypothesis, not proven capacity؛ Preserve logical service ownership on shared infrastructure؛ Do not infer three VMs or three database instances from three target services؛ Negative: Demand three VMs solely from three target services: reject unsupported infrastructure commitment؛ Boundary: Overload shared host in an authorized sandbox: report limit/hold decision without pretending existing host is sufficient
- **Test `TEST:CORE:C01:004`**؛ Environment: Authorized shared-host performance sandbox; PostgreSQL16/Redis logical roles؛ Oracle: Check every linked atomic behaviour and exception against the source-locked contract; all positive assertions must hold and the injected violation must be rejected. A passing API/file-existence check is insufficient.؛ وضعیت: `NOT_EXECUTED`
  - `TEST:CORE:C01:004.P` (POSITIVE): Evaluate existing-host Core/Adviser topology with measured limits and separate logical data roles
  - `TEST:CORE:C01:004.N` (NEGATIVE): Demand three VMs solely from three target services: reject unsupported infrastructure commitment
  - `TEST:CORE:C01:004.B` (BOUNDARY_OR_CONCURRENCY): Overload shared host in an authorized sandbox: report limit/hold decision without pretending existing host is sufficient

##### `REQ:CORE:005` — Service private schemas, data, jobs and transactions must have one owner; no direct cross-service private-table reads/writes.
- **مرجع:** B:1192;B:1212;B:1825
- **Source Unit:** `SU-B-00572`، `SU-B-00589`، `SU-B-00830`
- **مالک:** CoreArchitecture
- **وضعیت حکم:** APPROVED_EXPLICIT
- **شرط/استثنا:** All service and module private data / Only owner-authorized public contracts cross the boundary
- **رفتارهای اتمی:** `REQ:CORE:005.B01` Assign exactly one logical owner to private tables, schema, jobs and mutations؛ `REQ:CORE:005.B02` Deny direct cross-service private-table reads and writes؛ `REQ:CORE:005.B03` Deny direct cross-database foreign-key coupling and private tool access
- **Taskهای ردیابی‌شده:** `TASK:CORE:002`
- **AC `AC:CORE:C01:005`**؛ Task: `TASK:CORE:002`؛ Given: All service and module private data؛ When: Owner mutates own data through its transaction and exposes only permitted contract data؛ Then: Assign exactly one logical owner to private tables, schema, jobs and mutations؛ Deny direct cross-service private-table reads and writes؛ Deny direct cross-database foreign-key coupling and private tool access؛ Negative: Adviser SELECT/UPDATE private Core table or import neighbour private ORM: deny and record boundary violation؛ Boundary: Concurrent owner/consumer operations keep each commit local and reject a cross-database FK or consumer private-tool call
- **Test `TEST:CORE:C01:005`**؛ Environment: PostgreSQL16 separate service roles plus import-boundary fixture؛ Oracle: Check every linked atomic behaviour and exception against the source-locked contract; all positive assertions must hold and the injected violation must be rejected. A passing API/file-existence check is insufficient.؛ وضعیت: `NOT_EXECUTED`
  - `TEST:CORE:C01:005.P` (POSITIVE): Owner mutates own data through its transaction and exposes only permitted contract data
  - `TEST:CORE:C01:005.N` (NEGATIVE): Adviser SELECT/UPDATE private Core table or import neighbour private ORM: deny and record boundary violation
  - `TEST:CORE:C01:005.B` (BOUNDARY_OR_CONCURRENCY): Concurrent owner/consumer operations keep each commit local and reject a cross-database FK or consumer private-tool call

##### `REQ:CORE:006` — Core exposes versioned and authorized data/domain/catalogue interfaces with minimal fields, provenance, version and error behavior.
- **مرجع:** B:869;B:1212-1214
- **Source Unit:** `SU-B-00435`، `SU-B-00589`، `SU-B-00590`
- **مالک:** CoreArchitecture
- **وضعیت حکم:** APPROVED_EXPLICIT
- **شرط/استثنا:** Core data, domain and catalogue consumers / Catalogue visibility alone grants neither personal-data access nor an action
- **رفتارهای اتمی:** `REQ:CORE:006.B01` Expose versioned contracts with owner, consumer, purpose and minimal fields؛ `REQ:CORE:006.B02` Enforce identity, scope and authorization before releasing data؛ `REQ:CORE:006.B03` Preserve stable reference, provenance, version/freshness, approval and access metadata؛ `REQ:CORE:006.B04` Absent valid data or authorization produces detectable error/completion request/safe stop, never table bypass or fabricated result
- **Taskهای ردیابی‌شده:** `TASK:CORE:008`
- **AC `AC:CORE:C01:006`**؛ Task: `TASK:CORE:008`؛ Given: Core data, domain and catalogue consumers؛ When: Authorized consumer with correct purpose requests minimal catalogue evidence: returns stable ID, source, version/freshness and approval؛ Then: Expose versioned contracts with owner, consumer, purpose and minimal fields؛ Enforce identity, scope and authorization before releasing data؛ Preserve stable reference, provenance, version/freshness, approval and access metadata؛ Absent valid data or authorization produces detectable error/completion request/safe stop, never table bypass or fabricated result؛ Negative: Unauthorized or wrong-domain consumer requests private field: deny before response and do not query private table as fallback؛ Boundary: Revoke access between prior read and next call or supply stale/missing data: explicit stop/error, no fabricated recommendation
- **Test `TEST:CORE:C01:006`**؛ Environment: Core data/catalogue API fixture with PostgreSQL16 isolated roles, purpose/domain authorization and revocation races؛ Oracle: Check every linked atomic behaviour and exception against the source-locked contract; all positive assertions must hold and the injected violation must be rejected. A passing API/file-existence check is insufficient.؛ وضعیت: `NOT_EXECUTED`
  - `TEST:CORE:C01:006.P` (POSITIVE): Authorized consumer with correct purpose requests minimal catalogue evidence: returns stable ID, source, version/freshness and approval
  - `TEST:CORE:C01:006.N` (NEGATIVE): Unauthorized or wrong-domain consumer requests private field: deny before response and do not query private table as fallback
  - `TEST:CORE:C01:006.B` (BOUNDARY_OR_CONCURRENCY): Revoke access between prior read and next call or supply stale/missing data: explicit stop/error, no fabricated recommendation

##### `REQ:CORE:007` — No cross-module cyclic dependencies or private ORM leakage; reuse existing common capabilities instead of parallel authorities.
- **مرجع:** B:1827-1829;B:1986
- **Source Unit:** `SU-B-00831`، `SU-B-00832`، `SU-B-00899`
- **مالک:** CoreArchitecture
- **وضعیت حکم:** APPROVED_EXPLICIT
- **شرط/استثنا:** Cross-module use and reuse / Reuse does not merge Adviser/Assistant domain logic or authorities
- **رفتارهای اتمی:** `REQ:CORE:007.B01` Prevent module dependency cycles؛ `REQ:CORE:007.B02` Forbid private ORM imports across public module boundaries؛ `REQ:CORE:007.B03` Reuse existing identity, permission and shared infrastructure authorities
- **Taskهای ردیابی‌شده:** `TASK:CORE:002`
- **AC `AC:CORE:C01:007`**؛ Task: `TASK:CORE:002`؛ Given: Cross-module use and reuse؛ When: Build ownership map and directed imports through public ports, reusing existing account/permission authority؛ Then: Prevent module dependency cycles؛ Forbid private ORM imports across public module boundaries؛ Reuse existing identity, permission and shared infrastructure authorities؛ Negative: Inject domain-to-private-infrastructure import or cross-module ORM access: architecture check rejects؛ Boundary: Add A-to-B and B-to-A edges or duplicate identity authority: cycle/parallel-authority check fails
- **Test `TEST:CORE:C01:007`**؛ Environment: Static import DAG and facade checks with forbidden-edge fixtures؛ Oracle: Check every linked atomic behaviour and exception against the source-locked contract; all positive assertions must hold and the injected violation must be rejected. A passing API/file-existence check is insufficient.؛ وضعیت: `NOT_EXECUTED`
  - `TEST:CORE:C01:007.P` (POSITIVE): Build ownership map and directed imports through public ports, reusing existing account/permission authority
  - `TEST:CORE:C01:007.N` (NEGATIVE): Inject domain-to-private-infrastructure import or cross-module ORM access: architecture check rejects
  - `TEST:CORE:C01:007.B` (BOUNDARY_OR_CONCURRENCY): Add A-to-B and B-to-A edges or duplicate identity authority: cycle/parallel-authority check fails

##### `REQ:CORE:008` — Core retains deterministic loan recommendation, matching, reasons, loan rules and published serving Snapshot.
- **مرجع:** B:1629-1633;B:2284
- **Source Unit:** `SU-B-00743`، `SU-B-00744`، `SU-B-00745`، `SU-B-01087`
- **مالک:** CoreArchitecture
- **وضعیت حکم:** APPROVED_EXPLICIT
- **شرط/استثنا:** Loan recommendation in Adviser / Other domains need no recommendation engine merely because they have catalogue entries
- **رفتارهای اتمی:** `REQ:CORE:008.B01` Keep deterministic matching, ranking, reasons and rules in Core؛ `REQ:CORE:008.B02` Reuse the existing scorer and publication authority without reimplementing them in Adviser or frontend؛ `REQ:CORE:008.B03` Call Core synchronously for the short deterministic calculation
- **Taskهای ردیابی‌شده:** `TASK:CORE:004`
- **AC `AC:CORE:C01:008`**؛ Task: `TASK:CORE:004`؛ Given: Loan recommendation in Adviser؛ When: Run existing golden loan fixtures through Core API consumer: matching, reasons and versions retain canonical meaning؛ Then: Keep deterministic matching, ranking, reasons and rules in Core؛ Reuse the existing scorer and publication authority without reimplementing them in Adviser or frontend؛ Call Core synchronously for the short deterministic calculation؛ Negative: Frontend/Adviser supplies its own computed score or modifies rules: consumer/integrity test rejects it؛ Boundary: Present catalogue-only product in another domain: no dedicated engine is created without validated rules/use case
- **Test `TEST:CORE:C01:008`**؛ Environment: Existing backend golden/publication fixtures and Core/Adviser consumer harness؛ Oracle: Check every linked atomic behaviour and exception against the source-locked contract; all positive assertions must hold and the injected violation must be rejected. A passing API/file-existence check is insufficient.؛ وضعیت: `NOT_EXECUTED`
  - `TEST:CORE:C01:008.P` (POSITIVE): Run existing golden loan fixtures through Core API consumer: matching, reasons and versions retain canonical meaning
  - `TEST:CORE:C01:008.N` (NEGATIVE): Frontend/Adviser supplies its own computed score or modifies rules: consumer/integrity test rejects it
  - `TEST:CORE:C01:008.B` (BOUNDARY_OR_CONCURRENCY): Present catalogue-only product in another domain: no dedicated engine is created without validated rules/use case

##### `REQ:CORE:009` — A recommendation run uses one compatible published product Snapshot and rule version, never synthetic results after Core failure.
- **مرجع:** B:1216;B:2075;B:2326
- **Source Unit:** `SU-B-00591`، `SU-B-00942`، `SU-B-01119`
- **مالک:** CoreArchitecture
- **وضعیت حکم:** APPROVED_EXPLICIT
- **شرط/استثنا:** Every loan recommendation run / Non-sensitive cache can be eventually consistent but cannot supply authoritative scoring
- **رفتارهای اتمی:** `REQ:CORE:009.B01` Use one valid published catalogue Snapshot and compatible rule version for the whole run؛ `REQ:CORE:009.B02` Concurrent publication never mixes versions within a result؛ `REQ:CORE:009.B03` Expose catalogue and rule versions, and reject invalid or unapproved input؛ `REQ:CORE:009.B04` Core failure produces explicit unavailability rather than synthetic recommendation
- **Taskهای ردیابی‌شده:** `TASK:CORE:004`
- **AC `AC:CORE:C01:009`**؛ Task: `TASK:CORE:004`؛ Given: Every loan recommendation run؛ When: Recommend with approved catalogue S1 and rule R1: result and reasons identify exactly S1/R1؛ Then: Use one valid published catalogue Snapshot and compatible rule version for the whole run؛ Concurrent publication never mixes versions within a result؛ Expose catalogue and rule versions, and reject invalid or unapproved input؛ Core failure produces explicit unavailability rather than synthetic recommendation؛ Negative: Supply draft/invalid Snapshot or sever Core API: return typed failure, no cached/synthetic match score؛ Boundary: Publish S2/R2 while S1/R1 run is paused: old run finishes consistently at S1/R1 and next run uses a compatible published pair
- **Test `TEST:CORE:C01:009`**؛ Environment: PostgreSQL16 publication/concurrent recommendation fixture and controlled Core outage؛ Oracle: Check every linked atomic behaviour and exception against the source-locked contract; all positive assertions must hold and the injected violation must be rejected. A passing API/file-existence check is insufficient.؛ وضعیت: `NOT_EXECUTED`
  - `TEST:CORE:C01:009.P` (POSITIVE): Recommend with approved catalogue S1 and rule R1: result and reasons identify exactly S1/R1
  - `TEST:CORE:C01:009.N` (NEGATIVE): Supply draft/invalid Snapshot or sever Core API: return typed failure, no cached/synthetic match score
  - `TEST:CORE:C01:009.B` (BOUNDARY_OR_CONCURRENCY): Publish S2/R2 while S1/R1 run is paused: old run finishes consistently at S1/R1 and next run uses a compatible published pair

##### `REQ:CORE:010` — Short deterministic operations use synchronous APIs; long owner-controlled work uses durable asynchronous Job workflows when needed.
- **مرجع:** B:1192;B:2075
- **Source Unit:** `SU-B-00572`، `SU-B-00942`
- **مالک:** CoreArchitecture
- **وضعیت حکم:** APPROVED_EXPLICIT
- **شرط/استثنا:** Classifying a real operation / An independent broker is not a prerequisite
- **رفتارهای اتمی:** `REQ:CORE:010.B01` Use authenticated versioned synchronous API for short deterministic work؛ `REQ:CORE:010.B02` Use durable service-owned asynchronous Job only for actual long background work؛ `REQ:CORE:010.B03` Do not move short loan scoring behind a queue
- **Taskهای ردیابی‌شده:** `TASK:CORE:005`
- **AC `AC:CORE:C01:010`**؛ Task: `TASK:CORE:005`؛ Given: Classifying a real operation؛ When: Short scoring call uses authorized synchronous API; actual long ingestion job returns durable job identity؛ Then: Use authenticated versioned synchronous API for short deterministic work؛ Use durable service-owned asynchronous Job only for actual long background work؛ Do not move short loan scoring behind a queue؛ Negative: Move scoring to mandatory broker or execute long job in request router with no durable state: reject design؛ Boundary: No broker available but existing owner PostgreSQL/worker supported: long work remains recoverable while scoring stays synchronous
- **Test `TEST:CORE:C01:010`**؛ Environment: Synchronous API and durable long-job harness without independent broker؛ Oracle: Check every linked atomic behaviour and exception against the source-locked contract; all positive assertions must hold and the injected violation must be rejected. A passing API/file-existence check is insufficient.؛ وضعیت: `NOT_EXECUTED`
  - `TEST:CORE:C01:010.P` (POSITIVE): Short scoring call uses authorized synchronous API; actual long ingestion job returns durable job identity
  - `TEST:CORE:C01:010.N` (NEGATIVE): Move scoring to mandatory broker or execute long job in request router with no durable state: reject design
  - `TEST:CORE:C01:010.B` (BOUNDARY_OR_CONCURRENCY): No broker available but existing owner PostgreSQL/worker supported: long work remains recoverable while scoring stays synchronous

##### `REQ:CORE:011` — Each Job owner persists state/result in PostgreSQL and exposes versioned ports/adapters, safe cancel/resume and recovery.
