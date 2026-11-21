"""Owner-operated HTTPS acceptance check; at most two SMS, no API key or DB access.

Run interactively on the owner's machine/server. Phone, OTPs, challenge IDs and
session credentials stay in memory. Only named assertions/statuses are printed.
No retries, redirects, proxy inheritance, profile writes or service restarts.
"""

import getpass
import http.cookiejar
import json
import re
import sys
import time
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, HTTPRedirectHandler, ProxyHandler, Request, build_opener

ORIGIN = "https://shahabfintech.ir"
PREFIX = "/api/v1/account-access"


class CheckFailed(Exception):
    """Only fixed, non-sensitive stage identifiers may be exposed to the operator."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise CheckFailed("redirect_blocked")


class Client:
    def __init__(self):
        self.cookies = http.cookiejar.CookieJar()
        self.opener = build_opener(ProxyHandler({}), NoRedirect(), HTTPCookieProcessor(self.cookies))
        self.requests = 0
        self.sms_requests = 0

    def call(self, method, path, payload=None, token=None):
        if path not in {PREFIX + p for p in ("/request", "/verify", "/session", "/logout")} | {"/api/v1/profiles/me"}:
            raise CheckFailed("unexpected_endpoint")
        if path == PREFIX + "/request":
            if self.sms_requests >= 2:
                raise CheckFailed("sms_budget_exceeded")
            self.sms_requests += 1
        headers = {"Accept": "application/json", "Origin": ORIGIN}
        if token:
            headers["Authorization"] = "Bearer " + token
        body = None
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode()
        request = Request(ORIGIN + path, data=body, headers=headers, method=method)
        self.requests += 1
        try:
            response = self.opener.open(request, timeout=15)
        except HTTPError as error:
            response = error
        with response:
            raw = response.read(65537)
            if len(raw) > 65536:
                raise CheckFailed("response_too_large")
            if response.headers.get("Cache-Control", "").lower() != "no-store":
                raise CheckFailed("missing_no_store")
            # Error bodies and headers can contain sensitive details: do not emit them.
            data = json.loads(raw) if response.code == 200 else {}
            return response.code, data


def expect(client, stage, method, path, status, payload=None, token=None):
    actual, data = client.call(method, path, payload, token)
    if actual != status:
        if path == PREFIX + "/verify" and actual == 200:
            client.call("POST", PREFIX + "/logout")
        raise CheckFailed(f"{stage}: expected_http_{status}, received_http_{actual}")
    print(f"PASS {stage} HTTP {actual}", flush=True)
    return data


def ask_code(prompt):
    value = getpass.getpass(prompt).strip().translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
    if re.fullmatch(r"[0-9]{6}", value) is None:
        raise CheckFailed("invalid_code_input")
    return value


def challenge(client, phone, stage):
    started = time.monotonic()
    data = expect(client, stage, "POST", PREFIX + "/request", 200, {"phone": phone})
    if data.get("expiresIn") != 120 or not isinstance(data.get("challengeId"), str):
        raise CheckFailed("unexpected_challenge_contract")
    return data["challengeId"], started


def run(client):
    phone = getpass.getpass("شمارهٔ همراه خودتان (مخفی): ").strip()
    phone = phone.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))
    if re.fullmatch(r"09[0-9]{9}", phone) is None:
        raise CheckFailed("invalid_phone_input")
    expect(client, "anonymous_session", "GET", PREFIX + "/session", 401)
    first, _ = challenge(client, phone, "first_sms_requested")
    code = ask_code("کد پیامک اول (مخفی): ")
    wrong = f"{(int(code) + 1) % 1000000:06d}"
    wrong_status, _ = client.call("POST", PREFIX + "/verify", {"challengeId": first, "code": wrong})
    if wrong_status == 200:
        # Revoke any session mistakenly issued by the negative test before stopping.
        client.call("POST", PREFIX + "/logout")
    if wrong_status != 401:
        raise CheckFailed(f"wrong_code: expected_http_401, received_http_{wrong_status}")
    print("PASS wrong_code HTTP 401", flush=True)
    session = expect(client, "valid_code", "POST", PREFIX + "/verify", 200, {"challengeId": first, "code": code})
    token = session.get("accessToken")
    try:
        if not isinstance(token, str) or not token or session.get("expiresIn") != 3600:
            raise CheckFailed("unexpected_session_contract")
        cookie = next((c for c in client.cookies if c.name == "shahab_account_access"), None)
        if cookie is None or not cookie.secure or not cookie.has_nonstandard_attr("HttpOnly"):
            raise CheckFailed("missing_secure_httponly_cookie")
        expect(client, "cookie_session_restore", "GET", PREFIX + "/session", 200)
        expect(client, "profile_read", "GET", "/api/v1/profiles/me", 200)
        # A fresh cookie jar proves a consumed code cannot issue a second session.
        expect(
            Client(), "consumed_code_rejected", "POST", PREFIX + "/verify", 401, {"challengeId": first, "code": code}
        )
    finally:
        expect(client, "logout", "POST", PREFIX + "/logout", 204, token=token)
    # Explicitly reuse the OLD token; an empty post-logout jar alone proves nothing.
    expect(client, "revoked_session_rejected", "GET", PREFIX + "/session", 401, token=token)
    expect(client, "revoked_profile_rejected", "GET", "/api/v1/profiles/me", 401, token=token)
    second, started = challenge(client, phone, "second_sms_requested")
    expired_code = ask_code("کد پیامک دوم، فقط برای آزمون انقضا (مخفی): ")
    remaining = max(0, 123 - (time.monotonic() - started))
    print(f"انتظار برای انقضای واقعی کد: {remaining:.0f} ثانیه؛ برنامه را نبندید.", flush=True)
    # Operator-owned process, not a model/tool polling loop. No SMS retry is made.
    time.sleep(remaining)
    expect(
        client, "expired_code_rejected", "POST", PREFIX + "/verify", 401, {"challengeId": second, "code": expired_code}
    )
    print(json.dumps({"task": "US-11.T06", "result": "live_checks_passed", "smsRequests": client.sms_requests}))


def main():
    if not sys.stdin.isatty():
        raise SystemExit("اجرای تعاملی لازم است؛ شماره و کد را در فایل یا آرگومان نگذارید.")
    try:
        run(Client())
    except CheckFailed as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1
    except (Exception, KeyboardInterrupt):
        print("FAIL interrupted_or_transport_error; no automatic retry", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
