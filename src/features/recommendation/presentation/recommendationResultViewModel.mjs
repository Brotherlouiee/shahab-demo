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
    ...(typeof result.historyId === "string" ? { historyId: requireText(result.historyId, "historyId") } : {}),
    dataVersion: requireText(result.dataVersion, "dataVersion"),
    configVersion: requireText(result.configVersion, "configVersion"),
    rankedRecommendations: Object.freeze(
      requireArray(result.rankedRecommendations, "rankedRecommendations").map(toRankedViewModel),
    ),
    lowCompatibilityRecommendations: Object.freeze(
      requireArray(result.lowCompatibilityRecommendations, "lowCompatibilityRecommendations").map((item) =>
        Object.freeze({ ...toRankedViewModel(item), statusLabel: "تطابق پایین؛ پیشنهاد اصلی نیست" }),
      ),
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
    bankLogoReference: optionalLogoReference(recommendation.bankLogoReference),
    compatibilityScore: requireScore(recommendation.compatibilityScore),
    compatibilityReason: requireText(recommendation.compatibilityReason, "compatibilityReason"),
    loanSummary: optionalLoanSummary(recommendation.loanSummary),
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
    bankLogoReference: optionalLogoReference(recommendation.bankLogoReference),
    rankingExcludedReasons: Object.freeze(
      requireArray(recommendation.rankingExcludedReasons, "rankingExcludedReasons").map((reason) =>
        requireText(reason, "rankingExcludedReason"),
      ),
    ),
    warning: REVIEW_WARNING,
    loanSummary: optionalLoanSummary(recommendation.loanSummary),
    detailsHref: detailsHrefFor(loanId),
  });
}

function optionalLoanSummary(value) {
  // Current server responses contain this additive field. Older responses use
  // the existing detail endpoint fallback instead of inventing any loan facts.
  if (value === undefined || value === null) return null;
  const summary = requireRecord(value, "loanSummary");
  return Object.freeze({
    maxAmountTomans: optionalPublishedNumber(summary.maxAmountTomans, "maxAmountTomans"),
    monthlyInstallmentTomans: optionalPublishedNumber(summary.monthlyInstallmentTomans, "monthlyInstallmentTomans"),
    maxRepaymentMonths: optionalPublishedInteger(summary.maxRepaymentMonths, "maxRepaymentMonths"),
    interestRatePercent: optionalPublishedNumber(summary.interestRatePercent, "interestRatePercent"),
  });
}

function optionalPublishedNumber(value, label) {
  if (value === null) return null;
  if (typeof value !== "number" || !Number.isFinite(value) || value < 0) {
    throw new TypeError(`${label} must be a non-negative server number or null`);
  }
  return value;
}

function optionalPublishedInteger(value, label) {
  if (value === null) return null;
  if (!Number.isInteger(value) || value < 0) {
    throw new TypeError(`${label} must be a non-negative server integer or null`);
  }
  return value;
}

function optionalLogoReference(value) {
  if (typeof value !== "string") return null;
  const reference = value.trim();
  if (/^https?:\/\//i.test(reference) || /^\/(?!\/)/.test(reference)) return reference;
  return null;
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
