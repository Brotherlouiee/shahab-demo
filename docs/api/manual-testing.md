# تست دستی API — US-09.T081

این راهنما برای محیط آزمایشی محدود است. **هنوز URL آنلاین تأییدشده‌ای تحویل نشده است.** وجود فایل‌های زیر، تست محلی یا CI سبز به معنی پایان T081 نیست؛ وضعیت هر عملیات در [ماتریس پوشش](coverage.md) ثبت می‌شود.

## آنچه در ابزار می‌بینید

Swagger در `https://API_HOST/docs` عملیات فعلی را با گروه، method/path، ورودی و پاسخ، خطا و دکمهٔ **Try it out → Execute** نمایش می‌دهد. `API_HOST` نمونه است، نه دامنهٔ مستقر. در محیط محدود باید `SHAHAB_API_DOCS_INCLUDE_OPERATIONS=true` باشد تا health/readiness هم دیده شوند. این flag هیچ route یا مجوزی را فعال نمی‌کند؛ production همچنان `/docs`، `/redoc` و OpenAPI را 404 می‌دهد.

فایل‌های تولیدی از خود FastAPI، بدون اتصال به دیتابیس یا خواندن دادهٔ کاربر ساخته می‌شوند:

- [OpenAPI](generated/openapi.json)
- [Collection قابل import](generated/shahab.postman_collection.json)
- [Environment خالی](generated/shahab.postman_environment.json)
- [فهرست method/path](generated/operations.json)

فرمان تولید و کنترل drift از ریشهٔ پروژه:

```sh
python -m scripts.export_api_docs
python -m scripts.export_api_docs --check
```

در CI فرمان دوم و تست coverage اجرا می‌شوند. موجودی routeها مستقلاً از decoratorهای API بررسی می‌شود؛ health نیز در مرجع کامل پوشش دارد. endpoint محصولی جدید، پنل مدیریتی، SMS واقعی یا API بانک ایجاد نشده است.

## ورود به Postman

۱. Collection و Environment خالی را Import کنید و محیط را انتخاب کنید. برای اجرای آنلاین از Desktop یا Desktop Agent با دسترسی به شبکهٔ محدود محیط استفاده کنید؛ Cloud Agent ممکن است به محیط خصوصی دسترسی نداشته باشد.

۲. مقدار خصوصی `baseUrl` را ریشهٔ HTTPS API، **بدون** `/api/v1` و بدون slash انتهایی قرار دهید. برای localhost فقط در تست محلی HTTP مجاز است. gateway و مسیر `/api/v1` نباید بازنویسی یا حذف شوند.

۳. Cookie jar را فعال نگه دارید. `testPhone` شمارهٔ مصنوعی اختصاص‌یافتهٔ تست‌کننده است؛ از شماره و دادهٔ واقعی استفاده نکنید. `otpCode` در local/test فعلی `123456` است و پیامک ارسال نمی‌شود. این روش مالکیت واقعی تلفن را اثبات نمی‌کند؛ staging/production آن را رد می‌کنند.

۴. پس از پاسخ موفق request، `challengeId` و پس از verify، `accessToken` به Environment **خصوصی** همان تست‌کننده منتقل می‌شوند. پس از ساخت پرسشنامه نیز `sessionId` تنظیم می‌شود. مقدارهای `questionId`، `answerId`، `loanId` و `historyId` را مطابق پاسخ/قرارداد همان محیط پر کنید. نمونهٔ PUT پروفایل نیازمند ویرایش فیلدهاست؛ متن خالی یک پروفایل واقعی نیست.

۵. Environment پرشده، cookie، token، پاسخ‌های خصوصی و screenshot حاوی آن‌ها را export/share/commit نکنید. type=secret در Environment به‌تنهایی تضمین حذف مقدار از export نیست. فقط template خالی را اشتراک دهید؛ پس از تست مقدارها و cookie jar را پاک کنید.

## مسیر دستی در Swagger یا Postman

همهٔ گام‌ها را در **همان مرورگر یا cookie jar** انجام دهید. نشست حساب عمر مطلق یک ساعت دارد؛ نشست پرسشنامه TTL جداگانهٔ ۳۰ دقیقه و challenge OTP فقط ۱۲۰ ثانیه دارد. restore زمان حساب را تمدید نمی‌کند. Swagger با `withCredentials` cookieهای HttpOnly را خودکار می‌فرستد؛ نیازی به کپی cookie نیست. ذخیرهٔ Authorization در Swagger خاموش است؛ schema به validator خارجی ارسال نمی‌شود. دارایی‌های Swagger روی نسخهٔ مشخص `5.17.14` هستند؛ مرورگر باید به CDN دارایی‌ها دسترسی داشته باشد.

| گام | درخواست و ورودی | انتظار |
| --- | --- | --- |
| ۱ | GET `/api/v1/health/live` | 200، `status=ok`؛ فقط سلامت HTTP |
| ۲ | GET `/api/v1/health/ready` با token اختصاصی اپراتور در `X-Shahab-Readiness-Token` | 200؛ بدون token یا token اشتباه 404. readiness فعلی اثبات catalogue/DB نیست. |
| ۳ | POST `/api/v1/account-access/request` با `phone` آزمایشی | 200 و `challengeId` |
| ۴ | POST `/api/v1/account-access/verify` با `challengeId` و `code` | 200؛ ایجاد/بازیابی پروفایل در DB و cookie حساب |
| ۵ | GET `/api/v1/account-access/session` و GET `/api/v1/profiles/me` | بازیابی حساب و پروفایل همان شخص |
| ۶ | PUT `/api/v1/profiles` با phone همان حساب و فیلدهای مجاز؛ سپس GET `/me` | تغییر فقط حساب خود و بازخوانی مقدار ثبت‌شده؛ phone حساب دیگر 403 |
| ۷ | POST `/api/v1/questionnaire/sessions` بدون body | 201، `sessionId` و cookie اثبات سازنده |
| ۸ | PUT `/api/v1/questionnaire/sessions/{session_id}/answers/{question_id}` با `answerId` | برای هر ده سؤال یک گزینهٔ canonical؛ 200 |
| ۹ | GET `/api/v1/questionnaire/sessions/{session_id}` | ده پاسخ همان نشست؛ برای انقضای واقعی 410 |
| ۱۰ | POST `/api/v1/recommendations` فقط با `sessionId` | 200؛ سه مجموعهٔ واقعی سروری، data/config version؛ نقص ورودی 422 و نبود serving معتبر 503 |
| ۱۱ | GET `/api/v1/loans/{loan_id}` با ID یکی از خروجی‌ها | 200 و شرایط همان وام؛ ID ناموجود 404 |
| ۱۲ | GET `/api/v1/recommendation-history`؛ سپس GET `/{history_id}` | سابقهٔ حساب خود، تعداد ranked و snapshot بدون scoring مجدد |
| ۱۳ | DELETE `/api/v1/recommendation-history/{history_id}` **فقط سابقهٔ آزمایشی خود** | 204؛ از فهرست/جزئیات کاربر پنهان می‌شود، در DB حذف فیزیکی نمی‌شود؛ تکرار 404 |
| ۱۴ | PUT `/api/v1/bookmarks/{loan_id}` با `{}` یا `{"historyId":"UUID سابقهٔ قابل‌مشاهدهٔ خود"}` | 204 پس از commit؛ نسخه PUBLISHED و context همان حساب؛ retry بدون duplicate |
| ۱۵ | GET `/api/v1/bookmarks` | کارت ذخیره‌شدهٔ همان حساب، limit بین ۱ و ۵۰ و nextCursor برای ادامه؛ حساب دوم آن را نمی‌بیند |
| ۱۶ | DELETE `/api/v1/bookmarks/{loan_id}`، سپس GET فهرست | 204 و حذف از نمایش؛ تکرار DELETE هم 204؛ رکورد durable فیزیکی حذف نمی‌شود |
| ۱۷ | POST `/api/v1/account-access/logout` | 204؛ درخواست بعدی محافظت‌شده 401 |

Bearer تنها جای cookie اثبات سازندهٔ پرسشنامه را نمی‌گیرد. ورود بدون آن cookie و درخواست تاریخچه برای پرسشنامهٔ دیگری نباید موفق شود. برای تست حساب دوم یک browser context/cookie jar مستقل بسازید؛ context اول را به آن منتقل نکنید. برای pagination از `limit` مجاز و `nextCursor` همان پاسخ استفاده کنید؛ cursor را حدس نزنید.

شناسهٔ گزینه‌ها و متن مرجع در [questionnaire-configuration.v1.json](../../data/contracts/questionnaire-configuration.v1.json) است: `Q1..Q6,S7,S8,S10,S13`. برای هر سؤال یک `answerId` متعلق به همان سؤال انتخاب کنید؛ مثال Q1: `Q1.incomeInvestment`. route عمومی configuration در کد فعلی وجود ندارد؛ endpoint فرضی نسازید. سؤال‌های مالی نمایشیِ دو صفحهٔ نخست ورودی جدید API توصیه نیستند.

## اشتراک و اثبات نهایی

فقط لینک HTTPS **محدود** را با مالک و تست‌کنندهٔ دوم مجاز به اشتراک بگذارید. اجازهٔ دیدن مستندات، مجوز تغییر پروفایل یا history شخص دیگر نیست. راه‌اندازی مطابق [runbook محیط تست](../runbook/api-testing.md)، با PostgreSQL مستقل و دادهٔ رسمی تأییدشده انجام می‌شود.

روی همان URL، وضعیت هر یک از ۱۹ عملیات، SHA runtime، data/config version و بازخوانی persistence را ثبت کنید. فقط status و نام عملیات را در شواهد مشترک نگه دارید؛ مقادیر خصوصی، token، phone و answers حذف شوند. تا همهٔ عملیات مربوط، مالک و تست‌کنندهٔ دوم، cookie/proxy/TLS و خطاهای مالکیت در محیط آنلاین اثبات نشوند، T081 **Done نیست**.
