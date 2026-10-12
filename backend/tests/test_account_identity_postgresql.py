"""Real PostgreSQL acceptance: legacy preservation, generation isolation and two-connection races.

CI supplies a disposable test database. Never point these destructive fixture
setup/teardown helpers at user, staging or production databases.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from threading import Barrier
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from backend.app.accounts.profile_repository import ensure_profile
from backend.app.api.errors import ApiError
from backend.app.core.config import Settings
from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
from backend.app.infrastructure.db.account_backfill import backfill_accounts
from backend.app.main import create_app
from scripts.build_t05a_import_manifest import build_manifest
from scripts.build_t05a_recommendation_config import build_config

DATABASE_URL = os.environ.get("SHAHAB_TEST_DATABASE_URL")
ROOT = Path(__file__).parents[2]
OLD = "b4d8e1f2a3c5"
EXPAND = "aa11b02a2001"


@unittest.skipUnless(DATABASE_URL, "requires real PostgreSQL SHAHAB_TEST_DATABASE_URL")
class AccountIdentityPostgreSqlTests(unittest.TestCase):
    def setUp(self) -> None:
        self.environment = {**os.environ, "SHAHAB_DATABASE_URL": str(DATABASE_URL)}
        self.engine = create_engine(str(DATABASE_URL))
        self.alembic("downgrade", "base")

    def tearDown(self) -> None:
        # Tests asserting the guard restore their own synthetic fixture to the
        # pre-archive state before teardown. This is not a product archive API.
        self.alembic("downgrade", "base")
        self.engine.dispose()

    def alembic(self, *arguments: str, check: bool = True):
        return subprocess.run(
            [sys.executable, "-c", "from alembic.config import main; main()", *arguments],
            env=self.environment,
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=check,
        )

    def legacy_fixture(self) -> tuple[uuid.UUID, uuid.UUID]:
        self.alembic("upgrade", OLD)
        with Session(self.engine) as db, db.begin():
            materialize_official_sources(
                db,
                loan_manifest=build_manifest(),
                config_manifest=build_config(),
                questionnaire=json.loads((ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text()),
                identifiers=json.loads((ROOT / "data/contracts/canonical-identifiers.v1.json").read_text()),
                actor_reference="account-migration-fixture",
                approval_reason="synthetic fixture",
            )
        sid, hid = uuid.uuid4(), uuid.uuid4()
        now = datetime.now(UTC) - timedelta(minutes=5)
        with self.engine.begin() as c:
            for phone in ("09000000001", "09000000002"):
                c.execute(
                    text(
                        "INSERT INTO user_profiles "
                        "(phone,first_name,last_name,income,job,gender,avatar_data_url,created_at,updated_at) "
                        "VALUES (:p,'آزمون','تست','22-to-50','manager','female',:avatar,:created,:updated)"
                    ),
                    {
                        "p": phone,
                        "avatar": "data:image/png;base64,iVBORw0KGgpmaXh0dXJl",
                        "created": now,
                        "updated": now,
                    },
                )
            qv = c.scalar(text("SELECT questionnaire_version_id FROM questionnaire_versions LIMIT 1"))
            loan = c.scalar(text("SELECT loan_product_version_id FROM loan_product_versions LIMIT 1"))
            # A pre-owner-bind historical session and an unrelated anonymous session.
            for session_id in (sid, uuid.uuid4()):
                c.execute(
                    text(
                        "INSERT INTO questionnaire_sessions "
                        "(questionnaire_session_id,questionnaire_version_id,state,created_at,expires_at) "
                        "VALUES (:sid,:qv,'ACTIVE',:now,:expires)"
                    ),
                    {"sid": session_id, "qv": qv, "now": now, "expires": now + timedelta(minutes=30)},
                )
            answer = c.execute(text("SELECT question_id, answer_option_id FROM answer_options LIMIT 1")).one()
            c.execute(
                text("INSERT INTO questionnaire_answers VALUES (:id,:sid,:q,:a)"),
                {"id": uuid.uuid4(), "sid": sid, "q": answer[0], "a": answer[1]},
            )
            c.execute(
                text(
                    "INSERT INTO recommendation_history_runs "
                    "(recommendation_history_run_id,owner_phone,questionnaire_session_id,data_version,"
                    "config_version,created_at,hidden_at) "
                    "VALUES (:hid,'09000000001',:sid,'fixture-data','fixture-config',:now,:now)"
                ),
                {"hid": hid, "sid": sid, "now": now},
            )
            iid = uuid.uuid4()
            c.execute(
                text(
                    "INSERT INTO recommendation_history_items "
                    "(recommendation_history_item_id,recommendation_history_run_id,section,display_order,"
                    "loan_product_version_id,lender_name,loan_name,bank_logo_reference,compatibility_score,"
                    "compatibility_reason,max_amount_tomans,monthly_installment_tomans,max_repayment_months,"
                    "interest_rate_percent) "
                    "VALUES (:iid,:hid,'review',0,:loan,'fixture lender','fixture "
                    "loan',NULL,NULL,NULL,123456,2222,12,4)"
                ),
                {"iid": iid, "hid": hid, "loan": loan},
            )
            c.execute(
                text("INSERT INTO recommendation_history_item_reasons VALUES (:iid,0,'fixture exclusion')"),
                {"iid": iid},
            )
        return sid, hid

    def retained(self) -> dict:
        with self.engine.connect() as c:
            result = {}
            for table, omitted in (
                ("user_profiles", {"phone", "account_id"}),
                ("recommendation_history_runs", {"owner_phone", "owner_account_id"}),
                ("recommendation_history_items", set()),
                ("recommendation_history_item_reasons", set()),
                ("questionnaire_answers", set()),
            ):
                rows = [
                    {k: v for k, v in row.items() if k not in omitted}
                    for row in c.execute(text(f"SELECT * FROM {table}")).mappings()
                ]
                result[table] = sorted(rows, key=str)
            return result

    def test_legacy_snapshot_backfill_retry_and_lossless_rollback(self) -> None:
        sid, hid = self.legacy_fixture()
        before = self.retained()
        self.alembic("upgrade", EXPAND)
        with self.engine.begin() as c:
            first = backfill_accounts(c)
            mapping = c.execute(text("SELECT phone,account_id FROM accounts ORDER BY phone")).all()
        with self.engine.begin() as c:
            self.assertEqual(backfill_accounts(c), first)
            self.assertEqual(c.execute(text("SELECT phone,account_id FROM accounts ORDER BY phone")).all(), mapping)
        self.alembic("upgrade", "head")
        self.assertEqual(before, self.retained())
        with self.engine.connect() as c:
            aid = mapping[0][1]
            self.assertEqual(
                c.scalar(
                    text("SELECT owner_account_id FROM questionnaire_sessions WHERE questionnaire_session_id=:sid"),
                    {"sid": sid},
                ),
                aid,
            )
            self.assertEqual(
                c.scalar(
                    text(
                        "SELECT owner_account_id FROM recommendation_history_runs WHERE "
                        "recommendation_history_run_id=:hid"
                    ),
                    {"hid": hid},
                ),
                aid,
            )
            self.assertEqual(
                c.scalar(text("SELECT count(*) FROM questionnaire_sessions WHERE owner_account_id IS NULL")), 1
            )
            self.assertEqual(
                c.scalar(
                    text(
                        "SELECT count(*) FROM accounts a LEFT JOIN user_profiles p USING(account_id) WHERE "
                        "p.account_id IS NULL"
                    )
                ),
                0,
            )
        self.alembic("downgrade", EXPAND)
        legacy_indexes = {
            index["name"]: index["column_names"]
            for index in inspect(self.engine).get_indexes("recommendation_history_runs")
        }
        self.assertEqual(
            legacy_indexes["ix_recommendation_history_visible_owner_created"],
            ["owner_phone", "hidden_at", "created_at", "recommendation_history_run_id"],
        )
        self.assertEqual(before, self.retained())
        self.alembic("upgrade", "head")
        self.assertEqual(before, self.retained())
        with self.engine.connect() as c:
            self.assertEqual(c.execute(text("SELECT phone,account_id FROM accounts ORDER BY phone")).all(), mapping)
        self.alembic("downgrade", OLD)
        self.assertEqual(before, self.retained())

    def test_wrong_owner_composite_fk_and_bound_session_retarget_are_rejected(self) -> None:
        sid, _ = self.legacy_fixture()
        self.alembic("upgrade", "head")
        before = self.retained()
        with self.engine.connect() as c:
            other = c.scalar(text("SELECT account_id FROM accounts WHERE phone='09000000002'"))
        with self.assertRaises(IntegrityError), self.engine.begin() as c:
            c.execute(
                text("UPDATE recommendation_history_runs SET owner_account_id=:a WHERE questionnaire_session_id=:sid"),
                {"a": other, "sid": sid},
            )
        with self.assertRaises(DBAPIError), self.engine.begin() as c:
            c.execute(
                text("UPDATE questionnaire_sessions SET owner_account_id=:a WHERE questionnaire_session_id=:sid"),
                {"a": other, "sid": sid},
            )
        self.assertEqual(before, self.retained())

    def test_physical_schema_and_identity_constraints_match_the_contract(self) -> None:
        self.alembic("upgrade", "head")
        schema = inspect(self.engine)
        self.assertEqual(schema.get_pk_constraint("user_profiles")["constrained_columns"], ["account_id"])
        self.assertNotIn("phone", {column["name"] for column in schema.get_columns("user_profiles")})
        for table in ("questionnaire_sessions", "recommendation_history_runs"):
            self.assertNotIn("owner_phone", {column["name"] for column in schema.get_columns(table)})
        pair = next(
            fk
            for fk in schema.get_foreign_keys("recommendation_history_runs")
            if fk["name"] == "fk_history_session_owner"
        )
        self.assertEqual(pair["constrained_columns"], ["questionnaire_session_id", "owner_account_id"])
        self.assertEqual(pair["options"]["ondelete"], "RESTRICT")
        index = next(i for i in schema.get_indexes("accounts") if i["name"] == "uq_account_active_phone")
        self.assertTrue(index["unique"])
        self.assertIn("active", index["dialect_options"]["postgresql_where"])
        with Session(self.engine) as db:
            actor = ensure_profile("09000000001", db)
        for sql in (
            "UPDATE accounts SET phone='09000000002' WHERE account_id=:id",
            "DELETE FROM accounts WHERE account_id=:id",
        ):
            with self.assertRaises(DBAPIError), self.engine.begin() as c:
                c.execute(text(sql), {"id": actor.account_id})
        for phone, status in (("invalid", "active"), ("09000000002", "unknown"), ("09000000002", "archived")):
            with self.assertRaises(IntegrityError), self.engine.begin() as c:
                c.execute(
                    text("INSERT INTO accounts (account_id,phone,status) VALUES (:id,:p,:s)"),
                    {"id": uuid.uuid4(), "p": phone, "s": status},
                )

    def test_invalid_legacy_phone_refuses_cutover_without_data_loss(self) -> None:
        self.alembic("upgrade", EXPAND)
        with self.engine.begin() as c:
            c.execute(text("INSERT INTO user_profiles (phone) VALUES ('invalid')"))
        rejected = self.alembic("upgrade", "head", check=False)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("Legacy account audit failed", rejected.stderr)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(text("SELECT version_num FROM alembic_version")), EXPAND)
            self.assertEqual(c.scalar(text("SELECT count(*) FROM accounts")), 0)
            self.assertEqual(c.scalar(text("SELECT count(*) FROM user_profiles")), 1)

    def test_two_connections_create_only_one_complete_active_account(self) -> None:
        self.alembic("upgrade", "head")
        barrier = Barrier(2)

        def verify():
            with Session(self.engine) as db:
                scalar = db.scalar
                first = True

                def synchronized(*args, **kwargs):
                    nonlocal first
                    result = scalar(*args, **kwargs)
                    if first:
                        first = False
                        self.assertIsNone(result)
                        barrier.wait(timeout=10)
                    return result

                with patch.object(db, "scalar", side_effect=synchronized):
                    return ensure_profile("09000000001", db)

        with ThreadPoolExecutor(max_workers=2) as executor:
            a, b = list(executor.map(lambda _: verify(), range(2)))
        self.assertEqual(a.account_id, b.account_id)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(text("SELECT count(*) FROM accounts")), 1)
            self.assertEqual(c.scalar(text("SELECT count(*) FROM user_profiles")), 1)
        with self.assertRaises(IntegrityError), self.engine.begin() as c:
            c.execute(text("INSERT INTO accounts (account_id,phone) VALUES (:id,'09000000001')"), {"id": uuid.uuid4()})

    def test_profile_failure_rolls_back_account_before_capability_publication(self) -> None:
        self.alembic("upgrade", "head")
        with self.engine.begin() as c:
            c.execute(
                text(
                    "CREATE FUNCTION reject_fixture_profile() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN "
                    "RAISE EXCEPTION 'fixture'; END $$"
                )
            )
            c.execute(
                text(
                    "CREATE TRIGGER reject_fixture_profile BEFORE INSERT ON user_profiles FOR EACH ROW "
                    "EXECUTE FUNCTION reject_fixture_profile()"
                )
            )
        try:
            with Session(self.engine) as db, self.assertRaises(ApiError):
                ensure_profile("09000000001", db)
            with self.engine.connect() as c:
                self.assertEqual(c.scalar(text("SELECT count(*) FROM accounts")), 0)
                self.assertEqual(c.scalar(text("SELECT count(*) FROM user_profiles")), 0)
        finally:
            with self.engine.begin() as c:
                c.execute(text("DROP TRIGGER reject_fixture_profile ON user_profiles"))
                c.execute(text("DROP FUNCTION reject_fixture_profile()"))

    def test_archived_generation_stale_capability_and_downgrade_guard(self) -> None:
        self.legacy_fixture()
        self.alembic("upgrade", "head")
        old_snapshot = self.retained()
        with TestClient(create_app(Settings(database_url=str(DATABASE_URL)))) as client:

            def login():
                challenge = client.post("/api/v1/account-access/request", json={"phone": "09000000001"}).json()
                result = client.post(
                    "/api/v1/account-access/verify", json={"challengeId": challenge["challengeId"], "code": "123456"}
                )
                self.assertEqual(result.status_code, 200, result.text)
                return {"Authorization": "Bearer " + result.json()["accessToken"]}

            old_token = login()
            with self.engine.begin() as c:
                old_id = c.scalar(text("SELECT account_id FROM accounts WHERE phone='09000000001' AND status='active'"))
                c.execute(
                    text("UPDATE accounts SET status='archived', archived_at=now() WHERE account_id=:id"),
                    {"id": old_id},
                )
            new_id = None
            try:
                with self.assertRaises(DBAPIError), self.engine.begin() as c:
                    c.execute(
                        text("UPDATE accounts SET status='active', archived_at=NULL WHERE account_id=:id"),
                        {"id": old_id},
                    )
                new_token = login()
                for method, path, body in (
                    ("GET", "/api/v1/profiles/me", None),
                    ("GET", "/api/v1/recommendation-history", None),
                    ("PUT", "/api/v1/profiles", {"phone": "09000000001", "firstName": "forged"}),
                ):
                    response = client.request(method, path, headers=old_token, json=body)
                    self.assertEqual(response.status_code, 401)
                current = client.get("/api/v1/profiles/me", headers=new_token)
                self.assertEqual(current.status_code, 200)
                self.assertEqual(current.json()["firstName"], "")
                self.assertEqual(client.get("/api/v1/recommendation-history", headers=new_token).json()["items"], [])
                with self.engine.connect() as c:
                    new_id = c.scalar(
                        text("SELECT account_id FROM accounts WHERE phone='09000000001' AND status='active'")
                    )
                self.assertNotEqual(new_id, old_id)
                rejected = self.alembic("downgrade", OLD, check=False)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertIn("multiple retained generations", rejected.stderr)
                with self.engine.connect() as c:
                    self.assertEqual(c.scalar(text("SELECT version_num FROM alembic_version")), "bb11b02b0001")
                    self.assertEqual(c.scalar(text("SELECT count(*) FROM accounts WHERE phone='09000000001'")), 2)
                # Historical snapshots remain byte-equivalent; only one empty new profile was added.
                retained = self.retained()
                for key in old_snapshot:
                    if key != "user_profiles":
                        self.assertEqual(old_snapshot[key], retained[key])
            finally:
                # Fixture-only undo for reusable disposable database, not application behavior.
                with self.engine.begin() as c:
                    c.execute(text("DELETE FROM user_profiles WHERE account_id=:id"), {"id": new_id})
                    c.execute(text("DELETE FROM accounts WHERE account_id=:id"), {"id": new_id})
                    c.execute(text("ALTER TABLE accounts DISABLE TRIGGER protect_account_identity"))
                    c.execute(
                        text("UPDATE accounts SET status='active', archived_at=NULL WHERE account_id=:id"),
                        {"id": old_id},
                    )
                    c.execute(text("ALTER TABLE accounts ENABLE TRIGGER protect_account_identity"))
