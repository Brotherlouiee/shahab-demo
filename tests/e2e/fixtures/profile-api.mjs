import { expect } from "@playwright/test";

// Contract fixture only; real ownership/persistence is covered by API/PostgreSQL tests.
export async function installProfileApi(page, options = {}) {
  const state = { phone: options.profile?.phone || "", authenticated: Boolean(options.authenticated), savedLoans: new Map((options.savedLoans || []).map(item => [item.loanId, item])), availableLoans: new Map(), profile: options.profile || null, verifies: 0, writes: [], failWrites: 0 };
  const latin = (value) => value.replace(/[۰-۹]/g, (digit) => String("۰۱۲۳۴۵۶۷۸۹".indexOf(digit)));
  await page.route("**/api/v1/account-access/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith("/logout")) { state.authenticated = false; return route.fulfill({ status: 204 }); }
    // Initial page hydration probes the cookie-backed session. This fixture has
    // no server cookie jar, so it deliberately models an anonymous refresh.
    if (path.endsWith("/session")) return state.authenticated ? route.fulfill({ json: { phone: state.phone, accountId: "fixture-account", expiresIn: 1800 } }) : route.fulfill({ status: 401, json: {} });
    const body = route.request().postDataJSON();
    if (path.endsWith("/request")) {
      state.phone = body.phone;
      return route.fulfill({ json: { challengeId: "browser-test-challenge", expiresIn: 120 } });
    }
    state.verifies += 1;
    if (latin(body.code) !== "123456") return route.fulfill({ status: 401, json: {} });
    state.authenticated = true;
    state.profile ||= { phone: state.phone, firstName: "", lastName: "", income: "", job: "", gender: "", avatar: null };
    return route.fulfill({ json: { accessToken: "fixture", phone: state.phone, accountId: "fixture-account", expiresIn: 1800 } });
  });
  await page.route("**/api/v1/profiles/me", (route) => {
    expect(state.authenticated).toBe(true);
    expect([undefined, "Bearer fixture"]).toContain(route.request().headers().authorization);
    return state.profile ? route.fulfill({ json: state.profile }) : route.fulfill({ status: 404, json: {} });
  });
  await page.route("**/api/v1/profiles", (route) => {
    expect(state.authenticated).toBe(true);
    expect([undefined, "Bearer fixture"]).toContain(route.request().headers().authorization);
    const body = route.request().postDataJSON();
    state.writes.push(body);
    if (state.failWrites > 0) {
      state.failWrites -= 1;
      return route.fulfill({ status: 503, json: {} });
    }
    state.profile = body;
    return route.fulfill({ json: body });
  });
  page.on("response", async response => {
    if (!response.url().endsWith("/recommendations") || !response.ok()) return;
    try {
      const result = await response.json();
      for (const item of [...(result.rankedRecommendations || []), ...(result.lowCompatibilityRecommendations || []), ...(result.needsReview || [])]) state.availableLoans.set(item.loanId, item);
    } catch { /* Response bodies may be unavailable after closing this fixture page. */ }
  });
  await page.route("**/api/v1/bookmarks**", async route => {
    if (!state.authenticated) return route.fulfill({ status: 401, json: {} });
    const path = new URL(route.request().url()).pathname;
    if (route.request().method() === "GET") return route.fulfill({ json: { items: [...state.savedLoans.values()], nextCursor: null } });
    const id = decodeURIComponent(path.split("/").at(-1));
    if (route.request().method() === "DELETE") state.savedLoans.delete(id);
    else {
      expect(Object.keys(route.request().postDataJSON()).every(key => key === "historyId")).toBe(true);
      const item = state.availableLoans.get(id);
      if (!item) return route.fulfill({ status: 404, json: {} });
      state.savedLoans.set(id, item);
    }
    return route.fulfill({ status: 204 });
  });
  return state;
}
