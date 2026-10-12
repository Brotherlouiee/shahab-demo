# ADR-0008: هویت مستقل و چرخهٔ عمر نسلی حساب

- وضعیت: Accepted به‌عنوان قرارداد طراحی A.1؛ اجرای schema/runtime در T02A.2 و مراحل بعد.
- تاریخ: ۲۰۲۶-۱۰-۱۲
- مالک تصمیم: محصول (PD01–PD08) و توسعه backend (قرارداد فنی)
- تسک: US-11.T02A.1؛ base main `2e63479ae5e1034a50e9386cc42e2c3846ed8c27`

## زمینه

phone کلید پروفایل فعلی و FK owner session/history است. تصمیم مالک می‌خواهد account
قدیمی با همه داده‌ها بایگانی و login همان phone حساب تازه بدون سوابق قبلی بسازد.
phone-PK قادر به نمایش دو دوره مستقل نیست و credential phone-only می‌تواند داده
نسل قدیم را به نسل جدید نشت دهد.

## تصمیم

[قرارداد و ERD هدف](../database/account-identity-lifecycle.md) مرجع ستون/cardinality/
constraint و lifecycle است: accounts با UUID immutable، phone canonical immutable،
status active/archived و timestamp؛ partial unique active phone؛ profile 1:1 و
owner FKهای account. account archived احیا نمی‌شود و duplicate archive table
ساخته نمی‌شود. raw retention از durable snapshot مستقل و PD01–PD08 حفظ می‌شوند.
این ADR مجوز اجرا/استقرار/پایان رفع تهدیدها نیست.

## گزینه‌های بررسی‌شده

| گزینه | نتیجه و دلیل |
| --- | --- |
| حفظ phone-PK و فقط افزودن status | رد؛ account تازه با همان شماره، ID/روابط مستقل ندارد و stale credential ambiguity می‌ماند. |
| انتقال همه داده به archive tables موازی | رد؛ کپی graph و snapshot/FK و schema دوگانه بدون نیاز، ریسک orphan/restore/analytics و پیچیدگی آینده. |
| UUID حساب و UNIQUE(phone) سراسری | رد؛ نسل بایگانی و تازه یک phone را نمی‌توان نگه داشت. |
| UUID حساب و partial unique active phone، همان profile/history | پذیرفته؛ مدل ساده 3NF و DB integrity با دوره‌های مستقل، بدون انتقال فیزیکی گراف. |

## پیامدها و امنیت

API phone موجود می‌تواند در response از account join تأمین شود؛ public UI تغییر
نمی‌کند. actor داخلی، token و همه owner queryها باید account-bound شوند؛ حتی
capability قدیمی نباید با phone به active تازه resolve شود. permission اپراتور
مستقل است. archive و hide نگهداری/نمایش را جدا می‌کنند، نه erasure قانونی.
snapshot denormalized موجود طبق ADR-0011 یک شاهد immutable است، نه profile جدید.

## اعتبارسنجی و rollback

AC01–AC16 قرارداد، شامل concurrent login/archive، owner-composite FK، fixture
legacy/count preservation و guard downgrade طرح آزمون مراحل آینده‌اند. A.2 باید
migration افزایشی، backfill mapping idempotent و cutover adapter را روی PG واقعی
اثبات کند؛ G پیش از تکمیل owner/legacy credential cutover فعال نشود. پس از چند
نسل، downgrade phone-PK غیر lossless باید guard/refusal داشته باشد؛ roll-forward
بدون حذف archive. A.1 فقط اسناد و revert بدون اثر داده است.

## منابع

- [policy/task guide](../SHAHAB_PROJECT_DEVELOPMENT_CANONICAL_GUIDE.md)
- [profile ADR فعلی](../architecture/0010-profile-access-and-persistence.md)
- [history ADR فعلی](../architecture/0011-recommendation-history.md)
- [privacy/retention review](../security/privacy-retention-review.md)
