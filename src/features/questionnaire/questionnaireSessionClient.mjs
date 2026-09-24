/** Body-only client for US-07.T04; answer IDs never enter browser paths. */
export async function startQuestionnaireSession(apiBaseUrl) {
  const response = await fetch(`${apiBaseUrl}/questionnaire/sessions`, { method: "POST" });
  if (!response.ok) throw new Error("questionnaire_session_unavailable");
  return response.json();
}

export async function saveQuestionnaireAnswer(apiBaseUrl, sessionId, questionId, answerId) {
  const response = await fetch(`${apiBaseUrl}/questionnaire/sessions/${encodeURIComponent(sessionId)}/answers/${encodeURIComponent(questionId)}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answerId }),
  });
  if (!response.ok) throw new Error("questionnaire_answer_rejected");
  return response.json();
}
