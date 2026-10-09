import { expect } from "@playwright/test";

// Contract fixture only; real ownership/persistence is covered by API/PostgreSQL tests.
export async function installProfileApi(page, options = {}) {
  const state = { phone: "", profile: options.profile || null, verifies: 0, writes: [], failWrites: 0 };
  const latin = (value) => value.replace(/[۰-۹]/g, (digit) => String("۰۱۲۳۴۵۶۷۸۹".indexOf(digit)));
  await page.route("**/api/v1/account-access/**", async (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path.endsWith("/logout")) return route.fulfill({ status: 204 });
    const body = route.request().postDataJSON();
    if (path.endsWith("/request")) {
      state.phone = body.phone;
      return route.fulfill({ json: { challengeId: "browser-test-challenge", expiresIn: 120 } });
    }
    state.verifies += 1;
    if (latin(body.code) !== "123456") return route.fulfill({ status: 401, json: {} });
    return route.fulfill({ json: { accessToken: "fixture", phone: state.phone, expiresIn: 1800 } });
  });
  await page.route("**/api/v1/profiles/me", (route) => {
    expect(route.request().headers().authorization).toBe("Bearer fixture");
    return state.profile ? route.fulfill({ json: state.profile }) : route.fulfill({ status: 404, json: {} });
  });
  await page.route("**/api/v1/profiles", (route) => {
    expect(route.request().headers().authorization).toBe("Bearer fixture");
    const body = route.request().postDataJSON();
    state.writes.push(body);
    if (state.failWrites > 0) {
      state.failWrites -= 1;
      return route.fulfill({ status: 503, json: {} });
    }
    state.profile = body;
    return route.fulfill({ json: body });
  });
  return state;
}
