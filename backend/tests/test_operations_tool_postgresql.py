"""T04 local TLS authority + real PostgreSQL least-privilege tool integration.

Disposable database only. Creates/removes an ephemeral test LOGIN role with a
random runtime password, never a committed credential. No SQLite substitute.
"""

import os
import secrets
import subprocess
import sys
import unittest
from dataclasses import replace
from uuid import uuid4

from sqlalchemy import create_engine, event, func, select, text
from sqlalchemy.orm import sessionmaker

from backend.app.data_pipeline.domain.publication import ApprovalRecord
from backend.app.data_pipeline.infrastructure.operations_projection import verify_operations_database_role
from backend.app.data_pipeline.infrastructure.sqlalchemy_operations import SqlAlchemyServingVersionRepository
from backend.app.infrastructure.db.models import (
    AuditEvent,
    LoanProductVersion,
    OperationsImport,
    ServingCatalogueVersion,
)
from backend.app.operations.authorization import OperationsAccessDenied
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
