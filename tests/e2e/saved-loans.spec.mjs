import { expect, test } from "@playwright/test";
import { installProfileApi } from "./fixtures/profile-api.mjs";

const savedLoan = {
  loanId: "saved-loan-1",
  lenderName: "بانک آزمون",
  loanName: "وام آزمون",
  compatibilityScore: 0.85,
  loanSummary: {
    maxAmountTomans: 100000000,
    monthlyInstallmentTomans: 10000000,
    maxRepaymentMonths: 12,
    interestRatePercent: 18,
  },
};

test("shows the supplied empty artwork and no filters when no saved loan exists", async ({ page }) => {
  await installProfileApi(page, { authenticated: true, profile: { phone: "09000000001" } });
  const imageResponse = page.waitForResponse(response => response.url().endsWith("/saved-loans-empty.webp"));
  await page.goto("/saved-loans");

  await expect(page).toHaveURL(/\/saved-loans$/);
  await expect(page.locator(".hp-saved-loans-empty-state img")).toHaveAttribute("src", "/saved-loans-empty.webp");
  const emptyArtwork = page.locator(".hp-saved-loans-empty-state img");
  const artworkResponse = await imageResponse;
  expect(artworkResponse.headers()["content-type"]).toContain("image/webp");
  expect(Number(artworkResponse.headers()["content-length"])).toBeLessThan(100_000);
  await expect(emptyArtwork).toHaveJSProperty("complete", true);
  expect(await emptyArtwork.evaluate((image) => image.naturalWidth === 600 && image.naturalHeight === 623)).toBe(true);
  const timing = await emptyArtwork.evaluate((image) => {
    const resource = performance.getEntriesByName(image.currentSrc).at(-1);
    return resource && {
      durationMs: Math.round(resource.duration * 100) / 100,
      transferBytes: resource.transferSize,
      encodedBytes: resource.encodedBodySize,
    };
  });
  expect(timing).not.toBeNull();
  expect(timing.encodedBytes).toBeLessThan(100_000);
  console.info(`SAVED_EMPTY_ARTWORK ${JSON.stringify(timing)} cache-control=${artworkResponse.headers()["cache-control"] || "unspecified"}`);
  await expect(page.locator(".hp-loan-result-filters")).toHaveCount(0);
});

test("keeps a saved loan detail return path and hides filters for one loan", async ({ page }) => {
  await installProfileApi(page, { authenticated: true, profile: { phone: "09000000001" }, savedLoans: [savedLoan] });
  await page.route("**/api/v1/loans/saved-loan-1", (route) => route.fulfill({ json: {
    loanId: "saved-loan-1",
    lenderName: "بانک آزمون",
    loanName: "وام آزمون",
    maxAmountTomans: 100000000,
    monthlyInstallmentTomans: 10000000,
    maxRepaymentMonths: 12,
    interestRatePercent: 18,
    depositRequired: "ندارد",
    depositHoldingMonths: 0,
    loanToDepositRatioPercent: 0,
    guaranteeType: "ضامن",
    requiredDepositAccount: "ندارد",
    conditions: ["کارت ملی"],
    bankLogoReference: null,
    applicationLink: null,
  } }));
  await page.goto("/saved-loans");

  await expect(page.locator(".hp-loan-result-filters")).toHaveCount(0);
  await expect(page.locator(".hp-loan-docs-link .hp-loan-docs-icon")).toHaveCount(1);
  await page.locator(".hp-loan-docs-link").click();
  await expect(page).toHaveURL(/\/loan-details\?loanId=saved-loan-1&from=saved-loans$/);
  await page.getByRole("button", { name: "بازگشت" }).click();
  await expect(page).toHaveURL(/\/saved-loans$/);
});
