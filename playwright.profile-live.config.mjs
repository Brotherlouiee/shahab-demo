import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/profile-live",
  fullyParallel: false,
  // Shared real OTP quotas and disposable-DB fixtures require serial file execution.
  workers: 1,
  use: { viewport: { width: 390, height: 844 }, baseURL: "http://127.0.0.1:4174", browserName: "chromium", launchOptions: process.env.SHAHAB_E2E_BROWSER_PATH ? { executablePath: process.env.SHAHAB_E2E_BROWSER_PATH } : {}, trace: "retain-on-failure" },
  webServer: [
    { command: "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000", url: "http://127.0.0.1:8000/api/v1/health/live", reuseExistingServer: false },
    { command: "npm run build && npm run preview -- --host 127.0.0.1 --port 4174 --strictPort", url: "http://127.0.0.1:4174", reuseExistingServer: false },
  ],
});
