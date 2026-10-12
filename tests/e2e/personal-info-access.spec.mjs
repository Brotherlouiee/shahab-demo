import { expect, test } from "@playwright/test";

// Client interaction contracts; PostgreSQL/API proof is in tests/profile-live.
test("server-restored profile has a readonly phone and storage retry sends no OTP", async ({ page }) => {
  const otp = [];
  const profile = { phone: "09011112222", firstName: "آزمون", lastName: "کاربر", income: "up-to-22", job: "employee", gender: "female", avatar: null };
  let failWrite = true;
  await page.route("**/api/v1/account-access/**", route => {
    if (route.request().url().endsWith("/session")) return route.fulfill({ json: { phone: profile.phone, expiresIn: 67 } });
    otp.push(route.request().url());
    return route.fulfill({ status: 500, json: {} });
  });
  await page.route("**/api/v1/profiles/me", route => route.fulfill({ json: profile }));
  await page.route("**/api/v1/profiles", route => failWrite ? route.fulfill({ status: 503, json: {} }) : route.fulfill({ json: route.request().postDataJSON() }));
  await page.goto("/personal-info");
  const inputs = page.locator(".hp-personal-info-form input");
  await expect(inputs.nth(2)).toHaveValue("۰۱۱۱۱۲۲۲۲");
  await expect(inputs.nth(2)).not.toBeEditable();
  await inputs.first().fill("مریم");
  await page.getByRole("button", { name: "تایید", exact: true }).click();
  await expect(page.getByRole("alert")).toContainText("انجام نشد");
  await expect(inputs.first()).toHaveValue("مریم");
  failWrite = false;
  await page.getByRole("button", { name: "تایید", exact: true }).click();
  await expect(page).toHaveURL(/\/analysis$/);
  expect(otp).toEqual([]);
});

test("expiry rejects the canonical answer without creating and replaying a new questionnaire", async ({ page }) => {
  let starts = 0;
  await page.route("**/api/v1/questionnaire/sessions", route => {
    starts += 1;
    return route.fulfill({ status: 201, json: { sessionId: "expired-fixture", expiresAt: "2000-01-01T00:00:00Z", answers: {} } });
  });
  await page.route("**/api/v1/questionnaire/sessions/expired-fixture/answers/Q1", route => route.fulfill({ status: 410, json: {} }));
  await page.goto("/question/3");
  await page.getByRole("radio").first().click();
  await page.getByRole("button", { name: "پاسخ به سوال بعد" }).click();
  await expect(page.getByRole("alert")).toContainText("مهلت پرسشنامه تمام شده");
  expect(starts).toBe(1);
  await expect(page.getByRole("radio").first()).toHaveAttribute("aria-checked", "false");
});
