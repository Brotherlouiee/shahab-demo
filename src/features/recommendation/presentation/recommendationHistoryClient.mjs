import { authorizedRequest, ProfileApiError } from "../../account/profileClient.mjs";
import { buildRecommendationResultViewModel } from "./recommendationResultViewModel.mjs";

export async function fetchRecommendationHistory({ limit = 20, offset = 0 } = {}) {
  try { return await authorizedRequest(`recommendation-history?limit=${encodeURIComponent(limit)}&offset=${encodeURIComponent(offset)}`); }
  catch (error) { throw error instanceof ProfileApiError ? error : new ProfileApiError(0); }
}

export async function fetchHistoricalRecommendation(historyId) {
  try { return buildRecommendationResultViewModel(await authorizedRequest(`recommendation-history/${encodeURIComponent(historyId)}`)); }
  catch (error) { throw error instanceof ProfileApiError ? error : new ProfileApiError(0); }
}
