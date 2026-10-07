import React from "react";
import { createRoot } from "react-dom/client";
import App from "./home page.jsx";
import "./App.css";

const root = createRoot(document.getElementById("root"));

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

// The document-level fallback protects the first paint before JavaScript and
// styles are ready. Removing it after two frames avoids a blank flash while
// keeping #root itself empty in the initial HTML.
window.requestAnimationFrame(() => {
  window.requestAnimationFrame(() => {
    document.getElementById("initial-page-skeleton")?.remove();
  });
});
