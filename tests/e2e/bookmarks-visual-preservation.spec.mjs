import { expect, test } from "@playwright/test";
import { installProfileApi } from "./fixtures/profile-api.mjs";

const baselineUrl = process.env.SHAHAB_BOOKMARK_BASELINE_URL;
if (process.env.CI && !baselineUrl) throw new Error("CI requires the independent pre-F baseline server");
test.skip(!baselineUrl, "local visual comparison requires an independent pre-F worktree");
const loan = { loanId: "visual-fixture", lenderName: "بانک آزمون", loanName: "وام آزمون", compatibilityScore: .85,
  loanSummary: { maxAmountTomans: 100000000, monthlyInstallmentTomans: 10000000, maxRepaymentMonths: 12, interestRatePercent: 18 } };
const profile = { phone: "09000000001", firstName: "آزمون", lastName: "کاربر" };

for (const viewport of [{ width: 390, height: 844 }, { width: 1440, height: 900 }]) {
  for (const populated of [false, true]) {
    test(`preserves saved-loan ${populated ? "card" : "empty artwork"} pixels and geometry at ${viewport.width}`, async ({ browser, baseURL }, info) => {
      const context = await browser.newContext({ viewport });
      const beforePage = await context.newPage(); const afterPage = await context.newPage();
      const items = populated ? [loan] : [];
      try {
        for (const page of [beforePage, afterPage]) {
          // Identical fonts/environment; no masking or tolerance hides product changes.
          await page.route(/https:\/\/fonts\.(googleapis|gstatic)\.com\//, route => route.abort());
          await installProfileApi(page, { authenticated: true, profile, savedLoans: items });
          await page.addInitScript(({ items, profile }) => {
            localStorage.setItem("shahab.savedLoans", JSON.stringify(items));
            localStorage.setItem("shahab.accountProfile", JSON.stringify(profile));
          }, { items, profile });
        }
        await beforePage.goto(`${baselineUrl}/saved-loans`); await afterPage.goto(`${baseURL}/saved-loans`);
        const selector = populated ? ".hp-serving-loan-card" : ".hp-saved-loans-empty-state img";
        for (const page of [beforePage, afterPage]) {
          await expect(page.locator(selector)).toBeVisible();
          await page.evaluate(() => document.fonts.ready);
          if (populated) await expect(page.locator(".hp-loan-save-button")).toHaveAttribute("aria-pressed", "true");
          else expect(await page.locator(selector).evaluate(image => image.complete && image.naturalWidth > 0)).toBe(true);
        }
        const beforeRect = await beforePage.locator(selector).boundingBox();
        const afterRect = await afterPage.locator(selector).boundingBox();
        expect(afterRect).toEqual(beforeRect);
        const before = await beforePage.screenshot({ fullPage: true, animations: "disabled", caret: "hide" });
        const after = await afterPage.screenshot({ fullPage: true, animations: "disabled", caret: "hide" });
        await info.attach("baseline-before", { body: before, contentType: "image/png" });
        await info.attach("candidate-after", { body: after, contentType: "image/png" });
        expect(after.equals(before), "candidate must be pixel-identical to independently checked-out main before F").toBe(true);
      } finally { await context.close(); }
    });
  }
}
