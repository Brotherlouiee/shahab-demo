# Profile threat model — US-09.T072

| Threat | Control | Evidence / boundary |
| --- | --- | --- |
| Guessed phone reads / cross-account writes | GET /profiles/me and server-owned phone comparison | API access/ownership tests; old lookup removed |
| Forged cached identity | Opaque server session; bearer only in module memory | Cache never authorizes; forged-token tests |
| Replay/expired access | Single-use OTP, attempts/expiry, digested tokens/TTL/revocation | Access tests; API restart requires login |
| Mock in production | Local/test environment allowlist regardless of flag; explicit false disables local mock | Staging/production fail-closed tests |
| Silent storage failure / overwritten draft | Safe error, blocked advancement, draft retained, confirmed cache only after success | API/client/browser retry tests |
| Phone in URL / shared HTTP cache | /me and JSON body; no-store | API/client tests |
| Invalid input/avatar | Reject extras; income/job/gender allowlists; base64 raster signature/type and 100 KB server limit | Schema tests; SVG rejected |
| OTP brute force/memory exhaustion | Five attempts; client/phone quota; bounded stores | Attempt/quota/expiry tests |

Purpose: local/test editable profile persistence. Existing profiles remain until explicit owner/operator deletion. Automated deletion and production retention/consent policy remain separate account release gates. No analytics, training or third-party use is added. Real SMS, shared production sessions and full transport/security release gates are not delivered here.

## US-11.T02A.2 — انتقال اجرایی هویت

تغییر هویت با phone مشترک: capability به UUID immutable bind و هر request active همان ID را از DB validate می‌کند؛ archived credential هیچ داده نسل جدید را نمی‌خواند. migration از مالک legacy به mapping پایدار، guard rollback و race دو connection. mock/local-only و نشست حافظه‌ای/۱۸۰۰ قبلی باقی؛ C/H production gates مستقل‌اند.

## US-11.T02C — نشست مشترک یک‌ساعته

C credential digest/account UUID و expiry۱h در PostgreSQL، status و revocation تازه، OTP/attempt/quota مشترک و race واقعی. mock هنوز local/test و provider واقعی production فعال نیست؛ archive G و browser cleanup F، H transport جدا. [قرارداد](account-session-lifecycle.md).



## US-11.T06 — تهدیدهای ارسال واقعی OTP

| تهدید | کنترل و شاهد |
| --- | --- |
| key در URL/خطای upstream یا redirect | host HTTPS ثابت، redirect/proxy خاموش، خطای عمومی بدون URL/body؛ تست transport |
| brute-force آفلاین code digest | HMAC با راز مستقل و nonce تصادفی؛ کد/hash کم‌انتروپی در DB ذخیره نمی‌شود |
| استفاده از mock یا worker با config متفاوت | prefix sms1 و proof context، منع mock در production، راز یکسان workerها؛ config و cross-mode tests |
| SMS تکراری/دورزدن quota در outage | commit رزرو پیش از I/O، بدون retry، مصرف challenge شکست‌خورده و حفظ quota؛ fault tests |
| نگه‌داشتن قفل کل سیستم در شبکه | ارسال پس از commit؛ contract test و دو تست جدید PostgreSQL در suite موجود |
| ارسال ناخواسته در CI یا قبل تأیید | opt-in و approved پیش‌فرض false، config کامل PostgreSQL، CI/TEST guard؛ composition tests |

نام الگوی مالک OTP1؛ تأیید و ارسال واقعی هنوز pending. آماده‌سازی اتصال، gate انتشار
یا اثبات دریافت SMS نیست. provider شماره و کد را فقط برای هدف ورود دریافت می‌کند؛
response خام نگهداری نمی‌شود. رخداد و نرخ خطا از metrics موجود به‌صورت غیرشخصی است.
[runbook و rollback](../operations/kavenegar-otp.md).
