import assert from "node:assert/strict";
import test from "node:test";

import {
  applyRecommendationResultControls,
  formatServerCompatibilityScore,
  recommendationResultControlOptions,
  selectRecommendationResultMode,
} from "../../src/features/recommendation/presentation/recommendationResultControls.mjs";
import { displayItemsForResultMode } from "../../src/features/recommendation/presentation/loanResultDisplayOrder.mjs";

const result = Object.freeze({
  rankedRecommendations: Object.freeze([
    Object.freeze({ loanId: "l-1", lenderName: "بانک ب", loanName: "طرح یک", compatibilityScore: 0.8 }),
    Object.freeze({ loanId: "l-2", lenderName: "بانک الف", loanName: "طرح دو", compatibilityScore: 0.6 }),
    Object.freeze({ loanId: "l-3", lenderName: "بانک ب", loanName: "طرح سه", compatibilityScore: 0.7 }),
  ]),
  lowCompatibilityRecommendations: Object.freeze([
    Object.freeze({ loanId: "low-1", compatibilityScore: 0.1 }),
    Object.freeze({ loanId: "low-2", compatibilityScore: 0.2 }),
  ]),
  needsReview: Object.freeze([Object.freeze({ loanId: "review-1" })]),
});

test("selects the three server-owned partitions without calculating or reordering scores", () => {
  assert.deepEqual(
    selectRecommendationResultMode(result, recommendationResultControlOptions.resultModes.highest).map((item) => item.loanId),
    ["l-1", "l-2", "l-3"],
  );
  assert.deepEqual(
    selectRecommendationResultMode(result, recommendationResultControlOptions.resultModes.lowest).map((item) => item.loanId),
    ["low-1", "low-2"],
  );
  assert.deepEqual(
    selectRecommendationResultMode(result, recommendationResultControlOptions.resultModes.variable).map((item) => item.loanId),
    ["review-1"],
  );
  assert.throws(() => selectRecommendationResultMode(result, "scoreDesc"), /supported/);
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

test("presents only the server low-compatibility partition from its highest supplied score to lowest", () => {
  const items = displayItemsForResultMode(result, "lowest");

  assert.deepEqual(items.map((item) => item.loanId), ["low-2", "low-1"]);
  assert.equal(items[0], result.lowCompatibilityRecommendations[1]);
  assert.equal(items[1], result.lowCompatibilityRecommendations[0]);
  assert.deepEqual(displayItemsForResultMode(result, "highest").map((item) => item.loanId), ["l-1", "l-2", "l-3"]);
  assert.deepEqual(displayItemsForResultMode(result, "variable").map((item) => item.loanId), ["review-1"]);
});
