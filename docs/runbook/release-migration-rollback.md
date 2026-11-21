# ترتیب migration و طرح rollback/restore — US-12.T04

**طرح آماده‌سازی، نه دستور اجرای همین تسک.** مبنا `c17366f3bae710f58fa24ff0aa78ee192d68f5eb`؛ هیچ migration یا restore در T04 مستقل اجرا نمی‌شود. اجرای واقعی فقط روی محیط مشخص و مجاز، طبق T081/T07 و گیت‌های US-11.T05/US-12 انجام می‌شود. [runbook استقرار](production-deployment.md)، [migration](../database/migrations-and-rollback.md)، [هویت](../database/account-identity-migration-runbook.md) و [عملیات داده](../operations/operations-runbook.md) مرجع اجرا هستند؛ ابزار یا pipeline دوم نداریم.

## ۱. قرارداد نسخه و پیش‌پرواز

مسئول محیط، اپراتور و بازبین باید SHA پذیرفته‌شدهٔ backend/frontend، digest artifactها، revision واقعی DB، data/config version فعال، source digest، محیط/بازه/هدف و مجوز را ثبت کنند. metadata خصوصی backup و credential خارج Git باشد. کد قدیمیِ دارای نقص proof/مالکیت یا reader phone-only صرفاً چون زمانی روی main بوده گزینهٔ امن rollback نیست.

پیش از mutation، backup رمزنگاری‌شدهٔ سازگار و restore آزموده در DB ایزوله، ظرفیت/lock window و role جداگانهٔ migration لازم است. writers شامل تمام workerهای API، ابزار publication و scheduler/cleanup متوقف/فنس شوند؛ rollout ترکیبی reader قدیمی/جدیدِ ناسازگار ممنوع. نرخ/ظرفیت و RPO/RTO عدد حدسی نمی‌گیرند؛ با تصمیم مالک و اندازه‌گیری محیط تعیین شوند. نبود backup/نسخه/مجوز روشن → توقف.

از artifact همان SHA و private environment با نقش مجاز، فرمان‌های بررسی موجود:

```sh
python -m alembic heads
python -m alembic history
python -m alembic current
```

دو فرمان اول زنجیرهٔ artifact را می‌خوانند؛ current به DB منتخب وصل می‌شود. credential/DSN را در argv یا history ننویسید و log را پیش از اشتراک پالایش کنید. در مبنای این سند فقط یک head، `ff11b02f0001`، وجود دارد. head/revision خارج زنجیره، چند head یا DB نامعلوم نیازمند بررسی است؛ stamp یا دست‌کاری ledger راه رفع نیست. نبود ledger تنها در DB تازه و خالیِ صریحاً تأییدشده پذیرفته شود.

## ۲. زنجیرهٔ واقعی هجده migration در مبنا

جدول از revision/down_revision فایل‌های فعلی آمده است؛ ترتیب لغوی نام فایل معیار اجرا نیست. این inventory مجوز downgrade نیست و پس از تغییر migrationها باید دوباره تطبیق داده شود.

| ترتیب | revision | parent |
| --- | --- | --- |
| ۱ | `f0d0c68db55a` | `base` |
| ۲ | `4376ef397102` | `f0d0c68db55a` |
| ۳ | `7b3f2f4a9c10` | `4376ef397102` |
| ۴ | `91d5a005a01a` | `7b3f2f4a9c10` |
| ۵ | `a62c0b5b005b` | `91d5a005a01a` |
| ۶ | `c90f0d6e1a2b` | `a62c0b5b005b` |
| ۷ | `b6f2c0a9d4e7` | `c90f0d6e1a2b` |
| ۸ | `e8a5c7d2f4b1` | `b6f2c0a9d4e7` |
| ۹ | `d1a9e71b4c3f` | `e8a5c7d2f4b1` |
| ۱۰ | `e4c7b9a1d2f3` | `d1a9e71b4c3f` |
| ۱۱ | `f1a2b3c4d5e6` | `e4c7b9a1d2f3` |
| ۱۲ | `a3b7c9d1e2f4` | `f1a2b3c4d5e6` |
| ۱۳ | `b4d8e1f2a3c5` | `a3b7c9d1e2f4` |
| ۱۴ | `aa11b02a2001` | `b4d8e1f2a3c5` |
| ۱۵ | `aa11b02a2002` | `aa11b02a2001` |
| ۱۶ | `bb11b02b0001` | `aa11b02a2002` |
| ۱۷ | `cc11b02c0001` | `bb11b02b0001` |
| ۱۸ | `ff11b02f0001` | `cc11b02c0001` |

## ۳. ترتیب اعمال پس از مجوز محیط

اگر DB همین head را دارد migration را تکرار/بازنویسی نکنید؛ به audit سازگاری و smoke بروید. برای DB در ancestor مصوب، فقط مسیر باقی‌مانده اجرا شود. برای عبور از مرز هویت، با writers متوقف و backup/restore معتبر، مرحلهٔ expand و backfill مستقل را طبق runbook هویت از قلم نیندازید:

```sh
python -m alembic upgrade aa11b02a2001
python -m scripts.backfill_account_identity
```

دستور دوم dry-run/count است و صحت کامل backfill را ثابت نمی‌کند. تنها پس از بررسی داده و مجوز تغییر:

```sh
python -m scripts.backfill_account_identity --apply
python -m alembic upgrade aa11b02a2002
python -m alembic upgrade ff11b02f0001
```

این بلوک فقط وقتی current قبل/روی expand هویت است کاربرد دارد؛ برای DB بعد از contract هرگز upgrade به ancestor را اجرا نکنید. در DB بعد از contract فقط upgrade تا target مصوب کافی است. هدف pinned بالا متعلق به مبناست، نه دستور استفادهٔ دائمی؛ در release آینده با زنجیره و SHA واقعی تطبیق داده شود. backfill باید mapping/count/lineage را حفظ کند؛ owner متفاوت، orphan یا phone نامعتبر blocker است، نه مجوز normalize/merge حدسی.

پس از migration، head و قیود/countهای لازم با قبل مقایسه و همه backend workerهای نسخهٔ سازگار راه‌اندازی شوند. nullable proof قدیمی مجوز ندارد و پرسشنامهٔ legacy ممکن است به شروع تازه نیاز داشته باشد؛ snapshot حساب نباید حذف شود. API و frontend باید در ماتریس نسخه/schema/data سازگار باشند؛ manifest خالی این سازگاری را اثبات نمی‌کند.

publication/seed از schema جداست: ابتدا audit فقط‌خواندنی `python -m scripts.materialize_t05a`؛ اگر catalogue تأییدشده موجود است reuse شود. فقط شکاف مصوب با authority/MFA و ابزار عملیات import→review→prepare→approve→publish رفع شود؛ `materialize_t05a --publish`، UPDATE دستی یا fixture CI جای این مسیر نیست. سپس audit همان DB، versionها، conditions/categoryها و smoke [T03](preview-smoke.md)؛ سلامت process جای این شاهد نیست.

شکست migration: writers بسته بمانند، revision/schema واقعی پس از rollback تراکنش بررسی شود؛ خروج نامعلوم/timeout به معنی عدم commit نیست. اجرای کور دوباره، downgrade عمومی، reset volume یا تعمیر SQL ممنوع؛ اصلاح بازبینی‌شدهٔ roll-forward یا restore مجاز انتخاب شود. حجم/زمان قفل واقعی روی staging اندازه‌گیری شود، نه از CI تعمیم داده شود.

## ۴. انتخاب بازگشت

| نوع رخداد | مسیر و شرط ایمنی |
| --- | --- |
| فقط کد/فرانت/config، بدون تغییر DB/serving | artifact قبلی با SHA/digest ثبت‌شده تنها پس از اثبات سازگاری با schema، داده و قرارداد امنیتی فعلی؛ API و frontend به‌صورت جفت سازگار و smoke مجدد. حفظ schema معمولاً از downgrade امن‌تر است؛ صرف tag قدیمی کافی نیست. |
| schema تغییر کرده | اول roll-forward یا binary سازگار با schema فعلی؛ downgrade فقط در برنامهٔ مستقل، با backup، writers متوقف و اثبات lossless. guard migration دور زده نشود. CI downgrade روی DB disposable مجوز عملیات واقعی نیست. |
| انتشار داخلی داده نتیجهٔ نامعلوم دارد | head/audit/catalogue را با read-only بازخوانی کنید؛ publish را کور retry نکنید. rollback ابزار فقط target superseded قبلاً approved و expected-current درست را می‌پذیرد. |
| منبع/config نامعتبر | CLI فعلی rollback عمومی میان منبع/configهای دلخواه نیست؛ برای بازبینی‌های همان منبع/config projection مشترک دارد. توقف writers و تصمیم داده/نسخه یا restore مستقل لازم است؛ جعل hash یا ویرایش serving ممنوع. |
| backup/restore لازم است | فقط DB جدید و ایزوله؛ حفظ اصل آسیب‌دیده برای شواهد، آشتی‌دادن status/revocation پس از backup، purge و گیت پیش از reopen در بند۵. هیچ promotion خودکار نیست. |
| provider/secret مشکوک | incident و rotation/revocation طبق runbook مربوط؛ live OTP خاموش می‌تواند ورود تازه را مسدود کند، اما نشست‌ها را خودکار revoke نمی‌کند. key جدید یا rotate راز OTP جای ابطال نشست نیست. |

**guardهای مشخص:** bookmarks غیرخالی در `ff11b02f0001` downgrade را رد می‌کند؛ contract هویت `aa11b02a2002` چند نسل، status غیرactive یا profile مفقود را رد می‌کند. downgrade proof امنیت F01 را برمی‌گرداند؛ binary ناامن نباید public reopen شود. downgrade نشست مشترک، credentials/challenges را از بین می‌برد و TTL/سیاست binary قدیمی با قرارداد یک‌ساعته برابر نیست. downgrade audit شواهد را حذف می‌کند. حذف status/association/audit برای عبور از guard و downgrade base برای محیط محصول ممنوع؛ base تنها fixture آزمایشی disposable است.

## ۵. طرح rehearsal بازیابی و شرط بازگشایی

این مراحل **اجرا نشده‌اند**. هماهنگ با [checkpoint US-11.T05](../progress/us-11-t05.md) و [سیاست نشست](../security/account-session-lifecycle.md)، اپراتور باید در محیط مجاز:

1. snapshot point/UTC، سازگاری ابزار PostgreSQL16، backup رمزنگاری‌شده و کلید/KMS/ACL را بررسی کند؛ مقصد/راز و dump خام وارد Git یا CI artifact عمومی نشوند. RPO/RTO و retention باید مصوب باشند؛ نبود کلید یا restore موفق blocker است.
2. backup را فقط در PostgreSQL جداگانهٔ تازه provisionشده و غیرقابل دسترس کاربران restore کند. DB/volume مبدأ، local یا staging مشترک را drop/reset نکند. image/SHA و migration reader سازگار با backup انتخاب و وضعیت قبل/بعد ثبت شود.
3. revision، source/config/data و audit/head/catalogue، FK/owner/generation، counts پروفایل/history/items/reasons/bookmarks و active/archived، visible/hidden را تطبیق دهد؛ snapshotها rescoring نشوند. backup فقط وضعیت زمان خودش را دارد: archive/hide یا تغییر مالکیت بعد از snapshot باید با شواهد معتبر آشتی داده شوند؛ بدون آن‌ها عدم احیای دادهٔ خارج‌شده از دسترسی اثبات نشده و reopen ممنوع است.
4. **همه credential/OTPهای restoreشده پیش از reopen نامعتبر شوند**؛ logout/revoke بعد از backup ممکن است در آن نباشد. ابزار retention_tick فقط پاسخ خام را پاک می‌کند، نه تمام نشست/OTPها. مسیر عملیاتی سراسری invalidate/reconciliation در این task ساخته یا اجرا نشده؛ اجرا به روش محدود و بازبینی‌شدهٔ مستقل و تست عدم replay روی همه workerها نیاز دارد. عوض‌کردن API key، restart، clock دست‌کاری‌شده یا پاک‌کردن cookie جای این گیت نیست.
5. پاسخ‌های raw منقضی در ساعت DB پس از restore و قبل ترافیک طبق [runbook purge](../operations/raw-answer-retention.md) با role و مجوز مستقل پاک شوند. ابتدا dry-run؛ apply فقط روی مقصد restore تأییدشده. pending/backlog و خطا/lock بررسی و تا تخلیهٔ اثبات‌شده retry محدود شود؛ exit0 dry-run یا یک batch بدون processed، purge کامل را ثابت نمی‌کند. metadata مرتبط و snapshot/hidden/archive/owner/version حفظ شوند.
6. همه گیت‌های امنیت/proof/مالکیت/expiry، smoke API/مرورگر و restart روی مقصد بازسازی‌شده بررسی شوند؛ دسترسی حساب بایگانی و token قدیم رد، snapshot تاریخی بدون تغییر، TTLها تمدید نشوند. scheduler/monitor و هشدار واقعی طبق گیت سروری فعال و آزموده شوند؛ محدودیت OTP واقعی هم پابرجاست.
7. زمان واقعی backup/restore/اعتبارسنجی، RPO واقعی نسبت به نقطهٔ snapshot و RTO تا آمادگی، شمارش‌های غیرشخصی و نتیجهٔ هر مرحله ثبت شوند. تنها پس از تأیید مسئول مجاز، cutover و smoke post-deploy؛ اگر شکست خورد ترافیک بسته و محیط اصلی/شواهد حفظ شوند. هیچ موفقیت مشروط یا صرفاً CI، مجوز reopen نیست.

فرم [شواهد انتشار](../examples/release/release-evidence.json) را برای rehearsal در محل خصوصی عملیات کپی کنید؛ null/not-run یعنی ناتمام. شواهد امن، SHA/digest، نسخه‌ها، مسئول، UTC و محدودیت ثبت شوند؛ شماره، پاسخ، cookie، token، dump و آدرس کلیددار منتشر نشوند. این فرم به هیچ workflow/deploy متصل نیست و gate را خودکار اجرا یا تأیید نمی‌کند.

## ۶. تحویل مستقل و ادامه

T04 فقط release note/ترتیب/طرح را تکمیل می‌کند. rehearse آنلاین T04 و US-11.T05 در همان جدول پس از استقرار بازند؛ US-12.T05 فقط بعد از US-13، همه gateها و مجوز release است. rollback همین PR مستندات، revert پنج فایل آن است؛ هیچ اقدام runtime/DB لازم ندارد. قدم مستقل بعدی `US-12.T04A.1` است، بدون نشر خودکار image یا خرید سرور.
