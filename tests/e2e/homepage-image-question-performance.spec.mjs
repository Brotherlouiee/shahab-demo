import { expect, test } from "@playwright/test";
import { installProfileApi } from "./fixtures/profile-api.mjs";

test("home uses the existing mobile composition at phone and desktop viewport widths", async ({ page }) => {
  for (const viewport of [{ width: 390, height: 844 }, { width: 1440, height: 844 }]) {
    await page.setViewportSize(viewport);
    await page.goto("/");
    await expect(page.locator(".hp-mobile-home")).toBeVisible();
    await expect(page.locator(".hp-menu-button")).toBeVisible();
    await expect(page.locator(".hp-nav-left a")).toBeHidden();
    await expect(page.locator(".hp-hero")).toBeVisible();
    const mobilePresentation = await page.locator(".hp-hero").evaluate((hero) => ({
      headingSize: getComputedStyle(hero.querySelector("h1")).fontSize,
      headingWidth: getComputedStyle(hero.querySelector("h1")).maxWidth,
      formDirection: getComputedStyle(hero.querySelector("form")).flexDirection,
      pageBackground: getComputedStyle(hero.closest(".hp-page")).backgroundColor,
    }));
    expect(mobilePresentation).toEqual({
      headingSize: "33px",
      headingWidth: "348px",
      formDirection: "column",
      pageBackground: "rgb(255, 255, 255)",
    });
  }
});

test("about and contact artwork uses compact WebP assets and decodes successfully", async ({ page }) => {
  const transfers = [];
  page.on("response", async (response) => {
    if (!response.url().includes(".webp")) return;
    const body = await response.body();
    const timing = response.request().timing();
    transfers.push({
      url: new URL(response.url()).pathname,
      bytes: body.byteLength,
      durationMs: Math.max(0, timing.responseEnd - timing.requestStart),
      status: response.status(),
    });
  });

  await page.goto("/about");
  const aboutImage = page.locator(".hp-about-page > img");
  await expect(aboutImage).toBeVisible();
  await aboutImage.evaluate((image) => image.decode());
  await expect(aboutImage).toHaveAttribute("src", "/about-us-payment.webp");

  await page.goto("/contact");
  const contactImages = page.locator(".sh-contact-page img");
  await contactImages.evaluateAll((images) => Promise.all(images.map((image) => image.decode())));
  await expect(page.locator(".sh-contact-illustration")).toHaveCount(2);
  await expect(page.locator(".sh-contact-enamad img")).toHaveAttribute("src", /enamad.*\.webp$/);
  await expect.poll(() => transfers.length).toBeGreaterThanOrEqual(4);
  expect(transfers.every((item) => item.status === 200)).toBe(true);
  expect(transfers.reduce((sum, item) => sum + item.bytes, 0)).toBeLessThan(180_000);
  console.info(`IMAGE_TRANSFER_BUDGET ${JSON.stringify(transfers)}`);
});

test("questionnaire restores the current-session payload without a duplicate session read", async ({ page }) => {
  await installProfileApi(page);
  const sessionReads = [];
  const session = {
    sessionId: "restore-performance-session",
    expiresAt: "2027-01-01T00:00:00Z",
    answers: {},
    flowAnswers: { loan_type: "shahab", entity_type: "person" },
  };
  await page.route("**/api/v1/questionnaire/sessions/current", async (route) => {
    sessionReads.push("current");
    await route.fulfill({ json: session });
  });
  await page.route("**/api/v1/questionnaire/sessions/restore-performance-session", async (route) => {
    sessionReads.push("by-id");
    await route.fulfill({ json: session });
  });
  const navigationStartedAt = Date.now();
  await page.goto("/question/3", { waitUntil: "commit" });
  await expect(page.locator(".hp-question-card")).toBeVisible();
  await expect(page.locator(".hp-questionnaire-page")).not.toHaveAttribute("aria-busy", "true");
  await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  const elapsedMs = Date.now() - navigationStartedAt;
  expect(sessionReads).toEqual(["current"]);
  console.info(`QUESTIONNAIRE_RESTORE ${JSON.stringify({ elapsedMs, sessionReads })}`);
});
