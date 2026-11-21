"""Verify that the US-04.T01 conceptual data-model documentation remains complete."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]
ERD = ROOT / "docs/database/erd.md"
DICTIONARY = ROOT / "docs/database/data-dictionary.md"
REQUIRED_ENTITIES = {
    "lenders",
    "loan_products",
    "loan_product_versions",
    "loan_terms",
    "loan_variables",
    "variable_categories",
    "questionnaire_versions",
    "recommendation_config_versions",
    "recommendation_runs",
    "recommendation_results",
    "data_import_runs",
    "data_source_files",
    "staging_loan_rows",
    "data_quality_issues",
    "approval_records",
    "audit_events",
}


def validate() -> list[str]:
    """Return omissions without claiming a conceptual document is a physical schema."""
    missing: list[str] = []
    if not ERD.is_file() or not DICTIONARY.is_file():
        return ["ERD or data dictionary is missing"]
    erd_text = ERD.read_text(encoding="utf-8")
    dictionary_text = DICTIONARY.read_text(encoding="utf-8")
    for entity in sorted(REQUIRED_ENTITIES):
        if entity not in erd_text:
            missing.append(f"ERD omits {entity}")
        if entity not in dictionary_text:
            missing.append(f"data dictionary omits {entity}")
    for marker in ("3NF", "uuid", "timestamptz", "unknown", "ranking_excluded", "provenance"):
        if marker.casefold() not in erd_text.casefold():
            missing.append(f"ERD omits design marker {marker}")
    return missing


def main() -> None:
    missing = validate()
    if missing:
        raise SystemExit("conceptual data model validation failed:\n" + "\n".join(missing))
    print("conceptual data model validation passed")


if __name__ == "__main__":
    main()
