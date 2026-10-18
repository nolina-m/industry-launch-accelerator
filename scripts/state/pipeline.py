"""The pipeline: which stage units exist, what each one writes, and what it depends on (§9.0).

A *unit* is one approvable piece of work. Stages that run per industry have one
unit per industry, named `<stage>:<industry-id>` (for example `personas:technology`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Stage order and labels, as shown to the PMM.
STAGES: list[tuple[str, str]] = [
    ("intake", "Stage 0  Intake and gap check"),
    ("research", "Stage 1  Industry research"),
    ("competitive", "Stage 2  Competitive"),
    ("strategy", "Stage 3  Strategy check"),
    ("personas", "Stage 4  Personas"),
    ("messaging", "Stage 5  Messaging"),
    ("playbook", "Stage 6a Industry playbook"),
    ("demo", "Stage 6b Demo storyline"),
    ("web", "Stage 6c Webpage copy brief"),
    ("qa", "Stage 7  QA and packaging"),
]
STAGE_LABELS = dict(STAGES)
PER_INDUSTRY = {"research", "personas", "playbook", "demo", "web"}

# Files each stage writes, relative to the launch folder. `{i}` is the industry id.
# research/sources.json is a shared register written by several stages, so it is
# deliberately not part of any stage's outputs (and does not trigger staleness).
OUTPUTS: dict[str, list[str]] = {
    "intake": ["launch-context.yaml", "brand.yaml", "gap-report.md"],
    "research": ["research/industry-{i}.yaml"],
    "competitive": ["competitors/*.yaml", "competitive-overview.yaml"],
    "strategy": ["strategy-check.yaml"],
    "personas": ["personas/{i}.yaml"],
    "messaging": ["messaging.yaml"],
    "playbook": ["playbooks/{i}.yaml"],
    "demo": ["demos/{i}.yaml"],
    "web": ["web/{i}.yaml"],
    "qa": ["qa-report.md", "LAUNCH-KIT.md"],
}

# Human-readable asset each unit produces (for "which assets are affected").
ASSETS: dict[str, str] = {
    "intake": "Gap report and launch context",
    "research": "Industry brief ({name})",
    "competitive": "Battlecards and competitive overview",
    "strategy": "Strategy check",
    "personas": "Personas and buying committee ({name})",
    "messaging": "Messaging framework and grid",
    "playbook": "Industry playbook ({name})",
    "demo": "Demo storyline ({name})",
    "web": "Webpage copy brief ({name})",
    "qa": "QA report and LAUNCH-KIT.md",
}

INPUTS_KEY = "inputs/"  # pseudo-dependency: the PMM's input files


@dataclass(frozen=True)
class Unit:
    name: str  # e.g. "personas:technology" or "messaging"
    stage: str
    industry: str | None = None
    deps: tuple[str, ...] = field(default=())

    @property
    def outputs(self) -> list[str]:
        return [p.replace("{i}", self.industry or "") for p in OUTPUTS[self.stage]]


def unit_name(stage: str, industry: str | None = None) -> str:
    return f"{stage}:{industry}" if industry else stage


def build_units(industry_ids: list[str]) -> dict[str, Unit]:
    """All units for a launch with these industries, in pipeline order."""
    research = [unit_name("research", i) for i in industry_ids]
    personas = [unit_name("personas", i) for i in industry_ids]
    units: list[Unit] = [Unit("intake", "intake", deps=(INPUTS_KEY,))]
    units += [Unit(unit_name("research", i), "research", i, ("intake",)) for i in industry_ids]
    units.append(Unit("competitive", "competitive", deps=("intake",)))
    units.append(Unit("strategy", "strategy", deps=(*research, "competitive")))
    units += [
        Unit(unit_name("personas", i), "personas", i, ("strategy", unit_name("research", i)))
        for i in industry_ids
    ]
    units.append(Unit("messaging", "messaging", deps=("strategy", "competitive", *personas)))
    for stage in ("playbook", "demo", "web"):
        extra = ("competitive",) if stage == "playbook" else ()
        units += [
            Unit(unit_name(stage, i), stage, i, ("messaging", unit_name("personas", i), *extra))
            for i in industry_ids
        ]
    sales = [u.name for u in units if u.stage in ("playbook", "demo", "web")]
    units.append(Unit("qa", "qa", deps=tuple(sales)))
    return {u.name: u for u in units}


def downstream_of(units: dict[str, Unit], name: str) -> list[str]:
    """Every unit that depends on `name`, directly or indirectly, in pipeline order."""
    affected: set[str] = set()
    frontier = {name}
    while frontier:
        nxt = {u.name for u in units.values() if frontier & set(u.deps)} - affected
        affected |= nxt
        frontier = nxt
    return [n for n in units if n in affected]
