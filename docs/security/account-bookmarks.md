# نشان‌شده‌های حساب — US-11.T02F

مالکیت از actor احراز‌شده سرور می‌آید، نه شماره، مرورگر یا payload. جدول
`account_bookmarks` فقط account/version، reference اختیاری snapshot، زمان ایجاد و
زمان پنهان‌سازی دارد؛ facts، پاسخ خام، نام و شماره را تکثیر نمی‌کند. PK مرکب
(account_id, loan_product_version_id) و FK مرکب snapshot/owner مانع تکرار و اتصال
به تاریخچه حساب دیگر هستند. reference نسخه پس از ایجاد قابل انتقال نیست.

PUT `/api/v1/bookmarks/{loan_id}` با `{}` یا `{"historyId":"UUID"}` و DELETE همان
مسیر desired state هستند؛ retry سطر تازه نمی‌سازد. GET مالک‌محور keyset pagination
دارد. فقط نسخه منتشرشده قابل نشان‌کردن است؛ خواندن association قدیمی همان نسخه
ثابت و context تاریخی را حفظ می‌کند و نسخه تازه را جایگزین آن نمی‌کند. حذف،
`removed_at` را تنظیم می‌کند؛ داده برای سیاست بایگانی باقی می‌ماند. حذف حساب UI
در این تسک اضافه نشده است. بازگشت خطا به معنی empty state یا موفقیت ذخیره نیست.

کلاینت پس از تأیید commit سرور کارت و toast را تغییر می‌دهد. فهرست در ورود به
صفحه، refresh و focus از DB خوانده می‌شود. دو دستگاه یک حساب داده مشترک دارند؛
نسل تازه همان شماره accountId تازه دارد و cache نسل قبلی را به ارث نمی‌برد.
پروفایل، فیلدهای فرم و نتیجه فقط در حافظه tab هستند. پاسخ async حساب قدیمی پس از
تعویض حساب قابل نمایش نیست. نتیجه فعلی historyId سروری دارد؛ refresh snapshot
را از API تاریخچه می‌خواند و scoring را تکرار نمی‌کند. history.state فقط شناسه‌های
opaque دارد و JSON نتیجه قدیمی را authority نمی‌داند.

نشان‌شده legacy در localStorage مالک قابل اثبات ندارد: نه نمایش داده می‌شود و نه
خودکار به حساب فعلی upload می‌شود. تا خروج صریح در دیسک قرنطینه باقی می‌ماند.
خروج فقط کلیدهای `shahab.*` و حافظه/entry فعلی شهاب را پاک می‌کند؛ داده برنامه‌های
دیگر پاک نمی‌شود. cookie حساب و proofهای questionnaire نیز در سرور حذف می‌شوند.
شکست revoke خطای صریح و pending flag غیرشخصی دارد و پیش از restore/login تازه
retry می‌شود؛ هرگز به عنوان خروج موفق گزارش نمی‌شود. BroadcastChannel فقط lifecycle
را منتقل می‌کند. اگر شبکه و storage هر دو unavailable باشند revoke سروری یا flag
پایدار تضمین‌پذیر نیست؛ TTL سرور مستقل باقی می‌ماند.

Browser API پاک‌کردن همه entryهای قدیمی stack را ممکن نمی‌کند. نسخه جدید داده شخصی
در entry نمی‌نویسد؛ entry فعلی در خروج پاک می‌شود و entry legacy بازنمایی نمی‌شود.
حذف فیزیکی stack ساخته‌شده قبل از F به بستن tab نیاز دارد؛ این محدودیت پنهان نشده است.

Migration افزایشی `ff11b02f0001` از `cc11b02c0001` است. روی دیتابیس واقعی فقط مالک
طبق runbook، پس از backup و بررسی head آن را اجرا می‌کند؛ این تسک DB کاربر را تغییر
نمی‌دهد. downgrade با داده نشان‌شده عمداً رد می‌شود تا بایگانی حذف نشود؛ rollback
با نسخه سازگار برنامه یا roll-forward انجام شود. آزمون empty downgrade تنها روی
DB disposable و داده synthetic اجرا می‌شود. هیچ reset/backfill حدسی مرورگر نداریم.

آزمون‌های API/client و PostgreSQL ownership، idempotency، خطای transaction، نسل
هم‌شماره، FK و index با ۲۰۰۲ association را پوشش می‌دهند. browser واقعی دو دستگاه،
خروج و cookie، Back و refresh را بررسی می‌کند. مقایسه مستقل main پیش از F با نسخه
جدید در دو viewport برای empty و کارت، هندسه و PNG را دقیق مقایسه می‌کند؛ baseline
از خود شاخه پیشنهادی ساخته نمی‌شود و tolerance/mask ندارد. CSS، assets و source
وام/پرسشنامه تغییر نکرده‌اند. برای جزئیات اجرای ثبت‌شده و CI سند
[checkpoint](../progress/us-11-t02f.md) و [quality gates](../testing/quality-gates.md) را ببینید.
