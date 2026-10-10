import { expect, test } from "@playwright/test";

test.use({ viewport: { width: 390, height: 844 } });

async function signIn(page) {
  await page.goto("/");
  await page.locator("button.hp-menu-button").click();
  await page.getByRole("button", { name: "ورود کاربر" }).click();
  await page.getByLabel("شماره تلفن همراه").fill("912345678");
  const requested = page.waitForResponse(response => response.url().endsWith("/account-access/request"));
  await page.getByRole("button", { name: "ارسال کد یکبار مصرف" }).click();
  expect((await requested).status()).toBe(200);
  for (let index = 0; index < 6; index += 1) await page.getByLabel(`رقم ${index + 1} کد یکبار مصرف`).fill(String(index + 1));
  const verified = page.waitForResponse(response => response.url().endsWith("/account-access/verify"));
  await page.getByRole("button", { name: "ورود به حساب" }).click();
  expect((await verified).status()).toBe(200);
  await page.locator("button.hp-menu-button").click();
}

test("logout requires confirmation and preserves access when cancelled", async ({ page }) => {
  await signIn(page);
  await expect(page.locator(".hp-sidebar-name")).toBeVisible();

  await page.getByRole("button", { name: "خروج از حساب کاربری" }).click();
  const dialog = page.getByRole("alertdialog", { name: "آیا از خروج از حساب کاربری‌تان مطمئن هستید؟" });
  await expect(dialog).toBeVisible();
  await expect(dialog.getByRole("button", { name: "خیر" })).toBeVisible();
  await expect(dialog.getByRole("button", { name: "بله" })).toBeVisible();

  await dialog.getByRole("button", { name: "خیر" }).click();
  await expect(dialog).toBeHidden();
  await expect(page.locator(".hp-sidebar-name")).toBeVisible();

  await page.getByRole("button", { name: "خروج از حساب کاربری" }).click();
  const loggedOut = page.waitForResponse(response => response.url().endsWith("/account-access/logout") && response.request().method() === "POST");
  await page.getByRole("alertdialog", { name: "آیا از خروج از حساب کاربری‌تان مطمئن هستید؟" }).getByRole("button", { name: "بله" }).click();
  expect((await loggedOut).status()).toBe(204);
  await expect(page.getByRole("button", { name: "بررسی واجد شرایط بودن" })).toBeVisible();
});
