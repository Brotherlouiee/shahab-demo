"""Validate changed Markdown links and whitespace without installing dependencies."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from html import unescape
from pathlib import Path
from urllib.parse import unquote, urlsplit

LINK = re.compile(
    r"!"
    + re.escape("[")
    + "[^"
    + re.escape("]")
    + "]*"
    + re.escape("]")
    + re.escape("(")
    + r"(<[^>]+>|[^)\s]+)(?:\s+[^)]*)?"
    + re.escape(")")
)
MARKDOWN_SUFFIXES = {".md", ".mdx", ".rst", ".adoc"}


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], check=False, text=True, capture_output=True)


def changed_markdown(base: str, head: str) -> list[Path]:
    result = git("diff", "--name-only", "--diff-filter=ACMRT", base, head)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return [
        Path(line)
        for line in result.stdout.splitlines()
        if Path(line).suffix.casefold() in MARKDOWN_SUFFIXES and Path(line).is_file()
    ]


def visible_markdown(text: str) -> str:
    result: list[str] = []
    fence_char: str | None = None
    fence_size = 0
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            char, size = marker[0], len(marker)
            if fence_char is None:
                fence_char, fence_size = char, size
            elif char == fence_char and size >= fence_size:
                fence_char, fence_size = None, 0
            continue
        if fence_char is None:
            result.append(line)
    if fence_char is not None:
        raise ValueError("unclosed Markdown code fence")
    return "\n".join(result)


def check_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [f"{path}: file is not valid UTF-8"]
    try:
        visible = visible_markdown(text)
    except ValueError as exc:
        errors.append(f"{path}: {exc}")
        visible = text

    for match in LINK.finditer(visible):
        target = match.group(1).strip("<>")
        target = unquote(unescape(target))
        parsed = urlsplit(target)
        if parsed.scheme or target.startswith("//") or target.startswith("#"):
            continue
        target_path = parsed.path
        if not target_path:
            continue
        candidate = Path(target_path.lstrip("/")) if target_path.startswith("/") else path.parent / target_path
        if not candidate.exists():
            errors.append(f"{path}: broken local link target: {target_path}")
    return errors


def main() -> int:
    base = os.environ.get("BASE_SHA", "").strip()
    head = os.environ.get("HEAD_SHA", "").strip()
    if not base or not head:
        print("BASE_SHA and HEAD_SHA are required", file=sys.stderr)
        return 2

    fetched = git("fetch", "--no-tags", "--depth=1", "origin", base)
    if fetched.returncode:
        print(fetched.stderr, file=sys.stderr)
        return fetched.returncode
    diff_check = git("diff", "--check", base, head)
    if diff_check.returncode:
        print(diff_check.stdout + diff_check.stderr, file=sys.stderr)
        return diff_check.returncode

    files = changed_markdown(base, head)
    errors = [error for path in files for error in check_file(path)]
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"Documentation validation passed for {len(files)} changed Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
