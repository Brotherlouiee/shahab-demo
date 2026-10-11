# US-10R — checkpoint تعریف یوزر استوری (۲۰۲۶-۱۰-۱۱)

- activeTaskId: US-10R.PLAN؛ درخواست مالک ایجاد یوزر استوری مستقل و تسک‌های ریفکتور، با ممنوعیت تغییر ظاهر و رفتار.
- estimatedWorkScope/completionBudget: یک PR مستندات برای guide، CHANGELOG، project-current-state و همین checkpoint؛ ظرفیت برای تعریف، بررسی هدفمند، commit/PR و gateهای CI. اجرای T01 یا استخراج runtime جزو این PR نیست.
- مبنا: main `0a518bf6261f26a754fdfff6e290f5be763c0f54` پس از مرج PR #104؛ branch مستقل Codex `docs/us-10r-frontend-refactor-plan`. checkoutهای قبلی و فایل‌های محلی کاربر دست‌نخورده‌اند.
- سه قانون طلایی: مرحله‌بندی/بودجه رعایت شد؛ کل guide با blob `e1e719eda4cc7b999be5c495ad460253186b8b4c`، AGENTS و TASK_EXECUTION_PROTOCOL بازخوانی شدند؛ Done تنها پس از شواهد تست/مستندات/CI. تغییر برنامه بدون تغییر محصول.
- بررسی محدود: tree و محتوای main نشان می‌دهند LoanResultsScreen و LoanDetailsScreen پیش‌تر استخراج شده‌اند؛ چند صفحه، navigation و account flow هنوز در home page.jsx هستند. ساخت نسخه تکراری از featureهای موجود ممنوع است.
- محیط آزمون: playwright.config.mjs فقط Vite دارد؛ نام «e2e» اثبات API واقعی نیست. playwright.profile-live.config.mjs API و Vite را بالا می‌آورد؛ PostgreSQL/env/fixture لازم باید در T01 مطابق job مصوب آماده شود.
- معیار پذیرش این PR: شناسه یکتا، حضور US-10R بین US-10/11 در هر دو جدول، وابستگی US-11 و gate انتشار هماهنگ، چهار تسک و زیرتسک‌های کوچک، baseline مستقل از candidate، حفظ CSS cascade و React state identity، ممنوعیت تغییر API/DB/scoring و عدم اعلام اجرای T01.
- طرح تست این PR: انسجام ترتیب/شناسه/لینک‌ها، حفظ متن قوانین طلایی و T07/T081، diff allowlist، whitespace و scanner پروژه. suite runtime محلی برای تغییر مستندات تکرار نمی‌شود؛ چهار job موجود CI روی commit نهایی الزامی‌اند.
- actualScope: تعریف و اولویت یوزر استوری در guide و ثبت این checkpoint، وضعیت و CHANGELOG؛ هیچ runtime، CSS، تست مرورگر یا baseline تصویری تغییر/تولید نشده است.
- nextTaskId: US-10R.T01 پس از مرج PR برنامه؛ T02/T03 فقط پس از baseline معتبر T01 و هر زیرتسک پس از gate/مرج قبلی. US-11 پس از gate US-10R و دستور مربوط؛ US-09.T081 آنلاین/T07 همچنان بازند.
- زمان فعالیت‌ها از شروع ثبت شد؛ زمان قبل از راه‌اندازی timer (خواندن اولیه skill/کشف ابزار) جدا ثبت نشده است. گزارش تفکیکی، SHA و CI نهایی در PR ثبت می‌شوند تا برای درج CI یک push اضافی ایجاد نشود.
- پایان: بررسی‌های هدفمند و چهار CI، بدون merge/deploy. rollback فقط revert همین PR مستندات؛ دیتابیس تغییری ندارد.

