"""Documentation-only enrichment; never changes authentication or serving behavior."""

from copy import copy, deepcopy
from typing import Any

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.routing import APIRoute

from backend.app.api.errors import ErrorResponse
from backend.app.api.v1.health import router as health_router


def document_contract(schema: dict[str, Any], prefix: str, *, include_operations: bool = False) -> dict[str, Any]:
    """Describe the actual safe error/auth contract and optional restricted operations."""
    result = deepcopy(schema)
    if include_operations:
        routes = [copy(route) for route in health_router.routes if isinstance(route, APIRoute)]
        for route in routes:
            route.include_in_schema = True
        operational = get_openapi(title="Operations", version="1", routes=routes)
        result["paths"].update({prefix + path: value for path, value in operational["paths"].items()})
        result.setdefault("components", {}).setdefault("schemas", {}).update(operational["components"]["schemas"])
    components = result.setdefault("components", {})
    error_schema = ErrorResponse.model_json_schema(ref_template="#/components/schemas/{model}")
    components.setdefault("schemas", {}).update(error_schema.pop("$defs", {}))
    components["schemas"]["ErrorResponse"] = error_schema
    components["securitySchemes"] = {
        "AccountBearer": {"type": "http", "scheme": "bearer"},
        "AccountCookie": {"type": "apiKey", "in": "cookie", "name": "shahab_account_access"},
        "ReadinessToken": {"type": "apiKey", "in": "header", "name": "X-Shahab-Readiness-Token"},
    }
    for path, methods in result["paths"].items():
        for method, operation in methods.items():
            if method not in {"get", "post", "put", "delete", "patch", "head", "options"}:
                continue
            relative = path.removeprefix(prefix)
            protected = relative.startswith(("/profiles", "/recommendation-history")) or relative in {
                "/account-access/session",
                "/account-access/logout",
            }
            operation["security"] = [{"AccountBearer": []}, {"AccountCookie": []}] if protected else []
            if relative == "/health/ready":
                operation["security"] = [{"ReadinessToken": []}]
            if relative == "/recommendations":
                operation["security"] = [{}, {"AccountBearer": []}, {"AccountCookie": []}]
                operation["description"] = (
                    "Send only sessionId after completing all canonical answers. Authenticated persistence also "
                    "requires the unpredictable HttpOnly questionnaire proof cookie from session creation "
                    "in this same client. "
                    "Bearer alone does not prove questionnaire ownership. Anonymous results remain transient."
                )
            if relative == "/questionnaire/sessions" and method == "post":
                operation["description"] = (
                    "Creates a 30-minute session and its unpredictable HttpOnly proof cookie. "
                    "Keep this cookie jar; the secret is never returned in JSON."
                )
            if relative.startswith("/questionnaire/sessions/"):
                operation["description"] = (
                    "Requires the creator's per-session HttpOnly proof cookie, preserved by this cookie jar. "
                    "ID alone, legacy constant or another session's cookie is forbidden. After account binding, "
                    "the same active account session is also required. Valid expired proof returns 410; "
                    "missing/invalid proof and unknown IDs return the same safe 403. No TTL renewal."
                )
                operation["security"] = [{}, {"AccountBearer": []}, {"AccountCookie": []}]
            if relative == "/account-access/verify":
                operation["description"] = (
                    "Local/test verification creates or reuses the database profile "
                    "and sets a one-hour HttpOnly account cookie backed by PostgreSQL. "
                    "Mock OTP is forbidden in staging/production. No real phone ownership is asserted."
                )
            if relative == "/account-access/session":
                operation["description"] = (
                    "Restores the same active account and returns expiresIn as the remaining absolute lifetime. "
                    "A successful login lasts 3600 seconds; restore, refresh and questionnaire activity "
                    "never renew it. "
                    "Expired, revoked and archived-account credentials are denied across workers and restarts."
                )
            if relative == "/profiles" and method == "put":
                operation["description"] = (
                    "Changes the signed-in actor's database profile. Test only your own synthetic account; "
                    "the payload phone must match the server actor. Read /profiles/me to verify persistence."
                )
            if relative.startswith("/recommendation-history/") and method == "delete":
                operation["description"] = (
                    "Hides your own test history entry from user-facing reads; does not physically delete its "
                    "immutable database snapshot. Missing, already-hidden and another actor's IDs return 404."
                )
            if relative == "/account-access/logout":
                operation["description"] = (
                    "Revokes the current account session and clears its cookie. Protected requests subsequently "
                    "return 401; run this after completing the manual test flow."
                )
            examples = {
                "/account-access/request": {"phone": "09000000001"},
                "/account-access/verify": {"challengeId": "replace-with-your-challenge", "code": "123456"},
                "/profiles": {"phone": "09000000001", "firstName": "آزمون", "job": "employee"},
                "/recommendations": {"sessionId": "replace-with-your-active-session"},
            }
            content = operation.get("requestBody", {}).get("content", {}).get("application/json")
            if content is not None:
                if relative in examples:
                    content["example"] = examples[relative]
                elif relative.endswith("/answers/{question_id}"):
                    content["example"] = {"answerId": "Q1.incomeInvestment"}
            statuses = {"422": "Invalid input", "500": "Internal failure"}
            if relative == "/health/ready":
                statuses["404"] = "Missing/invalid readiness capability"
            if not relative.startswith("/health"):
                statuses["503"] = "Service/storage unavailable"
            if protected or relative in {"/account-access/verify", "/recommendations"}:
                statuses["401"] = "Missing/invalid/expired account access"
            if relative.startswith(("/profiles", "/recommendation-history", "/loans", "/questionnaire/sessions/")):
                statuses["404"] = "Missing or inaccessible resource"
            if (
                relative == "/recommendations"
                or relative == "/profiles"
                or relative.startswith("/questionnaire/sessions/")
            ):
                statuses["403"] = "Ownership denied"
            if relative == "/account-access/request":
                statuses["429"] = "Request quota exceeded"
            if relative.startswith("/questionnaire/sessions/"):
                statuses["410"] = "Questionnaire expired"
            for status, description in statuses.items():
                operation.setdefault("responses", {})[status] = {
                    "description": description,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}},
                }
    return result


class DocumentedFastAPI(FastAPI):
    """Add descriptions while retaining FastAPI generation and production docs policy."""

    def openapi(self) -> dict[str, Any]:
        settings = self.state.settings
        return document_contract(
            super().openapi(),
            settings.api_v1_prefix,
            include_operations=settings.api_docs_include_operations and settings.docs_enabled,
        )
