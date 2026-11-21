import { useEffect, useRef, useState } from "react";
import errorIconUrl from "../../assets/system-message-error.svg";
import successIconUrl from "../../assets/system-message-success.svg";
import warningIconUrl from "../../assets/system-message-warning.svg";
import { SYSTEM_MESSAGE_EVENT, createSystemMessage } from "./systemMessages.mjs";

const icons = {
  success: successIconUrl,
  warning: warningIconUrl,
  error: errorIconUrl,
};

export default function SystemMessageHost() {
  const [message, setMessage] = useState(null);
  const nextId = useRef(0);

  useEffect(() => {
    function handleSystemMessage(event) {
      try {
        const payload = createSystemMessage(event.detail?.type, event.detail?.message);
        setMessage({ ...payload, id: ++nextId.current });
      } catch {
        // Ignore malformed internal events; never break the application shell.
      }
    }

    window.addEventListener(SYSTEM_MESSAGE_EVENT, handleSystemMessage);
    return () => window.removeEventListener(SYSTEM_MESSAGE_EVENT, handleSystemMessage);
  }, []);

  useEffect(() => {
    if (!message) return undefined;
    const timeout = window.setTimeout(() => setMessage(null), 5000);
    return () => window.clearTimeout(timeout);
  }, [message?.id]);

  if (!message) return null;

  return (
    <div className="shahab-system-message-viewport">
      <div
        className="shahab-system-message"
        data-type={message.type}
        role={message.type === "error" ? "alert" : "status"}
        aria-live={message.type === "error" ? "assertive" : "polite"}
        aria-atomic="true"
      >
        <img className="shahab-system-message__icon" src={icons[message.type]} alt="" />
        <p>{message.message}</p>
        <button
          className="shahab-system-message__dismiss"
          type="button"
          aria-label="بستن پیام"
          onClick={() => setMessage(null)}
        >
          ×
        </button>
      </div>
    </div>
  );
}
