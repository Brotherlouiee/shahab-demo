"""Real PG retention acceptance on a disposable CI database, never customer data."""

import io
import json
import os
import unittest
import uuid
from contextlib import redirect_stderr, redirect_stdout
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from backend.app.accounts.identity import AccountActor
from backend.app.infrastructure.db.models import QuestionnaireSession, QuestionnaireSessionState
from backend.app.questionnaire.infrastructure.retention import pending_counts, purge_expired_batch
from backend.app.questionnaire.infrastructure.sqlalchemy_sessions import SqlAlchemyQuestionnaireSessionRepository
from backend.app.recommendation.infrastructure.history import RecommendationHistoryRepository
from backend.tests import test_account_identity_postgresql as fixture
from scripts.cleanup_questionnaire_sessions import main


@unittest.skipUnless(fixture.DATABASE_URL, "requires real PostgreSQL SHAHAB_TEST_DATABASE_URL")
class RawRetentionPostgreSqlTests(unittest.TestCase):
    setUp = fixture.AccountIdentityPostgreSqlTests.setUp
    alembic = fixture.AccountIdentityPostgreSqlTests.alembic
    legacy_fixture = fixture.AccountIdentityPostgreSqlTests.legacy_fixture

    def tearDown(self):
        # Fixture-only restoration for the established downgrade guard. Product
        # code never unarchives accounts or disables an integrity trigger.
        with self.engine.begin() as c:
            c.execute(text("ALTER TABLE accounts DISABLE TRIGGER protect_account_identity"))
            c.execute(text("UPDATE accounts SET status='active', archived_at=NULL WHERE status='archived'"))
            c.execute(text("ALTER TABLE accounts ENABLE TRIGGER protect_account_identity"))
        fixture.AccountIdentityPostgreSqlTests.tearDown(self)

    def prepare(self, *, visibility="visible", full=False):
        sid, hid = self.legacy_fixture()
        self.alembic("upgrade", "head")
        self.now = datetime.now(UTC)
        with self.engine.begin() as c:
            c.execute(
                text(
                    "UPDATE questionnaire_sessions SET created_at=:created,expires_at=:expired,"
                    "state=state WHERE questionnaire_session_id=:sid"
                ),
                {
                    "sid": sid,
                    "created": self.now - timedelta(hours=1),
                    "expired": self.now - timedelta(minutes=30),
                },
            )
            if full:
                options = c.execute(
                    text(
                        "SELECT DISTINCT ON (question_id) question_id,answer_option_id "
                        "FROM answer_options ORDER BY question_id,answer_option_id"
                    )
                ).all()
                for question, option in options:
                    c.execute(
                        text(
                            "INSERT INTO questionnaire_answers VALUES (:id,:sid,:q,:a) "
                            "ON CONFLICT (questionnaire_session_id,question_id) DO NOTHING"
                        ),
                        {"id": uuid.uuid4(), "sid": sid, "q": question, "a": option},
                    )
            if visibility == "visible":
                c.execute(
                    text(
                        "UPDATE recommendation_history_runs SET hidden_at=NULL WHERE recommendation_history_run_id=:id"
                    ),
                    {"id": hid},
                )
            if visibility == "archived":
                c.execute(
                    text(
                        "UPDATE accounts SET status='archived',archived_at=now() "
                        "WHERE account_id=(SELECT owner_account_id FROM questionnaire_sessions "
                        "WHERE questionnaire_session_id=:sid)"
                    ),
                    {"sid": sid},
                )
        return sid, hid

    def evidence(self):
        with self.engine.connect() as c:
            return {
                table: sorted([dict(row) for row in c.execute(text(f"SELECT * FROM {table}")).mappings()], key=str)
                for table in (
                    "accounts",
                    "user_profiles",
                    "recommendation_history_runs",
                    "recommendation_history_items",
                    "recommendation_history_item_reasons",
                    "questionnaire_versions",
                    "loan_product_versions",
                )
            }

    def seed_unlinked(self, *, expired=True, answer=True):
        sid = uuid.uuid4()
        with self.engine.begin() as c:
            version = c.scalar(text("SELECT questionnaire_version_id FROM questionnaire_versions LIMIT 1"))
            c.execute(
                text(
                    "INSERT INTO questionnaire_sessions (questionnaire_session_id,questionnaire_version_id,"
                    "state,created_at,expires_at) VALUES (:id,:v,'ACTIVE',:start,:end)"
                ),
                {
                    "id": sid,
                    "v": version,
                    "start": self.now - timedelta(hours=1),
                    "end": self.now + timedelta(minutes=-30 if expired else 30),
                },
            )
            if answer:
                question, option = c.execute(
                    text("SELECT question_id,answer_option_id FROM answer_options LIMIT 1")
                ).one()
                c.execute(
                    text("INSERT INTO questionnaire_answers VALUES (:id,:sid,:q,:a)"),
                    {"id": uuid.uuid4(), "sid": sid, "q": question, "a": option},
                )
        return sid

    def assert_snapshot_preserved(self, visibility, full):
        sid, hid = self.prepare(visibility=visibility, full=full)
        partial = self.seed_unlinked()
        empty = self.seed_unlinked(answer=False)
        active = self.seed_unlinked(expired=False)
        before = self.evidence()
        with self.engine.connect() as c:
            metadata = dict(
                c.execute(text("SELECT * FROM questionnaire_sessions WHERE questionnaire_session_id=:id"), {"id": sid})
                .mappings()
                .one()
            )
            raw_count = c.scalar(
                text("SELECT count(*) FROM questionnaire_answers WHERE questionnaire_session_id=:id"), {"id": sid}
            )
        self.assertGreater(raw_count, 1 if full else 0)
        with Session(self.engine) as db:
            # Exercise the old entry point without constructor reference-seeding.
            repository = SqlAlchemyQuestionnaireSessionRepository(db, None, reference_catalogue=(None, {}, {}))
            ids = repository.delete_expired(self.now)
            self.assertEqual(set(ids), {str(sid), str(partial), str(empty)})
            self.assertEqual(repository.delete_expired(self.now), ())
            self.assertEqual(pending_counts(db), {"pending_sessions": 0, "pending_answers": 0})
            for deleted in (partial, empty):
                self.assertIsNone(db.get(QuestionnaireSession, deleted))
            self.assertIsNotNone(db.get(QuestionnaireSession, active))
            kept = db.get(QuestionnaireSession, sid)
            self.assertEqual(kept.state, QuestionnaireSessionState.EXPIRED)
            if visibility == "visible":
                actor = AccountActor(kept.owner_account_id, "09000000001")
                result = RecommendationHistoryRepository(db).read_for_owner(actor, str(hid))
                self.assertEqual(result[0].recommendation_history_run_id, hid)
                self.assertEqual(len(result[1]), 1)
                self.assertEqual(list(result[2].values()), [("fixture exclusion",)])
        with self.engine.connect() as c:
            after = dict(
                c.execute(text("SELECT * FROM questionnaire_sessions WHERE questionnaire_session_id=:id"), {"id": sid})
                .mappings()
                .one()
            )
            self.assertEqual(
                c.scalar(
                    text("SELECT count(*) FROM questionnaire_answers WHERE questionnaire_session_id=:id"), {"id": sid}
                ),
                0,
            )
            self.assertEqual(
                c.scalar(
                    text("SELECT count(*) FROM questionnaire_answers WHERE questionnaire_session_id=:id"),
                    {"id": active},
                ),
                1,
            )
        self.assertEqual(
            {k: v for k, v in metadata.items() if k != "state"}, {k: v for k, v in after.items() if k != "state"}
        )
        self.assertEqual(before, self.evidence())

    def test_full_visible_snapshot_is_readable_without_answers(self):
        self.assert_snapshot_preserved("visible", True)

    def test_partial_hidden_snapshot_is_retained(self):
        self.assert_snapshot_preserved("hidden", False)

    def test_archived_owner_snapshot_profile_and_lineage_are_retained(self):
        self.assert_snapshot_preserved("archived", True)

    def test_failure_rolls_back_answers_and_metadata_then_retry_succeeds(self):
        sid, _ = self.prepare()
        unlinked = self.seed_unlinked()
        before = self.evidence()
        with self.engine.begin() as c:
            c.execute(
                text(
                    "CREATE FUNCTION reject_retention_fixture() RETURNS trigger LANGUAGE plpgsql AS $$ "
                    "BEGIN RAISE EXCEPTION 'fixture'; END $$"
                )
            )
            c.execute(
                text(
                    "CREATE TRIGGER reject_retention_fixture BEFORE UPDATE ON questionnaire_sessions "
                    "FOR EACH ROW EXECUTE FUNCTION reject_retention_fixture()"
                )
            )
        try:
            with Session(self.engine) as db, self.assertRaises(DBAPIError):
                purge_expired_batch(db, now=self.now)
            with self.engine.connect() as c:
                self.assertEqual(c.scalar(text("SELECT count(*) FROM questionnaire_answers")), 2)
                self.assertEqual(
                    c.scalar(
                        text("SELECT state FROM questionnaire_sessions WHERE questionnaire_session_id=:id"), {"id": sid}
                    ),
                    "ACTIVE",
                )
                self.assertIsNotNone(
                    c.scalar(
                        text(
                            "SELECT questionnaire_session_id FROM questionnaire_sessions "
                            "WHERE questionnaire_session_id=:id"
                        ),
                        {"id": unlinked},
                    )
                )
            self.assertEqual(before, self.evidence())
        finally:
            with self.engine.begin() as c:
                c.execute(text("DROP TRIGGER reject_retention_fixture ON questionnaire_sessions"))
                c.execute(text("DROP FUNCTION reject_retention_fixture()"))
        with Session(self.engine) as db:
            result = purge_expired_batch(db, now=self.now)
            self.assertEqual((result.deleted_answers, result.retained_sessions, result.deleted_sessions), (2, 1, 1))
            self.assertEqual(purge_expired_batch(db, now=self.now).processed_sessions, 0)

    def test_two_connections_skip_locked_batch_then_drain_without_lost_rows(self):
        sid, _ = self.prepare()
        others = {self.seed_unlinked() for _ in range(3)}
        with Session(self.engine) as locked, Session(self.engine) as worker:
            locked.scalar(
                select(QuestionnaireSession)
                .where(QuestionnaireSession.questionnaire_session_id == sid)
                .with_for_update()
            )
            result = purge_expired_batch(worker, batch_size=2, now=self.now)
            self.assertEqual(len(result.session_ids), 2)
            self.assertTrue(set(result.session_ids).issubset(set(map(str, others))))
            self.assertEqual(purge_expired_batch(worker, batch_size=2, now=self.now).processed_sessions, 1)
            self.assertEqual(purge_expired_batch(worker, now=self.now).processed_sessions, 0)
            # No-work is not backlog-zero while a row is held by a live request.
            self.assertEqual(pending_counts(worker)["pending_sessions"], 1)
            worker.rollback()
            locked.rollback()
            final = purge_expired_batch(worker, now=self.now)
            self.assertEqual(final.session_ids, (str(sid),))
            self.assertEqual(pending_counts(worker)["pending_sessions"], 0)

    def test_operator_cli_dry_run_apply_and_safe_partial_failure_counts(self):
        self.prepare()
        env = {"SHAHAB_DATABASE_URL": str(fixture.DATABASE_URL)}
        output = io.StringIO()
        with patch.dict(os.environ, env), redirect_stdout(output):
            self.assertEqual(main([]), 0)
        self.assertEqual(json.loads(output.getvalue())["pending_answers"], 1)
        with self.engine.connect() as c:
            self.assertEqual(c.scalar(text("SELECT count(*) FROM questionnaire_answers")), 1)
        output = io.StringIO()
        error = io.StringIO()
        actual = purge_expired_batch
        calls = 0

        def fail_second(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError("private fixture payload")
            return actual(*args, **kwargs)

        self.seed_unlinked()
        with (
            patch.dict(os.environ, env),
            redirect_stdout(output),
            redirect_stderr(error),
            patch("scripts.cleanup_questionnaire_sessions.purge_expired_batch", side_effect=fail_second),
        ):
            self.assertEqual(main(["--apply", "--batch-size", "1", "--max-batches", "2"]), 1)
        self.assertEqual(json.loads(error.getvalue())["completed_batches"], 1)
        self.assertNotIn("private fixture payload", error.getvalue())
        with patch.dict(os.environ, env), redirect_stdout(io.StringIO()):
            self.assertEqual(main(["--apply", "--max-batches", "10"]), 0)
