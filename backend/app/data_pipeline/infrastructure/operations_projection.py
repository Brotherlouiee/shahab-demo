"""Bridge authenticated T02/T03 operations to the existing approved materializer.

This release publishes only the already reviewed official extraction/config.
It never broadens D-005 or trusts a caller-supplied source hash on modified rows.
All writes share the repository's transaction; audit failure undoes publication.
"""

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from backend.app.data_pipeline.application.prepare_import import ImportManifestRow, prepare_import_manifest
from backend.app.data_pipeline.domain.publication import ApprovalRecord, ServingDataVersion
from backend.app.data_pipeline.infrastructure.materialize_official_sources import materialize_official_sources
from backend.app.infrastructure.db.models import ServingCatalogueVersion


class OfficialServingProjection:
    def __init__(self, *, loans: dict, configuration: dict, questionnaire: dict, identifiers: dict) -> None:
        self._loans, self._configuration = loans, configuration
        self._questionnaire, self._identifiers = questionnaire, identifiers
        self.rows = tuple(
            ImportManifestRow(
                item["sourceRowNumber"],
                item["lenderName"],
                item["loanName"],
                item["variableValues"],
                item["displayFields"],
            )
            for item in loans["rows"]
        )
        self.plan = prepare_import_manifest(
            source_file_sha256=loans["sourceFileSha256"], parser_version=loans["parserVersion"], rows=self.rows
        )
        self.public_code = f"official-{self.plan.source_file_sha256[:12]}-{configuration['configVersion']}"

    def _check(self, version: ServingDataVersion) -> None:
        if (version.source_file_sha256, version.parser_version, version.rows) != (
            self.plan.source_file_sha256,
            self.plan.parser_version,
            self.plan.accepted_rows,
        ):
            raise ValueError("version differs from the approved official extraction")

    def publish(self, session: Session, version: ServingDataVersion, decision: ApprovalRecord) -> None:
        self._check(version)
        # Cooperating tools already hold the workflow lock. Lock the active
        # public row too; drift from legacy/independent writers fails closed.
        active = session.scalar(
            select(ServingCatalogueVersion).where(ServingCatalogueVersion.active.is_(True)).with_for_update()
        )
        if active is not None and active.version_code != self.public_code:
            raise ValueError("public catalogue drift requires reviewed reconciliation")
        if version.approval is None:
            raise ValueError("explicit approval is required")
        materialize_official_sources(
            session,
            loan_manifest=self._loans,
            config_manifest=self._configuration,
            questionnaire=self._questionnaire,
            identifiers=self._identifiers,
            actor_reference=version.approval.actor_reference,
            approval_reason=version.approval.reason,
        )

    def rollback(self, session: Session, target: ServingDataVersion, current: ServingDataVersion) -> None:
        self._check(target)
        self._check(current)
        active = session.scalar(
            select(ServingCatalogueVersion).where(ServingCatalogueVersion.active.is_(True)).with_for_update()
        )
        if active is None or active.version_code != self.public_code or not active.approved_by_reference:
            raise ValueError("public catalogue is not the expected approved version")
        # Both revisions map to the sole currently approved source/config.
        # Reuse its immutable public projection; do not duplicate loans or
        # pretend this allowlist supports arbitrary future source/config edits.


def verify_operations_database_role(session: Session) -> None:
    """Reject database owners/inherited owner roles and schema/role creation rights."""
    if session.get_bind().dialect.name != "postgresql":
        raise ValueError("operations requires PostgreSQL")
    dangerous = session.scalar(
        text("""SELECT EXISTS (
        SELECT 1 FROM pg_roles WHERE pg_has_role(current_user, rolname, 'MEMBER') AND
            (rolsuper OR rolcreaterole OR rolcreatedb OR rolbypassrls)
        ) OR has_schema_privilege(current_user, 'public', 'CREATE') OR EXISTS (
        SELECT 1 FROM pg_tables WHERE schemaname='public' AND
            pg_has_role(current_user, tableowner, 'MEMBER')
        )""")
    )
    if dangerous:
        raise ValueError("operations requires a non-owner database role without DDL privileges")
