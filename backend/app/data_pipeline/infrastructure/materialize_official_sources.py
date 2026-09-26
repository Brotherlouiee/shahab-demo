"""Transactional, idempotent materialization of the six verified official sources.

Only a reviewed operator command may call this adapter. It does not expose an
HTTP route and does not read user sessions. Existing published rows are never
rewritten; a source version is either complete and reused or rejected.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.data_pipeline.application.prepare_import import ImportManifestRow, prepare_import_manifest
from backend.app.data_pipeline.domain.normalization import NormalizationState
from backend.app.infrastructure.db.models import (
    AnswerCategoryCompatibility,
    AnswerOption,
    AnswerOptionWeight,
    ClassificationState,
    DataImportRun,
    DataSourceFile,
    Lender,
    LoanCategoryAssignment,
    LoanConditions,
    LoanProduct,
    LoanProductVersion,
    LoanTerms,
    LoanVariable,
    PublicationState,
    Question,
    QuestionnaireVersion,
    QuestionVariableWeight,
    RecommendationConfigVersion,
    ServingCatalogueMember,
    ServingCatalogueVersion,
    VariableCategory,
)


@dataclass(frozen=True)
class MaterializationResult:
    data_version: str
    config_version: str
    loan_count: int
    rankable_count: int
    needs_review_count: int
    reused: bool


def _one(session: Session, model, *conditions):
    return session.scalar(select(model).where(*conditions))


def _get_or_create(session: Session, model, conditions: tuple, values: dict):
    item = _one(session, model, *conditions)
    if item is None:
        item = model(**values)
        session.add(item)
        session.flush()
    return item


def _classified_number(values, variable_id: str):
    item = values[variable_id]
    return item.numeric_value if item.state == NormalizationState.CLASSIFIED else None


def _classification_state(values, variable_id: str) -> ClassificationState:
    item = values[variable_id]
    if item.state == NormalizationState.CLASSIFIED:
        return ClassificationState.CLASSIFIED
    if item.state == NormalizationState.VARIABLE:
        return ClassificationState.VARIABLE
    return ClassificationState.UNKNOWN


def _manifest_digest(manifest: dict) -> str:
    encoded = json.dumps(manifest, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def materialize_official_sources(
    session: Session,
    *,
    loan_manifest: dict,
    config_manifest: dict,
    questionnaire: dict,
    identifiers: dict,
    actor_reference: str,
    approval_reason: str,
) -> MaterializationResult:
    """Publish only after complete source validation in the caller's transaction.

    A repeat with the same source/config returns the identical active version.
    The caller owns commit/rollback; an exception leaves no partial publication.
    """
    if not actor_reference.strip() or not approval_reason.strip():
        raise ValueError("an approval actor and reason are required")
    # Lock the parsed row content as well as the source-file identity. A caller
    # cannot attach the official source hash to edited loan facts or weights.
    if _manifest_digest(loan_manifest) != "e65e39c92a3d9ffc39e5782590cb1335880fbcf073095907161960c55d10146a":
        raise ValueError("loan manifest differs from the reviewed official extraction")
    if _manifest_digest(config_manifest) != "f7ddb191341328daa06a8c5cb9bb681589ba121e096f3d508f35448c985adae8":
        raise ValueError("configuration manifest differs from the reviewed official extraction")
    source_hash = loan_manifest["sourceFileSha256"]
    version_code = f"official-{source_hash[:12]}-{config_manifest['configVersion']}"
    if config_manifest["configVersion"] != "1.1.0" or not config_manifest["approved"]:
        raise ValueError("only the approved D-005 configuration can be published")
    if config_manifest["sources"]["answerWeightsSha256"] != (
        "f786ff278f58a5abb998dafca46625cbf3da5922db1e5c68d505487b57133749"
    ):
        raise ValueError("the official answer-weight source does not match D-005")
    if source_hash != "598052635954071b192bb43505e572f30ee88efd99b4d5ae757f6d555bfaae45":
        raise ValueError("unverified loan source")
    rows = tuple(
        ImportManifestRow(
            source_row_number=item["sourceRowNumber"],
            lender_name=item["lenderName"],
            loan_name=item["loanName"],
            variable_values=item["variableValues"],
            display_fields=item["displayFields"],
        )
        for item in loan_manifest["rows"]
    )
    plan = prepare_import_manifest(
        source_file_sha256=source_hash, parser_version=loan_manifest["parserVersion"], rows=rows
    )
    if not plan.is_publishable_candidate or len(plan.accepted_rows) != 102:
        raise ValueError("the reviewed source must contain exactly 102 accepted loan rows")
    active = _one(session, ServingCatalogueVersion, ServingCatalogueVersion.active.is_(True))
    existing = _one(session, ServingCatalogueVersion, ServingCatalogueVersion.version_code == version_code)
    if existing is not None:
        if existing.active and existing is active:
            count = (
                session.query(ServingCatalogueMember)
                .filter_by(serving_catalogue_version_id=existing.serving_catalogue_version_id)
                .count()
            )
            if count != len(rows):
                raise ValueError("published version is incomplete")
            return MaterializationResult(
                version_code,
                config_manifest["configVersion"],
                count,
                sum(not x.ranking_excluded_variable_ids for x in plan.accepted_rows),
                sum(bool(x.ranking_excluded_variable_ids) for x in plan.accepted_rows),
                True,
            )
        raise ValueError("source/config version exists but is not active; do not overwrite history")

    variable_ids = identifiers["loanVariableIds"]
    variables = {}
    categories = {}
    for order, variable_id in enumerate(variable_ids):
        variable = _get_or_create(
            session,
            LoanVariable,
            (LoanVariable.canonical_id == variable_id,),
            {"canonical_id": variable_id, "display_order": order},
        )
        variables[variable_id] = variable
        for category_id in identifiers["categoryIds"][variable_id]:
            category = _get_or_create(
                session,
                VariableCategory,
                (
                    VariableCategory.loan_variable_id == variable.loan_variable_id,
                    VariableCategory.canonical_id == category_id,
                ),
                {"loan_variable_id": variable.loan_variable_id, "canonical_id": category_id},
            )
            categories[(variable_id, category_id)] = category
    questionnaire_version = _get_or_create(
        session,
        QuestionnaireVersion,
        (QuestionnaireVersion.version_code == questionnaire["questionnaireVersion"],),
        {"version_code": questionnaire["questionnaireVersion"], "source_hash": questionnaire["source"]["sha256"]},
    )
    if questionnaire_version.source_hash != questionnaire["source"]["sha256"]:
        raise ValueError("questionnaire version collides with a different source")
    questions, answers = {}, {}
    for order, question_data in enumerate(questionnaire["questions"]):
        qid = question_data["questionId"]
        q = _get_or_create(
            session,
            Question,
            (
                Question.questionnaire_version_id == questionnaire_version.questionnaire_version_id,
                Question.canonical_id == qid,
            ),
            {
                "questionnaire_version_id": questionnaire_version.questionnaire_version_id,
                "canonical_id": qid,
                "display_order": order,
            },
        )
        questions[qid] = q
        for answer_data in question_data["answerOptions"]:
            aid = answer_data["answerId"]
            answers[aid] = _get_or_create(
                session,
                AnswerOption,
                (AnswerOption.question_id == q.question_id, AnswerOption.canonical_id == aid),
                {"question_id": q.question_id, "canonical_id": aid},
            )
    config = _get_or_create(
        session,
        RecommendationConfigVersion,
        (RecommendationConfigVersion.version_code == config_manifest["configVersion"],),
        {"version_code": config_manifest["configVersion"], "approved": True, "decision_id": "D-001..D-005"},
    )
    if not config.approved or config.decision_id != "D-001..D-005":
        raise ValueError("existing recommendation configuration is not the approved source")
    if _one(session, QuestionVariableWeight, QuestionVariableWeight.config_version_id == config.config_version_id):
        raise ValueError("existing config has weights; verify it independently before reusing")
    for group in config_manifest["questionWeights"]:
        variable = variables[group["variableId"]]
        q = questions[group["questionId"]]
        session.add(
            QuestionVariableWeight(
                config_version_id=config.config_version_id,
                question_id=q.question_id,
                loan_variable_id=variable.loan_variable_id,
                weight=Decimal(group["questionWeight"]),
            )
        )
        for answer in group["answers"]:
            session.add(
                AnswerOptionWeight(
                    config_version_id=config.config_version_id,
                    answer_option_id=answers[answer["answerId"]].answer_option_id,
                    loan_variable_id=variable.loan_variable_id,
                    weighted_value=Decimal(answer["sourceWeightedValue"]),
                    source_row_number=answer["sourceRow"],
                )
            )
    for item in config_manifest["compatibilities"]:
        session.add(
            AnswerCategoryCompatibility(
                config_version_id=config.config_version_id,
                answer_option_id=answers[item["answerId"]].answer_option_id,
                variable_category_id=categories[(item["variableId"], item["categoryId"])].variable_category_id,
                coefficient=Decimal(item["coefficient"]),
                source_row_number=item["sourceRow"],
                source_column_number=item["sourceColumn"],
            )
        )
    run = DataImportRun(state="approved", parser_version=loan_manifest["parserVersion"])
    session.add(run)
    session.flush()
    source_file = _get_or_create(
        session,
        DataSourceFile,
        (DataSourceFile.sha256 == source_hash,),
        {
            "data_import_run_id": run.data_import_run_id,
            "sha256": source_hash,
            "original_filename": "دیتابیس وام های بانکی.unitext",
        },
    )
    if active is not None:
        active.active = False
        active.state = "superseded"
        session.flush()
    publication = ServingCatalogueVersion(
        version_code=version_code,
        data_source_file_id=source_file.data_source_file_id,
        config_version_id=config.config_version_id,
        state="published",
        active=True,
        approved_by_reference=actor_reference.strip(),
        approval_reason=approval_reason.strip(),
    )
    session.add(publication)
    session.flush()
    rankable = 0
    for canonical in plan.accepted_rows:
        lender = _get_or_create(
            session,
            Lender,
            (Lender.canonical_name == canonical.lender_name,),
            {"canonical_name": canonical.lender_name},
        )
        product = _get_or_create(
            session,
            LoanProduct,
            (LoanProduct.lender_id == lender.lender_id, LoanProduct.canonical_name == canonical.loan_name),
            {"lender_id": lender.lender_id, "canonical_name": canonical.loan_name},
        )
        version = _one(
            session,
            LoanProductVersion,
            LoanProductVersion.source_file_id == source_file.data_source_file_id,
            LoanProductVersion.source_row_number == canonical.source_row_number,
        )
        if version is not None:
            raise ValueError("source row already has a version without an active catalogue")
        other_versions = session.scalars(
            select(LoanProductVersion.version_number).where(
                LoanProductVersion.loan_product_id == product.loan_product_id
            )
        ).all()
        version = LoanProductVersion(
            loan_product_id=product.loan_product_id,
            version_number=max(other_versions, default=0) + 1,
            publication_state=PublicationState.PUBLISHED,
            source_file_id=source_file.data_source_file_id,
            source_row_number=canonical.source_row_number,
        )
        session.add(version)
        session.flush()
        values = canonical.variables

        session.add(
            LoanTerms(
                loan_product_version_id=version.loan_product_version_id,
                max_amount=_classified_number(values, "maxAmount"),
                monthly_installment=_classified_number(values, "monthlyInstallment"),
                max_repayment_months=None
                if _classified_number(values, "maxRepaymentMonths") is None
                else int(_classified_number(values, "maxRepaymentMonths")),
                interest_rate=_classified_number(values, "interestRate"),
                max_amount_state=_classification_state(values, "maxAmount"),
                monthly_installment_state=_classification_state(values, "monthlyInstallment"),
                max_repayment_months_state=_classification_state(values, "maxRepaymentMonths"),
                interest_rate_state=_classification_state(values, "interestRate"),
            )
        )
        session.add(
            LoanConditions(
                loan_product_version_id=version.loan_product_version_id,
                source_text=canonical.display_fields.get("conditions", ""),
            )
        )
        session.add(
            ServingCatalogueMember(
                serving_catalogue_version_id=publication.serving_catalogue_version_id,
                loan_product_version_id=version.loan_product_version_id,
            )
        )
        for variable_id in variable_ids:
            item = values[variable_id]
            category = categories.get((variable_id, item.category_id))
            session.add(
                LoanCategoryAssignment(
                    loan_product_version_id=version.loan_product_version_id,
                    loan_variable_id=variables[variable_id].loan_variable_id,
                    variable_category_id=None if category is None else category.variable_category_id,
                    classification_state=item.state.value,
                    source_row_number=canonical.source_row_number,
                )
            )
        rankable += not canonical.ranking_excluded_variable_ids
    session.flush()
    return MaterializationResult(
        version_code, config_manifest["configVersion"], len(rows), rankable, len(rows) - rankable, False
    )
