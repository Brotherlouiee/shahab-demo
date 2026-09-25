/**
 * Presentation-only model for a recommendation response already calculated by the server.
 *
 * This module must never score, normalize, filter or reorder recommendations. It only
 * validates the read model, assigns Persian UI copy and builds a safe details route.
 */

const REVIEW_WARNING =
  "برای مقایسهٔ دقیق این گزینه، بخشی از اطلاعات وام در دادهٔ فعلی کامل نیست.";

export function buildRecommendationResultViewModel(response) {
  const result = requireRecord(response, "recommendation response");

  return Object.freeze({
    dataVersion: requireText(result.dataVersion, "dataVersion"),
    configVersion: requireText(result.configVersion, "configVersion"),
    rankedRecommendations: Object.freeze(
      requireArray(result.rankedRecommendations, "rankedRecommendations").map(toRankedViewModel),
    ),
    needsReview: Object.freeze(
      requireArray(result.needsReview, "needsReview").map(toNeedsReviewViewModel),
    ),
  });
}

function toRankedViewModel(item) {
  const recommendation = requireRecord(item, "ranked recommendation");
  const loanId = requireText(recommendation.loanId, "loanId");

  return Object.freeze({
    loanId,
    lenderName: requireText(recommendation.lenderName, "lenderName"),
    loanName: requireText(recommendation.loanName, "loanName"),
    compatibilityScore: requireScore(recommendation.compatibilityScore),
    compatibilityReason: requireText(recommendation.compatibilityReason, "compatibilityReason"),
    scoreCaption: "درصد تطابق محاسبه‌شده",
    detailsHref: detailsHrefFor(loanId),
  });
}

function toNeedsReviewViewModel(item) {
  const recommendation = requireRecord(item, "needs-review recommendation");
  const loanId = requireText(recommendation.loanId, "loanId");

  return Object.freeze({
    loanId,
    lenderName: requireText(recommendation.lenderName, "lenderName"),
    loanName: requireText(recommendation.loanName, "loanName"),
    rankingExcludedReasons: Object.freeze(
      requireArray(recommendation.rankingExcludedReasons, "rankingExcludedReasons").map((reason) =>
        requireText(reason, "rankingExcludedReason"),
      ),
    ),
    warning: REVIEW_WARNING,
    detailsHref: detailsHrefFor(loanId),
  });
}

function detailsHrefFor(loanId) {
  return `/loan-details?loanId=${encodeURIComponent(loanId)}`;
}

function requireRecord(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) {
    throw new TypeError(`${label} must be an object`);
  }
  return value;
}

function requireArray(value, label) {
  if (!Array.isArray(value)) {
    throw new TypeError(`${label} must be an array`);
  }
  return value;
}

function requireText(value, label) {
  if (typeof value !== "string" || !value.trim()) {
    throw new TypeError(`${label} must be a non-blank string`);
  }
  return value;
}

function requireScore(value) {
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 1) {
    throw new TypeError("compatibilityScore must be a server-supplied number from 0 to 1");
  }
  return value;
}
