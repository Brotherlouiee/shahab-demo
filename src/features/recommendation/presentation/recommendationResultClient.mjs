/**
 * Narrow transport adapter for a recommendation result calculated by the server.
 *
 * The active-tab opaque session ID is sent only in a JSON request body. This client
 * never sends answers, scoring inputs, data/config selectors, or ranking controls.
 */
import { buildRecommendationResultViewModel } from "./recommendationResultViewModel.mjs";

const apiBaseUrl = import.meta.env?.VITE_SHAHAB_API_BASE_URL || "/api/v1";

export class RecommendationResultApiError extends Error {
  constructor(status) {
    super("Recommendation result could not be loaded.");
    this.name = "RecommendationResultApiError";
    this.status = status;
  }
}

export async function fetchRecommendationResult(sessionId, { fetchImpl = fetch, signal } = {}) {
  if (typeof sessionId !== "string" || !sessionId.trim()) {
    throw new RecommendationResultApiError(400);
  }

  const response = await fetchImpl(`${apiBaseUrl}/recommendations`,
    {
      method: "POST",
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId }),
      signal,
    },
  );
  if (!response.ok) throw new RecommendationResultApiError(response.status);

  try {
    return buildRecommendationResultViewModel(await response.json());
  } catch {
    throw new RecommendationResultApiError(502);
  }
}
