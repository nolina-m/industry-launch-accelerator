"""Build brand.yaml for a launch (FR-INP-08..11, FR-INT-07, Appendix C).

Usage:
    python scripts/brand/extract_brand.py <slug>

brand.yaml is rebuilt from these layers, later ones winning:
  1. the neutral theme (scripts/brand/theme.py)
  2. fonts and colors found in a Word template in inputs/brand/
  3. intake/brand-notes.yaml: what the agent read in a brand book or brand page
     (same fields as brand.yaml; the agent writes it after the PMM confirms)
  4. inputs/brand-questionnaire.md: the PMM's own answers

It also writes intake/brand-candidates.yaml: hex colors and font names spotted in
brand documents, for the agent to confirm with the PMM. Nothing is guessed into
brand.yaml from those candidates.

With no brand input at all, brand.yaml uses the neutral theme with
unbranded: true, and every document is labeled "Unbranded draft" (FR-INP-11).
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.brand.inspect_template import inspect
from scripts.brand.theme import NEUTRAL_COLORS, NEUTRAL_FONTS
from scripts.extract.extract import IGNORED_NAMES, extract_text
from scripts.intake import markdown_template as md
from scripts.util import LAUNCHES_DIR, dump_yaml, load_yaml
from scripts.validate import validate_data

QUESTIONNAIRE = "inputs/brand-questionnaire.md"
NOTES = "intake/brand-notes.yaml"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
DOC_SUFFIXES = {".pdf", ".docx", ".md", ".txt", ".pptx"}
DARK_HINTS = ("white", "dark", "reverse", "inverse", "negative", "knockout")
HEX_RE = re.compile(r"#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{3})\b")
PLACEMENTS = ("header-left", "header-right", "header-center", "none")
# Common typefaces to look for in brand documents.
KNOWN_FONTS = [
    "Arial", "Helvetica", "Helvetica Neue", "Inter", "Roboto", "Open Sans", "Lato", "Montserrat",
    "Source Sans Pro", "Source Sans 3", "Poppins", "Nunito", "Raleway", "Work Sans", "IBM Plex Sans",
    "Noto Sans", "Calibri", "Segoe UI", "Georgia", "Times New Roman", "Garamond", "Merriweather",
    "Playfair Display", "Futura", "Gotham", "Proxima Nova", "Avenir", "Verdana", "Tahoma",
]


def normalize_hex(value: str) -> str | None:
    value = value.strip()
    if not value.startswith("#"):
        value = "#" + value
    if re.fullmatch(r"#[0-9A-Fa-f]{3}", value):
        value = "#" + "".join(ch * 2 for ch in value[1:])
    return value.upper() if re.fullmatch(r"#[0-9A-Fa-f]{6}", value) else None


def is_word_template(path: Path) -> bool:
    name = path.name.lower()
    return path.suffix.lower() == ".dotx" or (path.suffix.lower() == ".docx" and "template" in name)


def brand_files(launch_dir: Path) -> list[Path]:
    folder = launch_dir / "inputs" / "brand"
    if not folder.is_dir():
        return []
    return sorted(p for p in folder.rglob("*") if p.is_file() and p.name not in IGNORED_NAMES)


def read_questionnaire(launch_dir: Path) -> tuple[dict, list[str]]:
    """Partial brand.yaml from the PMM's questionnaire answers, plus warnings."""
    path = launch_dir / QUESTIONNAIRE
    if not path.exists() or not md.has_content(path.read_text(encoding="utf-8")):
        return {}, []
    q = md.parse(path.read_text(encoding="utf-8"))
    warnings: list[str] = []
    out: dict = {}

    def field(section: str, key: str) -> str:
        return q.get(section, {}).get("fields", {}).get(key, "")

    name = md.clean(q.get("company_name", {}).get("text", ""))
    if not md.is_empty(name):
        out["name"] = name

    colors: dict = {}
    for key, heading in (("primary", "primary_color"), ("secondary", "secondary_color"),
                         ("text", "text_color"), ("background", "background_color")):
        raw = md.clean(field("colors", heading))
        if md.is_empty(raw):
            continue
        found = HEX_RE.search(raw) or re.search(r"\b[0-9A-Fa-f]{6}\b", raw)
        value = normalize_hex(found.group(0)) if found else None
        if value:
            colors[key] = value
        else:
            warnings.append(f"{heading.replace('_', ' ')} '{raw}' is not a hex color like #0A2540; ignored")
    accents = [normalize_hex(m) for m in HEX_RE.findall(md.clean(field("colors", "accent_colors")))]
    if accents:
        colors["accent"] = [a for a in accents if a]
    if colors:
        out["colors"] = colors

    fonts = {}
    for key, heading in (("heading", "heading_font"), ("body", "body_font")):
        raw = md.clean(field("fonts", heading))
        if not md.is_empty(raw):
            fonts[key] = raw.splitlines()[0].strip()
    if fonts:
        out["fonts"] = fonts

    logo = {}
    for key, heading in (("light_bg", "logo_for_light_backgrounds"), ("dark_bg", "logo_for_dark_backgrounds")):
        raw = md.clean(field("logo", heading))
        if not md.is_empty(raw):
            file_name = raw.splitlines()[0].strip().strip("`")
            logo[key] = f"inputs/brand/{Path(file_name).name}"
    placement = md.clean(field("logo", "logo_placement")).lower()
    if placement in PLACEMENTS:
        logo["placement"] = placement
    if logo:
        out["logo"] = logo

    voice = {}
    traits = md.bullets(field("voice", "tone_traits"))
    if len(traits) == 1 and "," in traits[0]:
        traits = [t.strip() for t in traits[0].split(",") if t.strip()]
    if traits:
        voice["traits"] = traits
    for key, heading in (("do", "do"), ("dont", "dont")):
        items = md.bullets(field("voice", heading))
        if items:
            voice[key] = items
    if voice:
        out["voice"] = voice

    terms: dict = {}
    banned = md.bullets(field("terms", "banned_terms"))
    if banned:
        terms["banned"] = banned
    preferred = {}
    for line in md.bullets(field("terms", "preferred_terms")):
        parts = re.split(r"\s*(?:->|→|=>)\s*", line, maxsplit=1)
        if len(parts) == 2 and parts[0] and parts[1]:
            preferred[parts[0].strip()] = parts[1].strip()
        else:
            warnings.append(f"preferred term '{line}' should look like: avoid this -> use this; ignored")
    if preferred:
        terms["preferred"] = preferred
    names = md.bullets(field("terms", "product_names"))
    if names:
        terms["product_names"] = names
    if terms:
        out["terms"] = terms

    url = md.clean(q.get("brand_page_url", {}).get("text", ""))
    if not md.is_empty(url):
        out["_brand_page_url"] = url
    return out, warnings


def candidates_from_documents(launch_dir: Path, files: list[Path]) -> dict:
    """Hex colors and font names mentioned in brand documents (for the agent to confirm)."""
    colors: Counter = Counter()
    fonts: Counter = Counter()
    read = []
    for path in files:
        if path.suffix.lower() not in DOC_SUFFIXES or is_word_template(path):
            continue
        result = extract_text(path)
        if not result.text:
            continue
        read.append(path.relative_to(launch_dir).as_posix())
        for match in HEX_RE.findall(result.text):
            value = normalize_hex(match)
            if value:
                colors[value] += 1
        for font in KNOWN_FONTS:
            count = len(re.findall(rf"\b{re.escape(font)}\b", result.text))
            if count:
                fonts[font] += count
    return {
        "documents_read": read,
        "colors": [{"hex": c, "mentions": n} for c, n in colors.most_common(12)],
        "fonts": [{"name": f, "mentions": n} for f, n in fonts.most_common(6)],
    }


def _merge(base: dict, layer: dict) -> dict:
    for key, value in layer.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _merge(base[key], value)
        else:
            base[key] = deepcopy(value)
    return base


def build(launch_dir: Path) -> tuple[dict, dict, list[str]]:
    """Return (brand.yaml data, candidates, warnings)."""
    warnings: list[str] = []
    files = brand_files(launch_dir)
    brand: dict = {
        "colors": deepcopy(NEUTRAL_COLORS),
        "fonts": deepcopy(NEUTRAL_FONTS),
        "logo": {"light_bg": None, "dark_bg": None, "placement": "none"},
        "voice": {"traits": [], "do": [], "dont": []},
        "terms": {"banned": [], "preferred": {}, "product_names": []},
        "word_template": None,
        "unbranded": False,
    }

    # Layer 2: Word template
    templates = [p for p in files if is_word_template(p)]
    if len(templates) > 1:
        warnings.append("more than one Word template found; using " + templates[0].name)
    if templates:
        tpl = templates[0]
        try:
            info = inspect(tpl)
            brand["word_template"] = {"path": tpl.relative_to(launch_dir).as_posix(), "style_map": info["style_map"]}
            heading, body = info["hints"].get("heading1", {}), info["hints"].get("body", {})
            if heading.get("font"):
                brand["fonts"]["heading"] = heading["font"]
            if body.get("font"):
                brand["fonts"]["body"] = body["font"]
            if heading.get("color") and normalize_hex(heading["color"]):
                brand["colors"]["primary"] = normalize_hex(heading["color"])
            if info["unmatched"]:
                warnings.append(f"Word template has no style for: {', '.join(info['unmatched'])} (neutral style used)")
        except Exception as exc:
            warnings.append(f"could not read Word template {tpl.name} ({type(exc).__name__}); using the neutral theme")

    # Logos found in inputs/brand/
    images = [p for p in files if p.suffix.lower() in IMAGE_SUFFIXES]
    for img in images:
        rel = img.relative_to(launch_dir).as_posix()
        slot = "dark_bg" if any(h in img.stem.lower() for h in DARK_HINTS) else "light_bg"
        if brand["logo"][slot] is None:
            brand["logo"][slot] = rel
    if any(p.suffix.lower() == ".svg" for p in files):
        warnings.append("SVG logos can't be placed in Word files; please add a PNG version to inputs/brand/")

    # Layer 3: agent notes from a brand book or brand page
    notes_path = launch_dir / NOTES
    notes = load_yaml(notes_path) if notes_path.exists() else {}
    _merge(brand, notes or {})

    # Layer 4: the PMM's questionnaire
    answers, q_warnings = read_questionnaire(launch_dir)
    warnings += q_warnings
    url = answers.pop("_brand_page_url", None)
    _merge(brand, answers)

    for slot in ("light_bg", "dark_bg"):
        path = brand["logo"].get(slot)
        if path and not (launch_dir / path).is_file():
            warnings.append(f"logo file {path} was not found")
            brand["logo"][slot] = None
    if brand["logo"]["placement"] == "none" and (brand["logo"]["light_bg"] or brand["logo"]["dark_bg"]):
        brand["logo"]["placement"] = "header-right"

    has_input = bool(files or notes or answers or url)
    brand["unbranded"] = not has_input
    candidates = candidates_from_documents(launch_dir, files)
    if url:
        candidates["brand_page_url"] = url
    return brand, candidates, warnings


def run(launch_dir: Path) -> tuple[dict, dict, list[str]]:
    brand, candidates, warnings = build(launch_dir)
    problems = validate_data(brand, "brand.schema.json", "brand.yaml")
    if problems:
        raise ValueError("brand.yaml would be invalid:\n" + "\n".join(f"  - {p}" for p in problems))
    dump_yaml(brand, launch_dir / "brand.yaml")
    dump_yaml(candidates, launch_dir / "intake" / "brand-candidates.yaml")
    return brand, candidates, warnings


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    launch_dir = LAUNCHES_DIR / argv[0]
    if not (launch_dir / "launch.yaml").exists():
        print(f"[X] No launch called '{argv[0]}'.")
        return 1
    try:
        brand, candidates, warnings = run(launch_dir)
    except ValueError as exc:
        print(f"[X] {exc}")
        return 1
    if brand["unbranded"]:
        print("[OK] No brand guidelines found: using the neutral theme. Outputs will say 'Unbranded draft'.")
    else:
        print("[OK] Wrote brand.yaml")
    if brand.get("word_template"):
        print(f"  Word template: {brand['word_template']['path']}")
    print(f"  Logo: light={brand['logo']['light_bg']}, dark={brand['logo']['dark_bg']}")
    if candidates["colors"] or candidates["fonts"]:
        print("  Spotted in brand documents (confirm with the PMM, then record in intake/brand-notes.yaml):")
        if candidates["colors"]:
            print("    colors: " + ", ".join(c["hex"] for c in candidates["colors"]))
        if candidates["fonts"]:
            print("    fonts: " + ", ".join(f["name"] for f in candidates["fonts"]))
    if candidates.get("brand_page_url"):
        print(f"  Brand page to read: {candidates['brand_page_url']}")
    for w in warnings:
        print(f"  [!] {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
