import { expect, test } from "@playwright/test";

const approvedRoutes = [
  ["/question/3", "پولی که از این وام یا اعتبار به دست می‌آورید را دقیقاً در چه راهی صرف می‌کنید؟"],
  ["/question/4", "اگر دریافت این وام لغو شود و نتوانید آن را بگیرید"],
  ["/question/5", "در انتخاب یک وام، کدام حالت برای شما در اولویت اول قرار دارد؟"],
  ["/question/6", "بین مبلغ اقساط ماهانه و مدت‌زمان وام، کدام حالت را انتخاب می‌کنید؟"],
  ["/question/7", "چقدر برایتان مهم است که شرایط پرداخت اقساط قابل تغییر و منعطف باشد؟"],
  ["/question/8", "در حال حاضر، چه کسری از درآمد ماهانه شما صرف پرداخت اقساط"],
  ["/question/9", "تصور کنید روبروی کارشناس اعتبارات بانک نشسته‌اید"],
  ["/question/10", "برای یک سرمایه‌گذاری یا ارتقای کسب‌وکار به مبلغ ۲۰۰ میلیون تومان نیاز دارید."],
  ["/question/11", "برای توسعه کار به ۵۰۰ میلیون تومان سرمایه نیاز دارید."],
  ["/question/12", "فرض کنید برای تأمین مبلغ ۱۰۰ میلیون تومان"],
];

for (const [route, expectedQuestionPrefix] of approvedRoutes) {
  test(`preserves approved behavioural path ${route} and renders its canonical questionnaire screen`, async ({ page }) => {
    await page.goto(route);
    await expect(page).toHaveURL(new RegExp(`${route}$`));
    await expect(page.locator(".hp-questionnaire-page h1")).toContainText(expectedQuestionPrefix);
  });
}
