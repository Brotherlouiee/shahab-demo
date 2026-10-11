"""T03 real PostgreSQL proof; use ONLY a disposable SHAHAB_TEST_DATABASE_URL.

These tests migrate/downgrade the test database. No SQLite fallback and no mock
transaction is persistence proof. Credentials/role grants are explicit test inputs;
this does not claim an operator MFA verifier (T04).
"""

import os
import subprocess
import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from threading import Barrier
from unittest.mock import Mock
from uuid import uuid4

from sqlalchemy import create_engine, event, inspect, select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import sessionmaker

from backend.app.data_pipeline.application.operations import InternalDataOperations
from backend.app.data_pipeline.application.publish_serving_version import ServingPublicationService
from backend.app.data_pipeline.domain.publication import ApprovalRecord, ServingVersionState
from backend.app.data_pipeline.infrastructure.sqlalchemy_operations import (
    SqlAlchemyImportReviewRepository,
    SqlAlchemyServingVersionRepository,
)
from backend.app.infrastructure.db.models import AuditEvent
from backend.app.operations.authorization import (
    IdentityKind,
    OperationsAccessDenied,
    OperationsAuthorizer,
    OperationsIdentity,
    RoleGrant,
)
from backend.app.operations.policy import Role
from backend.tests.test_internal_data_operations import manifest

DATABASE_URL = os.environ.get("SHAHAB_TEST_DATABASE_URL")
NOW = datetime(2026, 10, 11, tzinfo=UTC)
PREVIOUS = "a3b7c9d1e2f4"


@unittest.skipUnless(DATABASE_URL, "requires real disposable PostgreSQL; absence is not persistence evidence")
class OperationsPostgreSQLTests(unittest.TestCase):
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
        cls.alembic("upgrade", PREVIOUS)
        cls.engine = create_engine(str(DATABASE_URL), pool_size=5)
        cls.fixture_id = uuid4()
        with cls.engine.begin() as c:
            c.execute(
                text("INSERT INTO lenders (lender_id, canonical_name) VALUES (:id, :name)"),
                {"id": cls.fixture_id, "name": "T03-preserved-" + str(cls.fixture_id)},
            )
        cls.alembic("upgrade", "head")

    @classmethod
    def tearDownClass(cls):
        cls.alembic("downgrade", PREVIOUS)
        with cls.engine.connect() as c:
            assert c.scalar(text("SELECT count(*) FROM lenders WHERE lender_id=:id"), {"id": cls.fixture_id}) == 1
        assert "audit_events" not in inspect(cls.engine).get_table_names()
        assert "approval_records" not in inspect(cls.engine).get_view_names()
        cls.engine.dispose()
        cls.alembic("downgrade", "base")

    def setUp(self):
        self.prefix = uuid4().hex
        self.sessions = sessionmaker(self.engine, expire_on_commit=False)
        self.reviews = SqlAlchemyImportReviewRepository(self.sessions)
        self.versions = SqlAlchemyServingVersionRepository(self.sessions)
        self.grants = Mock()
        self.grants.read_current.side_effect = lambda s: RoleGrant(
            s, frozenset({Role.DATA_EDITOR, Role.ADMIN}), NOW + timedelta(hours=1)
        )
        self.ops = InternalDataOperations(
            OperationsAuthorizer(self.grants, lambda: NOW),
            self.reviews,
            ServingPublicationService(self.versions),
            lambda: NOW,
        )
        self.actor = OperationsIdentity("operator-test", IdentityKind.OPERATOR_MFA, NOW + timedelta(hours=1))

    def import_plan(self, suffix="1", *, rows=None):
        return self.ops.import_data(
            self.actor,
            import_id=self.prefix + "i" + suffix,
            source_file_sha256="a" * 64,
            parser_version="v1",
            rows=manifest(suffix) if rows is None else rows,
            reason="Reviewed source",
        )

    def draft(self, suffix="1"):
        review = self.import_plan(suffix)
        return self.ops.prepare_version(
            self.actor, import_id=review.import_id, version_id=self.prefix + "v" + suffix, reason="Prepare exact source"
        )

    def approved(self, suffix="1"):
        draft = self.draft(suffix)
        return self.ops.approve_version(self.actor, version_id=draft.version_id, reason="Approve exact diff")

    def published(self, suffix="1"):
        approved = self.approved(suffix)
        return self.ops.publish_version(self.actor, version_id=approved.version_id, reason="Publish approved version")

    def count(self):
        with self.engine.connect() as c:
            return c.scalar(text("SELECT count(*) FROM audit_events"))

    def fail_audit(self, operation):
        def fail(conn, cursor, statement, parameters, context, executemany):
            if statement.lstrip().startswith("INSERT INTO audit_events"):
                raise RuntimeError("injected audit insert failure")

        count = self.count()
        before = self.versions.get_current_published()
        event.listen(self.engine, "before_cursor_execute", fail)
        try:
            with self.assertRaisesRegex(RuntimeError, "injected"):
                operation()
        finally:
            event.remove(self.engine, "before_cursor_execute", fail)
        self.assertEqual(self.count(), count)
        self.assertEqual(self.versions.get_current_published(), before)

    def test_restart_retry_dirty_evidence_and_actor_linkage(self):
        original = self.import_plan()
        retry = self.import_plan()
        self.assertEqual(original.correlation_id, retry.correlation_id)
        self.assertEqual(original.created_at, retry.created_at)
        fresh = SqlAlchemyImportReviewRepository(sessionmaker(self.engine))
        self.assertEqual(fresh.get_by_id(original.import_id), original)
        count = self.count()
        with self.assertRaises(ValueError):
            self.import_plan(rows=manifest("conflicting"))
        self.assertEqual(self.count(), count)
        dirty = self.import_plan("dirty", rows=(*manifest(), *manifest()))
        self.assertTrue(fresh.get_by_id(dirty.import_id).preparation.issues)
        with self.assertRaises(ValueError):
            self.ops.prepare_version(
                self.actor, import_id=dirty.import_id, version_id=self.prefix + "dirty", reason="Must reject"
            )
        approved = self.approved("2")
        restarted = SqlAlchemyServingVersionRepository(sessionmaker(self.engine))
        self.assertEqual(restarted.get_by_id(approved.version_id), approved)
        self.assertEqual(
            restarted.get_by_id(approved.version_id).approval.correlation_id, approved.approval.correlation_id
        )
        with self.engine.connect() as c:
            self.assertEqual(
                c.scalar(
                    text(
                        "SELECT count(*) FROM approval_records a JOIN operations_versions v "
                        "ON a.version_id=v.version_id WHERE v.version_code=:code"
                    ),
                    {"code": approved.version_id},
                ),
                1,
            )

    def test_publish_and_rollback_preserve_original_approval_and_before_after(self):
        old = self.published("1")
        new = self.published("2")
        restored = self.ops.rollback_version(
            self.actor,
            version_id=old.version_id,
            expected_current_version_id=new.version_id,
            reason="Restore approved history",
        )
        self.assertEqual(restored.rows, old.rows)
        self.assertEqual(restored.approval, old.approval)
        self.assertEqual(restored.approval.correlation_id, old.approval.correlation_id)
        self.assertEqual(self.versions.get_current_published(), restored)
        self.assertEqual(self.versions.get_by_id(new.version_id).state, ServingVersionState.SUPERSEDED)
        with self.sessions() as session:
            audit = session.scalar(
                select(AuditEvent)
                .where(AuditEvent.event_type == "rollback")
                .order_by(AuditEvent.event_order.desc())
                .limit(1)
            )
            self.assertEqual(audit.actor_reference, self.actor.subject)
            self.assertEqual(audit.reason, "Restore approved history")
            self.assertEqual((audit.before_state, audit.after_state), ("superseded", "published"))
            self.assertNotEqual(audit.before_version_id, audit.after_version_id)
            self.assertEqual(audit.occurred_at.utcoffset(), timedelta(0))
            self.assertNotEqual(audit.correlation_id, old.approval.correlation_id)

    def test_failure_rolls_back_import_draft_approval_publish_and_rollback(self):
        self.fail_audit(lambda: self.import_plan())
        self.assertIsNone(self.reviews.get_by_id(self.prefix + "i1"))
        review = self.import_plan()
        self.fail_audit(
            lambda: self.ops.prepare_version(
                self.actor, import_id=review.import_id, version_id=self.prefix + "v1", reason="prepare"
            )
        )
        self.assertIsNone(self.versions.get_by_id(self.prefix + "v1"))
        draft = self.ops.prepare_version(
            self.actor, import_id=review.import_id, version_id=self.prefix + "v1", reason="prepare"
        )
        self.fail_audit(lambda: self.ops.approve_version(self.actor, version_id=draft.version_id, reason="approve"))
        self.assertEqual(self.versions.get_by_id(draft.version_id).state, ServingVersionState.DRAFT)
        self.ops.approve_version(self.actor, version_id=draft.version_id, reason="approve")
        self.fail_audit(lambda: self.ops.publish_version(self.actor, version_id=draft.version_id, reason="publish"))
        self.assertEqual(self.versions.get_by_id(draft.version_id).state, ServingVersionState.APPROVED)
        old = self.ops.publish_version(self.actor, version_id=draft.version_id, reason="publish")
        new = self.published("2")
        self.fail_audit(
            lambda: self.ops.rollback_version(
                self.actor, version_id=old.version_id, expected_current_version_id=new.version_id, reason="rollback"
            )
        )

    def test_two_connections_rollback_has_one_winner_and_no_lost_pointer(self):
        old = self.published("1")
        new = self.published("2")
        target = self.versions.get_by_id(old.version_id)
        barrier = Barrier(2)
        count = self.count()

        def rollback():
            barrier.wait(timeout=10)
            try:
                repo = SqlAlchemyServingVersionRepository(sessionmaker(self.engine))
                repo.rollback_atomically(
                    target,
                    expected_current_version_id=new.version_id,
                    decision=ApprovalRecord("operator-test", "concurrent rollback", NOW),
                )
                return "won"
            except ValueError:
                return "stale"

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(rollback) for _ in range(2)]
            self.assertCountEqual([f.result(timeout=20) for f in futures], ["won", "stale"])
        self.assertEqual(self.count(), count + 1)
        self.assertEqual(self.versions.get_current_published().version_id, old.version_id)

    def test_concurrent_publication_of_same_approval_is_rejected_after_first_commit(self):
        target = self.approved()
        barrier = Barrier(2)
        count = self.count()

        def publish():
            barrier.wait(timeout=10)
            try:
                repo = SqlAlchemyServingVersionRepository(sessionmaker(self.engine))
                repo.publish_atomically(target, decision=ApprovalRecord("operator-test", "publish", NOW))
                return "won"
            except ValueError:
                return "stale"

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(publish) for _ in range(2)]
            self.assertCountEqual([f.result(timeout=20) for f in futures], ["won", "stale"])
        self.assertEqual(self.count(), count + 1)

    def test_sql_append_only_constraints_view_and_preserved_existing_data(self):
        approved = self.approved()
        self.assertIn("approval_records", inspect(self.engine).get_view_names())
        for table in ("audit_events", "operations_imports", "operations_versions", "approval_records"):
            mutations = [f"DELETE FROM {table}"]
            if table == "approval_records":
                mutations.append("UPDATE approval_records SET reason='changed'")
            else:
                mutations.append(f"TRUNCATE {table} CASCADE")
                column = (
                    "reason"
                    if table == "audit_events"
                    else "import_code"
                    if table == "operations_imports"
                    else "version_code"
                )
                mutations.append(f"UPDATE {table} SET {column}='changed'")
            for sql in mutations:
                with self.subTest(sql=sql), self.assertRaises(DBAPIError), self.engine.begin() as c:
                    c.execute(text(sql))
        self.assertEqual(self.versions.get_by_id(approved.version_id), approved)
        with self.engine.connect() as c:
            self.assertEqual(
                c.scalar(text("SELECT count(*) FROM lenders WHERE lender_id=:id"), {"id": self.fixture_id}), 1
            )
        with self.assertRaises(DBAPIError), self.engine.begin() as c:
            c.execute(text("INSERT INTO operations_workflow_head (head_id) VALUES (2)"))
        with self.assertRaises(DBAPIError), self.engine.begin() as c:
            c.execute(
                text(
                    "INSERT INTO operations_versions (version_id,version_code,import_id,diff) "
                    "VALUES (:id,'bad',:missing,'{}')"
                ),
                {"id": uuid4(), "missing": uuid4()},
            )
        with self.assertRaises(DBAPIError), self.engine.begin() as c:
            c.execute(
                text(
                    "INSERT INTO audit_events (event_id,event_type,import_id,version_id,actor_reference,reason,"
                    "occurred_at,correlation_id,before_state,after_state) SELECT :id,'publish',import_id,version_id,"
                    "'operator','bad',now(),:corr,'approved','published' FROM operations_versions "
                    "WHERE version_code=:code"
                ),
                {"id": uuid4(), "corr": uuid4(), "code": approved.version_id},
            )

    def test_ordered_keyset_query_has_bounded_index_path(self):
        self.import_plan()
        with self.engine.begin() as c:
            c.execute(text("SET LOCAL enable_seqscan=off"))
            plan = c.execute(
                text("EXPLAIN SELECT event_order FROM audit_events WHERE event_order > 0 ORDER BY event_order LIMIT 20")
            ).all()
            self.assertIn("Index", "\n".join(row[0] for row in plan))

    def test_denied_actor_and_forged_version_write_no_evidence(self):
        count = self.count()
        customer = replace(self.actor, kind=IdentityKind.MOCK_OTP)
        with self.assertRaises(OperationsAccessDenied):
            self.ops.import_data(
                customer,
                import_id=self.prefix + "denied",
                source_file_sha256="a" * 64,
                parser_version="v1",
                rows=manifest(),
                reason="denied",
            )
        self.assertEqual(self.count(), count)
        draft = self.draft()
        with self.assertRaises(ValueError):
            self.versions.replace_version(
                replace(
                    draft,
                    source_file_sha256="b" * 64,
                    state=ServingVersionState.APPROVED,
                    approval=ApprovalRecord("operator", "forged", NOW),
                )
            )
        self.assertEqual(self.versions.get_by_id(draft.version_id), draft)
