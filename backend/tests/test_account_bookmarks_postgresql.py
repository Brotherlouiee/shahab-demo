"""Real PostgreSQL bookmark migration, owner isolation, retries and transaction races.

The established fixture owns a disposable CI database. Its teardown deliberately
removes only its synthetic bookmark rows to exercise the guarded schema rollback;
never supply a customer/production URL to this suite.
"""

import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from fastapi.testclient import TestClient
from sqlalchemy import inspect, select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from backend.app.accounts.bookmarks import AccountBookmarkRepository
from backend.app.accounts.identity import AccountActor
from backend.app.core.config import Settings
from backend.app.infrastructure.db.models import AccountBookmark
from backend.app.main import create_app
from backend.tests import test_account_identity_postgresql as fixture


@unittest.skipUnless(fixture.DATABASE_URL, "requires real PostgreSQL SHAHAB_TEST_DATABASE_URL")
class AccountBookmarksPostgreSqlTests(unittest.TestCase):
    setUp = fixture.AccountIdentityPostgreSqlTests.setUp

    def alembic(self, *arguments, check=True):
        result = fixture.AccountIdentityPostgreSqlTests.alembic(self, *arguments, check=False)
        if check and result.returncode:
            self.fail(f"alembic {arguments}: {result.stdout}\n{result.stderr}")
        return result

    legacy_fixture = fixture.AccountIdentityPostgreSqlTests.legacy_fixture
    retained = fixture.AccountIdentityPostgreSqlTests.retained

    def tearDown(self):
        with self.engine.begin() as c:
            if inspect(c).has_table("account_bookmarks"):
                c.execute(text("DELETE FROM account_bookmarks"))
            if getattr(self, "performance_fixture", False):
                # Only the 2000 synthetic accounts created by this test; never user data.
                c.execute(
                    text(
                        "DELETE FROM accounts WHERE account_id IN "
                        "(SELECT md5('bookmark-fixture-'||i)::uuid FROM generate_series(10000,11999) i)"
                    )
                )
            if getattr(self, "new_generation", None):
                aid = self.new_generation
                c.execute(text("DELETE FROM account_access_sessions WHERE account_id=:id"), {"id": aid})
                c.execute(text("DELETE FROM user_profiles WHERE account_id=:id"), {"id": aid})
                c.execute(text("DELETE FROM accounts WHERE account_id=:id"), {"id": aid})
            if inspect(c).has_table("accounts"):
                c.execute(text("ALTER TABLE accounts DISABLE TRIGGER protect_account_identity"))
                c.execute(text("UPDATE accounts SET status='active',archived_at=NULL WHERE status='archived'"))
                c.execute(text("ALTER TABLE accounts ENABLE TRIGGER protect_account_identity"))
        fixture.AccountIdentityPostgreSqlTests.tearDown(self)

    def prepare(self, *, head=True):
        _, self.hid = self.legacy_fixture()
        self.alembic("upgrade", "head" if head else "cc11b02c0001")
        with self.engine.begin() as c:
            c.execute(
                text("UPDATE recommendation_history_runs SET hidden_at=NULL WHERE recommendation_history_run_id=:id"),
                {"id": self.hid},
            )
            self.loan = c.scalar(
                text(
                    "SELECT loan_product_version_id FROM recommendation_history_items "
                    "WHERE recommendation_history_run_id=:id LIMIT 1"
                ),
                {"id": self.hid},
            )
            accounts = c.execute(text("SELECT account_id,phone FROM accounts ORDER BY phone")).all()
            self.a, self.b = [AccountActor(*row) for row in accounts]

    def login(self, client, phone):
        challenge = client.post("/api/v1/account-access/request", json={"phone": phone})
        self.assertEqual(challenge.status_code, 200, challenge.text)
        response = client.post(
            "/api/v1/account-access/verify", json={"challengeId": challenge.json()["challengeId"], "code": "123456"}
        )
        self.assertEqual(response.status_code, 200, response.text)
        return {"Authorization": "Bearer " + response.json()["accessToken"]}

    def test_additive_upgrade_preserves_old_graph_constraints_and_guarded_rollback(self):
        self.prepare(head=False)
        before = self.retained()
        self.alembic("upgrade", "head")
        self.assertEqual(before, self.retained())
        schema = inspect(self.engine)
        self.assertEqual(
            schema.get_pk_constraint("account_bookmarks")["constrained_columns"],
            ["account_id", "loan_product_version_id"],
        )
        self.assertEqual(
            {c["name"] for c in schema.get_columns("account_bookmarks")},
            {"account_id", "loan_product_version_id", "source_history_run_id", "created_at", "removed_at"},
        )
        with Session(self.engine) as db, db.begin():
            AccountBookmarkRepository(db).save(self.a, self.loan, self.hid)
        for owner, version, source in (
            (self.b.account_id, self.loan, self.hid),
            (self.a.account_id, uuid.uuid4(), None),
        ):
            with self.assertRaises(IntegrityError), self.engine.begin() as c:
                c.execute(
                    text(
                        "INSERT INTO account_bookmarks (account_id,loan_product_version_id,source_history_run_id) "
                        "VALUES (:a,:l,:h)"
                    ),
                    {"a": owner, "l": version, "h": source},
                )
        with self.assertRaises(DBAPIError), self.engine.begin() as c:
            c.execute(
                text("UPDATE account_bookmarks SET account_id=:other WHERE account_id=:id"),
                {"other": self.b.account_id, "id": self.a.account_id},
            )
        refused = self.almbic_downgrade_guard()
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("Retained bookmarks", refused.stderr)
        self.assertEqual(before, self.retained())
        with self.engine.begin() as c:
            self.assertEqual(c.scalar(text("SELECT count(*) FROM account_bookmarks")), 1)
            c.execute(text("DELETE FROM account_bookmarks"))  # synthetic fixture only
        self.alembic("downgrade", "cc11b02c0001")
        self.assertEqual(before, self.retained())
        self.alembic("upgrade", "head")
        self.assertEqual(before, self.retained())

    def almbic_downgrade_guard(self):
        return self.alembic("downgrade", "cc11b02c0001", check=False)

    def test_two_real_api_devices_share_account_without_cross_account_access(self):
        self.prepare()
        before = self.retained()
        settings = Settings(database_url=str(fixture.DATABASE_URL))
        with (
            TestClient(create_app(settings)) as first,
            TestClient(create_app(settings)) as second,
            TestClient(create_app(settings)) as other,
        ):
            h1 = self.login(first, self.a.phone)
            h2 = self.login(second, self.a.phone)
            hb = self.login(other, self.b.phone)
            path = f"/api/v1/bookmarks/{self.loan}"
            for _ in range(2):
                self.assertEqual(first.put(path, headers=h1, json={"historyId": str(self.hid)}).status_code, 204)
            a = first.get("/api/v1/bookmarks", headers=h1).json()
            self.assertEqual(a, second.get("/api/v1/bookmarks", headers=h2).json())
            self.assertEqual(a["items"][0]["loanId"], str(self.loan))
            self.assertEqual(other.get("/api/v1/bookmarks", headers=hb).json()["items"], [])
            self.assertEqual(other.put(path, headers=hb, json={"historyId": str(self.hid)}).status_code, 404)
            self.assertEqual(other.delete(path, headers=hb).status_code, 204)
            self.assertEqual(first.get("/api/v1/bookmarks", headers=h1).json(), a)
            for _ in range(2):
                self.assertEqual(second.delete(path, headers=h2).status_code, 204)
            self.assertEqual(first.get("/api/v1/bookmarks", headers=h1).json()["items"], [])
            self.assertEqual(first.put(path, headers=h1, json={}).status_code, 204)
            self.assertEqual(first.post("/api/v1/account-access/logout", headers=h1).status_code, 204)
            self.assertEqual(first.get("/api/v1/bookmarks", headers=h1).status_code, 401)
            self.assertEqual(second.get("/api/v1/bookmarks", headers=h2).json(), a)
        self.assertEqual(before, self.retained())

    def test_concurrent_desired_state_insert_is_unique_and_retry_preserves_context(self):
        self.prepare()
        barrier = Barrier(2)

        def save():
            with Session(self.engine) as db, db.begin():
                barrier.wait(timeout=10)
                AccountBookmarkRepository(db).save(self.a, self.loan, self.hid)

        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(lambda _: save(), range(2)))
        with Session(self.engine) as db:
            row = db.scalar(select(AccountBookmark))
            original = (row.created_at, row.source_history_run_id)
            db.rollback()
            AccountBookmarkRepository(db).save(self.a, self.loan)
            db.commit()
            db.expire_all()
            row = db.scalar(select(AccountBookmark))
            self.assertEqual((row.created_at, row.source_history_run_id), original)
            self.assertEqual(len(list(db.scalars(select(AccountBookmark)))), 1)

    def test_write_failure_is_atomic_and_retry_safe(self):
        self.prepare()
        before = self.retained()
        with self.engine.begin() as c:
            c.execute(
                text(
                    "CREATE FUNCTION reject_bookmark_fixture() RETURNS trigger LANGUAGE plpgsql AS $$ "
                    "BEGIN RAISE EXCEPTION 'fixture'; END $$"
                )
            )
            c.execute(
                text(
                    "CREATE TRIGGER reject_bookmark_fixture BEFORE INSERT ON account_bookmarks "
                    "FOR EACH ROW EXECUTE FUNCTION reject_bookmark_fixture()"
                )
            )
        try:
            with TestClient(create_app(Settings(database_url=str(fixture.DATABASE_URL)))) as client:
                headers = self.login(client, self.a.phone)
                response = client.put(f"/api/v1/bookmarks/{self.loan}", headers=headers, json={})
                self.assertEqual(response.status_code, 503)
                self.assertNotIn("fixture", response.text)
            with self.engine.connect() as c:
                self.assertEqual(c.scalar(text("SELECT count(*) FROM account_bookmarks")), 0)
            self.assertEqual(before, self.retained())
        finally:
            with self.engine.begin() as c:
                c.execute(text("DROP TRIGGER reject_bookmark_fixture ON account_bookmarks"))
                c.execute(text("DROP FUNCTION reject_bookmark_fixture()"))
        with Session(self.engine) as db, db.begin():
            AccountBookmarkRepository(db).save(self.a, self.loan)

    def test_archived_generation_stale_token_new_same_phone_and_retained_bookmark(self):
        self.prepare()
        with TestClient(create_app(Settings(database_url=str(fixture.DATABASE_URL)))) as client:
            old = self.login(client, self.a.phone)
            path = f"/api/v1/bookmarks/{self.loan}"
            self.assertEqual(client.put(path, headers=old, json={}).status_code, 204)
            with self.engine.begin() as c:
                c.execute(
                    text("UPDATE accounts SET status='archived',archived_at=now() WHERE account_id=:id"),
                    {"id": self.a.account_id},
                )
            for method in ("get", "put", "delete"):
                response = getattr(client, method)(
                    "/api/v1/bookmarks" if method == "get" else path,
                    headers=old,
                    **({"json": {}} if method == "put" else {}),
                )
                self.assertEqual(response.status_code, 401)
            new = self.login(client, self.a.phone)
            with self.engine.connect() as c:
                self.new_generation = c.scalar(
                    text("SELECT account_id FROM accounts WHERE phone=:p AND status='active'"), {"p": self.a.phone}
                )
                self.assertNotEqual(self.new_generation, self.a.account_id)
                self.assertEqual(
                    c.scalar(
                        text("SELECT count(*) FROM account_bookmarks WHERE account_id=:a"), {"a": self.a.account_id}
                    ),
                    1,
                )
            self.assertEqual(client.get("/api/v1/bookmarks", headers=new).json()["items"], [])

    def test_keyset_pagination_and_selective_owner_index_on_representative_associations(self):
        self.prepare()
        self.performance_fixture = True
        with self.engine.begin() as c:
            c.execute(
                text(
                    "INSERT INTO accounts (account_id,phone,status) SELECT md5('bookmark-fixture-'||i)::uuid, "
                    "'09'||lpad(i::text,9,'0'),'active' FROM generate_series(10000,11999) i"
                )
            )
            c.execute(
                text(
                    "INSERT INTO account_bookmarks (account_id,loan_product_version_id) "
                    "SELECT account_id,:l FROM accounts"
                ),
                {"l": self.loan},
            )
            c.execute(text("ANALYZE account_bookmarks"))
            plan = c.scalar(
                text(
                    "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) SELECT loan_product_version_id "
                    "FROM account_bookmarks WHERE account_id=:a AND removed_at IS NULL "
                    "ORDER BY created_at,loan_product_version_id LIMIT 51"
                ),
                {"a": self.a.account_id},
            )
            self.assertIn("Index", str(plan))
        with Session(self.engine) as db:
            repository = AccountBookmarkRepository(db)
            self.assertEqual(len(repository.list_for_owner(self.a, 50)), 1)
            db.rollback()
            with self.engine.connect() as c:
                loans = (
                    c.execute(
                        text(
                            "SELECT loan_product_version_id FROM loan_product_versions "
                            "ORDER BY loan_product_version_id LIMIT 4"
                        )
                    )
                    .scalars()
                    .all()
                )
            for loan in loans:
                repository.save(self.a, loan)
            db.commit()
            first = repository.list_for_owner(self.a, 2)
            self.assertEqual(len(first), 3)
            cursor = (first[1][0].created_at, first[1][0].loan_product_version_id)
            second = repository.list_for_owner(self.a, 2, cursor)
            self.assertFalse(
                {r[0].loan_product_version_id for r in first[:2]} & {r[0].loan_product_version_id for r in second}
            )


    def test_server_archive_revokes_every_credential_and_preserves_bookmarks(self):
        from backend.app.accounts.identity import archive_account

        self.prepare()
        before = self.retained()
        with TestClient(create_app(Settings(database_url=str(fixture.DATABASE_URL)))) as first, TestClient(
            create_app(Settings(database_url=str(fixture.DATABASE_URL)))
        ) as second:
            original_one = self.login(first, self.a.phone)
            original_two = self.login(second, self.a.phone)
            path = f"/api/v1/bookmarks/{self.loan}"
            self.assertEqual(first.put(path, headers=original_one, json={"historyId": str(self.hid)}).status_code, 204)
            with Session(self.engine) as db:
                archive_account(self.a.account_id, db)
            for credentials in (original_one, original_two):
                self.assertEqual(first.get("/api/v1/profiles/me", headers=credentials).status_code, 401)
                self.assertEqual(second.get("/api/v1/bookmarks", headers=credentials).status_code, 401)
                self.assertEqual(first.get("/api/v1/recommendation-history", headers=credentials).status_code, 401)
            with self.engine.connect() as connection:
                self.assertEqual(
                    connection.scalar(text("SELECT count(*) FROM account_access_sessions WHERE account_id=:a AND revoked_at IS NOT NULL"),
                                      {"a": self.a.account_id}), 2
                )
                self.assertEqual(connection.scalar(text("SELECT count(*) FROM account_bookmarks WHERE account_id=:a"), {"a": self.a.account_id}), 1)
                self.assertEqual(connection.scalar(text("SELECT status FROM accounts WHERE account_id=:a"), {"a": self.a.account_id}), "archived")
            next_login = self.login(first, self.a.phone)
            self.assertEqual(first.get("/api/v1/bookmarks", headers=next_login).json()["items"], [])
            self.assertEqual(first.get("/api/v1/recommendation-history", headers=next_login).json()["items"], [])
            self.assertEqual(first.get("/api/v1/profiles/me", headers=next_login).json()["firstName"], "")
            with self.engine.connect() as connection:
                self.new_generation = connection.scalar(
                    text("SELECT account_id FROM accounts WHERE phone=:p AND status='active'"), {"p": self.a.phone}
                )
                self.assertNotEqual(self.new_generation, self.a.account_id)
        # The original owner graph must remain; a new empty profile is expected.
        after = self.retained()
        for table in ("recommendation_history_runs", "recommendation_history_items", "recommendation_history_item_reasons"):
            self.assertEqual(before[table], after[table])

    def test_archive_login_race_has_at_most_one_active_generation(self):
        from backend.app.accounts.identity import archive_account
        from backend.app.accounts.profile_repository import ensure_profile

        self.prepare()
        barrier = Barrier(2)

        def archive():
            with Session(self.engine) as db:
                barrier.wait(timeout=10)
                archive_account(self.a.account_id, db)

        def login():
            with Session(self.engine) as db:
                barrier.wait(timeout=10)
                return ensure_profile(self.a.phone, db).account_id

        with ThreadPoolExecutor(max_workers=2) as pool:
            first = pool.submit(archive)
            second = pool.submit(login)
            first.result(timeout=30)
            logged_in = second.result(timeout=30)
        with self.engine.connect() as connection:
            self.assertEqual(connection.scalar(
                text("SELECT status FROM accounts WHERE account_id=:a"), {"a": self.a.account_id}
            ), "archived")
            active = connection.scalar(
                text("SELECT account_id FROM accounts WHERE phone=:p AND status='active'"), {"p": self.a.phone}
            )
            if active is not None:
                self.assertEqual(logged_in, active)
                self.new_generation = active
        if getattr(self, "new_generation", None) is None:
            with Session(self.engine) as db:
                self.new_generation = ensure_profile(self.a.phone, db).account_id
        self.assertNotEqual(self.new_generation, self.a.account_id)
