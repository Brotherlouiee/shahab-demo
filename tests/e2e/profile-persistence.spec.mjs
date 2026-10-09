import { expect, test } from "@playwright/test";
import { installProfileApi } from "./fixtures/profile-api.mjs";

test("personal-info persists after verification, blocks failed storage and permits retry", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const api = await installProfileApi(page);
  api.failWrites = 1;
  await page.goto("/personal-info");
  const inputs = page.locator(".hp-personal-info-form input");
  await inputs.nth(0).fill("آزمون");
  await inputs.nth(1).fill("تست");
  await inputs.nth(2).fill("۹۱۲۳۴۵۶۷۸");
  await page.locator(".hp-personal-dropdown-trigger").nth(0).click();
  await page.getByRole("option", { name: "تا ۲۲ میلیون تومان" }).click();
  await page.locator(".hp-personal-dropdown-trigger").nth(1).click();
  await page.getByRole("option", { name: "کارمند (شرکت یا اداره)" }).click();
  await page.getByRole("button", { name: "تایید" }).click();
  await expect(page).toHaveURL(/\/verify-code$/);
  for (const [i, digit] of [..."۱۲۳۴۵۶"].entries()) await page.locator(".hp-loan-otp-row input").nth(i).fill(digit);
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  await expect(page.locator(".hp-loan-otp-error")).toContainText("انجام نشد");
  await expect(page).toHaveURL(/\/verify-code$/);
  expect(await page.evaluate(() => localStorage.getItem("shahab.accountProfile"))).toBeNull();
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  await expect(page).toHaveURL(/\/analysis$/);
  expect(api.verifies).toBe(1);
  expect(api.profile).toMatchObject({ phone: "09912345678", firstName: "آزمون", income: "up-to-22", job: "employee" });
});

test("profile preserves eleven digits and never treats a failed save as success", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const api = await installProfileApi(page, { profile: { phone: "09912345678", firstName: "آزمون", lastName: "تست", income: "up-to-22", job: "employee", gender: "", avatar: null } });
  await page.goto("/");
  await page.locator("button.hp-menu-button").click();
  await page.getByRole("button", { name: "ورود کاربر" }).click();
  await page.getByLabel("شماره تلفن همراه").fill("912345678");
  await page.getByRole("button", { name: "ارسال کد یکبار مصرف" }).click();
  for (let i = 0; i < 6; i += 1) await page.getByLabel(`رقم ${i + 1} کد یکبار مصرف`).fill(String(i + 1));
  await page.getByRole("button", { name: "ورود به حساب" }).click();
  await page.locator("button.hp-menu-button").click();
  await expect(page.locator(".hp-sidebar-name")).toHaveText("آزمون تست");
  await page.getByRole("button", { name: "پروفایل کاربر" }).click();
  const form = page.locator(".hp-account-profile-form");
  await expect(form.locator("input").first()).toHaveValue("۰۹۹۱۲۳۴۵۶۷۸");
  await expect(form.locator("input").nth(1)).toHaveValue("آزمون");
  await form.locator("input").nth(1).fill("علی");
  api.failWrites = 1;
  await page.getByRole("button", { name: "ذخیره تغییرات" }).click();
  await expect(page.getByRole("alert")).toContainText("انجام نشد");
  expect(JSON.parse(await page.evaluate(() => localStorage.getItem("shahab.accountProfile"))).firstName).toBe("آزمون");
  await expect(form.locator("input").nth(1)).toHaveValue("علی");
  await page.getByRole("button", { name: "ذخیره تغییرات" }).click();
  await expect(page.getByRole("status")).toHaveText("تغییرات ذخیره شد.");
  expect(api.profile.firstName).toBe("علی");
  await page.screenshot({ path: "docs/evidence/us-09-t072/profile-mobile.png" });
  expect(await page.evaluate(() => Object.entries(localStorage).some(([key, value]) => /accessToken|fixture/.test(key + value)))).toBe(false);
});


test("phone-only login shows generic sidebar name and refreshes saved database name", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  const api = await installProfileApi(page);
  await page.goto("/");
  await page.locator("button.hp-menu-button").click();
  await page.getByRole("button", { name: "ورود کاربر" }).click();
  await page.getByLabel("شماره تلفن همراه").fill("912345678");
  await page.getByRole("button", { name: "ارسال کد یکبار مصرف" }).click();
  for (let i = 0; i < 6; i += 1) await page.getByLabel(`رقم ${i + 1} کد یکبار مصرف`).fill(String(i + 1));
  await page.getByRole("button", { name: "ورود به حساب" }).click();
  await page.locator("button.hp-menu-button").click();
  await expect(page.locator(".hp-sidebar-name")).toHaveText("کاربر");
  await page.getByRole("button", { name: "بستن منو" }).click({ position: { x: 10, y: 400 } });
  api.profile.firstName = "علی";
  api.profile.lastName = "احمدی";
  await page.locator("button.hp-menu-button").click();
  await expect(page.locator(".hp-sidebar-name")).toHaveText("علی احمدی");
  await page.screenshot({ path: "docs/evidence/us-09-t072/sidebar-name-mobile.png" });
});
