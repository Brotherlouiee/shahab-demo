import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";
const questionnaire = JSON.parse(readFileSync(new URL("../../data/contracts/questionnaire-configuration.v1.json", import.meta.url), "utf8"));

const sessionId = "opaque-live-flow-test";
const additionalRankedRecommendations = [
  ["published-loan-2", "بانک توسعه تعاون", "طرح نیروگاه خورشیدی خانگی", 0.86],
  ["published-loan-3", "بانک دی", "وام دی", 0.82],
  ["published-loan-4", "بانک رفاه کارگران", "طرح رفاه سازمانی", 0.79],
  ["published-loan-5", "بانک صنعت و معدن", "تسهیلات توسعه صنعتی", 0.76],
  ["published-loan-6", "بانک ملی", "وام ملی", 0.73],
  ["published-loan-7", "بانک ایران و ونزوئلا", "طرح تأمین مالی زنجیره‌ای بنگاه‌های کوچک و متوسط", 0.69],
  ["published-loan-8", "بانک سینا", "وام سینا", 0.65],
].map(([loanId, lenderName, loanName, compatibilityScore]) => ({
  loanId,
  lenderName,
  loanName,
  bankLogoReference: `https://cdn.example.test/${loanId}.svg`,
  compatibilityScore,
  compatibilityReason: "سازگاری دسته‌بندی شرایط وام با پاسخ‌های ثبت‌شدهٔ شما",
}));
const response = {
  dataVersion: "official-source-v1", configVersion: "1.1.0",
  rankedRecommendations: [{ loanId: "published-loan", lenderName: "بانک ملت", loanName: "میثاق 2", bankLogoReference: "https://cdn.example.test/published-bank.svg", compatibilityScore: 0.91, compatibilityReason: "سازگاری دسته‌بندی شرایط وام با پاسخ‌های ثبت‌شدهٔ شما" }, ...additionalRankedRecommendations],
  lowCompatibilityRecommendations: [{ loanId: "low-loan", lenderName: "بانک ایران و ونزوئلا", loanName: "وام زیر آستانه", bankLogoReference: "https://cdn.example.test/low-bank.svg", compatibilityScore: 0.2, compatibilityReason: "تطابق پایین؛ پیشنهاد اصلی نیست" }],
  needsReview: [{ loanId: "unknown-loan", lenderName: "بانک شهر", loanName: "وام نیازمند بررسی", bankLogoReference: "https://cdn.example.test/review-bank.svg", rankingExcludedReasons: ["interestRate:unknown"] }],
};


async function reachAnalysis(page) {
  await page.route("**/api/v1/questionnaire/sessions", route => route.fulfill({ status: 201, json: { sessionId, answers: {} } }));
  await page.route("**/api/v1/questionnaire/sessions/*/answers/*", route => route.fulfill({ json: { sessionId, answers: {} } }));
  await page.goto("/question/3");
  for (const question of questionnaire.questions) {
    await expect(page.getByRole("heading", { name: question.prompt.replace(/[0-9]/g, digit => String.fromCharCode(0x6f0 + Number(digit))).replace(/\s+/g, " ").trim() })).toBeVisible();
    await page.getByRole("radio").first().click();
    await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
  }

  await expect(page).toHaveURL(/\/personal-info$/);
  const personalInputs = page.locator(".hp-personal-info-form input");
  await personalInputs.nth(0).fill("علی");
  await personalInputs.nth(1).fill("رضایی");
  await personalInputs.nth(2).fill("۹۱۲۳۴۵۶۷۸۹");
  await page.locator(".hp-personal-dropdown-trigger").nth(0).click();
  await page.getByRole("option", { name: "تا ۲۲ میلیون تومان" }).click();
  await page.locator(".hp-personal-dropdown-trigger").nth(1).click();
  await page.getByRole("option", { name: "کارمند (شرکت یا اداره)" }).click();
  await page.getByRole("button", { name: "تایید" }).click();
  await expect(page).toHaveURL(/\/verify-code$/);
  const otpInputs = page.locator(".hp-loan-otp-row input");
  for (const [index, digit] of [..."۱۲۳۴۵۶"].entries()) await otpInputs.nth(index).fill(digit);
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  await expect(page).toHaveURL(/\/analysis$/);

}

test("requests results during analysis and waits for a slow server without duplicate requests", async ({ page }) => {
  let posts = 0;
  let release;
  const pending = new Promise(resolve => { release = resolve; });
  await page.route("**/api/v1/recommendations", async route => {
    posts++;
    await pending;
    await route.fulfill({ json: response });
  });
  await reachAnalysis(page);
  await expect.poll(() => posts).toBe(1);
  await expect(page).toHaveURL(/\/analysis$/);
  await expect(page).toHaveURL(/\/loan-results$/, { timeout: 7000 });
  await expect(page.locator(".hp-serving-loan-card")).toHaveCount(0);
  expect(posts).toBe(1);
  release();
  await expect(page.locator(".hp-serving-loan-card").first()).toBeVisible();
  expect(posts).toBe(1);
});

test("a failed recommendation waits for explicit retry", async ({ page }) => {
  let posts = 0;
  await page.route("**/api/v1/recommendations", route => {
    posts++;
    return route.fulfill(posts === 1 ? { status: 503, json: { detail: "unavailable" } } : { json: response });
  });
  await reachAnalysis(page);
  await expect.poll(() => posts).toBe(1);
  await expect(page).toHaveURL(/\/loan-results$/, { timeout: 7000 });
  await expect(page.getByRole("button", { name: "تلاش مجدد" })).toBeVisible();
  expect(posts).toBe(1);
  await page.getByRole("button", { name: "تلاش مجدد" }).click();
  await expect(page.locator(".hp-serving-loan-card").first()).toBeVisible();
  expect(posts).toBe(2);
});

for (const viewport of [{ name: "desktop", width: 1280, height: 720 }, { name: "mobile", width: 360, height: 800 }]) {
  test(viewport.name + " pins detail CTA to viewport bottom and keeps final conditions reachable", async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.route("**/api/v1/loans/footer-loan", route => route.fulfill({ json: {
      loanId: "footer-loan", lenderName: "بانک ملت", loanName: "وام آزمایشی", maxAmountTomans: 500000000,
      monthlyInstallmentTomans: 12000000, maxRepaymentMonths: 48, interestRatePercent: 18,
      depositRequired: "خیر", depositHoldingMonths: null, loanToDepositRatioPercent: null,
      guaranteeType: "ضامن رسمی", requiredDepositAccount: null,
      conditions: Array.from({length: 30}, (_, index) => "شرط منتشرشده " + index),
    } }));
    await page.goto("/loan-details?loanId=footer-loan");
    const button = page.getByRole("button", { name: "تحلیل با هوش مصنوعی" });
    await expect(button).toBeVisible();
    async function assertFooter() {
      const bounds = await button.evaluate(el => ({ bottom: el.getBoundingClientRect().bottom, height: innerHeight }));
      expect(bounds.bottom).toBeCloseTo(bounds.height, 0);
    }
    await assertFooter();
    await page.locator(".hp-questionnaire-shell").evaluate(shell => { shell.scrollTop = shell.scrollHeight; });
    await assertFooter();
    const last = await page.locator(".hp-loan-details-conditions li").last().boundingBox();
    const bar = await page.locator(".hp-loan-details-analysis-bar").boundingBox();
    expect(last.y + last.height).toBeLessThan(bar.y);
    await button.click();
    await expect(page).toHaveURL(/\/ai-analysis/);
  });
}


test("questionnaire stays usable while the external font stylesheet is delayed", async ({ page }) => {
  let release;
  const delayedFont = new Promise(resolve => { release = resolve; });
  await page.route("https://fonts.googleapis.com/**", async route => {
    await delayedFont;
    await route.fulfill({ contentType: "text/css", body: "" });
  });
  try {
    await page.goto("/question/3", { waitUntil: "domcontentloaded" });
    await expect(page.getByRole("radio").first()).toBeVisible();
    await page.getByRole("radio").first().click();
    await expect(page.locator(".hp-next-question")).toBeEnabled();
  } finally {
    release();
  }
});
