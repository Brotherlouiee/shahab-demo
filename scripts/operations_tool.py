"""Protected one-command internal CLI; credentials never appear in arguments.

Use python -m scripts.operations_tool --command /private/command.json.
Issuer configuration and token come from the process secret environment; a
human may enter the token through getpass. No public FastAPI route is installed.
"""

import argparse
import getpass
import json
import os
import sys
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, model_validator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.data_pipeline.application.operations import InternalDataOperations
from backend.app.data_pipeline.application.publish_serving_version import ServingPublicationService
from backend.app.data_pipeline.infrastructure.operations_projection import (
    OfficialServingProjection,
    verify_operations_database_role,
)
from backend.app.data_pipeline.infrastructure.sqlalchemy_operations import (
    SqlAlchemyImportReviewRepository,
    SqlAlchemyServingVersionRepository,
)
from backend.app.operations.authorization import OperationsAuthorizer
from backend.app.operations.infrastructure.introspection import AuthorityConfiguration, IntrospectionAuthority
from backend.app.operations.infrastructure.local_ssh import LocalSshAuthority
from backend.app.operations.policy import Permission
from scripts.build_t05a_import_manifest import build_manifest
from scripts.build_t05a_recommendation_config import build_config

ROOT = Path(__file__).resolve().parents[1]


class OperationsCommand(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    operation: Literal["import", "review", "prepare", "approve", "publish", "rollback"]
    import_id: str | None = Field(default=None, min_length=1, max_length=120)
    version_id: str | None = Field(default=None, min_length=1, max_length=120)
    expected_current_version_id: str | None = Field(default=None, min_length=1, max_length=120)
    reason: str | None = Field(default=None, min_length=1, max_length=500)

    @model_validator(mode="after")
    def exact_fields(self):
        required = {
            "import": {"import_id", "reason"},
            "review": {"import_id"},
            "prepare": {"import_id", "version_id", "reason"},
            "approve": {"version_id", "reason"},
            "publish": {"version_id", "reason"},
            "rollback": {"version_id", "expected_current_version_id", "reason"},
        }
        fields = {k for k, v in self.model_dump().items() if v is not None and k != "operation"}
        if fields != required[self.operation]:
            raise ValueError("command requires exactly its documented fields")
        return self

    @property
    def permission(self) -> Permission:
        return {
            "import": Permission.IMPORT,
            "review": Permission.REVIEW,
            "prepare": Permission.IMPORT,
            "approve": Permission.APPROVE,
            "publish": Permission.PUBLISH,
            "rollback": Permission.ROLLBACK,
        }[self.operation]


def projection() -> OfficialServingProjection:
    return OfficialServingProjection(
        loans=build_manifest(),
        configuration=build_config(),
        questionnaire=json.loads((ROOT / "data/contracts/questionnaire-configuration.v1.json").read_text()),
        identifiers=json.loads((ROOT / "data/contracts/canonical-identifiers.v1.json").read_text()),
    )


def execute(
    command: OperationsCommand,
    authority: IntrospectionAuthority | LocalSshAuthority,
    sessions,
    serving: OfficialServingProjection,
):
    """Authenticate and authorize before database access; T02 checks fresh grants again."""
    identity = authority.authenticate()
    authorizer = OperationsAuthorizer(authority)
    authorizer.require(identity, command.permission)
    with sessions() as session:
        verify_operations_database_role(session)
    reviews = SqlAlchemyImportReviewRepository(sessions)
    versions = SqlAlchemyServingVersionRepository(sessions, projection=serving)
    ops = InternalDataOperations(authorizer, reviews, ServingPublicationService(versions))
    if command.operation == "import":
        result = ops.import_data(
            identity,
            import_id=str(command.import_id),
            reason=str(command.reason),
            source_file_sha256=serving.plan.source_file_sha256,
            parser_version=serving.plan.parser_version,
            rows=serving.rows,
        )
    elif command.operation == "review":
        result = ops.review_import(identity, import_id=str(command.import_id))
    elif command.operation == "prepare":
        result = ops.prepare_version(
            identity, import_id=str(command.import_id), version_id=str(command.version_id), reason=str(command.reason)
        )
    elif command.operation == "approve":
        result = ops.approve_version(identity, version_id=str(command.version_id), reason=str(command.reason))
    elif command.operation == "publish":
        result = ops.publish_version(identity, version_id=str(command.version_id), reason=str(command.reason))
    else:
        result = ops.rollback_version(
            identity,
            version_id=str(command.version_id),
            expected_current_version_id=str(command.expected_current_version_id),
            reason=str(command.reason),
        )
    # Bounded operator summary, never raw rows, secrets, credentials or DB URL.
    if command.operation in {"import", "review"}:
        return {
            "operation": command.operation,
            "import_id": result.import_id,
            "accepted": len(result.preparation.accepted_rows),
            "rejected": len(result.preparation.rejected_rows),
            "issues": len(result.preparation.issues),
            "eligible": result.preparation.is_publishable_candidate,
            "rejection_evidence": [
                {"code": item.code.value, "row": item.source_row_number, "message": item.message}
                for item in result.preparation.rejected_rows
            ],
            "issue_evidence": [
                {"code": item.code.value, "row": item.source_row_number, "message": item.message}
                for item in result.preparation.issues
            ],
        }
    return {"operation": command.operation, "version_id": result.version_id, "state": result.state.value}


def main() -> int:
    parser = argparse.ArgumentParser(description="ابزار داخلی عملیات شهاب؛ هویت مستقل و مجوز جاری الزامی است")
    parser.add_argument("--command", type=Path, required=True)
    parser.add_argument(
        "--local-ssh-operator", action="store_true", help="private CLI; require separate OS accounts and root policy"
    )
    parser.add_argument("--local-owner-operator", action="store_true", help="private CLI; one approved SSH owner")
    args = parser.parse_args()
    engine = None
    try:
        with args.command.open("rb") as source:
            payload = source.read(8193)
        if len(payload) > 8192:
            raise ValueError("command too large")
        command = OperationsCommand.model_validate_json(payload)
        if args.local_ssh_operator and args.local_owner_operator:
            raise ValueError("choose one local operator mode")
        if args.local_ssh_operator or args.local_owner_operator:
            authority = LocalSshAuthority(allow_root_owner=args.local_owner_operator)
        else:
            config = AuthorityConfiguration.model_validate_json(os.environ["SHAHAB_OPERATIONS_AUTHORITY"])
            credential = os.environ.get("SHAHAB_OPERATIONS_ACCESS_TOKEN")
            if credential is None:
                if not sys.stdin.isatty():
                    raise ValueError("credential is required")
                credential = getpass.getpass("توکن کوتاه‌عمر عملیات: ")
            authority = IntrospectionAuthority(config, SecretStr(credential))
        # Engine construction does not connect. execute authenticates/authorizes
        # before the first database call, then T02 checks current grants again.
        engine = create_engine(os.environ["SHAHAB_DATABASE_URL"], pool_pre_ping=True)
        result = execute(command, authority, sessionmaker(engine), projection())
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception:
        print("دستور اجرا نشد؛ هویت، مجوز، ورودی یا وضعیت محیط را بررسی کنید.", file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
