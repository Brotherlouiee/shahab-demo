import { mkdir, writeFile } from "node:fs/promises";
import { chromium, expect, test } from "@playwright/test";

// US-13.T01 records *independent* pre-refactor and current visual evidence.
// This is a characterization collector, not permission to weaken the strict
// per-feature pixel/behavior/network parity assertions required in T02/T03.
const reference = process.env.SHAHAB_US13_BASELINE_URL;
// The general e2e workflow has no reference server: skip only this collector.
// The dedicated baseline workflow sets SHA/URL explicitly and therefore runs it.
test.skip(!reference, "US-13 baseline collector runs only with the independent reference server");

const cases = [
  { name: "home", path: "/", selector: ".hp-nav" },
  { name: "about", path: "/about", selector: ".hp-about-page" },
  { name: "login", path: "/login", selector: ".hp-nav" },
];
const viewports = [
  { width: 390, height: 844 },
  { width: 430, height: 932 },
  { width: 1440, height: 900 },
];

test("freeze initial user-visible routes without mutating product state", async ({ baseURL }, info) => {
  const browser = await chromium.launch({
    args: ["--disable-gpu", "--disable-gpu-rasterization", "--disable-partial-raster", "--disable-skia-runtime-opts", "--force-color-profile=srgb"],
  });
  try {
    for (const viewport of viewports) {
      const context = await browser.newContext({ viewport, deviceScaleFactor: 1, locale: "fa-IR" });
      try {
        const page = await context.newPage();
        await page.route(/https:\/\/fonts\.(googleapis|gstatic)\.com\//, route => route.abort());
        for (const item of cases) {
          const output = `test-results/us13-t01/${item.name}-${viewport.width}`;
          await mkdir(output, { recursive: true });
          const captures = [];
          for (const [label, url] of [["baseline", reference], ["candidate", baseURL]]) {
            await page.goto(`${url}${item.path}`);
            const loc = page.locator(item.selector);
            await expect(loc).toBeVisible();
            await page.evaluate(() => document.fonts.ready);
            const rect = await loc.boundingBox();
            const screenshot = await page.screenshot({ fullPage: true, animations: "disabled", caret: "hide" });
            await writeFile(`${output}/${label}.png`, screenshot);
            await info.attach(`${item.name}-${viewport.width}-${label}`, { body: screenshot, contentType: "image/png" });
            captures.push({ label, path: item.path, width: viewport.width, height: viewport.height, rect, title: await page.title() });
          }
          // Geometry is the immediate invariant. Whole-screen PNGs are evidence
          // to review; strict per-component pixel tests are installed before
          // the corresponding later extraction (not silently treated as passing).
          expect(captures[1].rect).toEqual(captures[0].rect);
          await writeFile(`${output}/geometry.json`, JSON.stringify({ frozenCommit: "f5e50da0ea29b7d933a813736a2616169ee9b8f3", captures }, null, 2));
        }
      } finally { await context.close(); }
    }
  } finally { await browser.close(); }
});
