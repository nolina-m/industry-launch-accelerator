"""Stage 0, step 1: read every input and draft launch-context.yaml (FR-INT-01, FR-INT-02, FR-INP-03).

Usage:
    python scripts/intake/run_intake.py <slug>

What it does:
1. Extracts the text of every file in inputs/ (to intake/extracted/).
2. Reads the product brief template and records each field with its source file
   and a status: provided, thin (too short to use) or missing.
3. Reads the launch POV.
4. Lists brand files and optional inputs.

It is safe to run again. Values from the product brief template always win
(FR-INP-03). Values the agent filled in from other files or from the PMM's
answers are kept when the template is still empty for that field.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.extract.extract import IGNORED_NAMES, extract_launch
from scripts.intake import markdown_template as md
from scripts.intake.fields import FIELDS, SECTIONS, Field
from scripts.util import LAUNCHES_DIR, dump_yaml, load_yaml
from scripts.validate import validate_data

BRIEF = "inputs/product-brief.md"
POV = "inputs/launch-pov.md"
QUESTIONNAIRE = "inputs/brand-questionnaire.md"
OPTIONAL_TYPES = {
    "existing_messaging", "win_loss", "call_transcript", "case_study", "customer_metrics",
    "pricing_packaging", "analyst_report", "competitors",
}
TEMPLATE_KEYS = {md.heading_key(f.label): f for f in FIELDS}


def assess(field: Field, raw: str) -> dict:
    """Turn the text under one template heading into a launch-context field."""
    if md.is_empty(raw):
        return {"value": None, "source_file": None, "status": "missing"}
    if field.kind == "list":
        items = md.bullets(raw)
        status = "thin" if len(items) < field.min_items else "provided"
        return {"value": items, "source_file": BRIEF, "status": status}
    text = md.clean(raw)
    if field.kind == "choice":
        found = [c for c in field.choices if c in text.lower()]
        if len(found) == 1:
            return {"value": found[0], "source_file": BRIEF, "status": "provided"}
        return {"value": text, "source_file": BRIEF, "status": "thin"}
    status = "thin" if len(text.split()) < field.min_words else "provided"
    return {"value": text, "source_file": BRIEF, "status": status}


def read_brief(launch_dir: Path) -> dict[str, dict[str, str]]:
    """{section: {field_key: raw text}} from the product brief template."""
    path = launch_dir / BRIEF
    if not path.exists():
        return {}
    parsed = md.parse(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, str]] = {}
    for section in parsed.values():
        for heading, text in section["fields"].items():
            field = TEMPLATE_KEYS.get(heading)
            if field:
                out.setdefault(field.section, {})[field.key] = text
    anything_else = parsed.get("anything_else_we_should_know", {}).get("text", "")
    out.setdefault("free_form", {})["anything_else"] = anything_else
    return out


def merge_field(field: Field, raw: str | None, existing: dict | None) -> dict:
    new = assess(field, raw or "")
    if new["status"] != "missing":
        return new  # the template wins
    if existing and existing.get("source_file") not in (None, BRIEF) and not md.is_empty(existing.get("value")):
        return existing  # filled by the agent from another file or the PMM's answer
    return new


def read_pov(launch_dir: Path) -> tuple[str, list[str]]:
    """(POV text, industry lines listed under 'Target industries')."""
    path = launch_dir / POV
    if not path.exists():
        return "", []
    raw = path.read_text(encoding="utf-8")
    if not md.has_content(raw):
        return "", []
    lines = [line for line in md.clean(raw).splitlines() if not line.startswith("# ")]
    text = "\n".join(lines).strip()
    industries = md.bullets(md.parse(raw).get("target_industries", {}).get("text", ""))
    return text, industries


def list_files(folder: Path, launch_dir: Path) -> list[str]:
    if not folder.is_dir():
        return []
    return sorted(
        p.relative_to(launch_dir).as_posix()
        for p in folder.rglob("*")
        if p.is_file() and p.name not in IGNORED_NAMES
    )


def optional_inputs(launch_dir: Path, existing: list[dict]) -> list[dict]:
    known = {e["path"]: e for e in existing}
    result = []
    for rel in list_files(launch_dir / "inputs" / "optional", launch_dir):
        if rel in known:
            result.append(known[rel])
            continue
        parts = rel.split("/")
        folder = parts[2] if len(parts) > 3 else ""
        kind = folder.replace("-", "_") if folder.replace("-", "_") in OPTIONAL_TYPES else "other"
        result.append({"path": rel, "type": kind, "permission": "unknown"})
    return result


def build_context(launch_dir: Path) -> tuple[dict, list[str]]:
    """Return (launch-context data, industry lines from the POV)."""
    path = launch_dir / "launch-context.yaml"
    existing = load_yaml(path) if path.exists() else {}
    old_brief = existing.get("product_brief", {})
    brief_raw = read_brief(launch_dir)

    product_brief: dict[str, dict] = {s: {} for s in SECTIONS}
    for field in FIELDS:
        raw = brief_raw.get(field.section, {}).get(field.key)
        old = old_brief.get(field.section, {}).get(field.key)
        product_brief[field.section][field.key] = merge_field(field, raw, old)

    pov_text, pov_industries = read_pov(launch_dir)
    brand_inputs = list_files(launch_dir / "inputs" / "brand", launch_dir)
    q = launch_dir / QUESTIONNAIRE
    if q.exists() and md.has_content(q.read_text(encoding="utf-8")):
        brand_inputs.insert(0, QUESTIONNAIRE)

    context = {
        "product_brief": product_brief,
        "is_ai_product": bool(existing.get("is_ai_product")) or _looks_like_ai(product_brief),
        "launch_pov": {"text": pov_text, "source_file": POV},
        "industries": existing.get("industries", []),
        "brand_inputs": brand_inputs,
        "optional_inputs": optional_inputs(launch_dir, existing.get("optional_inputs", [])),
        "conflicts": existing.get("conflicts", []),
        "gaps": existing.get("gaps", []),
    }
    return context, pov_industries


def _looks_like_ai(product_brief: dict) -> bool:
    """First guess only; the agent confirms. True if the AI section or the solution mentions AI."""
    if any(f["status"] != "missing" for f in product_brief["ai_specifics"].values()):
        return True
    words = " ".join(
        str(f.get("value") or "") for f in product_brief["solution"].values()
    ).lower().replace(",", " ").replace(".", " ").split()
    return any(w in ("ai", "agentic", "llm", "llms", "genai", "ai-powered", "ai-native", "ai-driven") for w in words)


def run(launch_dir: Path) -> tuple[dict, list[str], list]:
    extracted = extract_launch(launch_dir)
    context, pov_industries = build_context(launch_dir)
    problems = validate_data(context, "launch-context.schema.json", "launch-context.yaml")
    if problems:
        raise RuntimeError("Internal error building launch-context.yaml: " + "; ".join(map(str, problems)))
    dump_yaml(context, launch_dir / "launch-context.yaml")
    return context, pov_industries, extracted


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    launch_dir = LAUNCHES_DIR / argv[0]
    if not (launch_dir / "launch.yaml").exists():
        print(f"[X] No launch called '{argv[0]}'. Start one with: launch.py new {argv[0]}")
        return 1
    context, pov_industries, extracted = run(launch_dir)

    print(f"[OK] Read {len(extracted)} input file(s); text saved in intake/extracted/")
    for r in extracted:
        if r.status != "ok":
            print(f"  [!] {r.path.relative_to(launch_dir).as_posix()}: {r.note}")
    counts: dict[str, list[str]] = {"provided": [], "thin": [], "missing": []}
    for field in FIELDS:
        if field.required:
            status = context["product_brief"][field.section][field.key]["status"]
            counts.setdefault(status, []).append(field.label)
    print(f"Required brief fields: {len(counts['provided'])} provided, "
          f"{len(counts['thin'])} too thin, {len(counts['missing'])} missing")
    for status in ("thin", "missing"):
        if counts[status]:
            print(f"  {status}: {', '.join(counts[status])}")
    print("Launch POV: " + ("found" if context["launch_pov"]["text"] else "MISSING (blocking)"))
    if pov_industries:
        print("Industries listed in the POV: " + "; ".join(pov_industries))
    print(f"AI product (first guess): {'yes' if context['is_ai_product'] else 'no'}")
    print("[OK] Wrote launch-context.yaml")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
