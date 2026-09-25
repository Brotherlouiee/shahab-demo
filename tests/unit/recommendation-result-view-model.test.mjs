import assert from "node:assert/strict";
import test from "node:test";

import { buildRecommendationResultViewModel } from "../../src/features/recommendation/presentation/recommendationResultViewModel.mjs";

const response = {
  dataVersion: "serving.v1",
  configVersion: "recommendation.v1",
  rankedRecommendations: [
    {
      loanId: "loan/a",
      lenderName: "بانک نمونه",
      loanName: "طرح نمونه",
      compatibilityScore: 0.75,
      compatibilityReason: "سقف وام و نرخ سود با ترجیح شما هماهنگ است.",
    },
  ],
  needsReview: [
    {
      loanId: "loan-review",
      lenderName: "بانک بررسی",
      loanName: "طرح اطلاعات ناقص",
      rankingExcludedReasons: ["interestRate:unknown"],
    },
  ],
};

test("maps server-calculated ranked and needs-review read models without changing score or order", () => {
  const viewModel = buildRecommendationResultViewModel(response);

  assert.equal(viewModel.dataVersion, "serving.v1");
  assert.equal(viewModel.configVersion, "recommendation.v1");
  assert.equal(viewModel.rankedRecommendations[0].compatibilityScore, 0.75);
  assert.equal(viewModel.rankedRecommendations[0].compatibilityReason, response.rankedRecommendations[0].compatibilityReason);
  assert.equal(viewModel.rankedRecommendations[0].detailsHref, "/loan-details?loanId=loan%2Fa");
  assert.equal(viewModel.needsReview[0].warning.includes("اطلاعات"), true);
  assert.deepEqual(viewModel.needsReview[0].rankingExcludedReasons, ["interestRate:unknown"]);
});

test("keeps a needs-review item free of score and provides a safe details action", () => {
  const viewModel = buildRecommendationResultViewModel(response);
  const review = viewModel.needsReview[0];

  assert.equal("compatibilityScore" in review, false);
  assert.equal(review.detailsHref, "/loan-details?loanId=loan-review");
});

test("rejects incomplete or client-invented response fields instead of guessing a result", () => {
  assert.throws(
    () =>
      buildRecommendationResultViewModel({
        ...response,
        rankedRecommendations: [{ ...response.rankedRecommendations[0], compatibilityReason: " " }],
      }),
    /compatibilityReason/,
  );
  assert.throws(
    () =>
      buildRecommendationResultViewModel({
        ...response,
        needsReview: [{ ...response.needsReview[0], rankingExcludedReasons: "interestRate:unknown" }],
      }),
    /rankingExcludedReasons/,
  );
});
