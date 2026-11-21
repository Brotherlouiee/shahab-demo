import assert from "node:assert/strict";
import test from "node:test";

import { createViteConfig } from "../../scripts/vite-dev-config.mjs";

test("development API requests use the explicit same-origin proxy", () => {
  const config = createViteConfig({ apiProxyTarget: "http://api:8000" });

  assert.deepEqual(config.server.proxy["/api/v1"], {
    target: "http://api:8000",
    changeOrigin: false,
  });
});

test("host-run Vite defaults to the local FastAPI port", () => {
  const previousTarget = process.env.VITE_DEV_API_PROXY_TARGET;
  delete process.env.VITE_DEV_API_PROXY_TARGET;

  try {
    assert.equal(createViteConfig().server.proxy["/api/v1"].target, "http://127.0.0.1:8000");
  } finally {
    if (previousTarget === undefined) delete process.env.VITE_DEV_API_PROXY_TARGET;
    else process.env.VITE_DEV_API_PROXY_TARGET = previousTarget;
  }
});
