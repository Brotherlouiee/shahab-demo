import { expect, test } from "@playwright/test";

test("loan-detail analysis toolbar stays at the viewport edge and keeps the final condition visible", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.route("**/api/v1/loans/t06n-footer-loan", (route) => route.fulfill({
    json: {
      loanId: "t06n-footer-loan", lenderName: "بانک ملت", loanName: "وام آزمایشی",
      maxAmountTomans: 500000000, monthlyInstallmentTomans: 12000000,
      maxRepaymentMonths: 48, interestRatePercent: 18, depositRequired: "خیر",
      depositHoldingMonths: null, loanToDepositRatioPercent: null,
      guaranteeType: "ضامن رسمی", requiredDepositAccount: null,
      conditions: Array.from({ length: 24 }, (_, index) => "شرط تأییدشدهٔ " + (index + 1)),
    },
  }));
  await page.goto("/loan-details?loanId=t06n-footer-loan");
  const bar = page.locator(".hp-loan-details-analysis-bar");
  await expect(page.getByRole("button", { name: "تحلیل با هوش مصنوعی" })).toBeVisible();
  const initial = await bar.evaluate((element) => ({ bottom: element.getBoundingClientRect().bottom, viewport: window.innerHeight }));
  expect(Math.abs(initial.bottom - initial.viewport)).toBeLessThanOrEqual(1);

  await page.locator(".hp-questionnaire-shell").evaluate((shell) => { shell.scrollTop = shell.scrollHeight; });
  const finalCondition = page.locator(".hp-loan-details-conditions li").last();
  await expect(finalCondition).toBeVisible();
  const geometry = await Promise.all([
    bar.evaluate((element) => element.getBoundingClientRect().top),
    finalCondition.evaluate((element) => element.getBoundingClientRect().bottom),
  ]);
  expect(geometry[1]).toBeLessThan(geometry[0]);
});
