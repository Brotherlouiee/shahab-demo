# Data-pipeline documentation

## US-05.T01 — raw ingest

منبع خام قبل از هر parser با SHA-256، نام اصلی، reference منبع، version اعلام‌شده، owner reference، زمان دریافت و byte count ثبت می‌شود. bytes با digest در raw store immutable و content-addressable نگهداری می‌شوند؛ ورود دوبارهٔ bytes یکسان object جدید یا overwrite ایجاد نمی‌کند.

`backend/app/data_pipeline/application/ingest_raw.py` فقط bytes را می‌پذیرد و metadata برمی‌گرداند. این مرحله parser، row، schema Excel، approval یا serving data تولید نمی‌کند. فایل‌های `.unitext` فقط پس از byte verification وارد این boundary می‌شوند.

filesystem adapter برای local/test است و فایل را با permission مالک و create انحصاری می‌نویسد. انتخاب object storage production، retention، access policy و persistence metadata در taskهای بعدی/operations انجام می‌شود.

## مراحل بعدی

staging validation، normalization، approval، publish، rollback و runbook import در ادامهٔ `US-05` ثبت می‌شوند.
