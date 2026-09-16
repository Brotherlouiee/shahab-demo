import React from "react";
import { createRoot } from "react-dom/client";
import App from "./home page.jsx";
import "./App.css";

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
