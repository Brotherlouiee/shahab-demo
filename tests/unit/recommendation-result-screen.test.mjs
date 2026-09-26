import assert from "node:assert/strict";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import RecommendationResultScreen from "../../src/features/recommendation/presentation/recommendationResultScreen.mjs";
import { buildRecommendationResultViewModel } from "../../src/features/recommendation/presentation/recommendationResultViewModel.mjs";

function result({ rankedRecommendations = [], needsReview = [] } = {}) {
  return buildRecommendationResultViewModel({
    dataVersion: "serving.v1",
    configVersion: "recommendation.v1",
    rankedRecommendations,
    needsReview,
  });
}

test("renders RTL-labelled manual controls and the server score as display text", () => {
  const markup = renderToStaticMarkup(createElement(RecommendationResultScreen, {
    result: result({
      rankedRecommendations: [{
        loanId: "loan-1",
        lenderName: "بانک الف",
        loanName: "طرح الف",
        compatibilityScore: 0.9,
        compatibilityReason: "این دلیل از سرور آمده است.",
      }],
    }),
  }));

  assert.match(markup, /dir="rtl"/);
  assert.match(markup, /for="recommendation-lender-filter"/);
  assert.match(markup, /for="recommendation-sort"/);
  assert.match(markup, /۹۰٪/);
  assert.match(markup, /href="\/loan-details\?loanId=loan-1"/);
  assert.match(markup, /به‌معنای تأیید دریافت وام نیست/);
});

test("keeps a needs-review item score-free and exposes loading/error states accessibly", () => {
  const reviewMarkup = renderToStaticMarkup(createElement(RecommendationResultScreen, {
    result: result({
      needsReview: [{
        loanId: "loan-review",
        lenderName: "بانک بررسی",
        loanName: "طرح ناقص",
        rankingExcludedReasons: ["interestRate:unknown"],
      }],
    }),
  }));
  const loadingMarkup = renderToStaticMarkup(createElement(RecommendationResultScreen, { status: "loading" }));
  const errorMarkup = renderToStaticMarkup(createElement(RecommendationResultScreen, { status: "error", onRetry() {} }));

  assert.match(reviewMarkup, /برای مقایسهٔ دقیق این گزینه/);
  assert.doesNotMatch(reviewMarkup, /درصد تطابق محاسبه‌شده/);
  assert.match(loadingMarkup, /role="status"/);
  assert.match(errorMarkup, /role="alert"/);
  assert.match(errorMarkup, /تلاش مجدد/);
});
