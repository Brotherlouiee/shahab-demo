import assert from "node:assert/strict";
import test from "node:test";

import {
  applyRecommendationResultControls,
  formatServerCompatibilityScore,
  recommendationResultControlOptions,
} from "../../src/features/recommendation/presentation/recommendationResultControls.mjs";

const result = Object.freeze({
  rankedRecommendations: Object.freeze([
    Object.freeze({ loanId: "l-1", lenderName: "بانک ب", loanName: "طرح یک", compatibilityScore: 0.8 }),
    Object.freeze({ loanId: "l-2", lenderName: "بانک الف", loanName: "طرح دو", compatibilityScore: 0.6 }),
    Object.freeze({ loanId: "l-3", lenderName: "بانک ب", loanName: "طرح سه", compatibilityScore: 0.7 }),
  ]),
  needsReview: Object.freeze([]),
});

test("filters only by lender while preserving the server sequence for the filter boundary", () => {
  const controls = applyRecommendationResultControls(result, { lenderName: "بانک ب" });

  assert.equal(controls.hasManualFilters, true);
  assert.deepEqual(controls.availableLenders, ["بانک ب", "بانک الف"]);
  assert.deepEqual(controls.filteredRankedRecommendations.map((item) => item.loanId), ["l-1", "l-3"]);
  assert.deepEqual(controls.orderedRankedRecommendations.map((item) => item.loanId), ["l-1", "l-3"]);
});

test("sorts only the already visible display items with a stable lender-name sort", () => {
  const controls = applyRecommendationResultControls(result, {
    sort: recommendationResultControlOptions.sorts.lenderNameAsc,
  });

  assert.deepEqual(controls.orderedRankedRecommendations.map((item) => item.loanId), ["l-2", "l-1", "l-3"]);
  assert.equal(controls.orderedRankedRecommendations[1], result.rankedRecommendations[0]);
  assert.equal(controls.orderedRankedRecommendations[2], result.rankedRecommendations[2]);
});

test("rejects unknown filters and never treats a score as a sorting input", () => {
  assert.throws(() => applyRecommendationResultControls(result, { lenderName: "بانک ناشناخته" }), /present/);
  assert.throws(() => applyRecommendationResultControls(result, { sort: "scoreDesc" }), /supported/);
  assert.equal(formatServerCompatibilityScore(0.905), "۹۱٪");
  assert.throws(() => formatServerCompatibilityScore(1.1), /server-supplied/);
});
