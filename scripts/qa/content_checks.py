"""QA checks on the YAML content (FR-QA-01, -02, -03, -06, -07, FR-OUT-03).

Each check takes the launch folder and returns a CheckResult. Heuristic checks are
deliberately simple and explain what they flagged, so the agent and the PMM can
judge each item.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

from scripts.qa.common import ERROR, LABEL_RE, WARNING, CheckResult, Finding, artifacts, sentences, walk
from scripts.sources import load as load_sources
from scripts.sources import months_between
from scripts.util import load_yaml, today
from scripts.validate import validate_launch

# ---------------------------------------------------------------------- FR-QA-01 structure


def check_structure(launch_dir: Path) -> CheckResult:
    result = CheckResult("FR-QA-01", "Structure: every YAML file matches its schema")
    for p in validate_launch(launch_dir):
        result.findings.append(Finding("FR-QA-01", ERROR, p.file, p.message, p.location))
    result.summary = "All files match their schemas." if not result.findings else \
        f"{len(result.findings)} schema problem(s)."
    return result


# ---------------------------------------------------------------------- FR-QA-02 citations

# Fields that are identifiers, enums, dates or the PMM's own words: not claims to cite.
SKIP_KEYS = {
    "id", "industry", "url", "source_id", "label", "status", "decision", "stance", "rating", "level", "category",
    "model", "buying_role", "provenance", "type", "date", "published_at", "retrieved_at", "researched_at",
    "responded_at", "persona_id", "pillar_id", "pain_ref", "competitor_id", "imperative_id", "moment_id", "offer",
    "influence", "from", "to", "pov_quote", "adjusted_direction", "reason", "term", "series_id", "connector",
    "unit", "jurisdiction", "name", "disclaimer", "role", "reports_to", "when", "value_metric", "free_tier",
    "proof_slot", "primary_cta", "cta", "title",
}
SKIP_PARENTS = {"discovery_questions", "landmines", "titles", "kpis", "language", "use", "avoid", "keywords",
                "capability_refs", "trend_ids", "imperative_ids", "competitor_ids", "strongest_competitor_ids",
                "moment_ids", "target_personas", "messaging_refs", "segments", "data_needed", "environment",
                "info_sources", "personas", "industries", "competitors", "tags", "components", "sources",
                "decision_sequence", "headline_variants"}
# Named laws ("Affordable Care Act", "Regulation (EU) 2024/1689") need a name before or after the keyword,
# so verbs like "Act on changes" at the start of a headline don't count.
REG_RE = re.compile(r"\b[A-Z][\w.&-]*\s+(Act|Rule|Directive)\b|\b(Regulation|Directive)\s+\(|"
                    r"\b(rules?|regulators?|regulation|law|statute|mandate[sd]?|requires?|required|"
                    r"compliance deadline|GDPR|HIPAA|CMS|FDA|SEC|FTC|FCC|CFPB|OCC|FDIC|EBA|FCA)\b")
ORG_RE = re.compile(r"\b(Inc|Corp|Corporation|LLC|Ltd|plc|GmbH|AG|S\.A\.)\b")
NUMBER_RE = re.compile(r"(?<![A-Za-z]-)(?<![A-Za-z]-\w)\b\d[\d,.]*\s*(%|percent|x\b|million|billion|bn|m\b|k\b)?|\$\d")
ID_REF_RE = re.compile(r"\b(?:T|I|R|MD|O|SC|SA|P|PL|DM|WS)-[\w-]+")


def _competitor_names(launch_dir: Path, data: dict) -> list[str]:
    names = set()
    launch = load_yaml(launch_dir / "launch.yaml") if (launch_dir / "launch.yaml").exists() else {}
    generic = {"status-quo", "build-in-house"}
    for c in launch.get("competitors", []):
        if c["id"] not in generic:
            names.add(c["name"])
    for rel, doc in data.items():
        if rel.startswith("competitors/") and isinstance(doc, dict) and doc.get("category") not in generic:
            names.add(doc.get("name", ""))
        elif rel.startswith("competitors/") and isinstance(doc, dict):
            names.discard(doc.get("name", ""))
    return sorted(n for n in names if n and len(n) > 2)


def claim_kinds(sentence: str, competitor_names: list[str]) -> list[str]:
    """Why a sentence counts as a detectable factual claim (empty list: it doesn't)."""
    text = ID_REF_RE.sub("", LABEL_RE.sub("", sentence))
    kinds = []
    if NUMBER_RE.search(text):
        kinds.append("number or date")
    if any(re.search(rf"\b{re.escape(n)}\b", text) for n in competitor_names) or ORG_RE.search(text):
        kinds.append("named company")
    if REG_RE.search(text):
        kinds.append("regulatory statement")
    return kinds


# Fields whose claim is backed by the sibling `evidence` list (other fields must cite inline).
EVIDENCE_BACKED = {"summary", "reasoning", "text", "statement", "headline"}


def _structurally_cited(parent, key) -> bool:
    """True when the object itself carries the citation: a source_id on a single-claim object
    (market data, recent moves, quotes), the evidence list for its main statement, or a label."""
    if not isinstance(parent, dict):
        return False
    if parent.get("source_id"):
        return True
    if parent.get("evidence") and key in EVIDENCE_BACKED:
        return True
    label = parent.get("label")
    return isinstance(label, str) and bool(LABEL_RE.search(label))


def check_citations(launch_dir: Path, target: float = 0.95) -> CheckResult:
    result = CheckResult("FR-QA-02", "Citations: every factual claim is cited or labeled")
    data = artifacts(launch_dir)
    names = _competitor_names(launch_dir, data)
    detected = covered = 0
    for rel, doc in data.items():
        for path, parent, key, text in walk(doc):
            parts = re.split(r"[.\[\]]", path)
            if str(key) in SKIP_KEYS or any(p in SKIP_PARENTS for p in parts):
                continue
            structured = _structurally_cited(parent, key)
            for s in sentences(text):
                if s.endswith("?"):
                    continue  # questions are not claims
                kinds = claim_kinds(s, names)
                if not kinds:
                    continue
                detected += 1
                if LABEL_RE.search(s) or structured:
                    covered += 1
                else:
                    result.findings.append(Finding("FR-QA-02", WARNING, rel, f"Uncited {' and '.join(kinds)}: \"{s}\"",
                                                   path))
    coverage = covered / detected if detected else 1.0
    result.summary = (f"{covered} of {detected} detectable claims cited or labeled "
                      f"({coverage:.0%}; target {target:.0%}).")
    if coverage < target:
        result.findings.insert(0, Finding("FR-QA-02", ERROR, "(all)", f"Citation coverage {coverage:.0%} is below "
                                                                    f"the {target:.0%} target."))
    result.coverage = coverage  # type: ignore[attr-defined]
    return result


# ---------------------------------------------------------------------- FR-QA-03 sources

LinkChecker = Callable[[str], int | None]


def check_sources(launch_dir: Path, link_checker: LinkChecker | None = None) -> CheckResult:
    result = CheckResult("FR-QA-03", "Sources: registered, dated, recent and of the right tier")
    register = {s["id"]: s for s in load_sources(launch_dir)["sources"]}
    data = artifacts(launch_dir)
    cited: dict[str, set[str]] = {}
    for rel, doc in data.items():
        for _, _parent, key, text in walk(doc):
            ids = set(re.findall(r"\[(S\d+)\]", text))
            if key == "source_id" and re.fullmatch(r"S\d+", text):
                ids.add(text)
            for sid in ids:
                cited.setdefault(sid, set()).add(rel)
        if isinstance(doc, dict):
            for sid in doc.get("sources", []) if isinstance(doc.get("sources"), list) else []:
                if isinstance(sid, str):
                    cited.setdefault(sid, set()).add(rel)
    for sid, files in sorted(cited.items(), key=lambda x: int(x[0][1:])):
        if sid not in register:
            result.findings.append(Finding("FR-QA-03", ERROR, ", ".join(sorted(files)),
                                           f"{sid} is cited but not in research/sources.json"))
    for sid, s in register.items():
        if not s.get("url") or not s.get("retrieved_at"):
            result.findings.append(Finding("FR-QA-03", ERROR, "research/sources.json",
                                           f"{sid} needs a URL and a retrieval date"))

    # Trend evidence: recency, independence and tier (FR-TRD-01, FR-WEB-R-02).
    for rel, doc in data.items():
        if not rel.startswith("research/industry-"):
            continue
        for t in doc.get("trends", []):
            ev = [register[e["source_id"]] for e in t.get("evidence", []) if e["source_id"] in register]
            old = [s for s in ev if s.get("published_at") and months_between(s["published_at"], today()) > 24]
            for s in old:
                result.findings.append(Finding("FR-QA-03", WARNING, rel, f"{t['id']} cites {s['id']}, published "
                                                f"{s['published_at']} (older than 24 months)"))
            if ev and not any(s.get("published_at") and months_between(s["published_at"], today()) <= 24
                              for s in ev):
                result.findings.append(Finding("FR-QA-03", WARNING, rel,
                                               f"{t['id']} has no source from the last 24 months"))
            if len({s["publisher"] for s in ev}) < 2:
                result.findings.append(Finding("FR-QA-03", WARNING, rel,
                                               f"{t['id']} needs at least 2 independent sources"))
            if ev and not any(s["tier"] in (1, 2) for s in ev):
                result.findings.append(Finding("FR-QA-03", WARNING, rel,
                                               f"{t['id']} needs at least one Tier 1 or 2 source"))
        for r in doc.get("regulatory", {}).get("items", []):
            ev = [register[e["source_id"]] for e in r.get("evidence", []) if e["source_id"] in register]
            if not any(s["tier"] in (1, 2) for s in ev):
                result.findings.append(Finding("FR-QA-03", WARNING, rel,
                                               f"{r['id']} needs at least one Tier 1 or 2 source"))
    # Competitor list prices need Tier 1 (FR-WEB-R-02, FR-CMP-04).
    for rel, doc in data.items():
        if rel.startswith("competitors/"):
            for lp in doc.get("pricing", {}).get("list_prices", []) or []:
                s = register.get(lp["source_id"])
                if s and s["tier"] != 1:
                    result.findings.append(Finding("FR-QA-03", ERROR, rel, f"List price '{lp['item']}' cites "
                                                    f"{s['id']} (tier {s['tier']}); pricing needs a Tier 1 source"))
    # Optional live check that links still answer.
    if link_checker:
        for sid, s in register.items():
            status = link_checker(s["url"])
            if status is None or status in (404, 410) or status >= 500:
                result.findings.append(Finding("FR-QA-03", WARNING, "research/sources.json",
                                               f"{sid} link didn't answer ({status or 'no response'}): {s['url']}"))
    result.summary = f"{len(register)} registered source(s), {len(cited)} cited."
    return result


# ---------------------------------------------------------------------- FR-QA-06 sameness

FEATURE_OPENERS = re.compile(r"^\s*(our|we|introducing|featuring|powered by|built on|built with|with our|meet|"
                             r"new|the (?:new|first|only)|ai[- ]powered|ai[- ]driven|an? (?:ai|platform|tool|"
                             r"dashboard|engine|api|app)\b)", re.I)
FEATURE_WORDS = {"platform", "engine", "dashboard", "api", "module", "feature", "features", "algorithm",
                 "integration", "integrations", "app", "software", "tool", "model", "llm"}


def opens_with_feature(text: str, product_names: list[str]) -> str | None:
    """Why a message looks feature-first (None if it leads with an outcome)."""
    t = LABEL_RE.sub("", text).strip()
    if not t:
        return None
    if FEATURE_OPENERS.search(t):
        return f"opens with \"{FEATURE_OPENERS.search(t).group(0).strip()}\""
    first = re.findall(r"[A-Za-z][\w-]*", t)[:3]
    if any(w.lower() in FEATURE_WORDS for w in first):
        return "names a feature in its first words"
    for name in product_names:
        if name and t.lower().startswith(name.lower()):
            return f"opens with the product name \"{name}\""
    return None


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def check_sameness(launch_dir: Path, threshold: float = 0.70) -> CheckResult:
    result = CheckResult("FR-QA-06", "Industry-specific and value-first")
    data = artifacts(launch_dir)
    personas = []
    for rel, doc in data.items():
        if rel.startswith("personas/"):
            personas += [(rel, p) for p in doc.get("personas", [])]
    pairs = 0
    for (rel_a, a), (rel_b, b) in combinations(personas, 2):
        if a["industry"] == b["industry"]:
            continue
        pairs += 1
        score = _similar(" ".join(x["text"] for x in a["pains"]), " ".join(x["text"] for x in b["pains"]))
        if score > threshold:
            result.findings.append(Finding("FR-QA-06", ERROR, f"{rel_a} / {rel_b}",
                                           f"{a['id']} and {b['id']} have pains {score:.0%} alike across industries; "
                                           "rewrite them for each industry"))
    messaging = data.get("messaging.yaml") or {}
    grid = messaging.get("grid", [])
    for a, b in combinations(grid, 2):
        if a["industry"] != b["industry"]:
            score = _similar(a["headline"], b["headline"])
            if score > threshold:
                result.findings.append(Finding("FR-QA-06", WARNING, "messaging.yaml",
                                               f"Headlines for {a['persona_id']} and {b['persona_id']} are "
                                               f"{score:.0%} alike across industries"))
    # Feature-first messages (FR-MSG-04).
    context = load_yaml(launch_dir / "launch-context.yaml") if (launch_dir / "launch-context.yaml").exists() else {}
    product = (context.get("product_brief", {}).get("basics", {}).get("product_name", {}) or {}).get("value")
    brand = load_yaml(launch_dir / "brand.yaml") if (launch_dir / "brand.yaml").exists() else {}
    product_names = [n for n in [product, *brand.get("terms", {}).get("product_names", [])] if isinstance(n, str)]
    messages = [("messaging.yaml", "elevator_pitch", messaging.get("elevator_pitch", ""))]
    messages += [("messaging.yaml", f"pillars.{p['id']}.headline", p["headline"]) for p in messaging.get("pillars", [])]
    messages += [("messaging.yaml", f"grid[{i}].headline", r["headline"]) for i, r in enumerate(grid)]
    for rel, doc in data.items():
        if rel.startswith("web/"):
            messages.append((rel, "hero.headline", doc.get("hero", {}).get("headline", "")))
            messages += [(rel, f"headline_variants[{i}]", h) for i, h in enumerate(doc.get("headline_variants", []))]
    for rel, loc, text in messages:
        why = opens_with_feature(text, product_names)
        if why:
            result.findings.append(Finding("FR-QA-06", WARNING, rel, f"Feature-first message ({why}): \"{text}\". "
                                           "Lead with the customer outcome.", loc))
    result.summary = f"Compared {pairs} persona pair(s) across industries; checked {len(messages)} message(s)."
    return result


# ---------------------------------------------------------------------- FR-QA-07 completeness

PER_INDUSTRY_FILES = {
    "industry brief": "research/industry-{i}.yaml",
    "personas": "personas/{i}.yaml",
    "playbook": "playbooks/{i}.yaml",
    "demo storyline": "demos/{i}.yaml",
    "webpage copy brief": "web/{i}.yaml",
}
RANGES = [  # (artifact glob, path to list, min, max, label)
    ("research/industry-*.yaml", "trends", 5, 8, "trends"),
    ("research/industry-*.yaml", "imperatives", 3, 5, "imperatives"),
    ("research/industry-*.yaml", "market_data", 3, 6, "market data points"),
    ("personas/*.yaml", "personas", 4, 6, "personas"),
    ("messaging.yaml", "pillars", 3, 4, "value pillars"),
    ("demos/*.yaml", "moments", 5, 7, "demo moments"),
    ("web/*.yaml", "headline_variants", 2, 3, "headline variants"),
]


def check_completeness(launch_dir: Path) -> CheckResult:
    result = CheckResult("FR-QA-07", "Completeness: every industry and competitor has every asset")
    launch = load_yaml(launch_dir / "launch.yaml")
    data = artifacts(launch_dir)
    for ind in launch["industries"]:
        for asset, pattern in PER_INDUSTRY_FILES.items():
            rel = pattern.format(i=ind["id"])
            if rel not in data:
                result.findings.append(Finding("FR-QA-07", ERROR, rel, f"{ind['name']}: {asset} is missing"))
        personas = (data.get(f"personas/{ind['id']}.yaml") or {}).get("personas", [])
        grid_ids = {r["persona_id"] for r in (data.get("messaging.yaml") or {}).get("grid", [])
                    if r["industry"] == ind["id"]}
        for p in personas:
            if p["id"] not in grid_ids:
                result.findings.append(Finding("FR-QA-07", ERROR, "messaging.yaml",
                                               f"No grid row for {p['id']} ({ind['name']})"))
    if "messaging.yaml" not in data:
        result.findings.append(Finding("FR-QA-07", ERROR, "messaging.yaml", "Messaging framework is missing"))
    if "competitive-overview.yaml" not in data:
        result.findings.append(Finding("FR-QA-07", ERROR, "competitive-overview.yaml",
                                       "Competitive overview is missing"))
    for c in launch["competitors"]:
        if f"competitors/{c['id']}.yaml" not in data:
            result.findings.append(Finding("FR-QA-07", ERROR, f"competitors/{c['id']}.yaml",
                                           f"No battlecard for {c['name']}"))
    strategy = data.get("strategy-check.yaml")
    if not strategy:
        result.findings.append(Finding("FR-QA-07", ERROR, "strategy-check.yaml", "Strategy check is missing"))
    else:
        auto = launch["options"].get("auto_mode") or strategy.get("auto_mode")
        for item in strategy.get("points", []) + strategy.get("additions", []):
            decision = (item.get("pmm_response") or {}).get("decision")
            if decision is None or (decision == "not_reviewed" and not auto):
                result.findings.append(Finding("FR-QA-07", ERROR, "strategy-check.yaml",
                                               f"{item['id']} has no PMM response"))
    # Recommended counts: warnings, never a reason to invent content.
    for pattern, key, lo, hi, label in RANGES:
        for path in sorted(launch_dir.glob(pattern)):
            rel = path.relative_to(launch_dir).as_posix()
            n = len((data.get(rel) or {}).get(key, []) or [])
            if not lo <= n <= hi:
                result.findings.append(Finding("FR-QA-07", WARNING, rel, f"{n} {label} (expected {lo}–{hi})"))
    for rel, doc in data.items():
        if rel.startswith("personas/"):
            for p in doc.get("personas", []):
                if len(p.get("discovery_questions", [])) != 5:
                    result.findings.append(Finding("FR-QA-07", WARNING, rel, f"{p['id']} has "
                                           f"{len(p.get('discovery_questions', []))} discovery questions (expected 5)"))
                if len(p.get("pains", [])) != 3:
                    result.findings.append(Finding("FR-QA-07", WARNING, rel, f"{p['id']} has "
                                                   f"{len(p.get('pains', []))} pains (expected 3)"))
        if rel.startswith("competitors/") and len(doc.get("objections", [])) < 5:
            result.findings.append(Finding("FR-QA-07", WARNING, rel,
                                           f"{len(doc.get('objections', []))} objections (expected the top 5)"))
    n_ind, n_comp = len(launch["industries"]), len(launch["competitors"])
    result.summary = f"{n_ind} industr{'y' if n_ind == 1 else 'ies'}, {n_comp} competitor(s) checked."
    return result


# ---------------------------------------------------------------------- FR-OUT-03 / FR-CMP-04 rules

PRICE_ADVICE_RE = re.compile(r"\b(we recommend (?:a )?pric\w*|recommended price|price (?:it|this|ours?) at|should "
                             r"(?:charge|price)|undercut\w*|price point of)\b", re.I)


def check_rules(launch_dir: Path) -> CheckResult:
    result = CheckResult("FR-OUT-03", "Cross-asset rules: customer copy, pricing, proof")
    data = artifacts(launch_dir)
    launch = load_yaml(launch_dir / "launch.yaml")
    names = _competitor_names(launch_dir, data)
    if not launch["options"].get("name_competitors_in_customer_copy"):
        for rel, doc in data.items():
            if rel.startswith(("demos/", "web/")):
                for path, _, _, text in walk(doc):
                    for n in names:
                        if re.search(rf"\b{re.escape(n)}\b", text):
                            result.findings.append(Finding("FR-OUT-03", ERROR, rel, f"Customer-facing copy names "
                                                           f"competitor '{n}' (not opted in)", path))
    for rel, doc in data.items():
        for path, _, _, text in walk(doc):
            if PRICE_ADVICE_RE.search(text):
                result.findings.append(Finding("FR-CMP-04", ERROR, rel, f"Looks like a price recommendation: "
                                               f"\"{text[:160]}\"", path))
    result.summary = "Checked customer-facing copy and pricing language."
    return result
