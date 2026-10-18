"""Read the filled-in input templates (Markdown with ## and ### headings)."""

from __future__ import annotations

import re

COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
PLACEHOLDERS = {"", "tbd", "tba", "todo", "?", "??", "n/a", "na", "-", "none yet", "unknown", "xxx"}


def heading_key(heading: str) -> str:
    """'Basics (required)' -> 'basics'; "Claims we can't make" -> 'claims_we_cant_make'."""
    heading = re.sub(r"\(.*?\)", "", heading)
    heading = heading.replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", "_", heading.lower()).strip("_")


def strip_comments(text: str) -> str:
    return COMMENT_RE.sub("", text)


def clean(text: str) -> str:
    """Remove guidance comments and surrounding blank lines."""
    lines = [line.rstrip() for line in strip_comments(text).splitlines()]
    return "\n".join(lines).strip()


def is_empty(text: str | list | None) -> bool:
    if text is None:
        return True
    if isinstance(text, list):
        return all(is_empty(t) for t in text)
    return clean(text).strip(" .*_").lower() in PLACEHOLDERS


def bullets(text: str) -> list[str]:
    """Split a block into items: one per bullet or numbered line (or per line if no bullets)."""
    items = []
    for line in clean(text).splitlines():
        line = line.strip()
        if not line:
            continue
        line = re.sub(r"^([-*+•]|\d+[.)])\s+", "", line)
        if not is_empty(line):
            items.append(line)
    return items


def parse(text: str) -> dict[str, dict]:
    """Split a template into {section_key: {"text": body, "fields": {field_key: body}}}.

    `##` headings are sections and `###` headings are fields inside them. Text that
    sits directly under a section (before any field) is that section's "text".
    The `#` title is ignored.
    """
    sections: dict[str, dict] = {}
    section = None
    field = None
    buffer: list[str] = []

    def flush():
        body = clean("\n".join(buffer))
        if section is None:
            return
        if field is None:
            sections[section]["text"] = body
        else:
            sections[section]["fields"][field] = body

    for line in strip_comments(text).splitlines():
        match = HEADING_RE.match(line)
        if match and len(match.group(1)) in (2, 3):
            flush()
            buffer = []
            key = heading_key(match.group(2))
            if len(match.group(1)) == 2:
                section, field = key, None
                sections.setdefault(section, {"text": "", "fields": {}})
            elif section is not None:
                field = key
            continue
        if match and len(match.group(1)) == 1:
            continue
        buffer.append(line)
    flush()
    return sections


def has_content(text: str) -> bool:
    """True if a document has any real content besides headings and guidance."""
    for line in clean(text).splitlines():
        if line.strip() and not HEADING_RE.match(line) and not is_empty(line):
            return True
    return False
