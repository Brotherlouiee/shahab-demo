"""T04 local TLS authority + real PostgreSQL least-privilege tool integration.

Disposable database only. Creates/removes an ephemeral test LOGIN role with a
random runtime password, never a committed credential. No SQLite substitute.
"""

import json
import os
import secrets
import subprocess
import sys
import unittest
from dataclasses import replace
from pathlib import Path
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete, event, func, select, text
from sqlalchemy.orm import sessionmaker

from backend.app.core.config import Settings
from backend.app.data_pipeline.domain.publication import ApprovalRecord
from backend.app.data_pipeline.infrastructure.operations_projection import verify_operations_database_role
from backend.app.data_pipeline.infrastructure.sqlalchemy_operations import SqlAlchemyServingVersionRepository
from backend.app.infrastructure.db.models import (
    AccountBookmark,
    AuditEvent,
    LoanProductVersion,
    OperationsImport,
    RecommendationHistoryRun,
    ServingCatalogueVersion,
)
from backend.app.main import create_app
from backend.app.operations.authorization import OperationsAccessDenied
from backend.app.operations.infrastructure.local_ssh import LocalSshAuthority
from backend.tests.operations_authority_fixture import TLSAuthorityFixture
from scripts.operations_tool import OperationsCommand, execute, projection

DATABASE_URL = os.environ.get("SHAHAB_TEST_DATABASE_URL")
TABLES = (
    "data_import_runs",
    "data_source_files",
    "lenders",
    "loan_products",
    "loan_product_versions",
    "loan_terms",
    "loan_variables",
    "variable_categories",
    "loan_category_assignments",
    "loan_conditions",
    "loan_serving_facts",
    "questionnaire_versions",
    "questions",
    "answer_options",
    "recommendation_config_versions",
    "question_variable_weights",
    "answer_option_weights",
    "answer_category_compatibilities",
    "serving_catalogue_versions",
    "serving_catalogue_members",
    "operations_imports",
    "operations_versions",
    "audit_events",
)


@unittest.skipUnless(DATABASE_URL, "requires disposable real PostgreSQL")
class OperationsToolPostgreSQLTests(unittest.TestCase):
    @classmethod
    def alembic(cls, *args):
        subprocess.run(
            [sys.executable, "-c", "from alembic.config import main; main()", *args],
            check=True,
            env={**os.environ, "SHAHAB_DATABASE_URL": str(DATABASE_URL)},
            capture_output=True,
            text=True,
        )

    @classmethod
    def setUpClass(cls):
        cls.alembic("upgrade", "head")
        cls.owner = create_engine(str(DATABASE_URL))
        cls.role = "t04_ops_" + uuid4().hex[:16]
        password = secrets.token_hex(24)
        with cls.owner.begin() as c:
            # Names/password are generated hex, not arbitrary user SQL.
            c.execute(text(f"CREATE ROLE {cls.role} LOGIN PASSWORD '{password}'"))
            c.execute(text(f"GRANT USAGE ON SCHEMA public TO {cls.role}"))
            c.execute(text(f"GRANT SELECT, INSERT ON {','.join(TABLES)} TO {cls.role}"))
            c.execute(text(f"GRANT SELECT, UPDATE ON operations_workflow_head TO {cls.role}"))
            c.execute(text(f"GRANT UPDATE ON serving_catalogue_versions TO {cls.role}"))
            c.execute(text(f"GRANT USAGE, SELECT ON SEQUENCE audit_events_event_order_seq TO {cls.role}"))
        cls.runtime = create_engine(cls.owner.url.set(username=cls.role, password=password))
        cls.sessions = sessionmaker(cls.runtime)
        cls.provider = TLSAuthorityFixture()
        cls.serving = projection()

    @classmethod
    def tearDownClass(cls):
        cls.provider.close()
        cls.runtime.dispose()
        with cls.owner.begin() as c:
            c.execute(text(f"DROP OWNED BY {cls.role}"))
            c.execute(text(f"DROP ROLE {cls.role}"))
        cls.owner.dispose()
        cls.alembic("downgrade", "base")

    def setUp(self):
        self.prefix = uuid4().hex
        self.provider.claims["active"] = True
        self.provider.claims["roles"] = ["data-editor", "admin"]

    def command(self, operation, **fields):
        return execute(
            OperationsCommand(operation=operation, **fields), self.provider.authority(), self.sessions, self.serving
        )

    def approved(self, suffix="1"):
        import_id, version_id = self.prefix + "i" + suffix, self.prefix + "v" + suffix
        self.command("import", import_id=import_id, reason="Import approved official source")
        review = self.command("review", import_id=import_id)
        self.assertEqual(review["accepted"], 102)
        self.command("prepare", import_id=import_id, version_id=version_id, reason="Prepare exact extraction")
        self.command("approve", version_id=version_id, reason="Approve reviewed official diff")
        return version_id

    def count(self, model):
        with self.sessions() as session:
            return session.scalar(select(func.count()).select_from(model))

    def remove_fixture_bookmark(self, history_id: str) -> None:
        """Remove only this disposable test's association after persistence checks."""
        with sessionmaker(self.owner).begin() as session:
            session.execute(delete(AccountBookmark).where(AccountBookmark.source_history_run_id == UUID(history_id)))

    def test_atomic_publication_audit_failure_leaves_no_serving_rows_then_reuses_catalogue(self):
        version_id = self.approved()
        previous = self.count(LoanProductVersion)
        audit_count = self.count(AuditEvent)

        def fail(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().startswith("INSERT INTO audit_events"):
                raise RuntimeError("injected audit failure")

        event.listen(self.runtime, "before_cursor_execute", fail)
        try:
            with self.assertRaisesRegex(RuntimeError, "injected audit"):
                self.command("publish", version_id=version_id, reason="Publish approved extraction")
        finally:
            event.remove(self.runtime, "before_cursor_execute", fail)
        self.assertEqual(self.count(LoanProductVersion), previous)
        self.assertEqual(self.count(AuditEvent), audit_count)
        result = self.command("publish", version_id=version_id, reason="Publish approved extraction")
        self.assertEqual(result["state"], "published")
        self.assertEqual(self.count(LoanProductVersion), 102)
        with self.sessions() as session:
            active = session.scalar(select(ServingCatalogueVersion).where(ServingCatalogueVersion.active.is_(True)))
            self.assertEqual(active.version_code, self.serving.public_code)
            self.assertEqual(active.approved_by_reference, "test-operator")
        other = self.approved("2")
        self.command("publish", version_id=other, reason="Reuse immutable official catalogue")
        self.command(
            "rollback",
            version_id=version_id,
            expected_current_version_id=other,
            reason="Restore approved workflow revision",
        )
        self.assertEqual(self.count(LoanProductVersion), 102)

    def test_local_ssh_operator_uses_same_transactional_workflow_and_rejects_cross_role(self):
        from datetime import UTC, datetime, timedelta

        expiry = (datetime.now(UTC) + timedelta(minutes=10)).isoformat()
        active_uid = [10001]
        authority = LocalSshAuthority()
        authority._uid = lambda: active_uid[0]
        authority._document = lambda: {
            "schemaVersion": 1,
            "singleOwner": False,
            "operators": [
                {"uid": 10001, "actor": "ssh-editor-1", "roles": ["data-editor"], "expiresAt": expiry},
                {"uid": 10002, "actor": "ssh-admin-2", "roles": ["admin"], "expiresAt": expiry},
            ],
        }

        def local(operation, **fields):
            return execute(OperationsCommand(operation=operation, **fields), authority, self.sessions, self.serving)

        import_id, version_id = self.prefix + "li", self.prefix + "lv"
        initial_imports = self.count(OperationsImport)
        with self.assertRaises(OperationsAccessDenied):
            local("publish", version_id=version_id, reason="wrong local role")
        self.assertEqual(self.count(OperationsImport), initial_imports)
        local("import", import_id=import_id, reason="official source via local operator")
        self.assertEqual(local("review", import_id=import_id)["accepted"], 102)
        local("prepare", import_id=import_id, version_id=version_id, reason="reviewed official source")
        active_uid[0] = 10002
        with self.assertRaises(OperationsAccessDenied):
            local("import", import_id=self.prefix + "denied", reason="wrong local role")
        local("approve", version_id=version_id, reason="separate operator approval")
        before_loans = self.count(LoanProductVersion)

        def fail(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().startswith("INSERT INTO audit_events"):
                raise RuntimeError("injected audit failure")

        event.listen(self.runtime, "before_cursor_execute", fail)
        try:
            with self.assertRaisesRegex(RuntimeError, "injected audit"):
                local("publish", version_id=version_id, reason="atomic local publish")
        finally:
            event.remove(self.runtime, "before_cursor_execute", fail)
        self.assertEqual(self.count(LoanProductVersion), before_loans)
        self.assertEqual(local("publish", version_id=version_id, reason="atomic local publish")["state"], "published")
        self.assertEqual(self.count(LoanProductVersion), 102)
        with self.sessions() as session:
            self.assertFalse(session.scalar(text("SELECT has_table_privilege(current_user,'user_profiles','SELECT')")))

    def test_single_owner_local_operator_records_same_actor_and_keeps_atomic_publish(self):
        from datetime import UTC, datetime, timedelta

        authority = LocalSshAuthority(allow_root_owner=True)
        authority._uid = lambda: 0
        authority._document = lambda: {
            "schemaVersion": 1,
            "singleOwner": True,
            "operators": [
                {
                    "uid": 0,
                    "actor": "owner-ssh-root",
                    "roles": ["data-editor", "admin"],
                    "expiresAt": (datetime.now(UTC) + timedelta(minutes=10)).isoformat(),
                }
            ],
        }

        def local(operation, **fields):
            return execute(OperationsCommand(operation=operation, **fields), authority, self.sessions, self.serving)

        import_id, version_id = self.prefix + "oi", self.prefix + "ov"
        local("import", import_id=import_id, reason="official source via owner")
        self.assertEqual(local("review", import_id=import_id)["accepted"], 102)
        local("prepare", import_id=import_id, version_id=version_id, reason="owner reviewed source")
        local("approve", version_id=version_id, reason="owner explicit approval; no second reviewer")
        before_loans = self.count(LoanProductVersion)

        def fail(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().startswith("INSERT INTO audit_events"):
                raise RuntimeError("injected audit failure")

        event.listen(self.runtime, "before_cursor_execute", fail)
        try:
            with self.assertRaisesRegex(RuntimeError, "injected audit failure"):
                local("publish", version_id=version_id, reason="owner explicit publish")
        finally:
            event.remove(self.runtime, "before_cursor_execute", fail)
        self.assertEqual(self.count(LoanProductVersion), before_loans)
        self.assertEqual(local("publish", version_id=version_id, reason="owner explicit publish")["state"], "published")
        with self.sessions() as session:
            actors = session.scalars(select(AuditEvent.actor_reference)).all()
            self.assertIn("owner-ssh-root", actors)
            self.assertFalse(session.scalar(text("SELECT has_table_privilege(current_user,'user_profiles','SELECT')")))

    def test_protected_fixture_publication_supports_owned_http_journey(self):
        """Disposable PG/TLS fixture proof, not deployed MFA or operational data approval."""
        version_id = self.approved()
        self.command("publish", version_id=version_id, reason="Test-only protected source publication")
        settings = Settings(database_url=str(DATABASE_URL))
        questions = json.loads(
            (Path(__file__).resolve().parents[2] / "data/contracts/questionnaire-configuration.v1.json").read_text(
                encoding="utf-8"
            )
        )["questions"]
        with TestClient(create_app(settings)) as owner, TestClient(create_app(settings)) as other:
            for client, phone in ((owner, "09000000001"), (other, "09000000002")):
                challenge = client.post("/api/v1/account-access/request", json={"phone": phone})
                self.assertEqual(challenge.status_code, 200)
                verified = client.post(
                    "/api/v1/account-access/verify",
                    json={"challengeId": challenge.json()["challengeId"], "code": "123456"},
                )
                self.assertEqual(verified.status_code, 200)
            started = owner.post("/api/v1/questionnaire/sessions")
            self.assertEqual(started.status_code, 201)
            session_id = started.json()["sessionId"]
            self.assertEqual(other.get(f"/api/v1/questionnaire/sessions/{session_id}").status_code, 403)
            for question in questions:
                written = owner.put(
                    f"/api/v1/questionnaire/sessions/{session_id}/answers/{question['questionId']}",
                    json={"answerId": question["answerOptions"][0]["answerId"]},
                )
                self.assertEqual(written.status_code, 200)
            recommended = owner.post("/api/v1/recommendations", json={"sessionId": session_id})
            self.assertEqual(recommended.status_code, 200)
            result = recommended.json()
            self.assertEqual(result["configVersion"], "1.1.0")
            self.assertEqual(
                sum(
                    len(result[key])
                    for key in ("rankedRecommendations", "lowCompatibilityRecommendations", "needsReview")
                ),
                102,
            )
            history_id = result["historyId"]
            loan_id = result["rankedRecommendations"][0]["loanId"]
            self.assertEqual(owner.get(f"/api/v1/loans/{loan_id}").status_code, 200)
            self.assertEqual(len(owner.get("/api/v1/recommendation-history").json()["items"]), 1)
            self.assertEqual(other.get("/api/v1/recommendation-history").json()["items"], [])
            self.assertEqual(owner.get(f"/api/v1/recommendation-history/{history_id}").status_code, 200)
            self.assertEqual(other.get(f"/api/v1/recommendation-history/{history_id}").status_code, 404)
            self.assertEqual(other.delete(f"/api/v1/recommendation-history/{history_id}").status_code, 404)
            self.assertEqual(owner.put(f"/api/v1/bookmarks/{loan_id}", json={"historyId": history_id}).status_code, 204)
            self.addCleanup(self.remove_fixture_bookmark, history_id)
            self.assertEqual(len(owner.get("/api/v1/bookmarks").json()["items"]), 1)
            self.assertEqual(other.get("/api/v1/bookmarks").json()["items"], [])
            self.assertEqual(owner.delete(f"/api/v1/recommendation-history/{history_id}").status_code, 204)
            self.assertEqual(owner.get(f"/api/v1/recommendation-history/{history_id}").status_code, 404)
            self.assertEqual(owner.delete(f"/api/v1/bookmarks/{loan_id}").status_code, 204)
            self.assertEqual(owner.get("/api/v1/bookmarks").json()["items"], [])
        with sessionmaker(self.owner)() as session:
            stored = session.get(RecommendationHistoryRun, history_id)
            self.assertIsNotNone(stored)
            self.assertIsNotNone(stored.hidden_at)
        with TestClient(create_app(settings)) as reopened:
            reopened.cookies.update(owner.cookies)
            self.assertEqual(reopened.get("/api/v1/account-access/session").status_code, 200)
            self.assertEqual(reopened.get("/api/v1/recommendation-history").json()["items"], [])

    def test_database_owner_and_customer_tables_are_not_allowed(self):
        with sessionmaker(self.owner)() as session, self.assertRaises(ValueError):
            verify_operations_database_role(session)
        with self.sessions() as session:
            verify_operations_database_role(session)
            self.assertFalse(session.scalar(text("SELECT has_table_privilege(current_user,'user_profiles','SELECT')")))
            self.assertFalse(session.scalar(text("SELECT has_schema_privilege(current_user,'public','CREATE')")))

    def test_service_import_only_and_customer_denial_do_not_write(self):
        imports = self.count(OperationsImport)
        self.provider.claims["roles"] = ["user"]
        with self.assertRaises(OperationsAccessDenied):
            self.command("import", import_id=self.prefix + "denied", reason="must reject")
        self.assertEqual(self.count(OperationsImport), imports)
        original = dict(self.provider.claims)
        self.provider.claims.update(client_id="service-import", amr=[], auth_time=None, roles=["service"])
        try:
            self.command("import", import_id=self.prefix + "service", reason="Service import")
            with self.assertRaises(OperationsAccessDenied):
                self.command("review", import_id=self.prefix + "service")
        finally:
            self.provider.claims = original

    def test_edited_rows_or_source_cannot_reach_materializer(self):
        version_id = self.approved()
        repo = SqlAlchemyServingVersionRepository(self.sessions, projection=self.serving)
        version = repo.get_by_id(version_id)
        before = self.count(LoanProductVersion)
        # Test the bridge's own immutable linkage defense independently of T02.
        with self.sessions() as session, session.begin(), self.assertRaises(ValueError):
            self.serving.publish(
                session,
                replace(version, rows=version.rows[:-1]),
                ApprovalRecord("test-operator", "must reject", version.approval.decided_at),
            )
        self.assertEqual(self.count(LoanProductVersion), before)
