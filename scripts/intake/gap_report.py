"""Stage 0, last step: work out the gaps and write gap-report.md (FR-INT-03..06, FR-INT-08, FR-INP-11).

Usage:
    python scripts/intake/gap_report.py <slug>

Reads launch-context.yaml (and brand.yaml), then:
- Required brief fields that are missing or too thin, a missing launch POV, or no
  target industries -> BLOCKING gaps. Research can't start until each is answered
  or the PMM explicitly waives it.
- Recommended fields that are missing -> non-blocking: the run continues and the
  related content is labeled [ASSUMPTION].
- Conflicts the agent recorded between files -> contradictions to resolve.
- At most 7 questions per round, most important first.

Gaps the agent added itself (any id not generated here) are kept as they are.
The agent may also rewrite a generated question to make it more specific; the
new wording is kept on later runs.

Exit code is 1 while blocking gaps are still open, so the agent can check it.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.intake.fields import FIELDS
from scripts.util import LAUNCHES_DIR, dump_yaml, load_yaml, today
from scripts.validate import validate_data

MAX_QUESTIONS = 7
OK_STATUSES = ("provided", "answered", "assumed")
RESOLVED = ("answered", "waived")
GENERATED_PREFIXES = ("G-field-", "G-launch-pov", "G-industries", "G-brand", "G-conflict-")


def _gap_id_for(field) -> str:
    return f"G-field-{field.section}-{field.key}".replace("_", "-")


def compute_gaps(context: dict, brand: dict | None) -> list[dict]:
    """The full, merged gap list (generated gaps + the agent's own)."""
    existing = {g["id"]: g for g in context.get("gaps", [])}
    gaps: list[dict] = []

    def add(gap: dict) -> None:
        old = existing.get(gap["id"])
        if old:
            if old.get("question"):
                gap["question"] = old["question"]
            if old.get("assumption"):
                gap["assumption"] = old["assumption"]
            if old.get("status") in RESOLVED:
                gap["status"] = old["status"]
        gaps.append(gap)

    # The launch POV and industries come first: nothing works without them.
    if not context.get("launch_pov", {}).get("text", "").strip():
        add({
            "id": "G-launch-pov", "field": "launch_pov", "severity": "blocking", "status": "open",
            "question": "Please write your launch POV in inputs/launch-pov.md: which industries and why, "
                        "priority buyers, the competitors that matter most, the story you believe will win, "
                        "and claims to avoid. A few sentences is enough.",
        })
    if not context.get("industries"):
        add({
            "id": "G-industries", "field": "industries", "severity": "blocking", "status": "open",
            "question": "Which industries should this launch target? For each, add any sub-segment, "
                        "region or company size you want to focus on.",
        })

    brief = context.get("product_brief", {})
    is_ai = bool(context.get("is_ai_product"))
    for field in FIELDS:
        if field.section == "free_form" or (field.ai_only and not is_ai):
            continue
        entry = brief.get(field.section, {}).get(field.key, {"status": "missing"})
        status = entry.get("status", "missing")
        if status in OK_STATUSES:
            old = existing.get(_gap_id_for(field))
            if old and old.get("status") in RESOLVED:
                gaps.append(old)  # keep the record of what was answered
            continue
        thin = status == "thin"
        if field.required:
            question = field.question
            if thin:
                question = f"{field.label} is a bit thin to work from. {question}"
            add({"id": _gap_id_for(field), "field": field.path, "severity": "blocking",
                 "status": "open", "question": question})
        else:
            add({"id": _gap_id_for(field), "field": field.path, "severity": "non_blocking",
                 "status": "assumed", "question": field.question,
                 "assumption": f"No {field.label.lower()} given: related content will be marked [ASSUMPTION]."})

    if brand is None or brand.get("unbranded"):
        add({"id": "G-brand", "field": "brand", "severity": "non_blocking", "status": "assumed",
             "question": "Do you have brand guidelines, a Word template or logo files you can add to inputs/brand/?",
             "assumption": "No brand guidelines: documents use the neutral theme and are labeled 'Unbranded draft'."})

    for n, conflict in enumerate(context.get("conflicts", []), start=1):
        if conflict.get("resolution"):
            continue
        values = "; ".join(f"\"{v['value']}\" ({v['source_file']})" for v in conflict.get("values", []))
        add({"id": f"G-conflict-{n}", "field": conflict["field"], "severity": "blocking", "status": "open",
             "question": f"Your inputs disagree on {conflict['field']}: {values}. Which one is right?"})

    generated = {g["id"] for g in gaps}
    for gap_id, gap in existing.items():
        if gap_id not in generated and not gap_id.startswith(GENERATED_PREFIXES):
            gaps.append(gap)  # added by the agent
    return gaps


BRIEF_EMPTY_QUESTION = {
    "id": "G-brief-empty", "field": "product_brief", "severity": "blocking", "status": "open",
    "question": "The product brief is empty. Please fill in inputs/product-brief.md (at least the sections "
                "marked required), or point me to a PRD or one-pager to start from.",
}


def questions_this_round(gaps: list[dict]) -> list[dict]:
    """Up to 7 questions: open blocking gaps first, then assumptions worth confirming.

    If no required brief field has been answered at all, one request to fill in the
    brief replaces the individual field questions.
    """
    blocking = [g for g in gaps if g["severity"] == "blocking" and g["status"] == "open" and g.get("question")]
    required_ids = {_gap_id_for(f) for f in FIELDS if f.required}
    open_required = [g for g in blocking if g["id"] in required_ids]
    if len(open_required) == len(required_ids):
        blocking = [g for g in blocking if g["id"] not in required_ids]
        first = ("G-launch-pov", "G-industries")
        position = next((i for i, g in enumerate(blocking) if not g["id"].startswith(first)), len(blocking))
        blocking.insert(position, BRIEF_EMPTY_QUESTION)
    optional = [g for g in gaps if g["severity"] == "non_blocking" and g["status"] in ("open", "assumed")
                and g.get("question")]
    return (blocking + optional)[:MAX_QUESTIONS]


def open_blocking(gaps: list[dict]) -> list[dict]:
    return [g for g in gaps if g["severity"] == "blocking" and g["status"] == "open"]


def render(context: dict, gaps: list[dict], launch_name: str, manifest: dict | None) -> str:
    blocking = [g for g in gaps if g["severity"] == "blocking"]
    assumptions = [g for g in gaps if g["severity"] == "non_blocking" and g["status"] == "assumed"]
    contradictions = [g for g in gaps if g["id"].startswith("G-conflict-")]
    still_open = open_blocking(gaps)
    lines = [
        f"# Gap report: {launch_name}",
        "",
        f"_Generated {today()} by Industry Launch Accelerator. Draft: verify before relying on it._",
        "",
        f"- **Blocking gaps still open:** {len(still_open)}"
        + (" (research can't start until these are answered or waived)" if still_open else ""),
        f"- **Assumptions (non-blocking):** {len(assumptions)}",
        f"- **Contradictions to resolve:** {len([g for g in contradictions if g['status'] == 'open'])}",
        "",
        "## Questions for you this round",
        "",
    ]
    questions = questions_this_round(gaps)
    if questions:
        for i, g in enumerate(questions, start=1):
            tag = "blocking" if g["severity"] == "blocking" else "optional"
            lines.append(f"{i}. {g['question']} _({tag}: {g['field']})_")
    else:
        lines.append("No questions. Intake has everything it needs.")

    lines += ["", "## Blocking gaps", ""]
    if blocking:
        lines += ["| ID | What | Status |", "|---|---|---|"]
        lines += [f"| {g['id']} | {g['field']} | {g['status']} |" for g in blocking]
    else:
        lines.append("None.")

    lines += ["", "## Assumptions (the run continues; related content is labeled [ASSUMPTION])", ""]
    if assumptions:
        lines += [f"- **{g['field']}**: {g.get('assumption', '')}" for g in assumptions]
    else:
        lines.append("None.")

    lines += ["", "## Contradictions", ""]
    conflicts = context.get("conflicts", [])
    if conflicts:
        for c in conflicts:
            values = "; ".join(f"\"{v['value']}\" in {v['source_file']}" for v in c.get("values", []))
            resolved = f" Resolved: {c['resolution']}" if c.get("resolution") else " Open."
            lines.append(f"- **{c['field']}**: {values}.{resolved}")
        lines.append("")
        lines.append("Where the product brief template disagrees with another file, the template wins.")
    else:
        lines.append("None found.")

    if manifest:
        lines += ["", "## Files read", "", "| File | Result |", "|---|---|"]
        for f in manifest.get("files", []):
            note = f" ({f['note']})" if f.get("note") else ""
            lines.append(f"| {f['file']} | {f['status']}{note} |")
    lines.append("")
    return "\n".join(lines)


def run(launch_dir: Path) -> tuple[list[dict], str]:
    context_path = launch_dir / "launch-context.yaml"
    context = load_yaml(context_path)
    brand_path = launch_dir / "brand.yaml"
    brand = load_yaml(brand_path) if brand_path.exists() else None
    gaps = compute_gaps(context, brand)
    context["gaps"] = gaps
    problems = validate_data(context, "launch-context.schema.json", "launch-context.yaml")
    if problems:
        raise ValueError("launch-context.yaml has problems:\n" + "\n".join(f"  - {p}" for p in problems))
    dump_yaml(context, context_path)
    launch = load_yaml(launch_dir / "launch.yaml") if (launch_dir / "launch.yaml").exists() else {}
    manifest_path = launch_dir / "intake" / "manifest.yaml"
    manifest = load_yaml(manifest_path) if manifest_path.exists() else None
    report = render(context, gaps, launch.get("name", launch_dir.name), manifest)
    (launch_dir / "gap-report.md").write_text(report, encoding="utf-8")
    return gaps, report


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__)
        return 2
    launch_dir = LAUNCHES_DIR / argv[0]
    if not (launch_dir / "launch-context.yaml").exists():
        print("[X] launch-context.yaml not found. Run scripts/intake/run_intake.py first.")
        return 1
    try:
        gaps, _ = run(launch_dir)
    except ValueError as exc:
        print(f"[X] {exc}")
        return 1
    still_open = open_blocking(gaps)
    print(f"[OK] Wrote gap-report.md: {len(still_open)} blocking gap(s) open, "
          f"{len([g for g in gaps if g['status'] == 'assumed'])} assumption(s)")
    for i, g in enumerate(questions_this_round(gaps), start=1):
        print(f"  {i}. {g['question']}")
    return 1 if still_open else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
