"""List the styles in a Word template and map them to the toolkit's needs (FR-INT-07, FR-INP-10).

Usage:
    python scripts/brand/inspect_template.py <template.docx|template.dotx>

Prints every paragraph, character and table style, a suggested style map
(heading1 -> "Heading 1", body -> "Normal", ...), and the fonts and colors the
template uses for headings and body text.
"""

from __future__ import annotations

import io
import re
import sys
import zipfile
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from docx import Document
from docx.enum.style import WD_STYLE_TYPE

# What the renderers need, and the built-in Word style names that usually provide it.
NEEDED: dict[str, list[str]] = {
    "title": ["Title"],
    "heading1": ["Heading 1"],
    "heading2": ["Heading 2"],
    "heading3": ["Heading 3"],
    "body": ["Normal", "Body Text"],
    "list_bullet": ["List Bullet", "List Paragraph"],
    "list_number": ["List Number", "List Paragraph"],
    "quote": ["Quote", "Intense Quote"],
    "caption": ["Caption"],
    "table": ["Table Grid", "Light Grid", "Light List"],
}

TEMPLATE_TYPE = b"application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml"
DOCUMENT_TYPE = b"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"


def open_document(path: Path):
    """Open a .docx or .dotx. python-docx only opens .docx, so a .dotx is relabeled in memory."""
    if path.suffix.lower() != ".dotx":
        return Document(str(path))
    buffer = io.BytesIO()
    with zipfile.ZipFile(path) as src, zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            data = src.read(item.filename)
            if item.filename == "[Content_Types].xml":
                data = data.replace(TEMPLATE_TYPE, DOCUMENT_TYPE)
            dst.writestr(item, data)
    buffer.seek(0)
    return Document(buffer)


def _norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def _style_font(style) -> dict:
    """Font name and color for a style, following its 'based on' chain."""
    info: dict = {}
    current = style
    while current is not None and ("font" not in info or "color" not in info):
        font = current.font
        if "font" not in info and font.name:
            info["font"] = font.name
        if "color" not in info and font.color is not None and font.color.type is not None and font.color.rgb:
            info["color"] = f"#{font.color.rgb}"
        current = current.base_style
    return info


def inspect(path: Path) -> dict:
    doc = open_document(path)
    kinds = {WD_STYLE_TYPE.PARAGRAPH: "paragraph", WD_STYLE_TYPE.CHARACTER: "character", WD_STYLE_TYPE.TABLE: "table"}
    styles = []
    for s in doc.styles:
        kind = kinds.get(s.type)
        if kind:
            styles.append({"name": s.name, "type": kind, "builtin": bool(s.builtin)})

    by_norm: dict[str, str] = {}
    for s in styles:
        by_norm.setdefault(_norm(s["name"]), s["name"])

    style_map: dict[str, str] = {}
    unmatched: list[str] = []
    for need, candidates in NEEDED.items():
        match = next((by_norm[_norm(c)] for c in candidates if _norm(c) in by_norm), None)
        if match is None and need.startswith("heading"):
            level = need[-1]
            match = next((s["name"] for s in styles if s["type"] == "paragraph"
                          and re.search(rf"(heading|h)\s*{level}\b", s["name"], re.I)), None)
        if match:
            style_map[need] = match
        else:
            unmatched.append(need)

    hints = {}
    for need in ("heading1", "body"):
        if need in style_map:
            try:
                hints[need] = _style_font(doc.styles[style_map[need]])
            except KeyError:
                pass
    return {"path": str(path), "styles": styles, "style_map": style_map, "unmatched": unmatched, "hints": hints}


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    path = Path(argv[0])
    try:
        result = inspect(path)
    except Exception as exc:
        print(f"[X] Could not open {path.name} as a Word template ({type(exc).__name__}: {exc})")
        return 1
    print(f"Styles in {path.name}:")
    for kind in ("paragraph", "character", "table"):
        names = [s["name"] for s in result["styles"] if s["type"] == kind]
        print(f"  {kind} ({len(names)}): {', '.join(names)}")
    print("Suggested style map:")
    for need, name in result["style_map"].items():
        print(f"  {need}: {name}")
    if result["unmatched"]:
        print(f"No match (the neutral style will be used): {', '.join(result['unmatched'])}")
    for need, hint in result["hints"].items():
        print(f"{need} uses: {hint or 'the default font and color'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
