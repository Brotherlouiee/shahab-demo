import { authorizedRequest, ProfileApiError } from "../../account/profileClient.mjs";
import { buildRecommendationResultViewModel } from "./recommendationResultViewModel.mjs";

export async function fetchRecommendationHistory({ limit = 20, cursor = null } = {}) {
  const query = `limit=${encodeURIComponent(limit)}${cursor ? `&cursor=${encodeURIComponent(cursor)}` : ""}`;
  try { return await authorizedRequest(`recommendation-history?${query}`); }
  catch (error) { throw error instanceof ProfileApiError ? error : new ProfileApiError(0); }
}

export async function fetchHistoricalRecommendation(historyId) {
  try { return buildRecommendationResultViewModel(await authorizedRequest(`recommendation-history/${encodeURIComponent(historyId)}`)); }
  catch (error) { throw error instanceof ProfileApiError ? error : new ProfileApiError(0); }
}

export async function hideRecommendationHistory(historyId) {
  try { await authorizedRequest(`recommendation-history/${encodeURIComponent(historyId)}`, { method: "DELETE" }); }
  catch (error) { throw error instanceof ProfileApiError ? error : new ProfileApiError(0); }
}
