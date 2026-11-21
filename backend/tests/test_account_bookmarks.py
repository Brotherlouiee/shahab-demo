"""Fast API contract tests. PostgreSQL suite owns migration, locking and durability proof."""

import unittest
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from backend.app.accounts.identity import AccountActor
from backend.app.api.v1.account_access import authenticated_account
from backend.app.core.dependencies import get_request_database_session
from backend.app.infrastructure.db.models import (
    Account,
    AccountBookmark,
    Base,
    Lender,
    LoanProduct,
    LoanProductVersion,
    PublicationState,
    QuestionnaireSession,
    QuestionnaireVersion,
    RecommendationHistoryItem,
    RecommendationHistoryRun,
)
from backend.app.main import create_app


class BookmarkApiTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        Base.metadata.create_all(self.engine)
        self.db = Session(self.engine)
        self.addCleanup(self.engine.dispose)
        self.addCleanup(self.db.close)
        a = Account(phone="09000000001", status="active")
        b = Account(phone="09000000002", status="active")
        lender = Lender(canonical_name="fixture bank")
        self.db.add_all([a, b, lender])
        self.db.flush()
        product = LoanProduct(lender_id=lender.lender_id, canonical_name="fixture loan")
        self.db.add(product)
        self.db.flush()
        version = LoanProductVersion(
            loan_product_id=product.loan_product_id, version_number=1, publication_state=PublicationState.PUBLISHED
        )
        self.db.add(version)
        self.db.commit()
        self.a, self.b = AccountActor(a.account_id, a.phone), AccountActor(b.account_id, b.phone)
        self.actor = self.a
        self.loan = version.loan_product_version_id
        self.app = create_app()
        self.app.dependency_overrides[get_request_database_session] = lambda: self.db
        self.app.dependency_overrides[authenticated_account] = lambda: self.actor
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def save(self, body=None):
        return self.client.put(f"/api/v1/bookmarks/{self.loan}", json={} if body is None else body)

    def test_desired_state_retry_retention_and_two_owner_isolation(self):
        self.assertEqual(self.save().status_code, 204)
        self.assertEqual(self.save().status_code, 204)
        page = self.client.get("/api/v1/bookmarks")
        self.assertEqual(page.status_code, 200, page.text)
        self.assertEqual(page.headers["Cache-Control"], "no-store")
        self.assertEqual(page.json()["items"][0]["loanId"], str(self.loan))
        self.assertIsNone(page.json()["items"][0]["compatibilityScore"])
        self.actor = self.b
        self.assertEqual(self.client.get("/api/v1/bookmarks").json()["items"], [])
        self.assertEqual(self.client.delete(f"/api/v1/bookmarks/{self.loan}").status_code, 204)
        self.actor = self.a
        self.assertEqual(len(self.client.get("/api/v1/bookmarks").json()["items"]), 1)
        for _ in range(2):
            self.assertEqual(self.client.delete(f"/api/v1/bookmarks/{self.loan}").status_code, 204)
        self.assertEqual(self.client.get("/api/v1/bookmarks").json()["items"], [])
        row = self.db.scalar(select(AccountBookmark))
        self.assertIsNotNone(row.removed_at)
        self.assertEqual(self.save().status_code, 204)
        self.assertEqual(len(list(self.db.scalars(select(AccountBookmark)))), 1)

    def test_draft_unknown_payload_owner_and_score_cannot_be_saved(self):
        self.assertEqual(self.save({"accountId": str(self.b.account_id)}).status_code, 422)
        self.assertEqual(self.save({"compatibilityScore": 1}).status_code, 422)
        self.assertEqual(self.save({"loanName": "forged"}).status_code, 422)
        self.assertEqual(self.client.put(f"/api/v1/bookmarks/{uuid4()}", json={}).status_code, 404)
        version = self.db.get(LoanProductVersion, self.loan)
        version.publication_state = PublicationState.DRAFT
        self.db.commit()
        self.assertEqual(self.save().status_code, 404)
        self.assertEqual(list(self.db.scalars(select(AccountBookmark))), [])

    def test_only_own_visible_matching_snapshot_can_supply_display_context(self):
        qv = QuestionnaireVersion(version_code="fixture", source_hash="f" * 64)
        self.db.add(qv)
        self.db.flush()
        now = datetime.now(UTC)
        sid = QuestionnaireSession(
            questionnaire_version_id=qv.questionnaire_version_id,
            owner_account_id=self.a.account_id,
            created_at=now,
            expires_at=now + timedelta(minutes=30),
        )
        self.db.add(sid)
        self.db.flush()
        run = RecommendationHistoryRun(
            owner_account_id=self.a.account_id,
            questionnaire_session_id=sid.questionnaire_session_id,
            data_version="fixture",
            config_version="fixture",
        )
        self.db.add(run)
        self.db.flush()
        item = RecommendationHistoryItem(
            recommendation_history_run_id=run.recommendation_history_run_id,
            loan_product_version_id=self.loan,
            section="ranked",
            display_order=0,
            lender_name="saved bank",
            loan_name="saved loan",
            compatibility_score=0.85,
        )
        self.db.add(item)
        self.db.commit()
        body = {"historyId": str(run.recommendation_history_run_id)}
        self.actor = self.b
        self.assertEqual(self.save(body).status_code, 404)
        self.actor = self.a
        self.assertEqual(self.save(body).status_code, 204)
        value = self.client.get("/api/v1/bookmarks").json()["items"][0]
        self.assertEqual((value["loanName"], value["compatibilityScore"]), ("saved loan", 0.85))
        run.hidden_at = now
        self.db.commit()
        self.assertEqual(self.save(body).status_code, 404)
        # Existing explicit bookmark context remains retained, never rescores.
        self.assertEqual(self.client.get("/api/v1/bookmarks").json()["items"][0], value)

    def test_bad_cursor_archived_actor_and_failed_storage_are_safe(self):
        self.assertEqual(self.client.get("/api/v1/bookmarks?cursor=invalid").status_code, 422)
        self.assertEqual(self.client.get("/api/v1/bookmarks?limit=51").status_code, 422)
        self.app.dependency_overrides[get_request_database_session] = lambda: None
        response = self.save()
        self.assertEqual(response.status_code, 503)
        self.app.dependency_overrides[get_request_database_session] = lambda: self.db
        account = self.db.get(Account, self.a.account_id)
        account.status = "archived"
        account.archived_at = datetime.now(UTC)
        self.db.commit()
        self.assertEqual(self.save().status_code, 401)

    def test_anonymous_real_dependency_never_accesses_owner_rows(self):
        del self.app.dependency_overrides[authenticated_account]
        for method in ("get", "put", "delete"):
            url = "/api/v1/bookmarks" if method == "get" else f"/api/v1/bookmarks/{self.loan}"
            result = getattr(self.client, method)(url, **({"json": {}} if method == "put" else {}))
            self.assertEqual(result.status_code, 401)
