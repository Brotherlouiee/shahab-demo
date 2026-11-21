"""Create a non-publishing, reviewable import plan from a JSON manifest.

Usage:
  python scripts/prepare_canonical_import.py --manifest path/to/manifest.json
  python scripts/prepare_canonical_import.py --manifest path/to/manifest.json --output plan.json

The command never connects to a database or publishes a version. It is an
operator safety gate before the separate approval/publish workflow.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from backend.app.data_pipeline.application.prepare_import import (
    ImportManifestRow,
    prepare_import_manifest,
)


def main() -> int:
    """Decode only the documented manifest fields and write non-sensitive evidence."""
    arguments = _parse_arguments()
    manifest = _load_manifest(arguments.manifest)
    rows = tuple(_decode_row(item) for item in _require_list(manifest, "rows"))
    plan = prepare_import_manifest(
        source_file_sha256=_require_string(manifest, "sourceFileSha256"),
        parser_version=_require_string(manifest, "parserVersion"),
        rows=rows,
    )
    payload = {
        "sourceFileSha256": plan.source_file_sha256,
        "parserVersion": plan.parser_version,
        "acceptedRowCount": len(plan.accepted_rows),
        "rejectedRows": [
            {"sourceRowNumber": item.source_row_number, "code": item.code, "message": item.message}
            for item in plan.rejected_rows
        ],
        "issues": [
            {"sourceRowNumber": item.source_row_number, "code": item.code, "message": item.message}
            for item in plan.issues
        ],
        "publishableCandidate": plan.is_publishable_candidate,
    }
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if arguments.output is None:
        print(rendered, end="")
    else:
        arguments.output.write_text(rendered, encoding="utf-8")
    return 0 if plan.is_publishable_candidate else 2


def _parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare a non-publishing Shahab canonical import plan.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def _load_manifest(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SystemExit(f"manifest cannot be read as UTF-8 JSON: {error}") from error
    if not isinstance(value, dict):
        raise SystemExit("manifest root must be an object")
    return value


def _decode_row(value: object) -> ImportManifestRow:
    if not isinstance(value, dict):
        raise SystemExit("each row must be an object")
    variable_values = value.get("variableValues")
    if not isinstance(variable_values, dict):
        raise SystemExit("row variableValues must be an object")
    display_fields = value.get("displayFields")
    if display_fields is not None and not isinstance(display_fields, dict):
        raise SystemExit("row displayFields must be an object when supplied")
    source_row_number = value.get("sourceRowNumber")
    if not isinstance(source_row_number, int) or isinstance(source_row_number, bool):
        raise SystemExit("row sourceRowNumber must be an integer")
    lender_name = value.get("lenderName")
    if lender_name is not None and not isinstance(lender_name, str):
        raise SystemExit("row lenderName must be a string when supplied")
    loan_name = value.get("loanName")
    if loan_name is not None and not isinstance(loan_name, str):
        raise SystemExit("row loanName must be a string when supplied")
    if any(
        not isinstance(key, str) or (item is not None and not isinstance(item, str))
        for key, item in variable_values.items()
    ):
        raise SystemExit("row variableValues must map strings to strings or null")
    if display_fields is not None and any(
        not isinstance(key, str) or not isinstance(item, str) for key, item in display_fields.items()
    ):
        raise SystemExit("row displayFields must map strings to strings")
    return ImportManifestRow(
        source_row_number=source_row_number,
        lender_name=lender_name,
        loan_name=loan_name,
        variable_values=variable_values,
        display_fields=display_fields,
    )


def _require_string(value: dict[str, Any], key: str) -> str:
    result = value.get(key)
    if not isinstance(result, str):
        raise SystemExit(f"{key} must be a string")
    return result


def _require_list(value: dict[str, Any], key: str) -> list[object]:
    result = value.get(key)
    if not isinstance(result, list):
        raise SystemExit(f"{key} must be a list")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
