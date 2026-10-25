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

for (const viewport of viewports) {
  test(`freeze initial user-visible routes at ${viewport.width} without mutating product state`, async ({ baseURL }, info) => {
    const browser = await chromium.launch({
      ...(process.env.SHAHAB_E2E_BROWSER_PATH ? { executablePath: process.env.SHAHAB_E2E_BROWSER_PATH } : {}),
      args: ["--disable-gpu", "--disable-gpu-rasterization", "--disable-partial-raster", "--disable-skia-runtime-opts", "--force-color-profile=srgb"],
    });
    try {
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
            // The shared nav can appear before the initial route finishes loading.
            // Compare both real phone forms, never a transient loading skeleton.
            if (item.name === "login") {
              await expect(page.locator(".hp-login-form")).toBeVisible();
              await expect(page.locator(".hp-deferred-skeleton")).toBeHidden();
            }
            const loc = page.locator(item.selector);
            await expect(loc).toBeVisible();
            await page.evaluate(() => document.fonts.ready);
            await page.locator("img:visible").evaluateAll(images => Promise.all(images.map(image => image.decode())));
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
    } finally { await browser.close(); }
});
}

test("AboutPage header actions preserve route, visuals, and API boundary", async ({ baseURL }, info) => {
  const browser = await chromium.launch({
    ...(process.env.SHAHAB_E2E_BROWSER_PATH ? { executablePath: process.env.SHAHAB_E2E_BROWSER_PATH } : {}),
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


test("T03.01: About and shared header computed CSS stays identical to frozen pre-refactor baseline", async ({ baseURL }, info) => {
  const browser = await chromium.launch({
    ...(process.env.SHAHAB_E2E_BROWSER_PATH ? { executablePath: process.env.SHAHAB_E2E_BROWSER_PATH } : {}),
    args: ["--disable-gpu", "--disable-gpu-rasterization", "--disable-partial-raster", "--disable-skia-runtime-opts", "--force-color-profile=srgb"],
  });
  const selectors = [
    ".hp-about-page",
    ".hp-about-page > img",
    ".hp-about-page > p",
    ".hp-account-header",
    ".hp-account-header .hp-questionnaire-brand",
    ".hp-account-header .hp-questionnaire-brand img",
    ".hp-account-header .hp-questionnaire-icon-button",
  ];
  const properties = [
    "display", "position", "box-sizing", "width", "height", "min-width", "min-height",
    "max-width", "max-height", "padding", "margin", "border", "border-radius",
    "background-color", "color", "font-family", "font-size", "font-weight",
    "line-height", "letter-spacing", "text-align", "direction", "object-fit",
    "flex", "align-items", "justify-content", "gap", "overflow",
    "transform", "opacity", "visibility", "box-shadow", "z-index",
  ];
  try {
    for (const viewport of [
      { width: 390, height: 844 },
      { width: 430, height: 932 },
      { width: 1440, height: 900 },
    ]) {
      const context = await browser.newContext({ viewport, deviceScaleFactor: 1, locale: "fa-IR" });
      try {
        const page = await context.newPage();
        await page.route(/https:\/\/fonts\.(googleapis|gstatic)\.com\//, (route) => route.abort());
        const evidence = [];
        for (const [label, origin] of [["baseline", reference], ["candidate", baseURL]]) {
          await page.goto(`${origin}/about`);
          await expect(page.locator(".hp-about-page")).toBeVisible();
          await page.evaluate(() => document.fonts.ready);
          const snapshot = await page.evaluate(({ selectors, properties }) =>
            selectors.map((selector) => ({
              selector,
              elements: [...document.querySelectorAll(selector)].map((element) => {
                const css = getComputedStyle(element);
                const rect = element.getBoundingClientRect();
                return {
                  css: Object.fromEntries(properties.map((name) => [name, css.getPropertyValue(name)])),
                  rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
                  text: element.innerText ?? element.getAttribute("alt") ?? "",
                };
              }),
            })), { selectors, properties });
          for (const group of snapshot) expect(group.elements.length, `missing ${group.selector}`).toBeGreaterThan(0);
          await info.attach(`t03-01-${viewport.width}-${label}-computed-styles`, {
            body: Buffer.from(JSON.stringify(snapshot, null, 2)),
            contentType: "application/json",
          });
          evidence.push(snapshot);
        }
        expect(evidence[1], `T03.01 About CSS/geometry must equal frozen baseline at ${viewport.width}`).toEqual(evidence[0]);
      } finally {
        await context.close();
      }
    }
  } finally {
    await browser.close();
  }
});

// T01 Hero gate: characterize the existing home flow against the immutable
// pre-refactor checkout. The test injects no application code or persisted data.
const heroViewports = [
  { width: 390, height: 844 },
  { width: 430, height: 932 },
  { width: 1440, height: 900 },
  // Both sides of the Hero's active 420px, 700px, and 900px CSS breakpoints.
  { width: 419, height: 932 },
  { width: 421, height: 932 },
  { width: 699, height: 932 },
  { width: 701, height: 932 },
  { width: 899, height: 932 },
  { width: 901, height: 932 },
];

const heroSelectors = [
  ".hp-hero",
  ".hp-hero h1",
  ".hp-hero h1 em",
  ".hp-hero > p",
  ".hp-hero-form",
  ".hp-submit",
  ".hp-select-wrap",
  ".hp-select-trigger",
  ".hp-select-menu",
  ".hp-select-menu button",
  ".hp-eligibility-message",
  ".hp-eligibility-message p",
  ".hp-eligibility-message button",
];

const heroStyleProperties = [
  "display", "position", "box-sizing", "width", "height", "min-height",
  "padding", "margin", "border", "border-radius", "background-color", "color",
  "font-family", "font-size", "font-weight", "line-height", "letter-spacing",
  "text-align", "direction", "flex-direction", "align-items", "justify-content",
  "gap", "overflow", "transform", "opacity", "visibility", "box-shadow", "z-index",
];

for (const viewport of heroViewports) {
  test(`T01 Hero interaction, geometry, pixels and network match frozen baseline at ${viewport.width}px`, async ({ baseURL }, info) => {
    const browser = await chromium.launch({
      ...(process.env.SHAHAB_E2E_BROWSER_PATH ? { executablePath: process.env.SHAHAB_E2E_BROWSER_PATH } : {}),
      args: ["--disable-gpu", "--disable-gpu-rasterization", "--disable-partial-raster", "--disable-skia-runtime-opts", "--force-color-profile=srgb"],
    });
    const evidence = [];
    try {
      for (const [label, origin] of [["baseline", reference], ["candidate", baseURL]]) {
        const context = await browser.newContext({ viewport, deviceScaleFactor: 1, locale: "fa-IR" });
        try {
          const output = `test-results/us13-t01/hero-${viewport.width}`;
          await mkdir(output, { recursive: true });
          await context.addInitScript(() => {
            const events = [];
            for (const type of ["click", "submit", "focusin", "focusout"]) {
              document.addEventListener(type, (event) => {
                if (!event.target.closest?.(".hp-hero")) return;
                events.push({
                  type,
                  tag: event.target.tagName,
                  className: event.target.getAttribute("class") || "",
                  text: (event.target.innerText || "").trim().replace(/\s+/g, " ").slice(0, 100),
                });
              }, true);
            }
            window.__us13HeroEvents = events;
          });
          const page = await context.newPage();
          const apiRequests = [];
          page.on("request", (request) => {
            const url = new URL(request.url());
            if (url.pathname.startsWith("/api/")) {
              apiRequests.push({ method: request.method(), path: url.pathname });
            }
          });
          await page.route(/https:\/\/fonts\.(googleapis|gstatic)\.com\//, (route) => route.abort());
          await page.goto(`${origin}/`);
          const hero = page.locator(".hp-hero");
          await expect(hero).toBeVisible();
          await page.evaluate(() => document.fonts.ready);

          const captures = [];
          const capture = async (state) => {
            await expect(hero).toBeVisible();
            // A click leaves the pointer over a menu option; move it to the
            // same neutral viewport corner before recording :hover styles.
            await page.mouse.move(viewport.width - 1, viewport.height - 1);
            const snapshot = await page.evaluate(({ selectors, properties }) => ({
              elements: selectors.map((selector) => ({
                selector,
                elements: [...document.querySelectorAll(selector)].map((element) => {
                  const style = getComputedStyle(element);
                  const rect = element.getBoundingClientRect();
                  return {
                    text: element.innerText || "",
                    attributes: {
                      ariaExpanded: element.getAttribute("aria-expanded"),
                      ariaDisabled: element.getAttribute("aria-disabled"),
                      disabled: Boolean(element.disabled),
                      type: element.getAttribute("type"),
                    },
                    css: Object.fromEntries(properties.map((name) => [name, style.getPropertyValue(name)])),
                    rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
                  };
                }),
              })),
              activeElement: document.activeElement?.getAttribute("class") || document.activeElement?.tagName || "",
              path: `${window.location.pathname}${window.location.search}`,
            }), { selectors: heroSelectors, properties: heroStyleProperties });
            const screenshot = await hero.screenshot({ animations: "disabled", caret: "hide" });
            captures.push({ state, snapshot, screenshot });
            await writeFile(`${output}/${label}-${state}.png`, screenshot);
            await info.attach(`t01-hero-${viewport.width}-${label}-${state}.png`, { body: screenshot, contentType: "image/png" });
          };

          await capture("initial-empty-closed");
          const submit = page.getByRole("button", { name: "بررسی واجد شرایط بودن" });
          await submit.click();
          const menu = page.locator(".hp-select-menu");
          await expect(menu).toBeVisible();
          await capture("empty-submit-opens-menu");

          const trigger = page.locator(".hp-select-trigger");
          await menu.getByRole("button", { name: "تا ۵۰ میلیون", exact: true }).click();
          await expect(trigger).toHaveText("تا ۵۰ میلیون");
          await expect(menu).toBeHidden();
          await capture("selected-amount-menu-closed");

          await submit.focus();
          await trigger.focus();
          await trigger.press("Enter");
          await expect(menu).toBeVisible();
          await capture("keyboard-focus-menu-open");
          await trigger.press("Shift+Tab");
          await expect(menu).toBeHidden();
          await expect(submit).toBeFocused();
          await capture("blur-closes-menu");

          await trigger.click();
          await expect(menu).toBeVisible();
          await capture("pointer-opens-menu");
          await menu.getByRole("button", { name: "۵۰ تا ۲۵۰ میلیون", exact: true }).click();
          await expect(trigger).toHaveText("۵۰ تا ۲۵۰ میلیون");
          await expect(menu).toBeHidden();
          await submit.click();
          const notice = page.locator(".hp-eligibility-message");
          await expect(notice).toBeVisible();
          await expect(notice.getByRole("button", { name: "متوجه شدم" })).toBeVisible();
          await capture("eligibility-notice");

          await notice.getByRole("button", { name: "متوجه شدم" }).click();
          await expect.poll(() => new URL(page.url()).pathname).toBe("/question/1");
          await expect(page.locator(".hp-questionnaire-page")).toBeVisible();
          const navigation = {
            path: new URL(page.url()).pathname,
            questionnaireVisible: await page.locator(".hp-questionnaire-page").isVisible(),
          };
          const events = await page.evaluate(() => window.__us13HeroEvents);
          evidence.push({ label, captures, apiRequests, events, navigation });
          await writeFile(`${output}/${label}-interaction-network.json`, JSON.stringify({
            frozenCommit: "f5e50da0ea29b7d933a813736a2616169ee9b8f3",
            label,
            viewport,
            states: captures.map(({ state, snapshot }) => ({ state, snapshot })),
            events,
            apiRequests,
            navigation,
          }, null, 2));
          await info.attach(`t01-hero-${viewport.width}-${label}-events-network.json`, {
            body: Buffer.from(JSON.stringify({ events, apiRequests, navigation }, null, 2)),
            contentType: "application/json",
          });
        } finally {
          await context.close();
        }
      }

      const [baseline, candidate] = evidence;
      expect(candidate.captures.map(({ state, snapshot }) => ({ state, snapshot })),
        `T01 Hero state, focus, text, computed style and geometry at ${viewport.width}px`).toEqual(
        baseline.captures.map(({ state, snapshot }) => ({ state, snapshot })),
      );
      const screenshotMatches = candidate.captures.map((capture, index) =>
        capture.screenshot.equals(baseline.captures[index].screenshot));
      expect(screenshotMatches,
        `T01 Hero screenshots must match frozen baseline at ${viewport.width}px`).toEqual(
        Array(candidate.captures.length).fill(true),
      );
      expect(candidate.events, `T01 Hero DOM event sequence at ${viewport.width}px`).toEqual(baseline.events);
      expect(candidate.apiRequests, `T01 Hero API request sequence at ${viewport.width}px`).toEqual(baseline.apiRequests);
      expect(candidate.navigation, `T01 Hero acknowledgement navigation at ${viewport.width}px`).toEqual(baseline.navigation);

      if (viewport.width === 390) {
        // Prove the strict visual oracle is sensitive without modifying source:
        // a test-only style mutation must produce a different Hero capture.
        const context = await browser.newContext({ viewport, deviceScaleFactor: 1, locale: "fa-IR" });
        try {
          const page = await context.newPage();
          await page.route(/https:\/\/fonts\.(googleapis|gstatic)\.com\//, (route) => route.abort());
          await page.goto(`${baseURL}/`);
          const hero = page.locator(".hp-hero");
          await expect(hero).toBeVisible();
          await page.evaluate(() => document.fonts.ready);
          const unchanged = await hero.screenshot({ animations: "disabled", caret: "hide" });
          await page.addStyleTag({ content: ".hp-hero { filter: grayscale(1) !important; }" });
          const mutated = await hero.screenshot({ animations: "disabled", caret: "hide" });
          expect(mutated.equals(unchanged), "test-only intentional Hero style mutation must be detected").toBe(false);
        } finally {
          await context.close();
        }
      }
    } finally {
      await browser.close();
    }
  });
}
