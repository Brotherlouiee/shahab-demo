import assert from "node:assert/strict";
import test from "node:test";

import { buildRecommendationResultDisplayState } from "../../src/features/recommendation/presentation/recommendationResultStates.mjs";
import { buildRecommendationResultViewModel } from "../../src/features/recommendation/presentation/recommendationResultViewModel.mjs";

function viewModel({ rankedRecommendations = [], needsReview = [] } = {}) {
  return buildRecommendationResultViewModel({
    dataVersion: "serving.v1",
    configVersion: "recommendation.v1",
    rankedRecommendations,
    needsReview,
  });
}

const ranked = [
  {
    loanId: "loan-1",
    lenderName: "بانک اول",
    loanName: "طرح اول",
    compatibilityScore: 0.9,
    compatibilityReason: "دلیل سرور",
  },
  {
    loanId: "loan-2",
    lenderName: "بانک دوم",
    loanName: "طرح دوم",
    compatibilityScore: 0.7,
    compatibilityReason: "دلیل دوم سرور",
  },
];
const review = {
  loanId: "loan-review",
  lenderName: "بانک بررسی",
  loanName: "طرح ناقص",
  rankingExcludedReasons: ["interestRate:unknown"],
};

test("keeps ranked results in server order and exposes a separate needs-review section", () => {
  const state = buildRecommendationResultDisplayState(
    viewModel({ rankedRecommendations: ranked, needsReview: [review] }),
  );

  assert.equal(state.ranked.kind, "ranked");
  assert.deepEqual(state.ranked.items.map((item) => item.loanId), ["loan-1", "loan-2"]);
  assert.equal(state.ranked.items[0].compatibilityScore, 0.9);
  assert.equal(state.needsReview.kind, "needsReview");
  assert.equal("compatibilityScore" in state.needsReview.items[0], false);
  assert.equal(state.emptyState, null);
});

test("distinguishes needs-review-only and no-candidate results", () => {
  const reviewOnly = buildRecommendationResultDisplayState(viewModel({ needsReview: [review] }));
  const noCandidate = buildRecommendationResultDisplayState(viewModel());

  assert.equal(reviewOnly.ranked, null);
  assert.equal(reviewOnly.needsReview.kind, "needsReview");
  assert.equal(reviewOnly.emptyState.kind, "needsReviewOnly");
  assert.match(reviewOnly.emptyState.message, /دادهٔ کافی/);
  assert.equal(noCandidate.emptyState.kind, "noCandidate");
  assert.match(noCandidate.emptyState.message, /بازبینی/);
});

test("distinguishes zero after a manual filter without implementing or reordering that filter", () => {
  const result = viewModel({ rankedRecommendations: ranked, needsReview: [review] });
  const state = buildRecommendationResultDisplayState(result, {
    hasManualFilters: true,
    visibleRankedRecommendations: [],
  });

  assert.equal(state.ranked, null);
  assert.equal(state.needsReview.kind, "needsReview");
  assert.equal(state.emptyState.kind, "zeroAfterFilter");
  assert.throws(
    () =>
      buildRecommendationResultDisplayState(result, {
        hasManualFilters: true,
        visibleRankedRecommendations: [result.rankedRecommendations[1], result.rankedRecommendations[0]],
      }),
    /preserve server order/,
  );
});
