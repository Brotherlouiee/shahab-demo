import { expect, test } from "@playwright/test";

async function login(page, suffix) {
  await page.goto("/");
  await page.locator("button.hp-menu-button").click();
  const logout = page.getByRole("button", { name: "خروج از حساب کاربری" });
  if (await logout.isVisible()) {
    await logout.click();
    await page.locator("button.hp-menu-button").click();
  }
  await page.getByRole("button", { name: "ورود کاربر" }).click();
  await page.getByLabel("شماره تلفن همراه").fill(suffix);
  const requested = page.waitForResponse(r => r.url().endsWith("/account-access/request"));
  await page.getByRole("button", { name: "ارسال کد یکبار مصرف" }).click();
  expect((await requested).status()).toBe(200);
  for (let i = 0; i < 6; i += 1) await page.getByLabel(`رقم ${i + 1} کد یکبار مصرف`).fill(String(i + 1));
  const verified = page.waitForResponse(r => r.url().endsWith("/account-access/verify"));
  await page.getByRole("button", { name: "ورود به حساب" }).click();
  expect((await verified).status()).toBe(200);
  await page.locator("button.hp-menu-button").click();
}

test("real Vite proxy and API accept fake OTP and create phone-only database profile", async ({ page }) => {
  await login(page, "123456789");
  await expect(page.locator(".hp-sidebar-name")).toHaveText("کاربر");
  await page.getByRole("button", { name: "پروفایل کاربر" }).click();
  await expect(page.locator(".hp-account-profile-form input").first()).toHaveValue("۰۹۱۲۳۴۵۶۷۸۹");
});

test("personal-info requests real API OTP and saved database name is recovered on fresh login", async ({ page }) => {
  await page.goto("/personal-info");
  const inputs = page.locator(".hp-personal-info-form input");
  await inputs.nth(0).fill("آزمون");
  await inputs.nth(1).fill("تست");
  await inputs.nth(2).fill("987654321");
  await page.locator(".hp-personal-dropdown-trigger").nth(0).click();
  await page.getByRole("option", { name: "تا ۲۲ میلیون تومان" }).click();
  await page.locator(".hp-personal-dropdown-trigger").nth(1).click();
  await page.getByRole("option", { name: "کارمند (شرکت یا اداره)" }).click();
  const requested = page.waitForResponse(r => r.url().endsWith("/account-access/request"));
  await page.getByRole("button", { name: "تایید" }).click();
  expect((await requested).status()).toBe(200);
  await expect(page).toHaveURL(/\/verify-code$/);
  for (const [i, digit] of [..."123456"].entries()) await page.locator(".hp-loan-otp-row input").nth(i).fill(digit);
  const saved = page.waitForResponse(r => r.url().endsWith("/profiles") && r.request().method() === "PUT");
  await page.getByRole("button", { name: "تایید و جستجوی وام" }).click();
  const response = await saved;
  expect(response.status()).toBe(200);
  expect(await response.json()).toMatchObject({ firstName: "آزمون", lastName: "تست", income: "up-to-22", job: "employee" });
  await expect(page).toHaveURL(/\/analysis$/);
  await login(page, "987654321");
  await expect(page.locator(".hp-sidebar-name")).toHaveText("آزمون تست");
});
