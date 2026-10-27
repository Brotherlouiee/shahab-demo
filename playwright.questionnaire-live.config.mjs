import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./tests/questionnaire-live",
  fullyParallel: false,
  workers: 1,
  use: {
    baseURL: "http://127.0.0.1:4176",
    browserName: "chromium",
    viewport: { width: 390, height: 844 },
    launchOptions: process.env.SHAHAB_E2E_BROWSER_PATH
      ? { executablePath: process.env.SHAHAB_E2E_BROWSER_PATH }
      : {},
    trace: "off",
  },
  webServer: [
    {
      command: "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000",
      url: "http://127.0.0.1:8000/api/v1/health/live",
      reuseExistingServer: false,
    },
    {
      command: "npm run dev -- --host=127.0.0.1 --port=4176 --strictPort",
      url: "http://127.0.0.1:4176",
      reuseExistingServer: false,
    },
  ],
});
