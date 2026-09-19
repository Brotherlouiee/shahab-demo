import { expect, test } from "@playwright/test";

const approvedRoutes = [
  ["/question/3", "۱-پولی که از این وام یا اعتبار به دست می‌آورید"],
  ["/question/4", "۲-اگر دریافت این وام لغو شود"],
  ["/question/5", "۳-در انتخاب یک وام"],
  ["/question/6", "۴-بین مبلغ اقساط ماهانه"],
  ["/question/7", "۵-چقدر برایتان مهم است"],
  ["/question/8", "۶-در حال حاضر، چه کسری از درآمد ماهانه شما"],
  ["/question/9", "۱-تصور کنید کارشناس اعتبارات بانک"],
  ["/question/10", "۲-برای یک سرمایه‌گذاری یا ارتقای کسب‌وکار"],
  ["/question/11", "۳-برای توسعه کار به ۵۰۰ میلیون تومان"],
  ["/question/12", "۴-برای تأمین مبلغ ۱۰۰ میلیون تومان"],
];

test("preserves every approved behavioural path and renders its mapped questionnaire screen", async ({ page }) => {
  for (const [route, expectedQuestionPrefix] of approvedRoutes) {
    await page.goto(route);
    await expect(page).toHaveURL(new RegExp(`${route}$`));
    await expect(page.locator(".hp-questionnaire-page h1")).toContainText(expectedQuestionPrefix);
  }
});
