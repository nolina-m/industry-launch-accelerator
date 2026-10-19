"""QA checks on rendered files and brand rules (FR-QA-04, FR-QA-05).

The brand check opens the Word and Excel files themselves, so it sees what Word
and Google Docs will see: the colors and fonts each used style resolves to,
including theme colors and theme fonts, which Word applies before plain values.
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

import yaml
from lxml import etree

from scripts.qa.common import ERROR, WARNING, CheckResult, Finding, artifacts, walk
from scripts.util import load_yaml

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS = {"w": W, "a": A, "s": S}
LIMITS_FILE = Path(__file__).with_name("limits.yaml")


def _q(tag: str) -> str:
    prefix, name = tag.split(":")
    return f"{{{NS[prefix]}}}{name}"


# ---------------------------------------------------------------------- Word internals


class DocxStyles:
    """Resolves the effective font and colors of the styles a .docx actually uses."""

    def __init__(self, z: zipfile.ZipFile):
        self.styles = {s.get(_q("w:styleId")): s for s in
                       etree.fromstring(z.read("word/styles.xml")).iter(_q("w:style"))}
        self.defaults = etree.fromstring(z.read("word/styles.xml")).find(".//w:docDefaults", NS)
        theme_name = next((n for n in z.namelist() if n.startswith("word/theme/") and n.endswith(".xml")), None)
        self.theme_fonts, self.theme_colors = {}, {}
        if theme_name:
            theme = etree.fromstring(z.read(theme_name))
            for kind in ("major", "minor"):
                latin = theme.find(f".//a:{kind}Font/a:latin", NS)
                if latin is not None:
                    self.theme_fonts[kind] = latin.get("typeface")
            scheme = theme.find(".//a:clrScheme", NS)
            if scheme is not None:
                for child in scheme:
                    tag = etree.QName(child).localname
                    clr = child.find("a:srgbClr", NS)
                    sys_clr = child.find("a:sysClr", NS)
                    value = clr.get("val") if clr is not None else None
                    if value is None and sys_clr is not None:
                        value = sys_clr.get("lastClr")
                    if value:
                        self.theme_colors[tag] = value.upper()
        aliases = {"text1": "dk1", "text2": "dk2", "background1": "lt1", "background2": "lt2"}
        for alias, real in aliases.items():
            if real in self.theme_colors:
                self.theme_colors[alias] = self.theme_colors[real]

    def chain(self, style_id: str | None):
        seen = set()
        while style_id and style_id in self.styles and style_id not in seen:
            seen.add(style_id)
            yield self.styles[style_id]
            based = self.styles[style_id].find("w:basedOn", NS)
            style_id = based.get(_q("w:val")) if based is not None else None

    def font_of(self, element) -> str | None:
        rfonts = element.find(".//w:rFonts", NS)
        if rfonts is None:
            return None
        theme = rfonts.get(_q("w:asciiTheme"))
        if theme:  # Word uses the theme font before any plain font name
            return self.theme_fonts.get("major" if theme.startswith("major") else "minor", f"theme:{theme}")
        return rfonts.get(_q("w:ascii"))

    def effective_font(self, style_id: str | None) -> str | None:
        for style in self.chain(style_id):
            font = self.font_of(style)
            if font:
                return font
        return self.font_of(self.defaults) if self.defaults is not None else None

    def color_of(self, el) -> str | None:
        theme = el.get(_q("w:themeColor"))
        if theme:  # Word uses the theme color before the plain value
            return self.theme_colors.get(theme, f"theme:{theme}")
        val = el.get(_q("w:val")) if etree.QName(el).localname == "color" else el.get(_q("w:color"))
        return None if val in (None, "auto") else val.upper()

    def colors_in(self, element) -> set[str]:
        found = set()
        for el in element.iter():
            name = etree.QName(el).localname
            if name == "color" or (name in ("top", "bottom", "left", "right", "insideH", "insideV")
                                   and el.get(_q("w:color"))):
                c = self.color_of(el)
                if c:
                    found.add(c)
            if name == "shd":
                fill = el.get(_q("w:fill"))
                if fill and fill != "auto":
                    found.add(fill.upper())
        return found


def docx_fonts_and_colors(path: Path) -> tuple[set[str], set[str]]:
    with zipfile.ZipFile(path) as z:
        styles = DocxStyles(z)
        parts = [n for n in z.namelist() if re.match(r"word/(document|header\d*|footer\d*)\.xml$", n)]
        used, fonts, colors = {"Normal"}, set(), set()
        for name in parts:
            root = etree.fromstring(z.read(name))
            for tag in ("w:pStyle", "w:rStyle", "w:tblStyle"):
                used |= {el.get(_q("w:val")) for el in root.iter(_q(tag))}
            colors |= styles.colors_in(root)
            for rfonts in root.iter(_q("w:rFonts")):
                f = rfonts.get(_q("w:ascii"))
                if f:
                    fonts.add(f)
        for sid in used:
            font = styles.effective_font(sid)
            if font:
                fonts.add(font)
            for style in styles.chain(sid):
                colors |= styles.colors_in(style)
    return fonts, colors


def xlsx_fonts_and_colors(path: Path) -> tuple[set[str], set[str]]:
    fonts, colors = set(), set()
    with zipfile.ZipFile(path) as z:
        root = etree.fromstring(z.read("xl/styles.xml"))
    for font in root.iter(_q("s:font")):
        name = font.find("s:name", NS)
        if name is not None:
            fonts.add(name.get("val"))
        color = font.find("s:color", NS)
        if color is not None and color.get("rgb"):
            colors.add(color.get("rgb")[-6:].upper())
    for fill in root.iter(_q("s:fgColor")):
        if fill.get("rgb"):
            colors.add(fill.get("rgb")[-6:].upper())
    return fonts, colors


# ---------------------------------------------------------------------- FR-QA-04 brand


def _palette(brand: dict) -> set[str]:
    c = brand["colors"]
    values = [c.get("primary"), c.get("secondary"), c.get("text"), c.get("background"), *(c.get("accent") or [])]
    return {v.lstrip("#").upper() for v in values if v}


def check_brand(launch_dir: Path) -> CheckResult:
    result = CheckResult("FR-QA-04", "Brand: palette, fonts and terms")
    brand = load_yaml(launch_dir / "brand.yaml") if (launch_dir / "brand.yaml").exists() else None
    if not brand:
        result.summary = "No brand.yaml yet."
        return result
    palette = _palette(brand)
    f = brand["fonts"]
    allowed_fonts = {f.get("heading"), f.get("body"), f.get("fallback_heading"), f.get("fallback_body")} - {None}
    # With the PMM's own Word template, its built-in colors and fonts are part of the brand: warn only.
    severity = WARNING if brand.get("word_template") else ERROR
    out = launch_dir / "outputs"
    files = sorted(out.glob("*.docx")) + sorted(out.glob("*.xlsx")) if out.is_dir() else []
    for path in files:
        fonts, colors = (docx_fonts_and_colors if path.suffix == ".docx" else xlsx_fonts_and_colors)(path)
        rel = path.relative_to(launch_dir).as_posix()
        bad_colors = sorted(colors - palette - {"FFFFFF", "000000"} if brand.get("word_template") else colors - palette)
        if bad_colors:
            result.findings.append(Finding("FR-QA-04", severity, rel, "Colors outside the brand palette: "
                                           + ", ".join(f"#{c}" for c in bad_colors)))
        bad_fonts = sorted(fonts - allowed_fonts)
        if bad_fonts:
            result.findings.append(Finding("FR-QA-04", severity, rel, "Fonts not declared in brand.yaml: "
                                           + ", ".join(bad_fonts)))
    # Terms in the content itself.
    terms = brand.get("terms", {})
    banned = [t for t in terms.get("banned", []) if t]
    preferred = terms.get("preferred", {}) or {}
    product_names = [n for n in terms.get("product_names", []) if n]
    for rel, doc in artifacts(launch_dir).items():
        for path, _, _, text in walk(doc):
            for term in banned:
                if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", text, re.I):
                    result.findings.append(Finding("FR-QA-04", ERROR, rel, f"Banned term \"{term}\"", path))
            for avoid, use in preferred.items():
                if re.search(rf"(?<!\w){re.escape(avoid)}(?!\w)", text, re.I):
                    result.findings.append(Finding("FR-QA-04", WARNING, rel, f"Use \"{use}\" instead of \"{avoid}\"",
                                                   path))
            for name in product_names:
                for m in re.finditer(rf"(?<!\w){re.escape(name)}(?!\w)", text, re.I):
                    if m.group(0) != name:
                        result.findings.append(Finding("FR-QA-04", ERROR, rel, f"Product name written \"{m.group(0)}\""
                                                       f"; should be \"{name}\"", path))
    result.summary = f"Checked {len(files)} Word/Excel file(s) against {len(palette)} brand color(s) and " \
                     f"{len(allowed_fonts)} font name(s); checked terms in the content."
    return result


# ---------------------------------------------------------------------- FR-QA-05 layout

# Placeholders, plus rendering artifacts that mean a template printed a Python object instead of text.
PLACEHOLDER_RE = re.compile(r"\b(TODO|TBD|FIXME|XXX|lorem ipsum)\b|\{\{|\}\}|<placeholder>|\[INSERT|"
                            r"<built-in method|<bound method|<function \w| object at 0x[0-9a-f]+", re.I)
EMPTY_FILLERS = {"none listed.", "none.", "none found.", "none yet.", "no sources cited."}
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$")


def _sections(lines: list[str]):
    """Yield (heading, level, body lines) for each heading in a Markdown file."""
    current, level, body = None, 0, []
    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            if current is not None:
                yield current, level, body
            current, level, body = m.group(2), len(m.group(1)), []
        else:
            body.append(line)
    if current is not None:
        yield current, level, body


def _limits(launch_dir: Path) -> dict[str, int]:
    limits = yaml.safe_load(LIMITS_FILE.read_text())
    override = launch_dir / "qa-limits.yaml"
    if override.exists():
        limits.update(yaml.safe_load(override.read_text()) or {})
    return limits


def check_layout(launch_dir: Path) -> CheckResult:
    result = CheckResult("FR-QA-05", "Layout: no empty sections, placeholders or broken tables; within length")
    out = launch_dir / "outputs"
    files = sorted(out.glob("*.md")) if out.is_dir() else []
    limits = _limits(launch_dir)
    for path in files:
        rel = path.relative_to(launch_dir).as_posix()
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        sections = list(_sections(lines))
        for i, (heading, level, body) in enumerate(sections):
            content = [b.strip() for b in body if b.strip() and b.strip() != "---"]
            has_child = i + 1 < len(sections) and sections[i + 1][1] > level
            if not content and not has_child:
                result.findings.append(Finding("FR-QA-05", ERROR, rel, f"Empty section \"{heading}\""))
            elif len(content) == 1 and content[0].lower() in EMPTY_FILLERS and heading != "Sources":
                result.findings.append(Finding("FR-QA-05", WARNING, rel, f"Section \"{heading}\" has nothing in it "
                                               f"(\"{content[0]}\")"))
        for n, line in enumerate(lines, start=1):
            if PLACEHOLDER_RE.search(line):
                result.findings.append(Finding("FR-QA-05", ERROR, rel, f"Placeholder text: \"{line.strip()[:120]}\"",
                                               f"line {n}"))
        # Tables: every row needs the same number of cells as the header.
        n = 0
        while n < len(lines):
            if lines[n].strip().startswith("|"):
                start, widths = n, []
                while n < len(lines) and lines[n].strip().startswith("|"):
                    widths.append(len(re.split(r"(?<!\\)\|", lines[n].strip().strip("|"))))
                    n += 1
                if len(set(widths)) > 1:
                    result.findings.append(Finding("FR-QA-05", ERROR, rel, "Broken table: rows have different "
                                                   f"numbers of cells {sorted(set(widths))}", f"line {start + 1}"))
            n += 1
        body = text.split("## Before you use this")[0]
        count = len(re.findall(r"\w+", body))
        key = next((k for k in sorted(limits, key=len, reverse=True) if path.stem.startswith(k)), None)
        if key and count > limits[key]:
            result.findings.append(Finding("FR-QA-05", WARNING, rel, f"{count} words; the limit for this asset is "
                                           f"{limits[key]}"))
    result.summary = f"Checked {len(files)} rendered Markdown file(s)."
    return result
