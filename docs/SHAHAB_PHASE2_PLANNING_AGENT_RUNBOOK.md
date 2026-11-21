# راهنمای ثابت عامل برای برنامه‌ریزی فاز دوم شهاب
> SHAHAB Phase 2 Planning Agent Runbook — v1.0 (2026-11-21)

## دامنه و تقدم قواعد
این راهنما برای مأموریت‌های تدوین بسته‌های برنامه یکپارچه فاز دوم در PR #251 است؛ مکمل `AGENTS.md`، `docs/TASK_EXECUTION_PROTOCOL.md`، راهنمای جامع و مهارت Git امن است و هیچ قاعده یا گیت مصوبی را لغو نمی‌کند. دستور صریح مالک و منابع مصوب مقدم‌اند. **این راهنما مجوز اجرای کد محصول، merge، deploy یا force-push نیست.**

## نقشه ثابت پروژه
- Repository: `Brotherlouiee/shahab-demo`
- PR تجمیعی: https://github.com/Brotherlouiee/shahab-demo/pull/251 — باید Open/Draft بماند
- Head branch: `docs/phase2-unified-implementation-plan`؛ base: `main`
- سند واحد: `docs/SHAHAB_PHASE_2_IMPLEMENTATION_PLAN.md`
- منابع: `docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` و `docs/SHAHAB_DIGITAL_WALLET.md`
- قواعد: `AGENTS.md`، `docs/TASK_EXECUTION_PROTOCOL.md`، `docs/SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md`، `.agents/skills/safe-git-ide-collaboration/SKILL.md`
- Graphify: مسیر واقعی را **از Git Tree** با جست‌وجوی `GRAPH_REPORT.md`، `graph.json`، `CORE_REGISTRY.jsonl` و `validation.json` کشف کن؛ مسیر حدسی را حقیقت فرض نکن.
- CI: PR #253 طبقه‌بندی docs-only را اصلاح کرده؛ نسخه جاری `main` و `scripts/ci/classify_changes.py` را بررسی کن.

## گیت صفر: Bootstrap قبل از تحلیل یا تغییر
1. ابزارهای محلی و اتصال GitHub را شناسایی کن. نداشتن credential در Git CLI به معنی نداشتن دسترسی GitHub API نیست.
2. PR #251، HEAD واقعی، Draft بودن، base و رجیستری ۳۶ واحد مستقل را بخوان. شمارنده، عنوان و وضعیت بسته‌ها را از رجیستری استخراج کن؛ زیربسته‌های a/b واحد مستقل‌اند.
3. Root واقعی repo را پیدا کن؛ پوشه پیوست یا scratch لزوماً مخزن نیست. Worktree/cloneهای Dirty یا متعلق به دیگری را دست‌نخورده بگذار؛ در صورت نیاز محیط ایزوله بساز.
4. `AGENTS.md` و منابع حاکم را طبق الزام خودشان بخوان؛ مطالعه اسناد حجیم را با ابزار مناسب و به‌طور کامل انجام بده، نه از خلاصه یا خروجی بریده‌شده.
5. گراف و ledger را در Git Tree جست‌وجو و هش‌های منبع را با Graph Report مقایسه کن. شکست اولین جست‌وجو دلیل غیبت گراف نیست.
6. **پیش از اولین ویرایش، مسیر امن انتشار را احراز کن.** اول Git CLI با احراز هویت معتبر؛ اگر موجود نبود، GitHub Contents API برای فایل‌های متنی کوچک، یا Git Data API فقط با base tree معتبر و کنترل قبل از update_ref. عملیات آزمایشی مخرب یا Commit آزمایشی ممنوع.
7. Checkpoint کوتاه ثبت کن: HEAD، مسیر واقعی منابع، وضعیت گراف، دامنه دو بسته، مالکیت شاخه، روش انتشار، آزمون‌های مستنداتی و زمان شروع.

اگر یک پیش‌شرط حیاتی احراز نشد، مسیر نامطمئن را تکرار نکن؛ دلیل و مسیر جایگزین امن را مشخص کن.

## کشف و تدوین
- Graph-First مشترک + جست‌وجوی تکمیلی متنی؛ متن مصوب مرجع نهایی است. روابط INFERRED/AMBIGUOUS بدون تأیید منبع، Requirement قطعی نیستند.
- پیش از Task، رجیستری منطقی مشترک Candidateها، مالک رفتار/داده/قرارداد و Handoffها را تثبیت کن؛ هیچ Candidate یا Requirement را کپی نکن.
- هر بسته: Requirement اتمی → Story/Enabler → Task/Subtask → AC/Test/Test Case با ردیابی دوسویه؛ RA و IPA مستقل.
- CPA-01..08 پس از تدوین هر دو بسته و **قبل از نخستین Push**؛ نقص‌ها را اصلاح و گیت‌های متأثر را تکرار کن.
- شمارنده‌ها و جدول وضعیت باید با واحدهای مستقل رجیستری برابر باشند؛ تصمیم باز را تصویب‌شده فرض نکن.
- سنجش زمان و بازکاری را از شروع واقعی ثبت کن؛ داده ناموجود = `NOT_MEASURED`.

## گیت یک: صحت فایل حجیم
سند برنامه حجیم است؛ خروجی خالی `fetch_file` یا متن کوتاه‌شده را نبود فایل یا نسخه کامل تلقی نکن.
- قبل از نوشتن، فایل کامل را در محیط محلی/Blob معتبر دریافت کن؛ طول بایتی، تعداد خطوط و SHA-256 را ثبت کن.
- متن بریده‌شده، خروجی محدود ابزار یا قطعه‌های ناقص را برای جایگزینی سند نفرست.
- اگر انتقال chunk لازم شد، ترتیب، تعداد، اندازه و هش بازترکیب را پیش از نوشتن تأیید کن.
- پس از انتشار، Blob کامل ریموت را بازخوانی و طول بایتی و SHA-256 را با نسخه نهایی محلی مقایسه کن.
- موفقیت پاسخ API به‌تنهایی اثبات صحت محتوا نیست؛ اختلاف هش = FAIL.

## گیت دو: صحت Tree و انتشار اتمی
- مسیر ترجیحی: Git در Worktree ایزوله، `git diff --check`، بررسی دقیق `git diff --name-status` و `git diff`، stage فقط فایل مجاز، Commitهای مستقل محلی، سپس یک Push.
- در GitHub Git Data API، `create_tree` **حتماً** باید `base_tree_sha` واقعی Tree والد داشته باشد. ساخت Tree از صفر برای تغییر یک فایل موجود ممنوع است.
- قبل از `update_ref`، Diff Commit پیشنهادی با Parent را بررسی کن؛ فقط فایل‌های مجاز مأموریت باید تغییر کنند. Tree ناقص یا حذف فایل غیرمرتبط = FAIL و **ممنوعیت Update Ref**.
- `update_ref` فقط fast-forward و با `expected_sha` برابر HEAD خوانده‌شده در لحظه انتشار؛ در تعارض، توقف و بازخوانی، نه force-push.
- برای سند بزرگ اگر Git CLI قابل Push نیست و Git Data API نمی‌تواند base tree/Blob کامل را تضمین کند، انتشار نکن؛ خروجی محلی و مانع را گزارش کن.
- هدف عادی مأموریت دوبسته‌ای: دو Commit محتوایی و یک Push؛ این هدف نباید باعث حذف ممیزی یا پنهان‌کردن اصلاح ضروری شود.
- هر خطای یکسان را حداکثر دوبار با شواهد و تغییر راهبرد بررسی کن؛ ده‌ها فراخوانی ترمیمی برای یک سند، راهکار عادی نیست.

## گیت سه: Docs-only و CI
- برای تغییر فقط سند برنامه، اجرای Build/Run/Test محصول، PostgreSQL migration، Redis، Docker، Image scan، Trivy image، Browser/E2E و Deploy توسط عامل ممنوع است.
- کنترل‌های سبک اسناد، Markdown، لینک، whitespace، شناسه‌ها، ردیابی و secret scan را اجرا کن؛ کنترل امنیتی را برای سبزکردن CI حذف نکن.
- پس از Push، CI را بر اساس **HEAD نهایی** بررسی کن؛ Jobهای سنگین باید `SKIPPED` یا `NOT_TRIGGERED` باشند. اجرای خودکار خلاف انتظار را گزارش کن؛ rerun دستی نکن.

## ترتیب اجباری و تعریف Done
**Discover once → Verify sources → Complete both packages → Independent RA/IPA → CPA → Registry/Document validation → File/Tree preflight → Publish once → Verify remote and CI.**

گیت‌های نهایی: هویت repo/PR، منابع و گراف، RA/IPA هر بسته، CPA 8/8، رجیستری، هش فایل کامل، سلامت Tree، فقط فایل‌های مجاز، fast-forward، PR Open/Draft و CI docs-only. هر گیت مسدودکننده FAIL شد، COMPLETE اعلام نکن.

گزارش نهایی: دو بسته و شمارنده، Candidate/Requirement/Task/AC/Test، RA/IPA/CPA، زمان واقعی یا NOT_MEASURED، مسیر انتشار، SHA/طول فایل، تعداد Commitهای **همین مأموریت**، فایل‌های Diff، HEAD و CI؛ هر Commit اصلاحی و علت آن را شفاف ثبت کن.
