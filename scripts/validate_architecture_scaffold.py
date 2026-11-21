"""Static checks for the US-03.T01 migration scaffold."""

from pathlib import Path

ROOT = Path(__file__).parents[1]
REQUIRED = (
    "frontend/src/app/README.md",
    "frontend/src/shared/README.md",
    "frontend/src/features/questionnaire/README.md",
    "frontend/src/features/recommendation/README.md",
    "frontend/src/features/loan-details/README.md",
    "backend/app/core/__init__.py",
    "backend/app/api/v1/__init__.py",
    "backend/app/shared/__init__.py",
    "backend/app/recommendation/domain/__init__.py",
    "docs/architecture/module-map.md",
    "docs/architecture/0001-staged-architecture-scaffold.md",
)


def main() -> None:
    missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
    if missing:
        raise SystemExit(f"architecture scaffold validation failed: missing {', '.join(missing)}")
    if not (ROOT / "src/main.jsx").is_file():
        raise SystemExit("architecture scaffold validation failed: active prototype entry is missing")
    print("architecture scaffold validation passed")


if __name__ == "__main__":
    main()
