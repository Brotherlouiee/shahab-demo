"""AST-based import-boundary and circular-dependency validation for backend layers."""

from __future__ import annotations

import ast
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parents[1]
BACKEND_ROOT = ROOT / "backend"

FORBIDDEN_PREFIXES = {
    "backend.app.domain": ("backend.app.api", "backend.app.core", "backend.app.infrastructure", "backend.app.application"),
    "backend.app.recommendation.domain": ("backend.app.api", "backend.app.core", "backend.app.infrastructure", "backend.app.application"),
    "backend.app.application": ("backend.app.api", "backend.app.infrastructure"),
    "backend.app.api": ("backend.app.infrastructure",),
}


def module_name(path: Path) -> str:
    relative = path.relative_to(ROOT).with_suffix("")
    parts = relative.parts
    return ".".join(parts[:-1] if parts[-1] == "__init__" else parts)


def imported_modules(path: Path) -> set[str]:
    """Resolve local absolute/relative imports from one Python source file."""
    source_module = module_name(path)
    package = source_module if path.name == "__init__.py" else source_module.rpartition(".")[0]
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = package.split(".")
            if node.level:
                base = base[: max(0, len(base) - node.level + 1)]
            if node.module:
                base.extend(node.module.split("."))
            if base:
                imports.add(".".join(base))
    return {item for item in imports if item.startswith("backend.")}


def is_forbidden(source: str, target: str) -> bool:
    """Return whether a directed local import violates the approved layer flow."""
    return any(
        source == source_prefix or source.startswith(f"{source_prefix}.")
        for source_prefix, targets in FORBIDDEN_PREFIXES.items()
        if any(target == target_prefix or target.startswith(f"{target_prefix}.") for target_prefix in targets)
    )


def find_cycles(graph: dict[str, set[str]]) -> list[list[str]]:
    """Return each local import cycle once, using a depth-first traversal."""
    visiting: set[str] = set()
    visited: set[str] = set()
    stack: list[str] = []
    cycles: list[list[str]] = []

    def visit(node: str) -> None:
        if node in visiting:
            start = stack.index(node)
            cycles.append(stack[start:] + [node])
            return
        if node in visited:
            return
        visiting.add(node)
        stack.append(node)
        for target in graph.get(node, set()):
            if target in graph:
                visit(target)
        stack.pop()
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)
    return cycles


def validate_repository(root: Path = ROOT) -> list[str]:
    """Collect import-boundary and cycle violations without importing application code."""
    backend_root = root / "backend"
    graph: dict[str, set[str]] = defaultdict(set)
    violations: list[str] = []
    for path in backend_root.rglob("*.py"):
        source = module_name(path) if root == ROOT else ".".join(path.relative_to(root).with_suffix("").parts)
        if path.name == "__init__.py":
            source = source.rpartition(".")[0]
        targets = imported_modules(path) if root == ROOT else set()
        graph[source].update(targets)
        for target in targets:
            if is_forbidden(source, target):
                violations.append(f"forbidden import: {source} -> {target}")
    for cycle in find_cycles(graph):
        violations.append(f"circular import: {' -> '.join(cycle)}")
    return violations


def main() -> None:
    violations = validate_repository()
    if violations:
        raise SystemExit("import boundary validation failed:\n" + "\n".join(sorted(violations)))
    print("import boundary validation passed")


if __name__ == "__main__":
    main()
