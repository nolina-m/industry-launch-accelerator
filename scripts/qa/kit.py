"""LAUNCH-KIT.md: the index of the whole kit (FR-QA-08, §8).

Lists every asset with links, status and open items; the top 10 things to verify
before field use; and summaries of the gap report, QA report, source register and
latest what-changed report.
"""

from __future__ import annotations

import re
from pathlib import Path

from scripts.qa.common import LABEL_RE, CheckResult, walk
from scripts.render.render import FOOTER
from scripts.sources import load as load_sources
from scripts.state.launch_state import LaunchState
from scripts.util import load_data, today

STATUS_TEXT = {"not_started": "not started", "in_progress": "in progress", "awaiting_approval": "awaiting approval",
               "approved": "approved", "stale": "stale (needs refresh)"}
# (output name pattern, unit pattern, YAML pattern, asset label, weight for "top 10 to verify")
ASSETS = [
    (r"01-industry-brief-(?P<x>.+)", "research:{x}", "research/industry-{x}.yaml", "Industry brief", 2),
    (r"02-competitive-overview", "competitive", "competitive-overview.yaml", "Competitive overview", 3),
    (r"02-battlecard-(?P<x>.+)", "competitive", "competitors/{x}.yaml", "Battlecard", 4),
    (r"03-strategy-check", "strategy", "strategy-check.yaml", "Strategy check", 1),
    (r"04-personas-(?P<x>.+)", "personas:{x}", "personas/{x}.yaml", "Personas and buying committee", 2),
    (r"05-messaging-framework", "messaging", "messaging.yaml", "Messaging framework", 4),
    (r"06-playbook-(?P<x>.+)", "playbook:{x}", "playbooks/{x}.yaml", "Industry playbook", 3),
    (r"07-demo-storyline-(?P<x>.+)", "demo:{x}", "demos/{x}.yaml", "Demo storyline", 4),
    (r"08-web-copy-(?P<x>.+)", "web:{x}", "web/{x}.yaml", "Webpage copy brief", 5),
]


def _asset_rows(launch_dir: Path, state: LaunchState) -> list[dict]:
    out = launch_dir / "outputs"
    rows = []
    names = {i["id"]: i["name"] for i in state.data["industries"]}
    for md in sorted(out.glob("*.md")) if out.is_dir() else []:
        for pattern, unit_p, yaml_p, label, weight in ASSETS:
            m = re.fullmatch(pattern, md.stem)
            if not m:
                continue
            x = m.groupdict().get("x", "")
            unit, rel = unit_p.format(x=x), yaml_p.format(x=x)
            data = load_data(launch_dir / rel) if (launch_dir / rel).exists() else {}
            counts = {"VERIFY": 0, "PROOF NEEDED": 0, "ASSUMPTION": 0}
            for _, _, _, text in walk(data):
                for lab in LABEL_RE.findall(text):
                    if lab in counts:
                        counts[lab] += 1
            files = [p.name for p in sorted(out.glob(f"{md.stem}.*"))]
            if md.stem == "05-messaging-framework" and (out / "05-messaging-grid.xlsx").exists():
                files.append("05-messaging-grid.xlsx")
            rec = state.record(unit) if unit in state.units else {"status": "not_started"}
            status = STATUS_TEXT[rec["status"]]
            if rec["status"] == "approved" and rec.get("reviewed") is False:
                status = "approved (not reviewed by PMM)"
            subject = names.get(x) or (data.get("name") if isinstance(data, dict) else "") or ""
            rows.append({"label": f"{label}{': ' + subject if subject else ''}", "files": files, "status": status,
                         "counts": counts, "yaml": rel, "data": data, "weight": weight})
    return rows


def top_to_verify(rows: list[dict], limit: int = 10) -> list[tuple[str, str]]:
    """The items most worth verifying before field use: customer-facing and numeric claims first."""
    scored = []
    for row in rows:
        for path, parent, _, text in walk(row["data"]):
            if not LABEL_RE.sub("", text).strip() and isinstance(parent, dict):
                # A bare label (e.g. a keyword's "[VERIFY]"): show what it's attached to.
                context = next((parent[k] for k in ("term", "item", "text", "title", "headline", "name")
                                if isinstance(parent.get(k), str) and parent[k] != text), None)
                text = f"{context} {text}" if context else text
            for kind, bonus in (("[VERIFY]", 3), ("[PROOF NEEDED]", 1)):
                if kind not in text:
                    continue
                score = row["weight"] + bonus
                if re.search(r"\d", LABEL_RE.sub("", text)):
                    score += 3
                if re.search(r"pric|competitor|regulat|legal|law", text, re.I):
                    score += 2
                snippet = text if len(text) <= 180 else text[:177] + "..."
                scored.append((score, row["label"], snippet, path))
    scored.sort(key=lambda s: (-s[0], s[1], s[3]))
    seen, out = set(), []
    for _, label, snippet, _ in scored:
        if snippet in seen:
            continue
        seen.add(snippet)
        out.append((label, snippet))
        if len(out) == limit:
            break
    return out


def write_kit(launch_dir: Path, results: list[CheckResult] | None = None) -> Path:
    state = LaunchState.load(launch_dir)
    state.refresh()
    launch = state.data
    rows = _asset_rows(launch_dir, state)
    approved = sum(state.status(u) == "approved" for u in state.units)
    lines = [
        f"# Launch kit: {launch['name']}",
        "",
        f"_Draft · generated {today()} by Industry Launch Accelerator"
        f"{' · auto mode: not reviewed by PMM' if launch['options'].get('auto_mode') else ''}_",
        "",
        f"- **Industries:** {', '.join(i['name'] for i in launch['industries']) or 'none yet'}",
        f"- **Competitors:** {', '.join(c['name'] for c in launch['competitors']) or 'none yet'}",
        f"- **Stages approved:** {approved} of {len(state.units)}",
        "",
        "## Assets",
        "",
        "| Asset | Files | Status | To verify | Proof needed | Assumptions |",
        "|---|---|---|---|---|---|",
    ]
    for r in rows:
        links = " · ".join(f"[{f.rsplit('.', 1)[1].upper()}](outputs/{f})" for f in r["files"])
        c = r["counts"]
        lines.append(f"| {r['label']} | {links} | {r['status']} | {c['VERIFY']} | {c['PROOF NEEDED']} | "
                     f"{c['ASSUMPTION']} |")
    if not rows:
        lines.append("| No assets rendered yet | | | | | |")

    lines += ["", "## Top 10 things to verify before field use", ""]
    top = top_to_verify(rows)
    lines += [f"{i}. **{label}:** {text}" for i, (label, text) in enumerate(top, start=1)] or ["Nothing flagged."]

    # Gap report summary
    lines += ["", "## Gap report", ""]
    ctx_path = launch_dir / "launch-context.yaml"
    if ctx_path.exists():
        gaps = load_data(ctx_path).get("gaps", [])
        blocking = sum(g["severity"] == "blocking" and g["status"] == "open" for g in gaps)
        waived = sum(g["status"] == "waived" for g in gaps)
        assumed = sum(g["status"] == "assumed" for g in gaps)
        lines.append(f"{blocking} blocking gap(s) open, {waived} waived, {assumed} assumption(s). "
                     "Full report: [gap-report.md](gap-report.md)")
    else:
        lines.append("Intake hasn't run yet.")

    # QA summary
    lines += ["", "## QA report", ""]
    if results is not None:
        errors = sum(r.errors for r in results)
        warnings = sum(r.warnings for r in results)
        for r in results:
            lines.append(f"- {r.check} {r.title}: {r.status} ({r.errors} errors, {r.warnings} warnings)")
        lines += ["", f"{errors} error(s), {warnings} warning(s) in total. Full report: [qa-report.md](qa-report.md)"]
    else:
        lines.append("QA hasn't run yet.")

    # Source register
    sources = load_sources(launch_dir)["sources"]
    lines += ["", "## Source register", ""]
    if sources:
        tiers = {t: sum(s["tier"] == t for s in sources) for t in (1, 2, 3)}
        lines += [f"{len(sources)} source(s): {tiers[1]} Tier 1, {tiers[2]} Tier 2, {tiers[3]} Tier 3. "
                  "Register: `research/sources.json`", "",
                  "| ID | Source | Publisher | Published | Tier |", "|---|---|---|---|---|"]
        for s in sources:
            title = s["title"].replace("|", "\\|")
            lines.append(f"| {s['id']} | [{title}]({s['url']}) | {s['publisher']} | "
                         f"{s.get('published_at') or 'undated'} | {s['tier']} |")
    else:
        lines.append("No sources registered yet.")

    # Latest refresh
    lines += ["", "## Latest what-changed report", ""]
    reports = sorted((launch_dir / "refresh").glob("*/what-changed.md")) if (launch_dir / "refresh").is_dir() else []
    if reports:
        latest = reports[-1].relative_to(launch_dir).as_posix()
        lines.append(f"[{latest}]({latest})")
    else:
        lines.append("No refresh run yet. Ask the agent to \"refresh the launch\" at any time.")

    lines += ["", "---", "", f"_{FOOTER.format(date=today())}_", ""]
    path = launch_dir / "LAUNCH-KIT.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path
