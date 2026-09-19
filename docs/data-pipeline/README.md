# Data-pipeline documentation

## US-05.T01 — raw ingest

منبع خام قبل از هر parser با SHA-256، نام اصلی، reference منبع، version اعلام‌شده، owner reference، زمان دریافت و byte count ثبت می‌شود. bytes با digest در raw store immutable و content-addressable نگهداری می‌شوند؛ ورود دوبارهٔ bytes یکسان object جدید یا overwrite ایجاد نمی‌کند.

`backend/app/data_pipeline/application/ingest_raw.py` فقط bytes را می‌پذیرد و metadata برمی‌گرداند. این مرحله parser، row، schema Excel، approval یا serving data تولید نمی‌کند. فایل‌های `.unitext` فقط پس از byte verification وارد این boundary می‌شوند.

filesystem adapter برای local/test است و فایل را با permission مالک و create انحصاری می‌نویسد. انتخاب object storage production، retention، access policy و persistence metadata در taskهای بعدی/operations انجام می‌شود.

## مراحل بعدی

## US-05.T02 — staging validation

`DelimitedStagingValidator` source bytes را بدون تغییر decode می‌کند و فقط چهار evidence قابل بازبینی می‌سازد: encoding ناسازگار، header نامطابق/تکراری، اختلاف تعداد ستون ردیف و hash منبع تکراری. نتیجهٔ دارای issue نباید به normalizer برسد. delimiter، encoding و headerهای مورد انتظار قرارداد صریح منبع هستند؛ هیچ حدس یا auto-repair وجود ندارد.

normalization، category mapping، approval، publish، rollback و runbook import در ادامهٔ `US-05` ثبت می‌شوند.
