# US-12.T04A.3 — انتشار دو image مصوب

این مسیر پیاده‌سازی انتشار است، نه شاهد انجام انتشار. تا ثبت دو digest واقعی و `status: complete` در artifact، A.3 باز است. به VPS، Docker لپ‌تاپ یا روشن‌بودن runner قبلی نیاز ندارد. A.4 (pull/smoke/rollback) و deploy جدا هستند.

## پیش‌نیاز مالک

1. namespace واقعی Docker Hub را مشخص کن؛ نام GitHub به‌جای آن حدس زده نمی‌شود. نام دو repository تأییدشده `shahab-api` و `shahab-frontend` است. مالک هر دو را در namespace خود ایجاد و visibility آن‌ها را تعیین کند؛ workflow repository یا حساب ایجاد نمی‌کند.
2. در Settings → General → Tag mutability هر دو repository، Specific tags immutable را با **همین regex** فعال کن:

   ```text
   ^(v[0-9]+\.[0-9]+\.[0-9]+|sha-[0-9a-f]{40})$
   ```

   همهٔ چهار tag باید پیش از شروع غایب باشند. کنترل سمت registry جلوی race بازنویسی را می‌گیرد. اگر قابلیت/دسترسی آن در حساب موجود نباشد، انتشار blocked است؛ policy خودکار شل نمی‌شود.
3. در GitHub → Settings → Environments محیط `dockerhub-publish` را بساز: تنها required reviewer، مالک repository؛ Deployment branches and tags → Selected branches and tags → فقط branch `main`. مالکِ تنها می‌تواند اجرای خودش را تأیید کند؛ Prevent self-review را برای این حالت فعال نکن. workflow تنظیم محیط را دوباره از API می‌خواند؛ نبود approval معتبر یا دسترسی خواندن config خطاست.
4. در **همین Environment** متغیر `DOCKERHUB_NAMESPACE` و دو Secret با نام‌های `DOCKERHUB_USERNAME` و `DOCKERHUB_TOKEN` قرار بده. PAT با Read/Write، بدون Delete و با کمترین دسترسی قابل‌اعطا به همین دو repo استفاده شود؛ اگر طرح حساب محدودیت repo ندارد، حساب اختصاصی نشر با دسترسی محدود لازم است. از password حساب استفاده نکن. token در چت/فایل/متغیر عمومی قرار نمی‌گیرد. ابزار GitHub این جلسه مدیریت secrets ندارد؛ ورود مقدار محرمانه توسط مالک انجام می‌شود.
5. پس از merge پیاده‌سازی، هفت job روی **همان commit از main** باید موفق باشند. مالک version جدید `vX.Y.Z` و SHA کامل آن را تصویب و tag را ایجاد کند؛ هیچ workflow اینجا tag یا release نمی‌سازد. tag باید به همان commit در تاریخچه main اشاره کند. نام نسخه از طرف عامل حدس زده نمی‌شود.
6. یافته‌های MEDIUM/LOW همان نسخه را از `container-build-contract-evidence/images/{api,web}-scan.json` بررسی کن. برای هر یافته تصمیم مستقل با مالک، mitigation و deadline لازم است. پذیرش A.2 یا یک SHA دیگر خودکار منتقل نمی‌شود. HIGH/CRITICAL یا severity ناشناخته هیچ override ندارد.

## تصمیم امنیت و اجرای دستی

در Actions → **Publish approved images to Docker Hub** → Run workflow → branch `main`، ورودی‌های `version_tag`، `approved_sha` و `security_review` وارد می‌شوند. review شامل تمام یافته‌های واقعی (نه مثال زیر) است؛ نبود یا تکرار/اضافه‌بودن یافته، نسخه متفاوت بسته، deadline منقضی یا تأییدکننده غیرمالک اجرا را می‌بندد. برای scan واقعاً بدون یافته، `findings: []` مجاز است.

ساختار نمونهٔ **غیرمصوب و غیرقابل اجرا**:

```json
{
  "sourceSha": "FULL_APPROVED_COMMIT",
  "approvedBy": "REPOSITORY_OWNER",
  "findings": [
    {
      "image": "api",
      "id": "ACTUAL_ADVISORY_ID",
      "package": "ACTUAL_PACKAGE",
      "version": "ACTUAL_INSTALLED_VERSION",
      "severity": "MEDIUM",
      "owner": "RESPONSIBLE_PERSON",
      "mitigation": "APPROVED_ACTION",
      "deadline": "FUTURE_UTC_ISO_TIMESTAMP",
      "decision": "pending"
    }
  ]
}
```

عامل تصمیم `accepted` را به‌جای مالک اختراع نمی‌کند. بعد از ساخت و scan تازه، job publish منتظر Environment approval می‌ماند؛ scan و DB باید هنگام انتشار حداکثر ۲۴ساعته باشند. اگر scan تازه یافته متفاوتی نشان داد، review قبلی رد می‌شود؛ یافته‌ها را بررسی و اجرای تازه با تصمیم صحیح لازم است، نه override.

## جریان و شواهد

- preflight بدون token Docker Hub: tag/SHA/main و آخرین اجراهای موفق هر هفت job، با artifact هویت smoke/scan/provenance بررسی می‌شوند. approval هیچ job شکست‌خورده‌ای را مجاز نمی‌کند.
- workflow موجود ساخت، smoke واقعی، scan و SBOM را برای همان SHA انجام می‌دهد؛ imageها `docker save` می‌شوند. round-trip آرشیو در CI هر PR نیز بررسی می‌شود. artifact image فقط در فراخوانی دستی معتبر، یک روز نگهداری می‌شود؛ build هیچ secret دریافت نمی‌کند.
- publish پس از approval، gateها را دوباره بررسی می‌کند. آرشیوهای **همان run** load و ID/config/revision با smoke/scan و provenance تطبیق می‌شوند؛ هیچ build هنگام نشر وجود ندارد. report hash، OS inventory، تازگی scan/DB و تصمیم هر finding دوباره بررسی می‌شوند.
- فقط این job `docker/login-action` دارد. HTTP credentials فقط به میزبان‌های ثابت Docker فرستاده می‌شوند؛ redirect blob به CDN بدون Authorization و با بررسی hash خوانده می‌شود. 401/403/429/خطای شبکه معادل tag غایب نیست.
- version push می‌شود؛ manifest و config از registry خوانده می‌شود، سپس SHA tag دقیقاً همان digest را می‌گیرد. ID محلی با config digest دوردست برابر است؛ digest manifest دوردست لزوماً با digest خروجی Docker exporter برابر نیست و از آن حدس زده نمی‌شود.
- SBOM و provenance کامل Buildx با ORAS 1.3.5 checksum-pinned به digest واقعی متصل می‌شوند. manifest/blob/referrer دوردست نیز بازخوانی می‌شوند. provenance **unsigned** است؛ گزارش امضای رمزنگاری‌شده یا هویت مستقل builder ادعا نمی‌کند. این مسیر Referrers API واقعی می‌خواهد؛ registry ناسازگار خطاست، fallback پنهان ندارد.
- artifact `dockerhub-publication-evidence` برای ۳۰ روز: source SHA، نسخه، namespace، هر دو remote digest، tags، evidence digest، run ID، scan/SBOM/provenance، eligibility و journal وضعیت. artifact را در پرونده release نگه دار؛ retention جای آرشیو بلندمدت release نیست. `complete` فقط پس از بازخوانی موفق هر دو image و attachment ثبت می‌شود. زمان run در GitHub و زمان scan در summary موجود است.

## لغو، انتشار جزئی و بازگشت

پیش از اولین write، journal وضعیت `incomplete` می‌گیرد؛ timeout یا خطای push ممکن است remote write انجام داده باشد. در این حالت نسخه قابل مصرف/Done نیست. journal می‌تواند فقط یک image یا یک tag را تأیید کرده باشد؛ این موفقیت کامل نیست. قطع سخت job ممکن است artifact را هم از دسترس خارج کند؛ run ناموفق همچنان شاهد موفقیت نیست.

**rerun کورکورانه ممنوع:** وجود هر release tag (حتی محتوای یکسان) پیش‌بررسی را می‌بندد. هیچ حذف، بازنویسی immutable tag، cleanup repo یا recovery خودکار وجود ندارد. برای شکست جزئی، مالک ابتدا هر چهار tag و digest و journal را بررسی می‌کند؛ بازیابی همان artifact یا تصمیم نسخه/commit جدید یک اقدام صریح جدا است. تغییر صرف version با همان SHA می‌تواند به‌علت SHA tag موجود همچنان بسته بماند. tag قبلی پاک یا overwrite نمی‌شود.

A.4 فقط جفت `complete` را با digest دریافت و smoke/rollback ایزوله را ثبت می‌کند؛ این workflow به سرور، Compose، DB یا سایت دست نمی‌زند.

## مبنای فنی

- [Docker Hub immutable tags](https://docs.docker.com/docker-hub/repos/manage/hub-images/immutable-tags/)
- [Hub repository API/schema](https://docs.docker.com/reference/api/hub/latest/schemas/repository_info/) و [immutable settings](https://docs.docker.com/reference/api/hub/latest/schemas/immutable_tags_settings/)
- [Hub authentication](https://docs.docker.com/reference/api/hub/latest/operations/AuthCreateAccessToken/) و [Registry authentication](https://docs.docker.com/reference/api/registry/auth/)
- [OCI artifacts در Docker Hub](https://docs.docker.com/docker-hub/repos/manage/hub-images/oci-artifacts/) و [ORAS attach](https://oras.land/docs/commands/oras_attach/)
- [GitHub environments REST](https://docs.github.com/en/rest/deployments/environments)

تست‌های مصنوعی فقط قرارداد نشر را بررسی می‌کنند؛ اتصال واقعی Docker Hub، مجوز PAT و دو digest را اثبات نمی‌کنند. وضعیت فعلی در [checkpoint](../progress/us-12-t04a3.md) ثبت است.
