import { expect, test } from "@playwright/test";
import { installProfileApi } from "./fixtures/profile-api.mjs";

const mobileViewport = { width: 430, height: 900 };
const desktopViewport = { width: 1440, height: 900 };

async function measure(page, viewport, route, selector, prepare) {
  await page.setViewportSize(viewport);
  if (prepare) await prepare();
  await page.goto(route);
  const element = page.locator(selector);
  await expect(element).toBeVisible();
  return element.evaluate(node => {
    const rect = node.getBoundingClientRect();
    return { width: rect.width, left: rect.left };
  });
}

test("about, contact and login retain the mobile canvas on desktop", async ({ page }) => {
  for (const [route, selector] of [
    ["/about", ".hp-about-page"],
    ["/contact", ".sh-contact-page"],
    ["/login", ".hp-mobile-login"],
  ]) {
    const mobile = await measure(page, mobileViewport, route, selector);
    const desktop = await measure(page, desktopViewport, route, selector);
    expect(desktop.width, `${route} canvas width`).toBe(mobile.width);
    expect(desktop.left, `${route} centered desktop offset`).toBe((desktopViewport.width - mobile.width) / 2);
  }

  await page.setViewportSize(desktopViewport);
  await page.goto("/login");
  await expect(page.locator(".hp-menu-button")).toBeVisible();
  await expect(page.locator(".hp-back-button")).toBeVisible();
  expect(await page.locator(".hp-login-form").evaluate(node => node.getBoundingClientRect().width)).toBe(326);
});

test("profile and recommendation history keep the mobile content width on desktop", async ({ page }) => {
  await installProfileApi(page, {
    authenticated: true,
    profile: { phone: "09123456789", firstName: "آزمون", lastName: "کاربر", income: "", job: "", gender: "", avatar: null },
  });
  await page.route("**/api/v1/recommendation-history*", route => route.fulfill({ json: { items: [], nextCursor: null } }));

  for (const [route, selector] of [
    ["/profile", ".hp-account-page:not(.hp-recommendation-history-page)"],
    ["/recommendation-history", ".hp-recommendation-history-page"],
  ]) {
    const mobile = await measure(page, mobileViewport, route, selector);
    const desktop = await measure(page, desktopViewport, route, selector);
    expect(desktop.width, `${route} canvas width`).toBe(mobile.width);
    expect(desktop.left, `${route} centered desktop offset`).toBe((desktopViewport.width - mobile.width) / 2);
  }
});
