# Data-pipeline documentation

## US-05.T01 — raw ingest

منبع خام قبل از هر parser با SHA-256، نام اصلی، reference منبع، version اعلام‌شده، owner reference، زمان دریافت و byte count ثبت می‌شود. bytes با digest در raw store immutable و content-addressable نگهداری می‌شوند؛ ورود دوبارهٔ bytes یکسان object جدید یا overwrite ایجاد نمی‌کند.

`backend/app/data_pipeline/application/ingest_raw.py` فقط bytes را می‌پذیرد و metadata برمی‌گرداند. این مرحله parser، row، schema Excel، approval یا serving data تولید نمی‌کند. فایل‌های `.unitext` فقط پس از byte verification وارد این boundary می‌شوند.

filesystem adapter برای local/test است و فایل را با permission مالک و create انحصاری می‌نویسد. انتخاب object storage production، retention، access policy و persistence metadata در taskهای بعدی/operations انجام می‌شود.

## مراحل بعدی

## US-05.T02 — staging validation

`DelimitedStagingValidator` source bytes را بدون تغییر decode می‌کند و فقط چهار evidence قابل بازبینی می‌سازد: encoding ناسازگار، header نامطابق/تکراری، اختلاف تعداد ستون ردیف و hash منبع تکراری. نتیجهٔ دارای issue نباید به normalizer برسد. delimiter، encoding و headerهای مورد انتظار قرارداد صریح منبع هستند؛ هیچ حدس یا auto-repair وجود ندارد.

## US-05.T03 — normalization and category mapping

`backend/app/data_pipeline/domain/normalization.py` مرز مستقل و framework-free
بین staging معتبر و مرحله‌های approval/scoring است. این ماژول هر هشت متغیر
مجاز قرارداد را به `NormalizedVariable` تبدیل می‌کند، اما امتیاز، انتشار
catalogue یا تصمیم پیشنهاد تولید نمی‌کند.

قواعد فقط از `.agents/documents/ماتریس گزینه های متغیرهای وام.unitext`
(نمای Markdown همان ماتریس) آمده‌اند. مرز مشترک دو ردیف مجاور به ردیف اول
تعلق دارد؛ این tie-break در test ثبت شده است. فاصله‌های صریح ماتریس، مقدار
بزرگ‌تر از سقف ۳۵ میلیارد تومان، range/prose، و برچسب متن آزاد هرگز حدس
نمی‌شوند. آن‌ها به ترتیب با `unmapped` یا `unparseable` ثبت می‌شوند.

خروجی‌های `unknown`، `variable`، `unparseable` و `unmapped` category
ندارند. سیاست neutral برای سه ویژگی سپرده و exclusion برای چهار ویژگی محوری
در مرحله scoring بعدی اعمال می‌شود؛ این normalizer آن سیاست را دور نمی‌زند.

approval، publish، rollback و runbook import در ادامهٔ `US-05` ثبت می‌شوند.

## US-05.T04 — approval and serving version

Canonical-row construction, typed rejection evidence, draft diff, named approval
and atomic serving-pointer publication are now isolated in domain/application
modules. The durable PostgreSQL adapter, import command and rollback operation
remain intentionally deferred; the in-memory adapter is only test/local evidence.
See `docs/data-pipeline/pipeline.md` and ADR 0005 for the state contract.

## US-05.T05 — prepared import command and operations runbook

The internal manifest command validates a narrow, reviewed hand-off into
canonical rows and emits a non-publishing plan with typed issue evidence. It
cannot move the serving pointer. The exact invocation, exit codes, review path
and recovery rules are in `docs/operations/import-runbook.md`.

## US-09.T05A — official source materialization

`build_t05a_import_manifest.py` و `build_t05a_recommendation_config.py` از بایت‌های UTF-16 تأییدشده manifest قطعی می‌سازند. D-005 وزن پرسش/پاسخ را فقط از جدول تبدیل پاسخ‌ها می‌گیرد؛ عدد ماتریس نگاشت در پیکربندی وارد نمی‌شود. ماتریس مستقل ضرایب تناسب یک‌به‌یک ۷۲۰ سلول سازگاری را تأمین می‌کند. `materialize_official_sources` پس از تأیید اپراتور، در یک transaction نسخهٔ config، ۱۰۲ loan version، ۸۱۶ assignment، شروط و active catalogue را ذخیره می‌کند؛ hash محتوای manifest هم قفل شده است. فرمان و حدود ممیزی دیتابیس در `docs/operations/t05a-materialization.md` است. آداپتور خواندن مصرف‌کننده در T05B ساخته می‌شود.
