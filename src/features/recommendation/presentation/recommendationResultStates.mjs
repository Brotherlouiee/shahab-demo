/**
 * Display-state contract for an already validated recommendation result.
 *
 * This module classifies presentation states only. It never calculates a score,
 * changes server rank order, or evaluates a manual filter. T04 may provide an
 * order-preserving filtered subset; this boundary rejects reordered input.
 */
const MESSAGES = Object.freeze({
  noCandidate: "در حال حاضر گزینهٔ قابل‌رتبه‌بندی متناسبی پیدا نشد. می‌توانید پاسخ‌ها را بازبینی کنید.",
  needsReviewOnly: "دادهٔ کافی برای رتبه‌بندی دقیق موجود نیست.",
  zeroAfterFilter: "با فیلترهای انتخاب‌شده گزینه‌ای باقی نمانده است. فیلترها را تغییر دهید.",
});

export function buildRecommendationResultDisplayState(
  result,
  { hasManualFilters = false, visibleRankedRecommendations } = {},
) {
  const viewModel = requireResultViewModel(result);
  if (typeof hasManualFilters !== "boolean") {
    throw new TypeError("hasManualFilters must be a boolean");
  }

  const visibleRanked = hasManualFilters
    ? requireOrderedSubset(visibleRankedRecommendations, viewModel.rankedRecommendations)
    : viewModel.rankedRecommendations;

  const ranked = visibleRanked.length
    ? Object.freeze({
        kind: "ranked",
        title: "گزینه‌های قابل مقایسه",
        items: Object.freeze([...visibleRanked]),
      })
    : null;
  const needsReview = viewModel.needsReview.length
    ? Object.freeze({
        kind: "needsReview",
        title: "گزینه‌هایی که برای مقایسهٔ دقیق به اطلاعات بیشتری نیاز دارند",
        items: Object.freeze([...viewModel.needsReview]),
      })
    : null;

  return Object.freeze({
    dataVersion: viewModel.dataVersion,
    configVersion: viewModel.configVersion,
    ranked,
    needsReview,
    emptyState: buildEmptyState(viewModel, visibleRanked, hasManualFilters),
  });
}

function buildEmptyState(viewModel, visibleRanked, hasManualFilters) {
  if (visibleRanked.length) return null;
  if (hasManualFilters && viewModel.rankedRecommendations.length) {
    return Object.freeze({ kind: "zeroAfterFilter", message: MESSAGES.zeroAfterFilter });
  }
  if (viewModel.needsReview.length) {
    return Object.freeze({ kind: "needsReviewOnly", message: MESSAGES.needsReviewOnly });
  }
  return Object.freeze({ kind: "noCandidate", message: MESSAGES.noCandidate });
}

function requireResultViewModel(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new TypeError("recommendation result view model must be an object");
  }
  if (!Array.isArray(value.rankedRecommendations) || !Array.isArray(value.needsReview)) {
    throw new TypeError("recommendation result must contain presentation arrays");
  }
  return value;
}

function requireOrderedSubset(value, source) {
  if (!Array.isArray(value)) {
    throw new TypeError("visibleRankedRecommendations must be an array when manual filters are active");
  }
  let previousIndex = -1;
  for (const recommendation of value) {
    const nextIndex = source.findIndex(
      (candidate, index) => index > previousIndex && candidate.loanId === recommendation?.loanId,
    );
    if (nextIndex === -1) {
      throw new TypeError("visibleRankedRecommendations must preserve server order and membership");
    }
    previousIndex = nextIndex;
  }
  return value;
}
