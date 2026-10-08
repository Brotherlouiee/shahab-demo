import { expect, test } from "@playwright/test";

test("guest signs in only from the hamburger menu and sees the authenticated menu", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "menu" }).click();
  await expect(page.getByRole("button", { name: "ورود کاربر" })).toBeVisible();
  await expect(page.getByRole("button", { name: "درباره ما" })).toBeVisible();
  await expect(page.getByRole("button", { name: "پروفایل کاربر" })).toHaveCount(0);

  await page.getByRole("button", { name: "ورود کاربر" }).click();
  await page.getByLabel("شماره تلفن همراه").fill("912345678");
  await page.getByRole("button", { name: "ارسال کد یکبار مصرف" }).click();
  const digits = page.locator(".hp-otp-row input");
  for (let index = 0; index < 6; index += 1) await digits.nth(index).fill(String(index + 1));

  await page.getByRole("button", { name: "menu" }).click();
  await expect(page.getByRole("button", { name: "پروفایل کاربر" })).toBeVisible();
  await expect(page.getByRole("button", { name: "وام‌های نشان شده" })).toBeVisible();
  await expect(page.getByRole("button", { name: "خروج از حساب کاربری" })).toBeVisible();
});

test("profile phone is immutable and oversized photos are rejected", async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem("shahab.accountProfile", JSON.stringify({ firstName: "کاربر", lastName: "آزمایشی", phone: "۰۹۱۲۳۴۵۶۷۸۹" }));
  });
  await page.goto("/profile");
  await expect(page.getByLabel("شماره تلفن همراه")).toHaveAttribute("readonly", "");
  await page.locator('input[type="file"]').setInputFiles({ name: "too-large.png", mimeType: "image/png", buffer: Buffer.alloc(100 * 1024 + 1) });
  await expect(page.getByRole("alert")).toContainText("۱۰۰ کیلوبایت");
});
