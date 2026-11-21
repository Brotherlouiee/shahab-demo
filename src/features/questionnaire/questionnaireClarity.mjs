const ALLOWED_ACTIONS = new Set([
  "step_viewed",
  "answer_selected",
  "answer_saved",
  "next_clicked",
  "back_clicked",
  "profile_step_viewed",
  "otp_step_viewed",
  "profile_submitted",
]);

/**
 * Send only a fixed action and an ordinal step number to Clarity.
 * Answer values, account/session identifiers, and profile data are never accepted.
 */
export function trackQuestionnaireClarity(action, stepNumber) {
  if (!ALLOWED_ACTIONS.has(action) || !Number.isInteger(stepNumber) || stepNumber < 1 || stepNumber > 20) {
    return false;
  }

  if (typeof window === "undefined" || typeof window.clarity !== "function") return false;

  window.clarity("event", `questionnaire_${action}_step_${String(stepNumber).padStart(2, "0")}`);
  return true;
}
