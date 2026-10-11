# مستندات عملیات شهاب

از [راهنمای عملیات و آموزش اپراتور — US-10.T05](operations-runbook.md) شروع کنید:
پیش‌نیاز، نمونه دستور، نقش هر مرحله، بازخوانی شواهد، retry، rollback و منع ویرایش
مستقیم دیتابیس را در یک مسیر توضیح می‌دهد.

- [قرارداد ابزار محافظت‌شده T04](protected-tool.md): authority/MFA، schema و DB role.
- [نقش‌ها T01](authorization.md) و [use caseها T02](data-use-cases.md).
- [audit دائمی T03](audit-runbook.md): شاهد append-only و rollback schema.
- [آماده‌سازی import](import-runbook.md): plan فقط، بدون انتشار مستقیم.
- [Docker محلی](docker-runbook.md) و [readiness داده](t05b-serving-readiness.md).
- [استقرار محیط پایدار](../runbook/production-deployment.md): gate مستقل T07 و URL واقعی.

CI موفق، provider پیکربندی‌شده، آموزش انسانی و deployment چهار نتیجه جدا هستند.
backup/restore rehearsal و hardening نهایی در US-11/US-12 تکمیل می‌شوند.
