"""Versioned immutable review evidence; decode never reruns normalization/scoring."""

from decimal import Decimal
from types import MappingProxyType
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from backend.app.data_pipeline.application.prepare_import import ImportPlanIssue, ImportPlanIssueCode, ImportPreparation
from backend.app.data_pipeline.domain.canonical_row import (
    CanonicalLoanRow,
    CanonicalRowRejection,
    RankingEligibility,
    RowRejectionCode,
)
from backend.app.data_pipeline.domain.normalization import NormalizationState, NormalizedVariable
from backend.app.data_pipeline.domain.publication import CatalogueDiff


class EvidenceModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class VariableEvidence(EvidenceModel):
    variable_id: str
    category_id: str | None
    numeric_value: Decimal | None = Field(allow_inf_nan=False)
    state: NormalizationState
    raw: str


class RowEvidence(EvidenceModel):
    source_row_number: int = Field(gt=0)
    source_row_fingerprint: str
    lender_name: str
    loan_name: str
    variables: dict[str, VariableEvidence]
    display_fields: dict[str, str]
    ranking_eligibility: RankingEligibility
    ranking_excluded_variable_ids: tuple[str, ...]


class RejectionEvidence(EvidenceModel):
    code: RowRejectionCode
    source_row_number: int
    message: str


class IssueEvidence(EvidenceModel):
    code: ImportPlanIssueCode
    message: str
    source_row_number: int | None


class PreparationEvidence(EvidenceModel):
    schema_version: Literal[1] = 1
    accepted_rows: tuple[RowEvidence, ...]
    rejected_rows: tuple[RejectionEvidence, ...]
    issues: tuple[IssueEvidence, ...]


class DiffEvidence(EvidenceModel):
    schema_version: Literal[1] = 1
    added: tuple[tuple[str, str], ...]
    changed: tuple[tuple[str, str], ...]
    removed: tuple[tuple[str, str], ...]


def encode_preparation(plan: ImportPreparation) -> dict[str, object]:
    rows = tuple(
        RowEvidence(
            source_row_number=r.source_row_number,
            source_row_fingerprint=r.source_row_fingerprint,
            lender_name=r.lender_name,
            loan_name=r.loan_name,
            variables={
                k: VariableEvidence(
                    variable_id=v.variable_id,
                    category_id=v.category_id,
                    numeric_value=v.numeric_value,
                    state=v.state,
                    raw=v.raw,
                )
                for k, v in r.variables.items()
            },
            display_fields=dict(r.display_fields),
            ranking_eligibility=r.ranking_eligibility,
            ranking_excluded_variable_ids=r.ranking_excluded_variable_ids,
        )
        for r in plan.accepted_rows
    )
    return PreparationEvidence(
        accepted_rows=rows,
        rejected_rows=tuple(
            RejectionEvidence(code=r.code, source_row_number=r.source_row_number, message=r.message)
            for r in plan.rejected_rows
        ),
        issues=tuple(
            IssueEvidence(code=i.code, message=i.message, source_row_number=i.source_row_number) for i in plan.issues
        ),
    ).model_dump(mode="json")


def decode_preparation(payload: object, *, source_hash: str, parser_version: str) -> ImportPreparation:
    evidence = PreparationEvidence.model_validate(payload)
    rows = tuple(
        CanonicalLoanRow(
            source_row_number=r.source_row_number,
            source_row_fingerprint=r.source_row_fingerprint,
            lender_name=r.lender_name,
            loan_name=r.loan_name,
            variables=MappingProxyType(
                {
                    k: NormalizedVariable(
                        variable_id=v.variable_id,
                        category_id=v.category_id,
                        numeric_value=v.numeric_value,
                        state=v.state,
                        raw=v.raw,
                    )
                    for k, v in r.variables.items()
                }
            ),
            display_fields=MappingProxyType(r.display_fields),
            ranking_eligibility=r.ranking_eligibility,
            ranking_excluded_variable_ids=r.ranking_excluded_variable_ids,
        )
        for r in evidence.accepted_rows
    )
    return ImportPreparation(
        source_hash,
        parser_version,
        rows,
        tuple(CanonicalRowRejection(r.code, r.source_row_number, r.message) for r in evidence.rejected_rows),
        tuple(ImportPlanIssue(i.code, i.message, i.source_row_number) for i in evidence.issues),
    )


def encode_diff(diff: CatalogueDiff) -> dict[str, object]:
    return DiffEvidence(added=diff.added, changed=diff.changed, removed=diff.removed).model_dump(mode="json")


def decode_diff(payload: object) -> CatalogueDiff:
    evidence = DiffEvidence.model_validate(payload)
    return CatalogueDiff(evidence.added, evidence.changed, evidence.removed)
