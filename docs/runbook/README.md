# Runbookهای عملیاتی

- [استقرار محیط پایدار](production-deployment.md): PostgreSQL دائمی، FastAPI HTTPS، Netlify، publication تأییدشده، آزمون URL واقعی و rollback.
- [عملیات Docker محلی](../operations/docker-runbook.md): فقط محیط توسعه؛ جایگزین runbook استقرار نیست.
- [ورود/انتشار دادهٔ T05A](../operations/t05a-materialization.md): audit و publication کاتالوگ تأییدشده.
- [آمادگی serving T05B](../operations/t05b-serving-readiness.md): backfill و قرارداد خواندن دادهٔ منتشرشده.

هیچ runbookی مجوز قرار دادن secret، credential یا دادهٔ شخصی در Git نیست.
