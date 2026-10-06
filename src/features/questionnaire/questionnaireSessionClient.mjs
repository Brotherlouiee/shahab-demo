/**
 * HTTP-only adapter for anonymous questionnaire progress.
 *
 * The opaque session identifier stays in the caller's in-memory state. Neither
 * it nor canonical answer values are encoded in a browser path or persisted in
 * web storage.
 */
const apiBaseUrl = import.meta.env?.VITE_SHAHAB_API_BASE_URL || "/api/v1";

export class QuestionnaireSessionApiError extends Error {
  constructor(code, status) {
    super(code);
    this.name = "QuestionnaireSessionApiError";
    this.status = status;
  }
}

async function parseResponse(response, failureCode) {
  if (!response.ok) throw new QuestionnaireSessionApiError(failureCode, response.status);
  return response.json();
}

export async function startQuestionnaireSession(fetchImpl = fetch) {
  return parseResponse(
    await fetchImpl(`${apiBaseUrl}/questionnaire/sessions`, { method: "POST" }),
    "questionnaire_session_unavailable",
  );
}

export async function saveQuestionnaireAnswer(sessionId, questionId, answerId, fetchImpl = fetch) {
  return parseResponse(
    await fetchImpl(
      `${apiBaseUrl}/questionnaire/sessions/${encodeURIComponent(sessionId)}/answers/${encodeURIComponent(questionId)}`,
      {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ answerId }),
      },
    ),
    "questionnaire_answer_rejected",
  );
}
