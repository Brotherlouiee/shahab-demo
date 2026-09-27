import assert from "node:assert/strict";
import test from "node:test";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";

import RecommendationResultScreen from "../../src/features/recommendation/presentation/recommendationResultScreen.mjs";
import { buildRecommendationResultViewModel } from "../../src/features/recommendation/presentation/recommendationResultViewModel.mjs";

function result({ rankedRecommendations = [], lowCompatibilityRecommendations = [], needsReview = [] } = {}) {
  return buildRecommendationResultViewModel({
    dataVersion: "serving.v1",
    configVersion: "recommendation.v1",
    rankedRecommendations,
    lowCompatibilityRecommendations,
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
  assert.match(markup, /بیشترین تطابق/);
  assert.match(markup, /کمترین تطابق/);
  assert.match(markup, /وضعیت متغیر/);
  assert.match(markup, /۹۰٪/);
  assert.match(markup, /href="\/loan-details\?loanId=loan-1"/);
  assert.match(markup, /به‌معنای تأیید دریافت وام نیست/);
});

test("keeps a needs-review item score-free and exposes loading/error states accessibly", () => {
  const reviewMarkup = renderToStaticMarkup(createElement(RecommendationResultScreen, {
    initialMode: "variable",
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

test("renders the server low partition and a clear missing-session recovery state", () => {
  const lowMarkup = renderToStaticMarkup(createElement(RecommendationResultScreen, {
    initialMode: "lowest",
    result: result({
      lowCompatibilityRecommendations: [{
        loanId: "loan-low",
        lenderName: "بانک واقعی",
        loanName: "طرح زیر آستانه",
        compatibilityScore: 0.2,
        compatibilityReason: "تطابق پایین؛ پیشنهاد اصلی نیست",
      }],
    }),
  }));
  const missingMarkup = renderToStaticMarkup(createElement(RecommendationResultScreen, {
    status: "sessionMissing",
    onStartQuestionnaire() {},
  }));

  assert.match(lowMarkup, /تطابق پایین؛ پیشنهاد اصلی نیست/);
  assert.match(lowMarkup, /۲۰٪/);
  assert.match(missingMarkup, /ابتدا پرسشنامه را در همین تب کامل کنید/);
  assert.match(missingMarkup, /شروع پرسشنامه/);
});
