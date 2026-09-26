/**
 * Local presentation controls for a recommendation result already produced by the server.
 *
 * Filtering is limited to lender identity and sorting is limited to explicit display order.
 * This module never calculates, normalizes or compares compatibility scores.
 */
const ALL_LENDERS = "all";
const SORTS = Object.freeze({
  serverOrder: "serverOrder",
  lenderNameAsc: "lenderNameAsc",
});

export function applyRecommendationResultControls(
  result,
  { lenderName = ALL_LENDERS, sort = SORTS.serverOrder } = {},
) {
  const ranked = requireRankedRecommendations(result);
  if (typeof lenderName !== "string") {
    throw new TypeError("lenderName must be a string");
  }
  if (!Object.values(SORTS).includes(sort)) {
    throw new TypeError("sort must be a supported display sort");
  }

  const availableLenders = uniqueLenders(ranked);
  if (lenderName !== ALL_LENDERS && !availableLenders.includes(lenderName)) {
    throw new TypeError("lenderName must be present in ranked recommendations");
  }

  const filteredRankedRecommendations = ranked.filter(
    (item) => lenderName === ALL_LENDERS || item.lenderName === lenderName,
  );
  const orderedRankedRecommendations = stableDisplaySort(filteredRankedRecommendations, sort);

  return Object.freeze({
    availableLenders: Object.freeze(availableLenders),
    hasManualFilters: lenderName !== ALL_LENDERS,
    lenderName,
    sort,
    filteredRankedRecommendations: Object.freeze(filteredRankedRecommendations),
    orderedRankedRecommendations: Object.freeze(orderedRankedRecommendations),
  });
}

/**
 * Formats a server-supplied normalized score for display only. It does not
 * participate in filtering, sorting or recommendation eligibility.
 */
export function formatServerCompatibilityScore(score) {
  if (typeof score !== "number" || !Number.isFinite(score) || score < 0 || score > 1) {
    throw new TypeError("compatibility score must be a server-supplied number from 0 to 1");
  }
  return `${Math.round(score * 100).toLocaleString("fa-IR")}٪`;
}

export const recommendationResultControlOptions = Object.freeze({
  allLenders: ALL_LENDERS,
  sorts: SORTS,
});

function requireRankedRecommendations(result) {
  if (!result || typeof result !== "object" || !Array.isArray(result.rankedRecommendations)) {
    throw new TypeError("result must contain rankedRecommendations");
  }
  return result.rankedRecommendations;
}

function uniqueLenders(rankedRecommendations) {
  return [...new Set(rankedRecommendations.map((item) => item.lenderName))];
}

function stableDisplaySort(items, sort) {
  if (sort === SORTS.serverOrder) return [...items];

  const collator = new Intl.Collator("fa", { sensitivity: "base" });
  return items
    .map((item, index) => ({ item, index }))
    .sort((left, right) => collator.compare(left.item.lenderName, right.item.lenderName) || left.index - right.index)
    .map(({ item }) => item);
}
