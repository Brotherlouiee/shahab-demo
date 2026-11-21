"""Idempotent, source-checked upgrade of an existing T05A publication."""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.data_pipeline.domain.normalization import NormalizationState, normalize_variable
from backend.app.infrastructure.db.models import (
    DataSourceFile,
    Lender,
    LoanConditions,
    LoanProduct,
    LoanProductVersion,
    LoanServingFacts,
    PublicationState,
    ServingCatalogueMember,
    ServingCatalogueVersion,
)


def _facts(row: dict, version_id) -> LoanServingFacts:
    values = row["variableValues"]
    months = normalize_variable("depositHoldingMonths", values["depositHoldingMonths"])
    ratio = normalize_variable("loanToDepositRatio", values["loanToDepositRatio"])
    return LoanServingFacts(
        loan_product_version_id=version_id,
        deposit_required_text=(values["depositRequired"] or "").strip() or None,
        deposit_holding_months=int(months.numeric_value)
        if months.state is NormalizationState.CLASSIFIED and months.numeric_value is not None
        else None,
        loan_to_deposit_ratio_percent=ratio.numeric_value if ratio.state is NormalizationState.CLASSIFIED else None,
        guarantee_type_text=(values["guaranteeType"] or "").strip() or None,
        required_deposit_account=row["displayFields"].get("requiredDepositAccount"),
        bank_logo_reference=row["displayFields"].get("bankLogo"),
    )


def _same(actual: LoanServingFacts, expected: LoanServingFacts) -> bool:
    keys = (
        "deposit_required_text",
        "deposit_holding_months",
        "loan_to_deposit_ratio_percent",
        "guarantee_type_text",
        "required_deposit_account",
        "bank_logo_reference",
    )
    return all(
        Decimal(str(getattr(actual, key))) == Decimal(str(getattr(expected, key)))
        if key == "loan_to_deposit_ratio_percent"
        and getattr(actual, key) is not None
        and getattr(expected, key) is not None
        else getattr(actual, key) == getattr(expected, key)
        for key in keys
    )


def backfill_official_serving_facts(session: Session, manifest: dict) -> int:
    """Fill only verified active source rows; caller owns transaction/approval."""
    digest = hashlib.sha256(
        json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if digest != "e65e39c92a3d9ffc39e5782590cb1335880fbcf073095907161960c55d10146a":
        raise ValueError("loan manifest differs from the reviewed source extraction")
    if manifest["sourceFileSha256"] != "598052635954071b192bb43505e572f30ee88efd99b4d5ae757f6d555bfaae45":
        raise ValueError("unverified loan source")
    active = session.scalar(select(ServingCatalogueVersion).where(ServingCatalogueVersion.active.is_(True)))
    if active is None:
        raise ValueError("no active serving catalogue")
    source = session.get(DataSourceFile, active.data_source_file_id)
    if source is None or source.sha256 != manifest["sourceFileSha256"]:
        raise ValueError("active catalogue has a different source")
    actual = session.execute(
        select(LoanProductVersion, LoanProduct, Lender, LoanConditions)
        .join(
            ServingCatalogueMember,
            ServingCatalogueMember.loan_product_version_id == LoanProductVersion.loan_product_version_id,
        )
        .join(LoanProduct, LoanProduct.loan_product_id == LoanProductVersion.loan_product_id)
        .join(Lender, Lender.lender_id == LoanProduct.lender_id)
        .join(LoanConditions, LoanConditions.loan_product_version_id == LoanProductVersion.loan_product_version_id)
        .where(ServingCatalogueMember.serving_catalogue_version_id == active.serving_catalogue_version_id)
    ).all()
    by_row = {
        version.source_row_number: (version, product, lender, conditions)
        for version, product, lender, conditions in actual
    }
    rows = manifest["rows"]
    if len(rows) != 102 or len(actual) != len(rows) or len(by_row) != len(rows):
        raise ValueError("published source coverage is incomplete")
    created = 0
    for row in rows:
        record = by_row.get(row["sourceRowNumber"])
        if record is None:
            raise ValueError("missing published source row")
        version, product, lender, conditions = record
        if (
            version.source_file_id != source.data_source_file_id
            or version.publication_state is not PublicationState.PUBLISHED
            or lender.canonical_name != row["lenderName"]
            or product.canonical_name != row["loanName"]
            or conditions.source_text != row["displayFields"].get("conditions", "")
        ):
            raise ValueError("published row differs from the verified source")
        expected = _facts(row, version.loan_product_version_id)
        existing = session.get(LoanServingFacts, version.loan_product_version_id)
        if existing is None:
            session.add(expected)
            created += 1
        elif not _same(existing, expected):
            raise ValueError("existing serving facts differ from the verified source")
    session.flush()
    return created
