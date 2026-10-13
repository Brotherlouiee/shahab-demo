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
          const pictures = [];
          for (const [label, url] of [["baseline", reference], ["candidate", baseURL]]) {
            await page.goto(`${url}${item.path}`);
            const loc = page.locator(item.selector);
            await expect(loc).toBeVisible();
            await page.evaluate(() => document.fonts.ready);
            const rect = await loc.boundingBox();
            const screenshot = await page.screenshot({ fullPage: true, animations: "disabled", caret: "hide" });
            await writeFile(`${output}/${label}.png`, screenshot);
            await info.attach(`${item.name}-${viewport.width}-${label}`, { body: screenshot, contentType: "image/png" });
            pictures.push(screenshot);
            captures.push({ label, path: item.path, width: viewport.width, height: viewport.height, rect, title: await page.title() });
          }
          // Full-page pixel and geometry assertions apply to these nine cases.
          // Other routes and interactive states still require their own gates.
          expect(captures[1].rect).toEqual(captures[0].rect);
          // All nine initial route/viewport combinations were independently
          // compared pixel-by-pixel on the frozen pre-refactor SHA. Keep this
          // exact zero-tolerance gate; never rebaseline to accommodate a diff.
          expect(pictures[1].equals(pictures[0]), `US-13 frozen ${item.name} at ${viewport.width}: entire screen must be pixel-identical`).toBe(true);
          await writeFile(`${output}/geometry.json`, JSON.stringify({ frozenCommit: "f5e50da0ea29b7d933a813736a2616169ee9b8f3", captures }, null, 2));
        }
      } finally { await context.close(); }
    }
  } finally { await browser.close(); }
});


test("AboutPage header actions preserve route, visuals, and API boundary", async ({ baseURL }, info) => {
  const browser = await chromium.launch({
    args: ["--disable-gpu", "--disable-gpu-rasterization", "--disable-partial-raster", "--disable-skia-runtime-opts", "--force-color-profile=srgb"],
  });
  try {
    for (const viewport of [{ width: 390, height: 844 }, { width: 1440, height: 900 }]) {
      const context = await browser.newContext({ viewport, deviceScaleFactor: 1, locale: "fa-IR" });
      try {
        const page = await context.newPage();
        await page.route(/https:\/\/fonts\.(googleapis|gstatic)\.com\//, route => route.abort());
        for (const action of [
          { name: "back", selector: ".hp-account-header button[aria-label='بازگشت']" },
          { name: "brand", selector: ".hp-account-header a.hp-questionnaire-brand" },
        ]) {
          const evidence = [];
          for (const [label, origin] of [["baseline", reference], ["candidate", baseURL]]) {
            const apiCalls = [];
            const listener = (request) => {
              if (new URL(request.url()).pathname.startsWith("/api/")) apiCalls.push({ method: request.method(), path: new URL(request.url()).pathname });
            };
            page.on("request", listener);
            await page.goto(`${origin}/about`);
            await expect(page.locator(".hp-about-page")).toBeVisible();
            const beforeText = await page.locator(".hp-about-page").innerText();
            await page.locator(action.selector).click();
            await expect.poll(() => new URL(page.url()).pathname).toBe("/");
            await page.evaluate(() => document.fonts.ready);
            const screenshot = await page.screenshot({ fullPage: true, animations: "disabled", caret: "hide" });
            await info.attach(`about-${action.name}-${viewport.width}-${label}`, { body: screenshot, contentType: "image/png" });
            evidence.push({ beforeText, apiCalls, screenshot, path: new URL(page.url()).pathname });
            page.off("request", listener);
          }
          expect(evidence[1].path).toBe(evidence[0].path);
          expect(evidence[1].beforeText).toBe(evidence[0].beforeText);
          expect(evidence[1].apiCalls).toEqual(evidence[0].apiCalls);
          expect(evidence[1].screenshot.equals(evidence[0].screenshot),
            `AboutPage ${action.name} at ${viewport.width}: post-navigation screenshot must be pixel-identical`).toBe(true);
        }
      } finally { await context.close(); }
    }
  } finally { await browser.close(); }
});
