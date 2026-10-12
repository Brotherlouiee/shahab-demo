# Anonymous questionnaire sessions — US-07.T04

## Confirmed retention and resume contract

The product owner confirmed a **30-minute** anonymous-session lifetime on 2026-09-24.

- A session contains only an opaque identifier, questionnaire version, expiry and canonical question/answer pairs.
- The identifier is held only in the active React instance. It is not included in URLs, localStorage, sessionStorage, analytics or public logs.
- Back/forward navigation within the active questionnaire view reuses the in-memory session. Refreshing, closing the tab, opening another tab or changing devices starts a new session; cross-device resume is out of scope.
- At expiry, reads and writes return a typed safe error. The UI leaves the user on the current question and presents a retryable message.
- A canonical answer is sent only in the JSON body of the answer-write request. Screen indexes and option positions are never sent as answer identities.

## Scope boundary

This task introduces no identity, credit decision, score, recommendation result, automatic deletion job, production persistence guarantee or public deployment. The current server adapter is an explicit development composition boundary; production storage/operational hardening remains ordered future work.


## US-07.T05 verification boundary

- Browser coverage verifies the RTL radiogroup and named controls, blocks an unanswered behavioural screen, and confirms that same-tab back navigation preserves the selected canonical option.
- The browser test intercepts the session contract and asserts a single POST session request followed by a PUT answer request with the canonical JSON `answerId`; the answer and opaque ID do not appear in the browser URL.
- On a session-start failure, the page remains on the question and exposes a retryable `role="alert"`; it does not advance with an unconfirmed answer.
- API tests cover canonical answer ownership, safe unknown-session errors and rejection of an answer supplied outside the JSON body.

These are completion tests for the current in-memory development adapter. They do not claim restart survival, durable storage, Redis availability or cross-tab/cross-device resume; those are acceptance criteria for **US-07.T06**.


## US-07.T06 durable persistence

PostgreSQL is the source of truth whenever `SHAHAB_DATABASE_URL` is configured. The repository stores only the anonymous session UUID, questionnaire version reference, timestamps and canonical question/answer references in normalized tables. Redis is an optional runtime cache configured with `SHAHAB_REDIS_URL`; its keys contain only a SHA-256 digest of the opaque session ID, failures are swallowed, and every cache miss falls back to PostgreSQL. Expired sessions and owned answers are removed idempotently through `cleanup_expired`.

## US-11.T02E — پاسخ خام مستقل از snapshot

`questionnaire/infrastructure/retention.py` هر بار حداکثر۱۰۰ (حد سخت۱۰۰۰) نشست
expired را با ترتیب expiry/UUID و `FOR UPDATE SKIP LOCKED` انتخاب می‌کند. حذف
answers، EXPIRED کردن metadata مرتبط و حذف metadata غیرمرتبط در یک transaction
commit یا rollback می‌شوند. لینک history با هیچ فیلتر hidden/status کنار گذاشته
نمی‌شود: profile/account/run/item/reason/owner و data/config/loan/questionnaire
version حفظ می‌شوند؛ هیچ cascade، انتقال خام به archive/JSON یا تغییر scoring وجود ندارد.
metadata مرتبط شامل UUID، version FK، owner UUID، created/expires، state و digest
immutable (یا NULL legacy) برای FK/idempotency/evidence همراه history همیشگی
باقی می‌ماند؛ digest secret قابل بازیابی/پاسخ خام نیست و expiry/state هرگز اجازه
استفاده دوباره نمی‌دهند. metadata غیرمرتبط پس از expiry نیاز durable ندارد و حذف
می‌شود. قرارداد proof/owner و TTL۱۸۰۰ تمدید/تضعیف نمی‌شوند.

این موتور و CLI به‌تنهایی scheduler نیستند. F02 مسیر FK/runtime در E اصلاح می‌شود؛
بستن کامل operational retention همچنان نیازمند scheduler/monitor/restore-before-reopen
در T05 است. expiry denial یا batch خالی معادل حذف اثبات‌شده نیست.
[فرمان و حدود عملیاتی](../operations/raw-answer-retention.md) و
[شواهد E](../progress/us-11-t02e.md).

## US-11.T02F — navigation privacy

در tab memory نتیجه سروری حفظ؛ history.state تنها sessionId و historyId opaque،
بدون snapshot JSON/raw answers/token. refresh result احراز‌شده با reference همان
history snapshot خوانده می‌شود و profile edit/scoring تازه روی آن اثر ندارد. خروج
current reference/memory و creator HttpOnly cookies را پاک؛ PD01/rawTTL۳۰ و history
همیشگی/owner gate ثابت. entryهای نسخه قدیمی بدون authority معتبر بازنمایی نمی‌شوند.
