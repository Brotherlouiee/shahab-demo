"""Safe plain-text parsing of approved loan conditions into display bullets."""

from __future__ import annotations

import re

_MARKER = re.compile(r"^(?:(?:[•●▪◦*\-–—]+)|(?:[0-9۰-۹٠-٩]+[.)،:]))\s*")


def parse_conditions_bullets(source_text: str | None) -> tuple[str, ...]:
    """Preserve source wording as text while removing only list formatting.

    The function never emits HTML, interprets tags or joins unrelated lines.
    Presentation must render each returned string as text, not trusted markup.
    """
    if not source_text:
        return ()
    bullets: list[str] = []
    for line in str(source_text).replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        text = " ".join(line.strip().split())
        while marker := _MARKER.match(text):
            text = text[marker.end() :].strip()
        if text:
            bullets.append(text)
    return tuple(bullets)
