const COMPATIBILITY_BANDS = Object.freeze([
  { minimumPercent: 80, name: "blue" },
  { minimumPercent: 60, name: "lime" },
  { minimumPercent: 40, name: "orange" },
  { minimumPercent: 20, name: "deep-orange" },
  { minimumPercent: 0, name: "red" },
]);

/** Use the same rounded percentage that is displayed; no score is recalculated. */
export function compatibilityBandForScore(score) {
  if (typeof score !== "number" || !Number.isFinite(score)) return null;
  const percent = Math.round(score * 100);
  if (percent < 0 || percent > 100) return null;
  return COMPATIBILITY_BANDS.find((band) => percent >= band.minimumPercent)?.name || null;
}
