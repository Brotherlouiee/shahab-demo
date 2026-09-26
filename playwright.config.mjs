import { defineConfig } from "@playwright/test";

const localBrowserPath = process.env.SHAHAB_E2E_BROWSER_PATH;

/** Browser tests target the built application through its public HTTP boundary. */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  use: {
    baseURL: "http://127.0.0.1:4173",
    browserName: "chromium",
    launchOptions: localBrowserPath ? { executablePath: localBrowserPath } : {},
    trace: "retain-on-failure",
  },
  webServer: {
    command: "npm run dev -- --host 127.0.0.1 --port 4173",
    url: "http://127.0.0.1:4173",
    reuseExistingServer: !process.env.CI,
  },
});
