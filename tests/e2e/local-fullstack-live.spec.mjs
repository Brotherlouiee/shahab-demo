import { expect, test } from "@playwright/test";
import { readFileSync } from "node:fs";

const questionnaire = JSON.parse(
  readFileSync(new URL("../../data/contracts/questionnaire-configuration.v1.json", import.meta.url), "utf8"),
);

test.describe("local full-stack recommendation journey", () => {
  test.skip(process.env.SHAHAB_LIVE_E2E !== "1", "requires the local Compose stack and published catalog");

  test("submits the questionnaire through Vite and renders live recommendations", async ({ page }) => {
    test.setTimeout(60_000);
    const recommendationResponse = page.waitForResponse(
      (response) => response.url().endsWith("/api/v1/recommendations") && response.request().method() === "POST",
    );

    await page.goto("/question/3");
    for (const question of questionnaire.questions) {
      await expect(page.getByRole("heading", { name: question.prompt })).toBeVisible();
      const answer = page.getByRole("radio").first();
      await answer.click();
      await expect(answer).toBeChecked();
      const next = page.getByRole("button", { name: "پاسخ به سوال بعد" });
      await expect(next).toBeEnabled();
      await next.click();
    }

    const response = await recommendationResponse;
    expect(response.status()).toBe(200);
    const payload = await response.json();
    expect(payload.rankedRecommendations.length).toBeGreaterThan(0);
    expect(payload.needsReview.length).toBeGreaterThan(0);
    expect(Object.keys(response.request().postDataJSON())).toEqual(["sessionId"]);

    await expect(page).toHaveURL(/\/loan-results$/);
    await expect(page.locator("main.hp-recommendation-results-screen")).toBeVisible();
    await expect(page.locator(".hp-recommendation-section").first()).toBeVisible();
    await page.locator(".hp-recommendation-section .hp-loan-docs-link").first().click();
    await expect(page.locator(".hp-loan-details-conditions")).toBeVisible();
  });
});
