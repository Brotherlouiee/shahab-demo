import { expect, test } from "@playwright/test";

for (const viewport of [
  { name: "desktop", width: 1280, height: 720 },
  { name: "mobile", width: 390, height: 844 },
]) {
  test("loan-detail analysis toolbar stays at the viewport edge and keeps the final condition visible (" + viewport.name + ")", async ({ page }) => {
    await page.setViewportSize(viewport);
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
    const frame = await Promise.all([
      bar.evaluate((element) => ({ top: element.getBoundingClientRect().top, bottom: element.getBoundingClientRect().bottom, height: element.getBoundingClientRect().height, viewport: window.innerHeight })),
      page.getByRole("button", { name: "تحلیل با هوش مصنوعی" }).evaluate((element) => ({ top: element.getBoundingClientRect().top, bottom: element.getBoundingClientRect().bottom })),
    ]);
    expect(Math.abs(frame[0].bottom - frame[0].viewport)).toBeLessThanOrEqual(1);
    expect(frame[0].height).toBeCloseTo(117, 0);
    expect(frame[1].top - frame[0].top).toBeCloseTo(35, 0);
    expect(frame[0].viewport - frame[1].bottom).toBeCloseTo(34, 0);

    await page.locator(".hp-questionnaire-shell").evaluate((shell) => { shell.scrollTop = shell.scrollHeight; });
    const finalCondition = page.locator(".hp-loan-details-conditions li").last();
    await expect(finalCondition).toBeVisible();
    const geometry = await Promise.all([
      bar.evaluate((element) => element.getBoundingClientRect().top),
      finalCondition.evaluate((element) => element.getBoundingClientRect().bottom),
    ]);
    expect(geometry[1]).toBeLessThan(geometry[0]);
  });
}


test("refresh never renders the removed legacy mock page", async ({ page }) => {
  // Assert application readiness rather than waiting for unrelated font/image load.
  await page.goto("/", { waitUntil: "commit" });
  await page.locator(".hp-nav").waitFor({ state: "visible" });
  await page.reload({ waitUntil: "commit" });
  await page.locator(".hp-nav").waitFor({ state: "visible" });

  for (const legacyText of ["محاسبه وام شهاب", "طرح نیک وام", "ثبت درخواست وام بانکی"]) {
    await expect(page.getByText(legacyText, { exact: true })).toHaveCount(0);
  }
});

