"""Render a launch's YAML into Markdown and Word files in outputs/ (FR-RND-01..06, FR-GRD-06).

Usage:
    python scripts/launch.py render <slug>            # everything that has data
    python scripts/launch.py render <slug> --unit X   # one stage unit, e.g. personas:technology

Every asset gets:
- a status line: Draft, plus "Unbranded draft", "Awaiting PMM approval" or
  "Not reviewed by PMM" when they apply;
- a "Before you use this" list of everything marked [VERIFY], with counts of
  [ASSUMPTION] and [PROOF NEEDED] (principle 7);
- the sources it cites;
- the footer "Draft generated with Industry Launch Accelerator on <date>. Verify
  items marked [VERIFY] before external use."
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from scripts.render import diagrams
from scripts.render.docx_writer import DocxWriter
from scripts.render.xlsx_writer import write_grid
from scripts.sources import load as load_sources
from scripts.state import edits
from scripts.state.launch_state import APPROVED, AWAITING, NOT_STARTED, LaunchState
from scripts.util import TEMPLATES_DIR, load_yaml, today


class DataFirstEnvironment(Environment):
    """Look up a YAML field before any Python attribute of the same name.

    Plain Jinja resolves `section.copy` to the dict's built-in copy() method, not
    the `copy` field, and prints "<built-in method copy ...>". Fields named like
    dict methods (copy, items, values, count...) must always mean the data.
    """

    def getattr(self, obj, attribute):
        if isinstance(obj, dict) and attribute in obj:
            return obj[attribute]
        return super().getattr(obj, attribute)


FOOTER = "Draft generated with Industry Launch Accelerator on {date}. Verify items marked [VERIFY] before external use."
LABEL_RE = {
    "verify": re.compile(r"\[VERIFY\]"),
    "assumption": re.compile(r"\[ASSUMPTION\]"),
    "proof": re.compile(r"\[PROOF NEEDED\]"),
}
CITE_RE = re.compile(r"\[(S\d+)\]")
MAX_VERIFY_LISTED = 25


@dataclass
class Rendered:
    unit: str
    title: str
    markdown: Path
    docx: Path
    xlsx: Path | None = None


# ---------------------------------------------------------------------- helpers
def _walk_strings(value, path=""):
    if isinstance(value, str):
        yield path, value
    elif isinstance(value, dict):
        for k, v in value.items():
            yield from _walk_strings(v, f"{path}.{k}" if path else str(k))
    elif isinstance(value, list):
        for i, v in enumerate(value):
            yield from _walk_strings(v, f"{path}[{i}]")


def labels_in(data) -> dict:
    """Everything marked [VERIFY], and counts of the other labels, in one artifact."""
    verify, counts = [], {"verify": 0, "assumption": 0, "proof": 0}
    for _, text in _walk_strings(data):
        for key, rx in LABEL_RE.items():
            n = len(rx.findall(text))
            counts[key] += n
            if key == "verify" and n:
                verify.append(text if len(text) <= 220 else text[:217] + "...")
    seen = set()
    unique = [v for v in verify if not (v in seen or seen.add(v))]
    return {"counts": counts, "verify": unique}


def cited_in(data) -> list[str]:
    ids = set()
    for path, text in _walk_strings(data):
        ids |= set(CITE_RE.findall(text))
        if path.endswith("source_id") and re.fullmatch(r"S\d+", text):
            ids.add(text)
    return sorted(ids, key=lambda s: int(s[1:]))


def _cell(value) -> str:
    if value is None:
        return ""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _bullets(items, empty="None listed.") -> str:
    items = [i for i in (items or []) if str(i).strip()]
    return "\n".join(f"- {i}" for i in items) if items else empty


def _cites(evidence) -> str:
    return " ".join(f"[{e['source_id']}]" for e in (evidence or [])) or "[VERIFY] no source yet"


class Renderer:
    def __init__(self, launch_dir: Path, force: bool = False):
        self.dir = launch_dir
        self.force = force  # overwrite Markdown files the PMM edited by hand
        self.kept: list[str] = []  # edited files left alone
        self.state = LaunchState.load(launch_dir)
        self.state.refresh()
        self.launch = self.state.data
        self.brand = self._load("brand.yaml") or self._neutral_brand()
        self.sources = {s["id"]: s for s in load_sources(launch_dir)["sources"]}
        self.date = today()
        self.out = launch_dir / "outputs"
        self.industries = {i["id"]: i for i in self.launch["industries"]}
        self.competitors = {c["id"]: c["name"] for c in self.launch["competitors"]}
        for path in sorted((launch_dir / "competitors").glob("*.yaml")):
            doc = load_yaml(path)
            self.competitors.setdefault(doc["id"], doc["name"])
        self.personas: dict[str, dict] = {}
        for path in sorted((launch_dir / "personas").glob("*.yaml")):
            for p in load_yaml(path).get("personas", []):
                self.personas[p["id"]] = p
        self.env = DataFirstEnvironment(loader=FileSystemLoader(str(TEMPLATES_DIR / "docs")),
                               trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True,
                               autoescape=False)
        self.env.filters.update({
            "cell": _cell,
            "bullets": _bullets,
            "cites": _cites,
            "competitor": lambda cid: self.competitors.get(cid, cid),
            "industry": lambda iid: self.industries.get(iid, {}).get("name", iid),
            "persona": lambda pid: self.personas.get(pid, {}).get("role", pid),
            "pain": self._pain,
        })

    def _load(self, rel: str):
        path = self.dir / rel
        return load_yaml(path) if path.exists() else None

    @staticmethod
    def _neutral_brand() -> dict:
        from scripts.brand.theme import NEUTRAL_COLORS, NEUTRAL_FONTS

        return {"colors": NEUTRAL_COLORS, "fonts": NEUTRAL_FONTS, "logo": {"placement": "none"},
                "word_template": None, "unbranded": True}

    def _pain(self, ref: str) -> str:
        pid, _, n = str(ref).partition("#")
        persona = self.personas.get(pid)
        if persona and n.isdigit() and 0 < int(n) <= len(persona["pains"]):
            return f"{persona['role']}: {persona['pains'][int(n) - 1]['text']}"
        return str(ref)

    # ------------------------------------------------------------------ labels
    def status_line(self, unit: str) -> str:
        parts = ["Draft"]
        if self.brand.get("unbranded"):
            parts.append("Unbranded draft")
        rec = self.state.record(unit)
        if rec["status"] == APPROVED and rec.get("reviewed") is False:
            parts.append("Not reviewed by PMM")
        elif rec["status"] == APPROVED:
            parts.append(f"Approved by PMM {rec.get('approved_at', '')[:10]}".strip())
        elif rec["status"] == AWAITING:
            parts.append("Awaiting PMM approval")
        else:
            parts.append(rec["status"].replace("_", " ").capitalize())
        return " · ".join(parts)

    def _wrap(self, unit: str, title: str, subtitle: str, body: str, data) -> str:
        labels = labels_in(data)
        lines = [f"# {title}", "", f"**{self.launch['name']}**{' · ' + subtitle if subtitle else ''}", "",
                 f"_{self.status_line(unit)}_", "", body.strip(), "", "## Before you use this", ""]
        c = labels["counts"]
        lines.append(f"- **[VERIFY]:** {c['verify']} · **[ASSUMPTION]:** {c['assumption']} · "
                     f"**[PROOF NEEDED]:** {c['proof']}")
        if labels["verify"]:
            lines += ["", "Items to verify:", ""]
            lines += [f"- {v}" for v in labels["verify"][:MAX_VERIFY_LISTED]]
            if len(labels["verify"]) > MAX_VERIFY_LISTED:
                lines.append(f"- ...and {len(labels['verify']) - MAX_VERIFY_LISTED} more in the YAML file")
        cited = cited_in(data)
        lines += ["", "## Sources", ""]
        if cited:
            for sid in cited:
                s = self.sources.get(sid)
                if s:
                    date = s.get("published_at") or "undated"
                    lines.append(f"- **[{sid}]** {s['title']}, {s['publisher']} ({date}; retrieved "
                                 f"{s['retrieved_at']}; tier {s['tier']}). {s['url']}")
                else:
                    lines.append(f"- **[{sid}]** [VERIFY] not found in the source register")
        else:
            lines.append("No sources cited.")
        lines += ["", "---", "", f"_{FOOTER.format(date=self.date)}_", ""]
        return "\n".join(lines)

    def _write(self, unit: str, name: str, title: str, subtitle: str, template: str, data, **extra) -> Rendered:
        body = self.env.get_template(template).render(data=data, launch=self.launch, **extra)
        markdown = self._wrap(unit, title, subtitle, body, data)
        md_path = self.out / f"{name}.md"
        docx_path = self.out / f"{name}.docx"
        if not self.force and edits.is_edited(self.out, md_path.name):
            self.kept.append(md_path.name)  # FR-STA-05: never overwrite a hand edit
            return Rendered(unit, title, md_path, docx_path)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(markdown, encoding="utf-8")
        edits.remember(self.out, md_path.name, markdown)
        footer = FOOTER.format(date=self.date)
        writer = DocxWriter(self.brand, self.dir, header_label=self.status_line(unit), footer=footer,
                            render_date=self.date)
        body_md = markdown.rsplit("\n---\n", 1)[0]  # the footer goes in the Word footer instead
        writer.add_markdown(body_md)
        writer.save(docx_path, title)
        return Rendered(unit, title, md_path, docx_path)

    # ------------------------------------------------------------------ assets
    def render_unit(self, unit: str) -> list[Rendered]:
        stage, _, ind = unit.partition(":")
        name = self.industries.get(ind, {}).get("name", ind)
        if stage == "research":
            data = self._load(f"research/industry-{ind}.yaml")
            if not data:
                return []
            i = self.industries.get(ind, {})
            focus = "; ".join(filter(None, [", ".join(i.get("sub_segments", [])), ", ".join(i.get("regions", [])),
                                            i.get("company_size", "")]))
            return [self._write(unit, f"01-industry-brief-{ind}", f"Industry brief: {name}", name,
                                "industry-brief.md.j2", data, focus=focus)]
        if stage == "competitive":
            out = []
            overview = self._load("competitive-overview.yaml")
            if overview:
                diagrams.positioning_map(overview, self.competitors, self.brand,
                                         self.out / "images" / "positioning-map.png")
                out.append(self._write(unit, "02-competitive-overview", "Competitive overview", "",
                                       "competitive-overview.md.j2", overview))
            for path in sorted((self.dir / "competitors").glob("*.yaml")):
                doc = load_yaml(path)
                out.append(self._write(unit, f"02-battlecard-{doc['id']}", f"Battlecard: {doc['name']}", "",
                                       "battlecard.md.j2", doc))
            return out
        if stage == "strategy":
            data = self._load("strategy-check.yaml")
            return [self._write(unit, "03-strategy-check", "Strategy check", "", "strategy-check.md.j2", data)] \
                if data else []
        if stage == "personas":
            data = self._load(f"personas/{ind}.yaml")
            if not data:
                return []
            roles = {p["id"]: p["role"] for p in data["personas"]}
            diagrams.committee_map(data["committee_map"], roles, self.brand,
                                   self.out / "images" / f"committee-{ind}.png")
            return [self._write(unit, f"04-personas-{ind}", f"Personas and buying committee: {name}", name,
                                "personas.md.j2", data, industry_id=ind,
                                personas_by_id={p["id"]: p for p in data["personas"]})]
        if stage == "messaging":
            data = self._load("messaging.yaml")
            if not data:
                return []
            result = self._write(unit, "05-messaging-framework", "Messaging framework", "", "messaging.md.j2", data)
            result.xlsx = write_grid(self.out / "05-messaging-grid.xlsx", data, industries=self.industries,
                                     personas=self.personas, pain_text=self._pain, brand=self.brand,
                                     status_line=self.status_line(unit), footer=FOOTER.format(date=self.date),
                                     render_date=self.date)
            return [result]
        if stage == "demo":
            data = self._load(f"demos/{ind}.yaml")
            return [self._write(unit, f"07-demo-storyline-{ind}", f"Demo storyline: {name}", name,
                                "demo.md.j2", data)] if data else []
        if stage == "web":
            data = self._load(f"web/{ind}.yaml")
            return [self._write(unit, f"08-web-copy-{ind}", f"Webpage copy brief: {name}", name,
                                "web.md.j2", data)] if data else []
        if stage == "playbook":
            data = self._load(f"playbooks/{ind}.yaml")
            return [self._write(unit, f"06-playbook-{ind}", f"Industry playbook: {name}", name,
                                "playbook.md.j2", data)] if data else []
        return []  # QA and the kit index are built by the QA stage

    def render_all(self, only: str | None = None) -> list[Rendered]:
        results = []
        for unit in self.state.units:
            if only and unit != only:
                continue
            if self.state.status(unit) == NOT_STARTED and not only:
                continue
            results.extend(self.render_unit(unit))
        return results
