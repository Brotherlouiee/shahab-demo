import { expect, test } from "@playwright/test";
const sessionId = "opaque-e2e-session";
const recommendationResponse = { dataVersion: "serving.v1", configVersion: "recommendation.v1", rankedRecommendations: [
  { loanId: "loan-ranked", lenderName: "بانک الف", loanName: "طرح قابل مقایسه", compatibilityScore: 0.87, compatibilityReason: "دلیل سازگاری از پاسخ معتبر سرور آمده است." },
  { loanId: "loan-second", lenderName: "بانک ب", loanName: "طرح دوم", compatibilityScore: 0.65, compatibilityReason: "دلیل دوم از سرور آمده است." },
], needsReview: [{ loanId: "loan-review", lenderName: "بانک بررسی", loanName: "طرح داده‌ناقص", rankingExcludedReasons: ["interestRate:unknown"] }] };
const detailResponse = { loanId: "loan-ranked", lenderName: "بانک الف", loanName: "طرح قابل مقایسه", maxAmountTomans: 100000000, monthlyInstallmentTomans: 10000000, maxRepaymentMonths: 12, interestRatePercent: 18, depositRequired: "دارد", depositHoldingMonths: 3, loanToDepositRatioPercent: 100, guaranteeType: "ضامن", requiredDepositAccount: "قرض الحسنه", conditions: ["کارت ملی", "یک ضامن معتبر"], bankLogoReference: null, applicationLink: null };
async function mockDetail(page) { await page.route("**/api/v1/loans/loan-ranked", (route) => route.fulfill({ json: detailResponse })); }
test("renders the validated server result in RTL, preserves needs-review without a score, and opens safe loan details", async ({ page }) => {
  const recommendationRequests = [];
  await page.route("**/api/v1/recommendations", async (route) => {
    recommendationRequests.push({ method: route.request().method(), url: route.request().url(), body: route.request().postDataJSON() });
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(recommendationResponse) });
  });
  await mockDetail(page);
  await page.goto("/tests/e2e/fixtures/recommendation-result-harness.html");
  await expect(page.locator("main.hp-recommendation-results-screen")).toHaveAttribute("dir", "rtl");
  await expect(page.getByRole("heading", { name: "نتیجهٔ مقایسهٔ وام‌ها" })).toBeVisible();
  await expect(page.getByText("۸۷٪")).toBeVisible();
  await expect(page.locator(".hp-recommendation-needs-review")).toContainText("طرح داده‌ناقص");
  await expect(page.locator(".hp-recommendation-needs-review")).not.toContainText("درصد تطابق محاسبه‌شده");
  await page.getByLabel("نام بانک").selectOption({ label: "بانک الف" });
  await expect(page.getByRole("status")).toContainText("۱ گزینهٔ قابل مقایسه");
  await page.getByLabel("مرتب‌سازی نمایش").selectOption("lenderNameAsc");
  expect(recommendationRequests).toEqual([{ method: "POST", url: expect.stringMatching(/\/api\/v1\/recommendations$/), body: { sessionId } }]);
  expect(recommendationRequests[0].url).not.toContain(sessionId);
  expect(page.url()).not.toContain(sessionId);
  await page.getByRole("link", { name: "مشاهدهٔ جزئیات، شرایط و مدارک" }).first().click();
  await expect(page).toHaveURL(/\/loan-details\?loanId=loan-ranked$/);
  await expect(page.locator("main.hp-loan-details-page")).toHaveAttribute("dir", "rtl");
  await expect(page.getByRole("heading", { name: "شرایط و مدارک مورد نیاز" })).toBeVisible();
  await expect(page.locator(".hp-loan-details-conditions")).toContainText("کارت ملی");
  await expect(page.locator(".hp-loan-details-conditions")).toContainText("یک ضامن معتبر");
});
test("shows a typed safe error and retries the result client without exposing a server payload", async ({ page }) => {
  let calls = 0;
  await page.route("**/api/v1/recommendations", (route) => {
    calls += 1;
    return calls === 1 ? route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ error: { message: "secret result payload" } }) }) : route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(recommendationResponse) });
  });
  await page.goto("/tests/e2e/fixtures/recommendation-result-harness.html");
  await expect(page.getByRole("alert")).toContainText("دریافت نتیجه در حال حاضر ممکن نیست.");
  await expect(page.getByText("secret result payload")).toHaveCount(0);
  await page.getByRole("button", { name: "تلاش مجدد" }).click();
  await expect(page.getByText("طرح قابل مقایسه")).toBeVisible();
  expect(calls).toBe(2);
});
