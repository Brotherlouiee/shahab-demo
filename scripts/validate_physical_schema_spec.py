"""Keep the US-04.T02 physical-schema specification complete before ORM work begins."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parents[1]
SPECIFICATION = ROOT / "docs/database/physical-schema-3nf.md"
RUNBOOK = ROOT / "docs/database/migrations-and-rollback.md"
REQUIRED_MARKERS = {
    "lenders",
    "loan_products",
    "loan_product_versions",
    "loan_terms",
    "recommendation_results",
    "data_import_runs",
    "staging_loan_rows",
    "uuid",
    "timestamptz",
    "unique",
    "check",
    "ranking_excluded",
    "3nf",
}
RUNBOOK_MARKERS = {"alembic", "upgrade", "downgrade", "backup", "rollback", "expand/contract"}


def validate() -> list[str]:
    """Report missing physical-design obligations without pretending the schema exists."""
    problems: list[str] = []
    if not SPECIFICATION.is_file() or not RUNBOOK.is_file():
        return ["physical schema specification or migration runbook is missing"]
    specification = SPECIFICATION.read_text(encoding="utf-8").casefold()
    runbook = RUNBOOK.read_text(encoding="utf-8").casefold()
    problems.extend(
        f"physical specification omits {marker}" for marker in sorted(REQUIRED_MARKERS) if marker not in specification
    )
    problems.extend(f"migration runbook omits {marker}" for marker in sorted(RUNBOOK_MARKERS) if marker not in runbook)
    return problems


def main() -> None:
    problems = validate()
    if problems:
        raise SystemExit("physical schema specification validation failed:\n" + "\n".join(problems))
    print("physical schema specification validation passed")


if __name__ == "__main__":
    main()
