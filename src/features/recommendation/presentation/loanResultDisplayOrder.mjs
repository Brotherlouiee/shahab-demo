/** Selects an existing server partition for presentation and applies its agreed low-view floor. */
import { selectRecommendationResultMode, recommendationResultControlOptions } from "./recommendationResultControls.mjs";
export function displayItemsForResultMode(result, mode) {
  if (!result) return [];
  if (mode === "lowest") {
    return selectRecommendationResultMode(result, recommendationResultControlOptions.resultModes.lowest)
      .map((item, index) => ({ item, index }))
      .sort((left, right) => right.item.compatibilityScore - left.item.compatibilityScore || left.index - right.index)
      .map(({ item }) => item);
  }
  if (mode === "variable") return selectRecommendationResultMode(result, recommendationResultControlOptions.resultModes.variable);
  return selectRecommendationResultMode(result, recommendationResultControlOptions.resultModes.highest);
}
