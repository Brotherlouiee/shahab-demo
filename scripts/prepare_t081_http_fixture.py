"""Publish the official test fixture to a fresh, isolated laptop PostgreSQL.

This is a test-only entry point. It uses the protected operations service and
TLS authority fixture, not direct serving-table writes or production credentials.
"""

from __future__ import annotations

import os
import secrets
import subprocess
import sys
from urllib.parse import urlsplit
from uuid import uuid4

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import sessionmaker

from backend.app.infrastructure.db.models import LoanProductVersion, ServingCatalogueVersion
from backend.tests.operations_authority_fixture import TLSAuthorityFixture
from scripts.operations_tool import OperationsCommand, execute, projection

TABLES = (
    "data_import_runs",
    "data_source_files",
    "lenders",
    "loan_products",
    "loan_product_versions",
    "loan_terms",
    "loan_variables",
    "variable_categories",
    "loan_category_assignments",
    "loan_conditions",
    "loan_serving_facts",
    "questionnaire_versions",
    "questions",
    "answer_options",
    "recommendation_config_versions",
    "question_variable_weights",
    "answer_option_weights",
    "answer_category_compatibilities",
    "serving_catalogue_versions",
    "serving_catalogue_members",
    "operations_imports",
    "operations_versions",
    "audit_events",
)
phase = "guard"


def publish() -> None:
    global phase
    database_url = os.environ.get("SHAHAB_TEST_DATABASE_URL", "")
    address = urlsplit(database_url)
    if (
        os.environ.get("SHAHAB_ENVIRONMENT") != "local"
        or address.scheme != "postgresql+psycopg"
        or address.hostname != "127.0.0.1"
        or address.port != 55432
    ):
        raise RuntimeError("only the isolated laptop fixture database is allowed")
    phase = "migration"
    subprocess.run(
        [sys.executable, "-c", "from alembic.config import main; main()", "upgrade", "head"],
        env={**os.environ, "SHAHAB_DATABASE_URL": database_url},
        check=True,
        capture_output=True,
    )
    owner = create_engine(database_url)
    role = "t081_ops_" + uuid4().hex[:16]
    password = secrets.token_hex(24)
    provider = None
    runtime = None
    try:
        phase = "least-privilege role"
        with owner.begin() as connection:
            connection.execute(text(f"CREATE ROLE {role} LOGIN PASSWORD '{password}'"))
            connection.execute(text(f"GRANT USAGE ON SCHEMA public TO {role}"))
            connection.execute(text(f"GRANT SELECT, INSERT ON {','.join(TABLES)} TO {role}"))
            connection.execute(text(f"GRANT SELECT, UPDATE ON operations_workflow_head TO {role}"))
            connection.execute(text(f"GRANT UPDATE ON serving_catalogue_versions TO {role}"))
            connection.execute(text(f"GRANT USAGE, SELECT ON SEQUENCE audit_events_event_order_seq TO {role}"))
        runtime = create_engine(owner.url.set(username=role, password=password))
        sessions = sessionmaker(runtime)
        phase = "test TLS authority"
        provider = TLSAuthorityFixture()
        provider.claims.update(active=True, roles=["data-editor", "admin"])
        serving = projection()
        prefix = uuid4().hex

        def command(operation: str, **fields):
            return execute(OperationsCommand(operation=operation, **fields), provider.authority(), sessions, serving)

        import_id, version_id = prefix + "i", prefix + "v"
        phase = "protected import"
        command("import", import_id=import_id, reason="Test-only official source import")
        phase = "protected review"
        reviewed = command("review", import_id=import_id)
        if reviewed["accepted"] != 102 or reviewed["rejected"] != 0:
            raise AssertionError("official fixture review did not match the approved test contract")
        phase = "protected prepare"
        command("prepare", import_id=import_id, version_id=version_id, reason="Test-only exact extraction")
        phase = "protected approve"
        command("approve", version_id=version_id, reason="Test-only reviewed fixture approval")
        phase = "protected publish"
        published = command("publish", version_id=version_id, reason="Test-only protected fixture publication")
        if published["state"] != "published":
            raise AssertionError("test fixture was not published")
        phase = "published fixture verification"
        with sessionmaker(owner)() as session:
            count = session.scalar(select(func.count()).select_from(LoanProductVersion))
            active = session.scalar(select(ServingCatalogueVersion).where(ServingCatalogueVersion.active.is_(True)))
            if count != 102 or active is None or active.version_code != serving.public_code:
                raise AssertionError("published fixture is not active")
        print("protected test fixture published: 102 loan versions; operational approval not implied")
    finally:
        if provider is not None:
            provider.close()
        if runtime is not None:
            runtime.dispose()
        with owner.begin() as connection:
            connection.execute(text(f"DROP OWNED BY {role}"))
            connection.execute(text(f"DROP ROLE {role}"))
        owner.dispose()


if __name__ == "__main__":
    try:
        publish()
    except Exception as error:
        print(f"isolated protected fixture preparation failed at {phase}: {type(error).__name__}")
        raise SystemExit(1) from None
