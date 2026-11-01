export const SYSTEM_MESSAGE_EVENT = "shahab:system-message";

const messageTypes = new Set(["success", "warning", "error"]);

export function createSystemMessage(type, message) {
  if (!messageTypes.has(type)) {
    throw new TypeError("نوع پیام سیستم معتبر نیست.");
  }

  const text = String(message ?? "").trim();
  if (!text) {
    throw new TypeError("متن پیام سیستم نمی‌تواند خالی باشد.");
  }

  return { type, message: text };
}

export function showSystemMessage(type, message) {
  if (typeof window === "undefined" || typeof window.dispatchEvent !== "function") {
    return false;
  }

  const detail = createSystemMessage(type, message);
  window.dispatchEvent(new CustomEvent(SYSTEM_MESSAGE_EVENT, { detail }));
  return true;
}
