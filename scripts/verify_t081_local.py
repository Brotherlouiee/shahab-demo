"""Run redacted HTTP checks only against the isolated local T081 Compose API.

This is not the online two-tester acceptance test. It never publishes data.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import json
import secrets
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from uuid import UUID

PROJECT = "shahab-t081-local"
BASE = "http://127.0.0.1:8000"
ROOT = Path(__file__).resolve().parents[1]


def docker(*args: str) -> str:
    result = subprocess.run(["docker", *args], cwd=ROOT, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def require_isolated_local_api() -> None:
    container = docker("compose", "-p", PROJECT, "ps", "-q", "api")
    if not container or len(container.splitlines()) != 1:
        raise RuntimeError("isolated local API is not running")
    metadata = json.loads(docker("inspect", container))[0]
    labels = metadata["Config"]["Labels"]
    env = dict(item.split("=", 1) for item in metadata["Config"]["Env"] if "=" in item)
    ports = metadata["NetworkSettings"]["Ports"].get("8000/tcp") or []
    expected_root = str(ROOT).casefold()
    actual_root = labels.get("com.docker.compose.project.working_dir", "").casefold()
    if (
        labels.get("com.docker.compose.project") != PROJECT
        or labels.get("com.docker.compose.service") != "api"
        or actual_root != expected_root
        or env.get("SHAHAB_ENVIRONMENT") != "local"
        or env.get("SHAHAB_PROFILE_MOCK_OTP_ENABLED", "").lower() != "true"
        or not ports
        or any(entry.get("HostIp") != "127.0.0.1" or entry.get("HostPort") != "8000" for entry in ports)
    ):
        raise RuntimeError("API does not match the isolated local-only test boundary")


class Client:
    def __init__(self) -> None:
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

    def request(self, method: str, path: str, payload: dict | None = None) -> tuple[int, dict]:
        data = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(
            BASE + path,
            data=data,
            headers={"Content-Type": "application/json"} if data is not None else {},
            method=method,
        )
        try:
            response = self.opener.open(request, timeout=15)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else {}


def check(label: str, actual: int, expected: int | tuple[int, ...]) -> None:
    allowed = (expected,) if isinstance(expected, int) else expected
    print(f"{label}: {actual}")
    if actual not in allowed:
        raise AssertionError(f"{label}: unexpected HTTP status")


def run(*, restart_api: bool) -> None:
    require_isolated_local_api()
    anonymous, first, second = Client(), Client(), Client()
    nil = str(UUID(int=0))
    check("live", anonymous.request("GET", "/api/v1/health/live")[0], 200)
    check("ready without token", anonymous.request("GET", "/api/v1/health/ready")[0], 404)
    for label, path in (
        ("anonymous session", "/api/v1/account-access/session"),
        ("anonymous profile", "/api/v1/profiles/me"),
        ("anonymous bookmarks", "/api/v1/bookmarks"),
        ("anonymous history", "/api/v1/recommendation-history"),
    ):
        check(label, anonymous.request("GET", path)[0], 401)
    check("invalid phone", anonymous.request("POST", "/api/v1/account-access/request", {"phone": "bad"})[0], 422)

    # Fresh synthetic identifiers are not printed; test records remain only in the isolated local DB.
    suffix = secrets.randbelow(9000000) + 1000000
    phones = ("0900" + f"{suffix:07d}", "0900" + f"{(suffix + 1) % 10000000:07d}")
    for label, client, phone in (("A", first, phones[0]), ("B", second, phones[1])):
        status, challenge = client.request("POST", "/api/v1/account-access/request", {"phone": phone})
        check(f"{label} challenge", status, 200)
        status, _ = client.request(
            "POST", "/api/v1/account-access/verify", {"challengeId": challenge["challengeId"], "code": "123456"}
        )
        check(f"{label} mock verification", status, 200)
        check(f"{label} session", client.request("GET", "/api/v1/account-access/session")[0], 200)
        check(f"{label} profile read", client.request("GET", "/api/v1/profiles/me")[0], 200)
        profile = {
            "phone": phone,
            "firstName": "Test",
            "lastName": "Account",
            "income": "up-to-22",
            "job": "employee",
            "gender": "",
        }
        check(f"{label} profile write", client.request("PUT", "/api/v1/profiles", profile)[0], 200)
        status, stored = client.request("GET", "/api/v1/profiles/me")
        check(f"{label} profile persisted", status, 200)
        if stored.get("firstName") != profile["firstName"]:
            raise AssertionError("profile did not persist")
        for collection in ("recommendation-history", "bookmarks"):
            status, page = client.request("GET", "/api/v1/" + collection)
            check(f"{label} {collection} empty", status, 200)
            if page.get("items") != []:
                raise AssertionError("test account was not empty")

    check("cross-account profile write", first.request("PUT", "/api/v1/profiles", {"phone": phones[1]})[0], 403)
    status, questionnaire = first.request("POST", "/api/v1/questionnaire/sessions")
    check("questionnaire create", status, 201)
    session_id = questionnaire["sessionId"]
    session_path = "/api/v1/questionnaire/sessions/" + session_id
    check("questionnaire owner read", first.request("GET", session_path)[0], 200)
    check("questionnaire cross-account read", second.request("GET", session_path)[0], 403)
    check(
        "incomplete recommendation", first.request("POST", "/api/v1/recommendations", {"sessionId": session_id})[0], 422
    )
    questions = json.loads((ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text(encoding="utf-8"))[
        "questions"
    ]
    for question in questions:
        path = session_path + "/answers/" + question["questionId"]
        answer = {"answerId": question["answerOptions"][0]["answerId"]}
        check("answer " + question["questionId"], first.request("PUT", path, answer)[0], 200)
    first_answer = questions[0]
    path = session_path + "/answers/" + first_answer["questionId"]
    check(
        "cross-account answer denied",
        second.request("PUT", path, {"answerId": first_answer["answerOptions"][0]["answerId"]})[0],
        403,
    )
    check("invalid answer", first.request("PUT", path, {"answerId": "invalid"})[0], 422)
    status, resumed = first.request("GET", session_path)
    check("questionnaire persisted", status, 200)
    if len(resumed.get("answers", {})) != len(questions):
        raise AssertionError("questionnaire answers did not persist")
    check(
        "unpublished catalogue fails closed",
        first.request("POST", "/api/v1/recommendations", {"sessionId": session_id})[0],
        503,
    )
    check("missing published loan", first.request("GET", "/api/v1/loans/" + nil)[0], 404)
    check("missing history detail", first.request("GET", "/api/v1/recommendation-history/" + nil)[0], 404)
    check("missing history hide", first.request("DELETE", "/api/v1/recommendation-history/" + nil)[0], 404)
    check("missing bookmark save", first.request("PUT", "/api/v1/bookmarks/" + nil, {})[0], 404)
    check("missing bookmark remove", first.request("DELETE", "/api/v1/bookmarks/" + nil)[0], 204)

    if restart_api:
        require_isolated_local_api()
        docker("compose", "-p", PROJECT, "restart", "api")
        deadline = time.monotonic() + 90
        while True:
            try:
                status, _ = second.request("GET", "/api/v1/account-access/session")
                if status == 200:
                    break
            except OSError:
                pass
            if time.monotonic() >= deadline:
                raise AssertionError("isolated API did not recover after restart")
            time.sleep(1)
        check("B session after local restart", status, 200)
        check("B profile after local restart", second.request("GET", "/api/v1/profiles/me")[0], 200)

    check("A logout", first.request("POST", "/api/v1/account-access/logout")[0], 204)
    check("A after logout", first.request("GET", "/api/v1/account-access/session")[0], 401)
    check("B remains signed in", second.request("GET", "/api/v1/account-access/session")[0], 200)
    print("local checks completed; catalogue-dependent and online acceptance remain open")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--restart-api", action="store_true", help="restart only the guarded local T081 API")
    args = parser.parse_args()
    try:
        run(restart_api=args.restart_api)
    except (AssertionError, RuntimeError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        # Never echo HTTP bodies, request URLs, cookies, environment, or subprocess output.
        print(f"verification stopped: {type(exc).__name__}")
        raise SystemExit(1) from None
