import { expect, test } from "@playwright/test";
import { installProfileApi } from "./fixtures/profile-api.mjs";

const enamad = "https://trustseal.enamad.ir/?id=8316058&Code=YCgntg1cyA41RMpSVRpI0XieeveRCHnk";

for (const viewport of [{ width: 390, height: 974 }, { width: 1440, height: 1000 }, { width: 320, height: 844 }]) {
  test(`contact page, links and history work at ${viewport.width}px`, async ({ page }, info) => {
    await page.setViewportSize(viewport);
    await installProfileApi(page);
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    const externalRequests = [];
    page.on("request", request => { if (/(^|\.)(linkedin\.com|enamad\.ir)$/.test(new URL(request.url()).hostname)) externalRequests.push(request.url()); });
    await page.goto(viewport.width >= 768 ? "/contact" : "/");
    await page.getByRole("button", { name: "menu", exact: true }).click();
    const menu = page.locator(".hp-sidebar-menu");
    await expect(menu.locator("button")).toHaveText(["ورود کاربر", "تماس با ما", "درباره ما"]);
    await expect(page.locator(".hp-sidebar-support")).toHaveCount(0);
    expect(await menu.locator("button").first().evaluate(el => getComputedStyle(el).borderBottomWidth)).toBe("1px");
    await expect(menu.getByRole("button", { name: "تماس با ما" }).locator("img")).toHaveAttribute("src", /call-calling|^data:image\/svg\+xml/);
    await menu.getByRole("button", { name: "تماس با ما" }).click();
    await expect(page).toHaveURL(/\/contact$/);
    await expect(page.getByRole("main", { name: "تماس با ما" })).toBeVisible();
    await expect(page.locator(".hp-sidebar-layer")).toHaveAttribute("aria-hidden", "true");
    await expect(page.locator("a[href='tel:09371410602']")).toHaveText("۰۹۳۷۱۴۱۰۶۰۲");
    await expect(page.getByText("از شنبه تا چهارشنبه")).toBeVisible();
    await expect(page.getByText("۹ تا ۲۰", { exact: true })).toBeVisible();
    await expect(page.getByRole("link", { name: "لینکدین", exact: true })).toHaveAttribute("href", "https://www.linkedin.com/company/shahabfintech");
    await expect(page.getByRole("link", { name: "استعلام نماد اعتماد الکترونیکی شهاب" })).toHaveAttribute("href", enamad);
    for (const label of ["تلگرام", "اینستاگرام", "ایکس"]) await expect(page.getByRole("button", { name: `${label}؛ صفحه هنوز ایجاد نشده است` })).toBeDisabled();
    await expect(page.locator(".sh-contact-page form")).toHaveCount(0);
    await page.reload();
    await expect(page).toHaveURL(/\/contact$/);
    await expect(page.locator(".sh-contact-details")).toBeVisible();
    await page.evaluate(() => document.fonts.ready);
    await page.locator(".sh-contact-page img").evaluateAll(images => Promise.all(images.map(image => image.decode())));
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    const screenshot = await page.screenshot({ fullPage: true, animations: "disabled" });
    await info.attach(`contact-${viewport.width}`, { body: screenshot, contentType: "image/png" });
    await page.screenshot({ path: `test-results/contact-${viewport.width}.png`, fullPage: true });
    expect(externalRequests).toEqual([]); // Badges are local; no third-party request before a click.
    // Test navigation without contacting third-party services or placing calls.
    for (const [name, destination] of [["لینکدین", "https://www.linkedin.com/company/shahabfintech"], ["استعلام نماد اعتماد الکترونیکی شهاب", enamad]]) {
      let sentReferer;
      await page.context().route(destination, route => {
        sentReferer = route.request().headers().referer;
        return route.fulfill({ contentType: "text/html", body: "External destination fixture" });
      });
      const popupPromise = page.waitForEvent("popup");
      await page.getByRole("link", { name, exact: true }).click();
      const popup = await popupPromise;
      await expect(popup).toHaveURL(destination);
      if (destination === enamad) {
        expect(sentReferer).toBe(`${new URL(page.url()).origin}/`);
        expect(new URL(popup.url()).searchParams.has("code")).toBe(false);
      }
      expect(await popup.evaluate(() => window.opener === null)).toBe(true);
      await popup.close();
    }
    await page.getByRole("button", { name: "menu", exact: true }).click();
    await menu.getByRole("button", { name: "درباره ما" }).click();
    await expect(page).toHaveURL(/\/about$/);
    await page.goBack();
    await expect(page).toHaveURL(/\/contact$/);
    await expect(page.locator(".sh-contact-details")).toBeVisible();
    await page.goForward();
    await expect(page).toHaveURL(/\/about$/);
    await page.goBack();
    await page.getByRole("button", { name: "بازگشت", exact: true }).click();
    await expect(page).toHaveURL(/\/$/);
    expect(errors).toEqual([]);
  });
}

test("authenticated drawer preserves account items with contact before about below separator", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await installProfileApi(page, { authenticated: true, profile: { phone: "09912345678", firstName: "آزمون", lastName: "تست" } });
  await page.goto("/");
  await page.locator("button.hp-menu-button").click();
  await expect(page.locator(".hp-sidebar-name")).toHaveText("آزمون تست");
  const buttons = page.locator(".hp-sidebar-menu button");
  await expect(buttons).toHaveText(["پروفایل کاربر", "سوابق درخواست وام", "سوابق وام‌های توصیه شده", "وام‌های نشان شده", "تماس با ما", "درباره ما", "خروج از حساب کاربری"]);
  expect(await buttons.nth(3).evaluate(el => getComputedStyle(el).borderBottomWidth)).toBe("1px");
  await page.getByRole("button", { name: "تماس با ما", exact: true }).click();
  await expect(page.locator(".sh-contact-details")).toBeVisible();
  await page.getByRole("button", { name: "menu", exact: true }).click();
  await expect(page.locator(".hp-sidebar-name")).toHaveText("آزمون تست");
});
