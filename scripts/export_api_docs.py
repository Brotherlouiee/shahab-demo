"""Generate all API documentation artifacts from the actual FastAPI contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from backend.app.core.config import Settings
from backend.app.main import create_app

METHODS = {"get", "post", "put", "delete", "patch", "head", "options"}
FIELD_VARIABLES = {
    "phone": "testPhone",
    "challengeId": "challengeId",
    "code": "otpCode",
    "sessionId": "sessionId",
    "loan_id": "loanId",
    "history_id": "historyId",
    "session_id": "sessionId",
    "question_id": "questionId",
    "answerId": "answerId",
}


def sample(schema: dict[str, Any], definitions: dict[str, Any], name: str = "", depth: int = 0) -> Any:
    """Produce editable synthetic examples; never inspect runtime settings or data."""
    if name in FIELD_VARIABLES:
        return "{{" + FIELD_VARIABLES[name] + "}}"
    if depth > 12:
        return None
    if "$ref" in schema:
        return sample(definitions[schema["$ref"].rsplit("/", 1)[-1]], definitions, name, depth + 1)
    if "example" in schema:
        return schema["example"]
    if "anyOf" in schema:
        choice = next((item for item in schema["anyOf"] if item.get("type") != "null"), {})
        return sample(choice, definitions, name, depth + 1)
    if "default" in schema:
        return schema["default"]
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type")
    if kind == "object":
        return {key: sample(value, definitions, key, depth + 1) for key, value in schema.get("properties", {}).items()}
    if kind == "array":
        return []
    if kind in {"integer", "number"}:
        return schema.get("minimum", 0)
    if kind == "boolean":
        return False
    return ""


def artifacts() -> dict[str, str]:
    """Export deterministically without database startup or external service requests."""
    app = create_app(Settings(environment="test", api_docs_include_operations=True))
    schema = app.openapi()
    schema["info"]["version"] = "0.1.0"
    schema["servers"] = [{"url": "/", "description": "Same-origin API; configure baseUrl in Postman"}]
    definitions = schema["components"]["schemas"]
    groups: dict[str, list[dict[str, Any]]] = {}
    inventory = []
    for path, methods in sorted(schema["paths"].items()):
        for method, operation in sorted(methods.items()):
            if method not in METHODS:
                continue
            inventory.append({"method": method.upper(), "path": path, "operationId": operation["operationId"]})
            url = "{{baseUrl}}" + path
            headers = [{"key": "Accept", "value": "application/json"}]
            query = []
            for parameter in operation.get("parameters", []):
                name = parameter["name"]
                if parameter["in"] == "path":
                    url = url.replace("{" + name + "}", "{{" + FIELD_VARIABLES.get(name, name) + "}}")
                elif parameter["in"] == "query":
                    query.append({"key": name, "value": str(parameter["schema"].get("default", "")), "disabled": True})
            request: dict[str, Any] = {
                "method": method.upper(),
                "header": headers,
                "url": {
                    "raw": url,
                    "host": ["{{baseUrl}}"],
                    "path": url.removeprefix("{{baseUrl}}").lstrip("/").split("/"),
                    "query": query,
                },
                "description": operation.get("description", operation.get("summary", "")),
            }
            security = operation.get("security", [])
            if security and {} not in security and any("AccountBearer" in value for value in security):
                request["auth"] = {
                    "type": "bearer",
                    "bearer": [{"key": "token", "value": "{{accessToken}}", "type": "string"}],
                }
            if path.endswith("/health/ready"):
                headers.append({"key": "X-Shahab-Readiness-Token", "value": "{{readinessToken}}"})
            body_schema = operation.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema")
            if body_schema:
                headers.append({"key": "Content-Type", "value": "application/json"})
                request["body"] = {
                    "mode": "raw",
                    "raw": json.dumps(sample(body_schema, definitions), ensure_ascii=False, indent=2),
                    "options": {"raw": {"language": "json"}},
                }
            events = []
            captures = {
                "/account-access/request": {"challengeId": "challengeId"},
                "/account-access/verify": {"accessToken": "accessToken", "phone": "testPhone"},
                "/questionnaire/sessions": {"sessionId": "sessionId"},
            }
            for suffix, mapping in captures.items():
                if method == "post" and path.endswith(suffix):
                    lines = [
                        "if (pm.response.code >= 200 && pm.response.code < 300) {",
                        "  const value = pm.response.json();",
                    ]
                    lines += [
                        f'  pm.environment.set("{variable}", value["{field}"]);' for field, variable in mapping.items()
                    ]
                    lines.append("}")
                    events.append({"listen": "test", "script": {"type": "text/javascript", "exec": lines}})
            if path.endswith("/recommendations"):
                request["description"] += " Keep account and questionnaire proof cookies in this Postman cookie jar."
            groups.setdefault(operation.get("tags", ["API"])[0], []).append(
                {
                    "name": method.upper() + " " + path,
                    "request": request,
                    "event": events,
                    "response": [],
                }
            )
    collection = {
        "info": {
            "name": "Shahab API — manual testing",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
            "description": (
                "Restricted test environment only. Keep cookies enabled. "
                "Never publish populated environments or tokens."
            ),
        },
        "item": [{"name": name, "item": items} for name, items in sorted(groups.items())],
    }
    variables = sorted(
        {
            "baseUrl",
            "accessToken",
            "readinessToken",
            "testPhone",
            "otpCode",
            "challengeId",
            "sessionId",
            "questionId",
            "answerId",
            "loanId",
            "historyId",
        }
    )
    environment = {
        "name": "Shahab — private test values",
        "values": [
            {
                "key": name,
                "value": "",
                "type": "secret" if name in {"accessToken", "readinessToken", "otpCode"} else "default",
                "enabled": True,
            }
            for name in variables
        ],
        "_postman_variable_scope": "environment",
    }
    return {
        name: json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        for name, value in {
            "openapi.json": schema,
            "shahab.postman_collection.json": collection,
            "shahab.postman_environment.json": environment,
            "operations.json": inventory,
        }.items()
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("docs/api/generated"))
    parser.add_argument("--check", action="store_true", help="Fail on drift; do not write")
    args = parser.parse_args()
    output = artifacts()
    if args.check:
        drift = [
            name
            for name, value in output.items()
            if not (args.output / name).exists() or (args.output / name).read_text() != value
        ]
        if drift:
            parser.error("API artifact drift: " + ", ".join(drift))
    else:
        args.output.mkdir(parents=True, exist_ok=True)
        for name, value in output.items():
            (args.output / name).write_text(value, encoding="utf-8")


if __name__ == "__main__":
    main()
