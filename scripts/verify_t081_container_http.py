"""Exercise the published fixture through a guarded, loopback-bound API container."""

from __future__ import annotations

import hashlib
import json
import os
import secrets
import subprocess
import time
from pathlib import Path
from urllib.parse import urlsplit
from uuid import UUID

from sqlalchemy import create_engine, text

from scripts import verify_t081_local as local

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "tests/t081-fixture.compose.yml"
ENV_FILE = ROOT / ".env"
BASE = "http://127.0.0.1:58001"


def compose(*args: str) -> str:
    project = os.environ["SHAHAB_T081_COMPOSE_PROJECT"]
    result = subprocess.run(
        ["docker", "compose", "-p", project, "-f", str(COMPOSE), "--env-file", str(ENV_FILE), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def guard() -> str:
    project = os.environ.get("SHAHAB_T081_COMPOSE_PROJECT", "")
    address = urlsplit(os.environ.get("SHAHAB_TEST_DATABASE_URL", ""))
    if (
        not project.startswith("shahab-t081-fixture-")
        or os.environ.get("SHAHAB_ENVIRONMENT") != "local"
        or address.hostname != "127.0.0.1"
        or address.port != 55432
    ):
        raise RuntimeError("container HTTP verification requires the isolated local fixture")
    container = compose("ps", "-q", "api")
    if not container or len(container.splitlines()) != 1:
        raise RuntimeError("isolated API container is unavailable")
    metadata = json.loads(
        subprocess.run(["docker", "inspect", container], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    )[0]
    labels = metadata["Config"]["Labels"]
    environment = dict(item.split("=", 1) for item in metadata["Config"]["Env"] if "=" in item)
    ports = metadata["NetworkSettings"]["Ports"].get("8000/tcp") or []
    if (
        labels.get("com.docker.compose.project") != project
        or labels.get("com.docker.compose.service") != "api"
        or environment.get("SHAHAB_ENVIRONMENT") != "local"
        or environment.get("SHAHAB_PROFILE_MOCK_OTP_ENABLED", "").lower() != "true"
        or ports != [{"HostIp": "127.0.0.1", "HostPort": "58001"}]
    ):
        raise RuntimeError("API does not match the isolated loopback boundary")
    return metadata["Image"]


def expire(sql: str, **parameters) -> None:
    guard()
    engine = create_engine(os.environ["SHAHAB_TEST_DATABASE_URL"])
    try:
        with engine.begin() as connection:
            changed = connection.execute(text(sql), parameters)
            if changed.rowcount != 1:
                raise AssertionError("expected exactly one disposable test row for expiry")
    finally:
        engine.dispose()


def run() -> None:
    image_id = guard()
    local.BASE = BASE
    check = local.check
    anonymous, owner, other = local.Client(), local.Client(), local.Client()
    check("container liveness", anonymous.request("GET", "/api/v1/health/live")[0], 200)
    check("private readiness without token", anonymous.request("GET", "/api/v1/health/ready")[0], 404)
    for name, path in (
        ("session", "/api/v1/account-access/session"),
        ("profile", "/api/v1/profiles/me"),
        ("history", "/api/v1/recommendation-history"),
        ("bookmarks", "/api/v1/bookmarks"),
    ):
        check(f"anonymous {name}", anonymous.request("GET", path)[0], 401)
    check("invalid phone", anonymous.request("POST", "/api/v1/account-access/request", {"phone": "invalid"})[0], 422)

    suffix = secrets.randbelow(9000000) + 1000000
    phones = ("0900" + f"{suffix:07d}", "0900" + f"{(suffix + 1) % 10000000:07d}")
    for name, client, phone in (("owner", owner, phones[0]), ("other", other, phones[1])):
        status, challenge = client.request("POST", "/api/v1/account-access/request", {"phone": phone})
        check(f"{name} challenge", status, 200)
        check(
            f"{name} mock verify",
            client.request(
                "POST", "/api/v1/account-access/verify", {"challengeId": challenge["challengeId"], "code": "123456"}
            )[0],
            200,
        )
        check(f"{name} account session", client.request("GET", "/api/v1/account-access/session")[0], 200)
        profile = {
            "phone": phone,
            "firstName": "Test",
            "lastName": "Account",
            "income": "up-to-22",
            "job": "employee",
            "gender": "",
        }
        check(f"{name} profile write", client.request("PUT", "/api/v1/profiles", profile)[0], 200)
        status, stored = client.request("GET", "/api/v1/profiles/me")
        check(f"{name} profile read", status, 200)
        if stored.get("firstName") != "Test":
            raise AssertionError("profile was not persisted")

    check("cross-account profile write", owner.request("PUT", "/api/v1/profiles", {"phone": phones[1]})[0], 403)
    status, created = owner.request("POST", "/api/v1/questionnaire/sessions")
    check("questionnaire create", status, 201)
    questionnaire = "/api/v1/questionnaire/sessions/" + created["sessionId"]
    check("owner questionnaire read", owner.request("GET", questionnaire)[0], 200)
    check("other questionnaire read", other.request("GET", questionnaire)[0], 403)
    check(
        "incomplete recommendation",
        owner.request("POST", "/api/v1/recommendations", {"sessionId": created["sessionId"]})[0],
        422,
    )
    questions = json.loads((ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text(encoding="utf-8"))[
        "questions"
    ]
    for question in questions:
        path = questionnaire + "/answers/" + question["questionId"]
        answer = {"answerId": question["answerOptions"][0]["answerId"]}
        check("owner answer", owner.request("PUT", path, answer)[0], 200)
    first = questions[0]
    answer_path = questionnaire + "/answers/" + first["questionId"]
    check(
        "other answer denied",
        other.request("PUT", answer_path, {"answerId": first["answerOptions"][0]["answerId"]})[0],
        403,
    )
    check("invalid answer", owner.request("PUT", answer_path, {"answerId": "invalid"})[0], 422)
    started = time.perf_counter()
    status, recommendation = owner.request("POST", "/api/v1/recommendations", {"sessionId": created["sessionId"]})
    elapsed_ms = round((time.perf_counter() - started) * 1000)
    check("published recommendation", status, 200)
    if (
        recommendation.get("configVersion") != "1.1.0"
        or sum(
            len(recommendation[k]) for k in ("rankedRecommendations", "lowCompatibilityRecommendations", "needsReview")
        )
        != 102
    ):
        raise AssertionError("published recommendation contract drifted")
    history_id = recommendation["historyId"]
    loan_id = recommendation["rankedRecommendations"][0]["loanId"]
    history_path = "/api/v1/recommendation-history/" + history_id
    bookmark_path = "/api/v1/bookmarks/" + loan_id
    check("published loan detail", owner.request("GET", "/api/v1/loans/" + loan_id)[0], 200)
    check("history detail owner", owner.request("GET", history_path)[0], 200)
    check("history detail other", other.request("GET", history_path)[0], 404)
    check("bookmark save", owner.request("PUT", bookmark_path, {"historyId": history_id})[0], 204)
    for name, path in (("history", "/api/v1/recommendation-history"), ("bookmarks", "/api/v1/bookmarks")):
        status, page = owner.request("GET", path)
        check(f"nonempty {name} before restart", status, 200)
        if len(page.get("items", [])) != 1:
            raise AssertionError("expected one persisted owner item before restart")
        status, page = other.request("GET", path)
        check(f"other {name} before restart", status, 200)
        if page.get("items") != []:
            raise AssertionError("other account saw owner data")

    guard()
    compose("--profile", "http", "restart", "api")
    deadline = time.monotonic() + 90
    while True:
        try:
            status, _ = owner.request("GET", "/api/v1/account-access/session")
            if status == 200:
                break
        except OSError:
            pass
        if time.monotonic() >= deadline:
            raise AssertionError("isolated API did not recover after restart")
        time.sleep(1)
    guard()
    check("owner session after restart", status, 200)
    check("other session after restart", other.request("GET", "/api/v1/account-access/session")[0], 200)
    check("profile after restart", owner.request("GET", "/api/v1/profiles/me")[0], 200)
    check("questionnaire after restart", owner.request("GET", questionnaire)[0], 200)
    for name, path in (("history", "/api/v1/recommendation-history"), ("bookmarks", "/api/v1/bookmarks")):
        status, page = owner.request("GET", path)
        check(f"nonempty {name} after restart", status, 200)
        if len(page.get("items", [])) != 1:
            raise AssertionError("owner data did not survive API restart")
    check("other history denied after restart", other.request("GET", history_path)[0], 404)
    check("other history hide denied", other.request("DELETE", history_path)[0], 404)
    check("owner history hide", owner.request("DELETE", history_path)[0], 204)
    check("hidden history detail", owner.request("GET", history_path)[0], 404)
    check("owner bookmark remove", owner.request("DELETE", bookmark_path)[0], 204)
    for name, path in (("history", "/api/v1/recommendation-history"), ("bookmarks", "/api/v1/bookmarks")):
        status, page = owner.request("GET", path)
        check(f"empty {name} after hide/remove", status, 200)
        if page.get("items") != []:
            raise AssertionError("removed item remains visible")
    engine = create_engine(os.environ["SHAHAB_TEST_DATABASE_URL"])
    try:
        with engine.connect() as connection:
            hidden = connection.scalar(
                text(
                    "SELECT hidden_at IS NOT NULL FROM recommendation_history_runs "
                    "WHERE recommendation_history_run_id=:id"
                ),
                {"id": UUID(history_id)},
            )
            removed = connection.scalar(
                text("SELECT removed_at IS NOT NULL FROM account_bookmarks WHERE source_history_run_id=:id"),
                {"id": UUID(history_id)},
            )
            if hidden is not True or removed is not True:
                raise AssertionError("hidden history or removed bookmark did not persist as retained rows")
    finally:
        engine.dispose()

    status, expiring = other.request("POST", "/api/v1/questionnaire/sessions")
    check("expiring questionnaire create", status, 201)
    expire(
        "UPDATE questionnaire_sessions SET created_at=now()-interval '31 minutes', "
        "expires_at=now()-interval '1 minute' WHERE questionnaire_session_id=:id",
        id=UUID(expiring["sessionId"]),
    )
    check(
        "expired questionnaire", other.request("GET", "/api/v1/questionnaire/sessions/" + expiring["sessionId"])[0], 410
    )
    check("owner logout", owner.request("POST", "/api/v1/account-access/logout")[0], 204)
    check("owner session after logout", owner.request("GET", "/api/v1/account-access/session")[0], 401)
    check("other remains signed in", other.request("GET", "/api/v1/account-access/session")[0], 200)
    expired_token = secrets.token_urlsafe(32)
    expire(
        "INSERT INTO account_access_sessions (token_digest, account_id, issued_at, expires_at) "
        "SELECT :digest, account_id, now()-interval '2 hours', now()-interval '1 hour' "
        "FROM accounts WHERE phone=:phone AND status='active'",
        digest=hashlib.sha256(expired_token.encode()).hexdigest(),
        phone=phones[1],
    )
    expired = local.Client()
    expired.opener.addheaders = [("Cookie", "shahab_account_access=" + expired_token)]
    check("expired account session", expired.request("GET", "/api/v1/account-access/session")[0], 401)
    print(f"container HTTP checks passed; image_id={image_id}; recommendation_duration_ms={elapsed_ms}")


if __name__ == "__main__":
    try:
        run()
    except Exception:
        print("container HTTP verification stopped; inspect only the isolated fixture project")
        raise SystemExit(1) from None
