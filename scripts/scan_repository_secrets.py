"""Conservative pre-commit/CI scan for accidentally committed credential assignments."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[1]
EXCLUDED_DIRECTORIES = {".git", "node_modules", "dist", "__pycache__"}
TEXT_EXTENSIONS = {".json", ".js", ".jsx", ".md", ".mjs", ".py", ".toml", ".txt", ".yml", ".yaml"}
ASSIGNMENT_PATTERN = re.compile(
    r"(?i)\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password|private[_-]?key)\b\s*[:=]\s*['\"]([^'\"]{8,})['\"]"
)
ALLOWED_EXAMPLE_VALUES = {"replace-with-a-local-secret", "test-readiness-token"}


def candidate_files(root: Path = ROOT) -> list[Path]:
    """Return tracked-source-like text files while avoiding generated and binary directories."""
    return [
        path
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in EXCLUDED_DIRECTORIES for part in path.parts)
        and path.suffix in TEXT_EXTENSIONS
    ]


def find_secret_assignments(root: Path = ROOT) -> list[str]:
    """Return source locations with credential-shaped literals not explicitly allowed as test placeholders."""
    findings: list[str] = []
    for path in candidate_files(root):
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except UnicodeDecodeError:
            continue
        for number, line in enumerate(lines, start=1):
            for match in ASSIGNMENT_PATTERN.finditer(line):
                if match.group(1) not in ALLOWED_EXAMPLE_VALUES:
                    findings.append(f"{path.relative_to(root)}:{number}")
    return findings


def main() -> None:
    findings = find_secret_assignments()
    if findings:
        raise SystemExit("potential committed secret assignment(s):\n" + "\n".join(findings))
    print("secret scan passed")


if __name__ == "__main__":
    main()
