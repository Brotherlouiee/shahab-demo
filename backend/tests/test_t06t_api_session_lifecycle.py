"""US-09.T06T regression tests for FastAPI-owned SQLAlchemy resources."""

from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient
from starlette.requests import Request

from backend.app.core.config import AppEnvironment, Settings
from backend.app.core.dependencies import get_request_database_session
from backend.app.main import create_app


class ApiSessionLifecycleTests(unittest.TestCase):
    def test_lifespan_creates_one_engine_and_disposes_it_at_shutdown(self) -> None:
        engine = Mock()
        session_factory = Mock()
        settings = Settings(environment=AppEnvironment.TEST, database_url="sqlite+pysqlite:///:memory:")

        with (
            patch("backend.app.main.create_database_engine", return_value=engine) as create_engine,
            patch("backend.app.main.create_session_factory", return_value=session_factory) as create_factory,
        ):
            app = create_app(settings)
            with TestClient(app):
                self.assertIs(app.state.database_engine, engine)
                self.assertIs(app.state.database_session_factory, session_factory)
                create_engine.assert_called_once_with(settings)
                create_factory.assert_called_once_with(engine)

        engine.dispose.assert_called_once_with()

    def test_request_dependency_creates_distinct_sessions_and_closes_each(self) -> None:
        app = create_app(Settings(environment=AppEnvironment.TEST))
        first_session = Mock()
        second_session = Mock()
        factory = Mock(side_effect=(first_session, second_session))
        app.state.database_session_factory = factory
        request = Request({"type": "http", "app": app, "method": "GET", "path": "/"})

        first_dependency = get_request_database_session(request)
        second_dependency = get_request_database_session(request)
        self.assertIs(next(first_dependency), first_session)
        self.assertIs(next(second_dependency), second_session)
        with self.assertRaises(StopIteration):
            next(first_dependency)
        with self.assertRaises(StopIteration):
            next(second_dependency)

        self.assertEqual(factory.call_count, 2)
        first_session.close.assert_called_once_with()
        second_session.close.assert_called_once_with()

    def test_development_timing_logs_fixed_labels_without_request_identifiers(self) -> None:
        app = create_app(Settings(environment=AppEnvironment.TEST))
        with self.assertLogs("shahab", level="INFO") as logs, TestClient(app) as client:
            started = client.post("/api/v1/questionnaire/sessions")
            self.assertEqual(started.status_code, 201)
            session_id = started.json()["sessionId"]
            answer_id = "Q1.incomeInvestment"
            response = client.put(
                f"/api/v1/questionnaire/sessions/{session_id}/answers/Q1",
                json={"answerId": answer_id},
            )
            self.assertEqual(response.status_code, 200)

        output = "\n".join(logs.output)
        self.assertIn("endpoint=questionnaire_session_create", output)
        self.assertIn("endpoint=questionnaire_answer_write", output)
        self.assertIn("duration_ms=", output)
        self.assertNotIn(session_id, output)
        self.assertNotIn(answer_id, output)
