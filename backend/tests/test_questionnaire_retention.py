"""Fast contract checks; real transaction/locking acceptance lives in PostgreSQL suite."""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.infrastructure.db.models import (
    Base,
    QuestionnaireAnswer,
    QuestionnaireSession,
    QuestionnaireSessionState,
    QuestionnaireVersion,
)
from backend.app.questionnaire.application.use_cases import QuestionnaireSessionService
from backend.app.questionnaire.domain.session import QuestionnaireRetentionPolicy, new_anonymous_session
from backend.app.questionnaire.infrastructure.memory_sessions import InMemoryQuestionnaireSessionRepository
from backend.app.questionnaire.infrastructure.retention import PurgeBatch, pending_counts, purge_expired_batch
from scripts.cleanup_questionnaire_sessions import main


class RawRetentionTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        Base.metadata.create_all(self.engine)
        self.addCleanup(self.engine.dispose)
        self.now = datetime.now(UTC)
        with Session(self.engine) as db:
            version = QuestionnaireVersion(version_code="fixture", source_hash="f" * 64)
            db.add(version)
            db.flush()
            self.version = version.questionnaire_version_id
            db.commit()

    def seed(self, expires):
        with Session(self.engine) as db:
            row = QuestionnaireSession(
                questionnaire_version_id=self.version,
                created_at=self.now - timedelta(hours=1),
                expires_at=expires,
                state=QuestionnaireSessionState.ACTIVE,
            )
            db.add(row)
            db.commit()
            return row.questionnaire_session_id

    def test_bounded_unlinked_cleanup_and_active_untouched(self):
        expired = {self.seed(self.now - timedelta(minutes=1)) for _ in range(3)}
        active = self.seed(self.now + timedelta(minutes=1))
        with Session(self.engine) as db:
            a = purge_expired_batch(db, batch_size=2, now=self.now)
            self.assertEqual(
                a.counts(),
                {"processed_sessions": 2, "deleted_answers": 0, "deleted_sessions": 2, "retained_sessions": 0},
            )
            self.assertTrue(set(a.session_ids).issubset(set(map(str, expired))))
            b = purge_expired_batch(db, batch_size=2, now=self.now)
            self.assertEqual(b.processed_sessions, 1)
            self.assertEqual(purge_expired_batch(db, now=self.now), PurgeBatch())
            self.assertIsNotNone(db.get(QuestionnaireSession, active))

    def test_invalid_bounds_and_naive_cutoff_never_write(self):
        sid = self.seed(self.now - timedelta(minutes=1))
        with Session(self.engine) as db:
            for size in (0, 1001, True, -1, "100"):
                with self.assertRaises(ValueError):
                    purge_expired_batch(db, batch_size=size)
            with self.assertRaises(ValueError):
                purge_expired_batch(db, now=datetime.now())
            self.assertIsNotNone(db.get(QuestionnaireSession, sid))
            self.assertEqual(pending_counts(db)["pending_sessions"], 1)

    def test_pending_business_writes_cannot_be_accidentally_committed(self):
        with Session(self.engine) as db:
            db.add(QuestionnaireAnswer())
            with self.assertRaises(ValueError):
                purge_expired_batch(db)

    def test_local_service_invalidation_is_bounded_and_only_committed_ids(self):
        repository = InMemoryQuestionnaireSessionRepository()
        for _ in range(101):
            repository.create(
                new_anonymous_session(
                    "fixture", QuestionnaireRetentionPolicy(timedelta(minutes=30)), self.now - timedelta(hours=1)
                )
            )
        cache = Mock()
        service = QuestionnaireSessionService(repository, Mock(), Mock(), cache)
        self.assertEqual(service.cleanup_expired(self.now), 100)
        self.assertEqual(cache.delete.call_count, 100)
        self.assertEqual(service.cleanup_expired(self.now), 1)
        self.assertEqual(service.cleanup_expired(self.now), 0)
        with patch.object(repository, "delete_expired", side_effect=RuntimeError("fixture")):
            with self.assertRaises(RuntimeError):
                service.cleanup_expired(self.now)
        self.assertEqual(cache.delete.call_count, 101)

    def test_cli_error_does_not_leak_configuration_exception(self):
        output = io.StringIO()
        with (
            patch("scripts.cleanup_questionnaire_sessions.Settings", side_effect=ValueError("private fixture")),
            redirect_stderr(output),
        ):
            self.assertEqual(main([]), 1)
        self.assertNotIn("private fixture", output.getvalue())
        self.assertIn('"completed_batches": 0', output.getvalue())

    def test_cli_default_is_read_only_and_reports_remaining_locked_work(self):
        settings = Mock(database_url_value="synthetic")
        engine = Mock()
        engine.dialect.name = "postgresql"
        for arguments, expected in (([], 0), (["--apply"], 2)):
            with (
                patch("scripts.cleanup_questionnaire_sessions.Settings", return_value=settings),
                patch("scripts.cleanup_questionnaire_sessions.create_engine", return_value=engine),
                patch("scripts.cleanup_questionnaire_sessions.Session"),
                patch(
                    "scripts.cleanup_questionnaire_sessions.pending_counts",
                    return_value={"pending_sessions": 1, "pending_answers": 1},
                ),
                patch("scripts.cleanup_questionnaire_sessions.purge_expired_batch", return_value=PurgeBatch()) as purge,
                redirect_stdout(io.StringIO()),
            ):
                self.assertEqual(main(arguments), expected)
                self.assertEqual(purge.call_count, int(bool(arguments)))
