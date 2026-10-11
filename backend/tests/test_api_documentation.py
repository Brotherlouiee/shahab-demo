"""Documentation coverage, drift, safe sharing and interactive policy regressions."""

import ast
import json
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.core.config import AppEnvironment, Settings
from backend.app.main import create_app
from scripts.export_api_docs import METHODS, artifacts

ROOT = Path(__file__).resolve().parents[2]


class ApiDocumentationTests(unittest.TestCase):
    def test_all_declared_api_operations_are_exported_once(self) -> None:
        declared = set()
        for path in (ROOT / "backend/app/api/v1").glob("*.py"):
            module = ast.parse(path.read_text())
            prefix = None
            for node in ast.walk(module):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "APIRouter":
                    prefix = next((ast.literal_eval(k.value) for k in node.keywords if k.arg == "prefix"), "")
            if prefix is None:
                continue
            for node in ast.walk(module):
                if isinstance(node, ast.FunctionDef):
                    for decorator in node.decorator_list:
                        if (
                            isinstance(decorator, ast.Call)
                            and isinstance(decorator.func, ast.Attribute)
                            and isinstance(decorator.func.value, ast.Name)
                            and decorator.func.value.id == "router"
                            and decorator.func.attr in METHODS
                        ):
                            declared.add(
                                (decorator.func.attr.upper(), "/api/v1" + prefix + ast.literal_eval(decorator.args[0]))
                            )
        inventory = json.loads(artifacts()["operations.json"])
        exported = {(row["method"], row["path"]) for row in inventory}
        self.assertEqual(exported, declared)
        self.assertEqual(len(inventory), len(exported))
        self.assertEqual(len({row["operationId"] for row in inventory}), len(inventory))

    def test_health_visibility_and_production_policy_remain_explicit(self) -> None:
        normal = create_app(Settings()).openapi()
        self.assertNotIn("/api/v1/health/ready", normal["paths"])
        restricted = create_app(Settings(api_docs_include_operations=True)).openapi()
        self.assertEqual(restricted["paths"]["/api/v1/health/ready"]["get"]["security"], [{"ReadinessToken": []}])
        client = TestClient(
            create_app(Settings(environment=AppEnvironment.PRODUCTION, api_docs_include_operations=True))
        )
        for path in ("/docs", "/redoc", "/api/v1/openapi.json"):
            self.assertEqual(client.get(path).status_code, 404)
        self.assertEqual(client.get("/api/v1/health/ready").status_code, 404)

    def test_error_and_auth_schemas_match_transport(self) -> None:
        app = create_app(Settings())
        schema = app.openapi()
        operation = schema["paths"]["/api/v1/profiles/me"]["get"]
        self.assertEqual(operation["security"], [{"AccountBearer": []}, {"AccountCookie": []}])
        error_ref = operation["responses"]["401"]["content"]["application/json"]["schema"]["$ref"]
        self.assertEqual(error_ref, "#/components/schemas/ErrorResponse")
        response = TestClient(app).get("/api/v1/profiles/me")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(set(response.json()), {"error"})
        self.assertIn("correlationId", response.json()["error"])
        recommendations = schema["paths"]["/api/v1/recommendations"]["post"]
        self.assertIn("proof cookie", recommendations["description"])
        self.assertIn({}, recommendations["security"])

    def test_collection_covers_operations_and_has_no_shared_secrets(self) -> None:
        output = artifacts()
        collection = json.loads(output["shahab.postman_collection.json"])
        rows = [item for group in collection["item"] for item in group["item"]]
        self.assertEqual(len(rows), len(json.loads(output["operations.json"])))
        for row in rows:
            url = row["request"]["url"]
            self.assertTrue(url["raw"].startswith("{{baseUrl}}/api/v1/"))
            self.assertTrue(url["path"])
        environment = json.loads(output["shahab.postman_environment.json"])
        self.assertTrue(all(value["value"] == "" for value in environment["values"]))
        self.assertNotIn("console.log", output["shahab.postman_collection.json"])

    def test_generated_files_have_no_drift(self) -> None:
        first = artifacts()
        self.assertEqual(first, artifacts())
        for name, content in first.items():
            self.assertEqual((ROOT / "docs/api/generated" / name).read_text(), content, name)

    def test_swagger_preserves_cookies_without_persisting_authorization(self) -> None:
        client = TestClient(create_app(Settings()))
        response = client.get("/docs")
        self.assertEqual(response.status_code, 200)
        for expected in (
            '"withCredentials": true',
            '"persistAuthorization": false',
            '"validatorUrl": null',
            "@5.17.14/",
        ):
            self.assertIn(expected, response.text)

    def test_swagger_schema_url_respects_reverse_proxy_root(self) -> None:
        client = TestClient(create_app(Settings()), root_path="/restricted")
        self.assertIn("/restricted/api/v1/openapi.json", client.get("/docs").text)
