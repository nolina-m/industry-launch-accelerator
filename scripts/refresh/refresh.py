"""On-demand refresh: pull fresh data and report what changed (FR-REF-01..04).

Usage:
    python scripts/launch.py refresh <slug> [--no-links]

What it re-checks with the data connectors (the agent adds web search on top,
see instructions/11-refresh.md):
- each competitor: recent news (GDELT, Hacker News, Currents if keyed) and new
  SEC filings (if ILA_CONTACT_EMAIL is set);
- each industry: new or proposed rules for the regulations in its brief
  (Federal Register, EUR-Lex, Regulations.gov if keyed);
- every market data point that came from a connector: is there a newer value?
- every source in the register: does the link still answer, and is it older
  than 24 months?

Results are compared with the previous refresh (or, the first time, with the
research date) and written to refresh/<date>/: what-changed.md for the PMM,
changes.yaml for the agent, snapshot.json for the next comparison.

It never edits an approved asset (FR-REF-04): updates go through the normal
checkpoints, asset by asset.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from connectors import registry
from scripts.qa.common import artifacts
from scripts.sources import load as load_sources
from scripts.sources import months_between
from scripts.state.launch_state import LaunchState
from scripts.state.pipeline import downstream_of
from scripts.util import dump_yaml, today

GENERIC_COMPETITORS = {"status-quo", "build-in-house"}
MARKET_CONNECTORS = {"bls", "fred", "worldbank"}  # fetch(series_id) returns the latest observations


@dataclass
class Query:
    key: str  # stable id, used to compare runs
    category: str  # competitor news | competitor filings | regulation | market data
    connector: str
    method: str
    args: list
    kwargs: dict
    about: str  # competitor or industry name, or the market data id
    unit: str  # pipeline unit whose asset it affects
    file: str  # YAML file it affects
    section: str


@dataclass
class ChangeItem:
    category: str
    title: str
    url: str
    published: str | None
    source: str
    about: str
    assets: list[str]
    also_review: list[str]
    section: str
    action: str
    detail: str = ""


@dataclass
class RefreshResult:
    folder: Path
    changes: list[ChangeItem] = field(default_factory=list)
    checked: list[str] = field(default_factory=list)
    unavailable: list[str] = field(default_factory=list)
    baseline: str = ""


ACTIONS = {
    "competitor news": "Read it. If it's a launch, pricing or packaging change, funding, acquisition, leadership "
                       "change or notable hiring, add it to Recent moves in the battlecard and check positioning, "
                       "pricing and objections.",
    "competitor filings": "Check the filing for strategy, pricing or risk-factor changes; update the battlecard if "
                          "they matter for deals.",
    "regulation": "Check whether it applies to the product and its regions. If so, update the regulatory section of "
                  "the industry brief, then objections and talk tracks that mention it.",
    "market data": "Update this data point in the industry brief with the new figure, period and retrieval date.",
    "source offline": "Find where the page moved, or a replacement source, and update the citation.",
    "source old": "Find a more recent source for the trend claims that cite it (trend evidence prefers the last "
                  "24 months).",
}


def _unit_label(state: LaunchState, unit: str) -> str:
    try:
        return state.asset_label(unit)
    except Exception:
        return unit


def build_plan(launch_dir: Path, state: LaunchState) -> list[Query]:
    plan: list[Query] = []
    data = artifacts(launch_dir)
    for c in state.data["competitors"]:
        if c["id"] in GENERIC_COMPETITORS or (data.get(f"competitors/{c['id']}.yaml") or {}).get("category") in (
                "status-quo", "build-in-house"):
            continue
        rel, name = f"competitors/{c['id']}.yaml", c["name"]
        for connector, method, args, kwargs, category in (
                ("gdelt", "search", [f'"{name}"'], {"limit": 25}, "competitor news"),
                ("hackernews", "search", [name], {"limit": 20}, "competitor news"),
                ("currents", "search", [name], {"limit": 20}, "competitor news"),
                ("sec-edgar", "search", [f'"{name}"'], {"forms": "8-K,10-K,10-Q", "limit": 20}, "competitor filings")):
            plan.append(Query(f"{category}:{c['id']}:{connector}", category, connector, method, args, kwargs, name,
                              "competitive", rel, "Recent moves"))
    for ind in state.data["industries"]:
        rel = f"research/industry-{ind['id']}.yaml"
        research = data.get(rel) or {}
        names = []
        for item in research.get("regulatory", {}).get("items", []):
            short = re.split(r"\s*\(", item["name"])[0].strip()
            if short and short not in names:
                names.append(short)
        for name in names[:6]:
            for connector in ("federal-register", "eurlex", "regulations-gov"):
                plan.append(Query(f"regulation:{ind['id']}:{connector}:{name}", "regulation", connector, "search",
                                  [name], {"limit": 10}, ind["name"], f"research:{ind['id']}", rel,
                                  "Regulatory and compliance landscape"))
        for md in research.get("market_data", []):
            if md.get("connector") in MARKET_CONNECTORS and md.get("series_id"):
                plan.append(Query(f"market:{ind['id']}:{md['id']}", "market data", md["connector"], "fetch",
                                  [md["series_id"]], {"limit": 1}, md["id"], f"research:{ind['id']}", rel,
                                  "Market data"))
    return plan


def _previous(launch_dir: Path, current: str) -> tuple[str | None, dict]:
    root = launch_dir / "refresh"
    earlier = sorted(p for p in root.glob("*/snapshot.json") if p.parent.name != current) if root.is_dir() else []
    if not earlier:
        return None, {}
    latest = earlier[-1]
    return latest.parent.name[:10], json.loads(latest.read_text(encoding="utf-8"))


def _baseline(state: LaunchState, data: dict, query: Query, previous_date: str | None) -> str:
    if previous_date:
        return previous_date
    doc = data.get(query.file) or {}
    return doc.get("researched_at") or (state.record(query.unit).get("approved_at") or "")[:10] or "1900-01-01"


def _folder(launch_dir: Path, day: str) -> Path:
    folder = launch_dir / "refresh" / day
    n = 2
    while folder.exists():
        folder = launch_dir / "refresh" / f"{day}-{n}"
        n += 1
    folder.mkdir(parents=True)
    return folder


def refresh(launch_dir: Path, env: dict, transport=None, link_checker=None, sleep=None,
            day: str | None = None) -> RefreshResult:
    state = LaunchState.load(launch_dir)
    state.refresh()
    data = artifacts(launch_dir)
    day = day or today()
    folder = _folder(launch_dir, day)
    previous_date, previous = _previous(launch_dir, folder.name)
    result = RefreshResult(folder, baseline=previous_date or "the original research")
    snapshot: dict[str, list[dict]] = {}

    def downstream(unit: str) -> list[str]:
        return [_unit_label(state, u) for u in downstream_of(state.units, unit)
                if u in state.units and u not in ("qa",)][:6]

    for q in build_plan(launch_dir, state):
        kwargs = {"cache_dir": launch_dir / "research" / "cache", "env": env, "use_cache": False}
        if transport:
            kwargs["transport"] = transport
        if sleep:
            kwargs["sleep"] = sleep
        c = registry.get(q.connector, **kwargs)
        if not c.available()[0]:
            label = f"{c.name} ({c.available()[1]})"
            if label not in result.unavailable:
                result.unavailable.append(label)
            continue
        records = getattr(c, q.method)(*q.args, **q.kwargs)
        if c.last_error:
            result.unavailable.append(f"{c.name} for {q.about}: {c.last_error}")
            continue
        result.checked.append(f"{c.name}: {q.category} for {q.about}")
        snapshot[q.key] = [r.to_dict() for r in records]
        asset = _unit_label(state, q.unit)
        if q.category == "market data":
            md = next((m for m in (data.get(q.file) or {}).get("market_data", []) if m["id"] == q.about), None)
            latest = next((r for r in records if r.value is not None), None)
            if md and latest and _num(latest.value) != _num(md["value"]):
                period = f" ({latest.period})" if latest.period else ""
                result.changes.append(ChangeItem(
                    q.category, f"{q.about}: new value {latest.value}{period}",
                    latest.url, latest.retrieved_at[:10], c.name, q.about, [asset], downstream(q.unit), q.section,
                    ACTIONS["market data"], f"The brief cites {md['value']} (retrieved {md['retrieved_at']})."))
            continue
        seen = {r["id"] for r in previous.get(q.key, [])}
        since = _baseline(state, data, q, previous_date)
        for r in records:
            if r.id in seen or not r.published_at or r.published_at[:10] <= since:
                continue
            result.changes.append(ChangeItem(q.category, r.title, r.url, r.published_at[:10], c.name, q.about,
                                             [asset], downstream(q.unit), q.section, ACTIONS[q.category]))

    # Source health (FR-REF-02).
    register = load_sources(launch_dir)["sources"]
    citing = _citing_assets(state, data)
    for s in register:
        assets = citing.get(s["id"], [])
        if link_checker:
            status = link_checker(s["url"])
            if status is None or status in (404, 410) or status >= 500:
                result.changes.append(ChangeItem(
                    "source health", f"{s['id']} no longer answers ({status or 'no response'}): {s['title']}",
                    s["url"], None, s["publisher"], s["id"], assets, [], "Sources", ACTIONS["source offline"]))
        if s.get("published_at") and months_between(s["published_at"], day) > 24:
            result.changes.append(ChangeItem(
                "source health", f"{s['id']} is older than 24 months ({s['published_at']}): {s['title']}",
                s["url"], s["published_at"], s["publisher"], s["id"], assets, [], "Sources", ACTIONS["source old"]))

    _dedupe(result)
    (folder / "snapshot.json").write_text(json.dumps(snapshot, indent=1, ensure_ascii=False), encoding="utf-8")
    dump_yaml({"date": day, "baseline": result.baseline, "changes": [asdict(c) for c in result.changes],
               "unavailable": result.unavailable}, folder / "changes.yaml")
    (folder / "what-changed.md").write_text(render(state, result, day), encoding="utf-8")
    return result


def _num(v):
    try:
        return round(float(str(v).replace(",", "")), 6)
    except (TypeError, ValueError):
        return v


def _citing_assets(state: LaunchState, data: dict) -> dict[str, list[str]]:
    """{source id: [asset labels that cite it]}"""
    file_to_unit = {}
    for name, unit in state.units.items():
        for pattern in unit.outputs:
            file_to_unit[pattern] = name
    out: dict[str, set[str]] = {}
    for rel, doc in data.items():
        unit = file_to_unit.get(rel) or ("competitive" if rel.startswith("competitors/") else None)
        text = json.dumps(doc, default=str)
        for sid in {a or b for a, b in re.findall(r'\[(S\d+)\]|"source_id": "(S\d+)"', text)}:
            if unit:
                out.setdefault(sid, set()).add(_unit_label(state, unit))
    return {k: sorted(v) for k, v in out.items()}


def _dedupe(result: RefreshResult) -> None:
    seen, unique = set(), []
    for c in result.changes:
        key = (c.category, c.url, c.about, c.title)
        if key not in seen:
            seen.add(key)
            unique.append(c)
    result.changes = unique


def render(state: LaunchState, result: RefreshResult, day: str) -> str:
    order = ["competitor news", "competitor filings", "regulation", "market data", "source health"]
    titles = {"competitor news": "Competitor news", "competitor filings": "Competitor filings",
              "regulation": "Regulation", "market data": "Market data", "source health": "Source health"}
    lines = [f"# What changed: {state.data['name']} ({day})", "",
             f"_Compared with {result.baseline}. Generated by Industry Launch Accelerator. Nothing in the kit has "
             "been changed: each update goes through its normal checkpoint._", ""]
    counts = {k: sum(c.category == k for c in result.changes) for k in order}
    lines.append(f"**{len(result.changes)} change(s) found:** " +
                 ", ".join(f"{titles[k].lower()} {n}" for k, n in counts.items() if n) if result.changes
                 else "**No changes found by the data connectors.**")
    lines += ["", "The agent also checks with web search (competitor launches, pricing pages, funding, acquisitions, "
              "leadership changes, hiring) and adds what it finds below.", ""]
    for cat in order:
        items = [c for c in result.changes if c.category == cat]
        if not items:
            continue
        lines += [f"## {titles[cat]}", ""]
        for c in items:
            lines.append(f"### {c.title}")
            lines.append("")
            lines.append(f"- **Source:** {c.source}{', ' + c.published if c.published else ''}: {c.url}")
            if c.detail:
                lines.append(f"- **Detail:** {c.detail}")
            if c.assets:
                lines.append(f"- **Affects:** {', '.join(c.assets)} ({c.section})")
            if c.also_review:
                lines.append(f"- **May also affect:** {', '.join(c.also_review)}")
            lines.append(f"- **Suggested action:** {c.action}")
            lines.append("")
    lines += ["## What was checked", ""]
    lines += [f"- {x}" for x in result.checked] or ["- Nothing could be checked with the data connectors."]
    if result.unavailable:
        lines += ["", "## Not checked (source unavailable; covered by web search instead)", ""]
        lines += [f"- {x}" for x in result.unavailable]
    lines.append("")
    return "\n".join(lines)


def main_summary(result: RefreshResult) -> str:
    rel = result.folder.name
    return (f"{len(result.changes)} change(s) found; compared with {result.baseline}. "
            f"Report: refresh/{rel}/what-changed.md")

