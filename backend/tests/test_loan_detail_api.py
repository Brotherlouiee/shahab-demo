"""US-06.T04 transport tests for approved loan-detail presentation data."""

from __future__ import annotations

import unittest
from decimal import Decimal

from fastapi.testclient import TestClient
from pydantic import SecretStr

from backend.app.core.config import AppEnvironment, Settings
from backend.app.core.dependencies import get_loan_details_use_case
from backend.app.loans.application.use_cases import GetLoanDetails
from backend.app.loans.domain.models import (
    LoanDetail,
    LoanSummary,
    PublishedLoanRecord,
    ServingCatalogueUnavailableError,
)
from backend.app.loans.infrastructure.in_memory_catalogue import InMemoryServingLoanCatalogueRepository
from backend.app.main import create_app


class LoanDetailApiTests(unittest.TestCase):
    def setUp(self) -> None:
        settings = Settings(environment=AppEnvironment.TEST, readiness_token=SecretStr("test-readiness-token"))
        self.app = create_app(settings)
        record = PublishedLoanRecord(
            serving_version_id="approved-v1",
            summary=LoanSummary("loan-approved", "بانک نمونه", "طرح نمونه", "internal-logo"),
            detail=LoanDetail(
                loan_id="loan-approved",
                lender_name="بانک نمونه",
                loan_name="طرح نمونه",
                bank_logo_reference="internal-logo",
                max_amount_tomans=Decimal("100000000"),
                monthly_installment_tomans=Decimal("10000000"),
                max_repayment_months=12,
                interest_rate_percent=Decimal("18"),
                deposit_required="دارد",
                deposit_holding_months=3,
                loan_to_deposit_ratio_percent=Decimal("100"),
                guarantee_type="ضامن",
                required_deposit_account="قرض الحسنه",
                conditions_source_text="۱. کارت ملی\n- <script>alert(1)</script>",
            ),
        )
        repository = InMemoryServingLoanCatalogueRepository(active_serving_version_id="approved-v1", records=(record,))
        self.app.dependency_overrides[get_loan_details_use_case] = lambda: GetLoanDetails(repository)
        self.client = TestClient(self.app, raise_server_exceptions=False)

    def test_detail_is_allowlisted_and_conditions_are_plain_text_bullets(self) -> None:
        response = self.client.get("/api/v1/loans/loan-approved")
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/json", response.headers["content-type"])
        payload = response.json()
        self.assertEqual(payload["loanId"], "loan-approved")
        self.assertEqual(payload["conditions"], ["کارت ملی", "<script>alert(1)</script>"])
        self.assertNotIn("conditionsSourceText", payload)
        self.assertNotIn("bankLogoReference", payload)
        self.assertNotIn("servingVersionId", payload)
        self.assertNotIn("authorization", response.request.headers)

    def test_unknown_loan_has_a_typed_not_found_response(self) -> None:
        response = self.client.get("/api/v1/loans/loan-missing")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "not_found")

    def test_unconfigured_catalogue_is_a_typed_unavailable_response(self) -> None:
        app = create_app(Settings(environment=AppEnvironment.TEST))
        response = TestClient(app, raise_server_exceptions=False).get("/api/v1/loans/loan-approved")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "service_unavailable")

    def test_storage_failure_is_a_typed_unavailable_response(self) -> None:
        class BrokenDetails:
            def execute(self, loan_id: str):
                raise ServingCatalogueUnavailableError("storage failure")

        self.app.dependency_overrides[get_loan_details_use_case] = lambda: BrokenDetails()
        response = self.client.get("/api/v1/loans/loan-approved")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "service_unavailable")
        self.assertNotIn("storage failure", response.text)
