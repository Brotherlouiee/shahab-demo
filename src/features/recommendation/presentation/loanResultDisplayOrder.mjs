/**
 * Selects an existing server partition for presentation. Only the explicitly
 * requested low-compatibility view is ordered by its server-supplied score;
 * scores, thresholds and membership are never calculated in the browser.
 */
export function displayItemsForResultMode(result, mode) {
  if (!result) return [];
  if (mode === "lowest") {
    return result.lowCompatibilityRecommendations
      .map((item, index) => ({ item, index }))
      .sort((left, right) => right.item.compatibilityScore - left.item.compatibilityScore || left.index - right.index)
      .map(({ item }) => item);
  }
  if (mode === "variable") return result.needsReview;
  return result.rankedRecommendations;
}
