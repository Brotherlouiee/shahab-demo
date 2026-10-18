import { mkdir, writeFile } from "node:fs/promises";
import { chromium, expect, test } from "@playwright/test";
import { installProfileApi } from "./fixtures/profile-api.mjs";

const baselineUrl = process.env.SHAHAB_BOOKMARK_BASELINE_URL;
if (process.env.CI && !baselineUrl) throw new Error("CI requires the independent pre-F baseline server");
test.skip(!baselineUrl, "local visual comparison requires an independent pre-F worktree");
const loan = { loanId: "visual-fixture", lenderName: "بانک آزمون", loanName: "وام آزمون", compatibilityScore: .85,
  loanSummary: { maxAmountTomans: 100000000, monthlyInstallmentTomans: 10000000, maxRepaymentMonths: 12, interestRatePercent: 18 } };
const profile = { phone: "09000000001", firstName: "آزمون", lastName: "کاربر" };

for (const viewport of [{ width: 390, height: 844 }, { width: 1440, height: 900 }]) {
  for (const populated of [false, true]) {
    test(`preserves saved-loan ${populated ? "card" : "empty artwork"} pixels and geometry at ${viewport.width}`, async ({ baseURL }, info) => {
      // Chromium can round anti-aliased border-radius edge colors differently
      // across partial raster tiles and CPU-dependent Skia code paths.
      // Force full tiles and the generic Skia path for BOTH independently
      // checked-out versions; keep the screenshot pixel comparison exact.
      const browser = await chromium.launch({
    ...(process.env.SHAHAB_E2E_BROWSER_PATH ? { executablePath: process.env.SHAHAB_E2E_BROWSER_PATH } : {}),
        args: [
          "--disable-gpu",
          "--disable-gpu-rasterization",
          "--disable-partial-raster",
          "--disable-skia-runtime-opts",
          "--force-color-profile=srgb",
          "--disable-features=PaintHolding",
        ],
      });
      const context = await browser.newContext({ viewport });
      const page = await context.newPage();
      const items = populated ? [loan] : [];
      try {
        // Capture both origins in the SAME Chromium page. Independent pages can
        // rasterize rounded corners one color step differently (observed:
        // exactly 8 top-left pixels at 390px, RGB delta <= 1 on pre-F vs main).
        // This keeps zero pixel tolerance and the independent pre-F worktree.
        await page.route(/https:\/\/fonts\.(googleapis|gstatic)\.com\//, route => route.abort());
        await installProfileApi(page, { authenticated: true, profile, savedLoans: items });
        await page.addInitScript(({ items, profile }) => {
          localStorage.setItem("shahab.savedLoans", JSON.stringify(items));
          localStorage.setItem("shahab.accountProfile", JSON.stringify(profile));
        }, { items, profile });
        const selector = populated ? ".hp-serving-loan-card" : ".hp-saved-loans-empty-state img";
        async function capture(url) {
          await page.goto(url);
          const element = page.locator(selector);
          await expect(element).toBeVisible();
          await page.evaluate(() => document.fonts.ready);
          if (populated) await expect(page.locator(".hp-loan-save-button")).toHaveAttribute("aria-pressed", "true");
          else {
            await element.evaluate(image => image.decode());
            expect(await element.evaluate(image => image.complete && image.naturalWidth > 0)).toBe(true);
          }
          const rect = await element.boundingBox();
          const pixels = await element.screenshot({ animations: "disabled", caret: "hide" });
          return { rect, pixels };
        }
        const before = await capture(`${baselineUrl}/saved-loans`);
        const after = await capture(`${baseURL}/saved-loans`);
        expect(after.rect).toEqual(before.rect);
        const evidence = `test-results/f-visual-${viewport.width}-${populated ? "card" : "empty"}`;
        await mkdir(evidence, { recursive: true });
        await writeFile(`${evidence}/baseline.png`, before.pixels);
        await writeFile(`${evidence}/candidate.png`, after.pixels);
        await info.attach("baseline-before", { body: before.pixels, contentType: "image/png" });
        await info.attach("candidate-after", { body: after.pixels, contentType: "image/png" });
        expect(after.pixels.equals(before.pixels), "saved element must be pixel-identical to independently checked-out main before F").toBe(true);
      } finally { await context.close(); await browser.close(); }
    });
  }
}
