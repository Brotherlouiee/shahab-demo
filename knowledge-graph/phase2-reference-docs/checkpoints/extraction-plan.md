# برنامهٔ استخراج معنایی کامل دو سند مرجع

**وضعیت:** آمادهٔ اجرا؛ استخراج انبوه شروع نشده است. آزمون delegation محدود موفق شد.

## خط مبنای منابع

- `docs/SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` — 2,550 خط، 196 عنوان، SHA-256 `0709c84fe9e47e1d9218c6d0f93a82c89a62d6b234565e9b0ca2d4158759f266`
- `docs/SHAHAB_DIGITAL_WALLET.md` — 1,780 خط، 130 عنوان، SHA-256 `8b8d139b64f25f8f9592f936c070ece37b3e97df55d4e6b1d0cf305933960b74`

مجموع **4,330 خط** در **22 قطعه**؛ مرزها پیوسته‌اند، هم‌پوشانی یا شکاف ندارند.

## روش اجرا و ادامه پس از وقفه

- هر قطعه یک بازهٔ خطی پیوسته است که مرز آن از ابتدای عنوان Markdown انتخاب می‌شود. هدف ۲۰۰ خط و سقف ۲۶۰ خط است؛ هیچ متن بند، ردیف جدول یا عنوانی حذف نمی‌شود.
- هر عامل فقط برش مشخص‌شده را می‌خواند و از extraction-spec Graphify پیروی می‌کند. برای هر گره و رابطه: فایل، خط شاهد، نقل‌قول واقعی، رابطه، درجه اطمینان، وضعیت مصوبه و مالک ثبت می‌شود. موارد استنباطی مصوبه تلقی نمی‌شوند؛ مالک نامشخص صریحاً null می‌ماند.
- هر خروجی اول در `chunks/GSEM-NNN.json` ذخیره و از نظر JSON، خواندن کل بازه، تطبیق نقل‌قول/خط، یکتایی ID، endpointها، status/owner و برچسب EXTRACTED/INFERRED/AMBIGUOUS اعتبارسنجی می‌شود. فقط خروجی PASS وارد پیش‌نمایش ادغام می‌شود.
- `progress.json` checkpoint مرجع است. پیش از ادامه hash هر دو منبع تطبیق داده شود. پس از هر قطعه، وضعیت آن با نوشتن موقت و rename اتمی ثبت شود. پس از وقفه، فقط قطعات ناقص دوباره اجرا شوند؛ خروجی‌های PASS حفظ می‌شوند.
- در پایان، پوشش همهٔ خطوط، جدول‌ها و عنوان‌ها با manifest سنجیده؛ duplicateها و تعارض‌ها بازبینی؛ سپس query/path/explain و dangling endpoints آزمون می‌شوند. COMPLETE فقط پس از این گیت‌ها مجاز است.

## قطعات

| ID | منبع | بازهٔ خط | تعداد خط | وضعیت |
|---|---|---:|---:|---|
| GSEM-001 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 1–197 | 197 | NOT_STARTED |
| GSEM-002 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 198–398 | 201 | NOT_STARTED |
| GSEM-003 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 399–595 | 197 | NOT_STARTED |
| GSEM-004 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 596–795 | 200 | NOT_STARTED |
| GSEM-005 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 796–998 | 203 | NOT_STARTED |
| GSEM-006 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 999–1189 | 191 | NOT_STARTED |
| GSEM-007 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 1190–1392 | 203 | NOT_STARTED |
| GSEM-008 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 1393–1583 | 191 | NOT_STARTED |
| GSEM-009 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 1584–1773 | 190 | NOT_STARTED |
| GSEM-010 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 1774–1959 | 186 | NOT_STARTED |
| GSEM-011 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 1960–2155 | 196 | NOT_STARTED |
| GSEM-012 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 2156–2345 | 190 | NOT_STARTED |
| GSEM-013 | `SHAHAB_PHASE_2_DEVELOPMENT_BLUEPRINT.md` | 2346–2550 | 205 | NOT_STARTED |
| GSEM-014 | `SHAHAB_DIGITAL_WALLET.md` | 1–201 | 201 | NOT_STARTED |
| GSEM-015 | `SHAHAB_DIGITAL_WALLET.md` | 202–398 | 197 | NOT_STARTED |
| GSEM-016 | `SHAHAB_DIGITAL_WALLET.md` | 399–603 | 205 | NOT_STARTED |
| GSEM-017 | `SHAHAB_DIGITAL_WALLET.md` | 604–808 | 205 | NOT_STARTED |
| GSEM-018 | `SHAHAB_DIGITAL_WALLET.md` | 809–998 | 190 | NOT_STARTED |
| GSEM-019 | `SHAHAB_DIGITAL_WALLET.md` | 999–1192 | 194 | NOT_STARTED |
| GSEM-020 | `SHAHAB_DIGITAL_WALLET.md` | 1193–1398 | 206 | NOT_STARTED |
| GSEM-021 | `SHAHAB_DIGITAL_WALLET.md` | 1399–1612 | 214 | NOT_STARTED |
| GSEM-022 | `SHAHAB_DIGITAL_WALLET.md` | 1613–1780 | 168 | NOT_STARTED |
