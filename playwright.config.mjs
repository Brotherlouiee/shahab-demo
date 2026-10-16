import { defineConfig } from "@playwright/test";

const localBrowserPath = process.env.SHAHAB_E2E_BROWSER_PATH;
const serveMode = process.env.SHAHAB_E2E_BUILT === "1" ? "preview" : "dev";
const e2ePort = process.env.SHAHAB_E2E_PORT || "4173";

/** Browser tests target the built application through its public HTTP boundary. */
export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: false,
  // Keep browser memory bounded on the shared local runner.
  ...(process.env.SHAHAB_E2E_BROWSER_PATH ? { workers: 1 } : {}),
  use: {
    baseURL: `http://127.0.0.1:${e2ePort}`,
    browserName: "chromium",
    launchOptions: localBrowserPath ? { executablePath: localBrowserPath } : {},
    trace: "retain-on-failure",
  },
  webServer: [{
    command: `npm run ${serveMode} -- --host=127.0.0.1 --port=${e2ePort}`,
    url: `http://127.0.0.1:${e2ePort}`,
    reuseExistingServer: !process.env.CI,
  }, ...(process.env.SHAHAB_BOOKMARK_BASELINE_DIR ? [{
    command: `npm --prefix ${process.env.SHAHAB_BOOKMARK_BASELINE_DIR} run ${serveMode} -- --host=127.0.0.1 --port=4175`,
    url: process.env.SHAHAB_BOOKMARK_BASELINE_URL,
    reuseExistingServer: false,
  }] : []), ...(process.env.SHAHAB_US13_BASELINE_DIR ? [{
    command: `npm --prefix ${process.env.SHAHAB_US13_BASELINE_DIR} run ${serveMode} -- --host=127.0.0.1 --port=4177`,
    url: process.env.SHAHAB_US13_BASELINE_URL,
    reuseExistingServer: false,
  }] : [])],
});
