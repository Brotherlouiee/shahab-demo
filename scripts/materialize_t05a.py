"""Review existing PostgreSQL data, then optionally publish official source v1.1.

Default is read-only. Publication requires an explicit operator reference and
reason and one transaction; it is never performed by CI or by importing this module.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from backend.app.data_pipeline.domain.normalization import normalize_variable
from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
from backend.app.infrastructure.db.models import (
    AnswerCategoryCompatibility,
    DataSourceFile,
    Lender,
    LoanCategoryAssignment,
    LoanConditions,
    LoanProduct,
    LoanProductVersion,
    LoanVariable,
    RecommendationConfigVersion,
    ServingCatalogueVersion,
    VariableCategory,
)
from scripts.build_t05a_import_manifest import build_manifest
from scripts.build_t05a_recommendation_config import build_config

ROOT = Path(__file__).resolve().parents[1]


def audit_database(session: Session) -> dict:
    """Count actual database records before any import; never infer population from DDL."""
    source_hash = "598052635954071b192bb43505e572f30ee88efd99b4d5ae757f6d555bfaae45"
    source = session.scalar(select(DataSourceFile).where(DataSourceFile.sha256 == source_hash))
    active = session.scalar(select(ServingCatalogueVersion).where(ServingCatalogueVersion.active.is_(True)))
    expected = {row["sourceRowNumber"]: row for row in build_manifest()["rows"]}
    observed = {}
    if source is not None:
        for row_number, lender, loan, conditions, version_id in session.execute(
            select(
                LoanProductVersion.source_row_number,
                Lender.canonical_name,
                LoanProduct.canonical_name,
                LoanConditions.source_text,
                LoanProductVersion.loan_product_version_id,
            )
            .join(LoanProduct, LoanProduct.loan_product_id == LoanProductVersion.loan_product_id)
            .join(Lender, Lender.lender_id == LoanProduct.lender_id)
            .outerjoin(
                LoanConditions, LoanConditions.loan_product_version_id == LoanProductVersion.loan_product_version_id
            )
            .where(LoanProductVersion.source_file_id == source.data_source_file_id)
        ):
            observed[row_number] = (lender, loan, conditions, version_id)
    shared = expected.keys() & observed.keys()
    assignment_counts = {
        version_id: count
        for version_id, count in session.execute(
            select(LoanCategoryAssignment.loan_product_version_id, func.count())
            .where(LoanCategoryAssignment.loan_product_version_id.in_([observed[n][3] for n in shared]))
            .group_by(LoanCategoryAssignment.loan_product_version_id)
        )
    }
    actual_categories = {}
    for version_id, variable_id, state, category_id in session.execute(
        select(
            LoanCategoryAssignment.loan_product_version_id,
            LoanVariable.canonical_id,
            LoanCategoryAssignment.classification_state,
            VariableCategory.canonical_id,
        )
        .join(LoanVariable, LoanVariable.loan_variable_id == LoanCategoryAssignment.loan_variable_id)
        .outerjoin(
            VariableCategory, VariableCategory.variable_category_id == LoanCategoryAssignment.variable_category_id
        )
        .where(LoanCategoryAssignment.loan_product_version_id.in_([observed[n][3] for n in shared]))
    ):
        actual_categories[(version_id, variable_id)] = (state, category_id)
    category_mismatches = []
    for row_number in shared:
        version_id = observed[row_number][3]
        for variable_id, raw in expected[row_number]["variableValues"].items():
            normalized = normalize_variable(variable_id, raw)
            if actual_categories.get((version_id, variable_id)) != (normalized.state.value, normalized.category_id):
                category_mismatches.append({"row": row_number, "variableId": variable_id})

    def count(model, condition=None):
        query = select(func.count()).select_from(model)
        return session.scalar(query if condition is None else query.where(condition))

    return {
        "allLoanVersions": count(LoanProductVersion),
        "publishedLoanVersions": count(LoanProductVersion, LoanProductVersion.publication_state == "PUBLISHED"),
        "officialSourceRegistered": source is not None,
        "officialSourceLoanVersions": 0
        if source is None
        else count(LoanProductVersion, LoanProductVersion.source_file_id == source.data_source_file_id),
        "loanCategoryAssignments": count(LoanCategoryAssignment),
        "loanConditions": count(LoanConditions),
        "compatibilityCells": count(AnswerCategoryCompatibility),
        "approvedConfigurations": count(RecommendationConfigVersion, RecommendationConfigVersion.approved.is_(True)),
        "activeDataVersion": None if active is None else active.version_code,
        "missingSourceRows": sorted(expected.keys() - observed.keys()),
        "unexpectedSourceRows": sorted(n for n in observed.keys() - expected.keys() if n is not None),
        "unidentifiedSourceVersions": int(None in observed),
        "identityMismatchRows": sorted(
            n for n in shared if observed[n][:2] != (expected[n]["lenderName"], expected[n]["loanName"])
        ),
        "conditionsMismatchRows": sorted(
            n for n in shared if observed[n][2] != expected[n]["displayFields"].get("conditions", "")
        ),
        "incompleteCategoryRows": sorted(n for n in shared if assignment_counts.get(observed[n][3], 0) != 8),
        "categoryMismatchCells": category_mismatches,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--actor-reference")
    parser.add_argument("--approval-reason")
    args = parser.parse_args()
    url = os.environ.get("SHAHAB_DATABASE_URL")
    if not url:
        raise SystemExit("SHAHAB_DATABASE_URL is required; no database was inspected")
    if args.publish and (not args.actor_reference or not args.approval_reason):
        raise SystemExit("publication requires --actor-reference and --approval-reason")
    engine = create_engine(url, pool_pre_ping=True)
    try:
        with Session(engine) as session:
            before = audit_database(session)
            if not args.publish:
                print(json.dumps({"mode": "read_only", "database": before}, ensure_ascii=False))
                return
            manifest = build_manifest()
            config = build_config()
            questionnaire = json.loads(
                (ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text(encoding="utf-8")
            )
            identifiers = json.loads(
                (ROOT / "data/contracts/canonical-identifiers.v1.json").read_text(encoding="utf-8")
            )
            with session.begin_nested():
                result = materialize_official_sources(
                    session,
                    loan_manifest=manifest,
                    config_manifest=config,
                    questionnaire=questionnaire,
                    identifiers=identifiers,
                    actor_reference=args.actor_reference,
                    approval_reason=args.approval_reason,
                )
            session.commit()
            print(
                json.dumps(
                    {
                        "mode": "published",
                        "before": before,
                        "dataVersion": result.data_version,
                        "loanCount": result.loan_count,
                        "rankableCount": result.rankable_count,
                        "needsReviewCount": result.needs_review_count,
                        "reused": result.reused,
                    },
                    ensure_ascii=False,
                )
            )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
