"""Reading, updating and saving launch.yaml: stage status, checkpoints and staleness.

Status rules (FR-STA-01, FR-STA-02, FR-STA-04):

    not_started -> in_progress -> awaiting_approval -> approved
                         ^               |               |
                         +---- redo -----+               v
                         +----------------------------- stale (an upstream unit changed)

- A unit can only start once every unit it depends on is approved.
- Approving records a fingerprint of the unit's own files and of each upstream
  unit's files. If any of those later change, the unit becomes `stale`.
- If the unit's own files change after approval (the PMM edited them), it goes
  back to `awaiting_approval`, and everything downstream becomes stale. Undoing
  the edit returns it to `approved`.
- Staleness is recalculated each time, so if an upstream change is undone, the
  unit returns to `approved` on its own.
- In auto mode (FR-STA-03), submitting a unit approves it with reviewed: false.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from scripts.state.hashing import existing_outputs, hash_files
from scripts.state.pipeline import (
    ASSETS,
    INPUTS_KEY,
    STAGE_LABELS,
    Unit,
    build_units,
    downstream_of,
)
from scripts.util import TOOLKIT_VERSION, dump_yaml, load_yaml, now_iso
from scripts.validate import schema_for, validate_data, validate_file

NOT_STARTED = "not_started"
IN_PROGRESS = "in_progress"
AWAITING = "awaiting_approval"
APPROVED = "approved"
STALE = "stale"

EDITED = "its files were edited after approval"
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")
LAUNCH_SUBDIRS = [
    "inputs/brief",
    "inputs/brand",
    "inputs/optional",
    "research/cache",
    "competitors",
    "personas",
    "playbooks",
    "demos",
    "web",
    "industries",
    "outputs",
    "refresh",
]


class StateError(Exception):
    """A request that the rules do not allow. The message is shown to the PMM as-is."""


@dataclass
class Change:
    unit: str
    old: str
    new: str
    reasons: list[str] = field(default_factory=list)


class LaunchState:
    def __init__(self, launch_dir: Path, data: dict):
        self.dir = launch_dir
        self.data = data

    # ------------------------------------------------------------------ load / save
    @classmethod
    def create(cls, launch_dir: Path, slug: str, name: str | None = None) -> LaunchState:
        if not SLUG_RE.match(slug):
            raise StateError(
                f"'{slug}' can't be used as a launch name. Use lowercase letters, numbers and "
                "hyphens, for example: q3-analytics-launch"
            )
        if (launch_dir / "launch.yaml").exists():
            raise StateError(f"A launch called '{slug}' already exists.")
        for sub in LAUNCH_SUBDIRS:
            (launch_dir / sub).mkdir(parents=True, exist_ok=True)
        data = {
            "slug": slug,
            "name": name or slug,
            "created_at": now_iso(),
            "toolkit_version": TOOLKIT_VERSION,
            "industries": [],
            "competitors": [],
            "options": {"name_competitors_in_customer_copy": False, "auto_mode": False},
            "stages": {},
        }
        state = cls(launch_dir, data)
        state.refresh()
        state.save()
        return state

    @classmethod
    def load(cls, launch_dir: Path) -> LaunchState:
        path = launch_dir / "launch.yaml"
        if not path.exists():
            raise StateError(f"No launch found at {launch_dir}. Start one with: launch.py new <name>")
        problems = validate_file(path, "launch.schema.json")
        if problems:
            details = "\n".join(f"  - {p}" for p in problems)
            raise StateError(f"launch.yaml has problems:\n{details}")
        return cls(launch_dir, load_yaml(path))

    def save(self) -> None:
        problems = validate_data(self.data, "launch.schema.json", "launch.yaml")
        if problems:  # a bug in the scripts, never the PMM's fault
            raise RuntimeError("Refusing to save an invalid launch.yaml: " + "; ".join(map(str, problems)))
        dump_yaml(self.data, self.dir / "launch.yaml")

    # ------------------------------------------------------------------ structure
    @property
    def industry_ids(self) -> list[str]:
        return [i["id"] for i in self.data["industries"]]

    @property
    def units(self) -> dict[str, Unit]:
        return build_units(self.industry_ids)

    @property
    def auto_mode(self) -> bool:
        return bool(self.data["options"].get("auto_mode"))

    def record(self, name: str) -> dict:
        return self.data["stages"].setdefault(name, {"status": NOT_STARTED})

    def status(self, name: str) -> str:
        return self.record(name)["status"]

    def asset_label(self, name: str) -> str:
        unit = self.units[name]
        names = {i["id"]: i["name"] for i in self.data["industries"]}
        return ASSETS[unit.stage].format(name=names.get(unit.industry, unit.industry))

    def _unit(self, name: str) -> Unit:
        units = self.units
        if name not in units:
            known = ", ".join(units)
            raise StateError(f"There is no stage called '{name}'. Stages in this launch: {known}")
        return units[name]

    # ------------------------------------------------------------------ fingerprints
    def _current_hashes(self) -> dict[str, str]:
        hashes = {INPUTS_KEY: hash_files(self.dir, [INPUTS_KEY])}
        for name, unit in self.units.items():
            hashes[name] = hash_files(self.dir, unit.outputs)
        return hashes

    # ------------------------------------------------------------------ staleness
    def refresh(self) -> list[Change]:
        """Recalculate statuses from what is on disk. Returns what changed."""
        units = self.units
        hashes = self._current_hashes()
        changes: list[Change] = []

        for gone in [n for n in self.data["stages"] if n not in units]:
            changes.append(Change(gone, self.data["stages"][gone]["status"], "removed",
                                  ["its industry is no longer in this launch"]))
            del self.data["stages"][gone]

        for name, unit in units.items():
            rec = self.record(name)
            old = rec["status"]
            edited = old == AWAITING and rec.get("stale_reasons") == [EDITED]
            if old not in (APPROVED, STALE) and not edited:
                continue
            approval = rec.get("approval", {})
            if hashes[name] != approval.get("output_hash"):
                new, reasons = AWAITING, [EDITED]
            else:
                reasons = []
                for dep in unit.deps:
                    if dep != INPUTS_KEY and self.status(dep) != APPROVED:
                        reasons.append(f"{dep} is {self.status(dep).replace('_', ' ')}")
                    elif hashes[dep] != approval.get("input_hashes", {}).get(dep):
                        what = "the input files" if dep == INPUTS_KEY else dep
                        reasons.append(f"{what} changed")
                new = STALE if reasons else APPROVED
            if reasons:
                rec["stale_reasons"] = reasons
            else:
                rec.pop("stale_reasons", None)
            if new != old:
                rec["status"] = new
                changes.append(Change(name, old, new, reasons))
        return changes

    # ------------------------------------------------------------------ transitions
    def _require_deps_approved(self, unit: Unit, action: str) -> None:
        waiting = [d for d in unit.deps if d != INPUTS_KEY and self.status(d) != APPROVED]
        if waiting:
            listed = ", ".join(f"{d} ({self.status(d).replace('_', ' ')})" for d in waiting)
            raise StateError(
                f"Can't {action} {unit.name} yet. These earlier stages need to be approved first: {listed}"
            )

    def start(self, name: str) -> None:
        """Begin (or redo) a unit. Refused until everything upstream is approved."""
        self.refresh()
        unit = self._unit(name)
        self._require_deps_approved(unit, "start")
        rec = self.record(name)
        rec["status"] = IN_PROGRESS
        rec["started_at"] = now_iso()
        rec.pop("stale_reasons", None)

    def submit(self, name: str) -> list[str]:
        """The agent has finished a unit: check its files and post it for review.

        Returns a list of messages to show. In auto mode the unit is approved straight away.
        """
        self.refresh()
        unit = self._unit(name)
        if self.status(name) != IN_PROGRESS:
            raise StateError(f"{name} is {self.status(name).replace('_', ' ')}, not in progress. Start it first.")
        self._require_deps_approved(unit, "submit")
        self._check_outputs(unit)
        rec = self.record(name)
        rec["submitted_at"] = now_iso()
        if self.auto_mode:
            if unit.stage == "strategy":
                self._mark_strategy_not_reviewed()
            self._approve(unit, reviewed=False)
            return [f"{name} approved automatically (auto mode). Assets will say 'Not reviewed by PMM'."]
        rec["status"] = AWAITING
        return [f"{name} is ready for your review."]

    def approve(self, name: str) -> None:
        self.refresh()
        unit = self._unit(name)
        status = self.status(name)
        if status not in (AWAITING, STALE):
            raise StateError(
                f"{name} is {status.replace('_', ' ')}. Only work that is awaiting approval (or stale) "
                "can be approved."
            )
        self._require_deps_approved(unit, "approve")
        self._check_outputs(unit)
        if unit.stage == "strategy":
            self._check_strategy_responses()
        self._approve(unit, reviewed=True)

    def _approve(self, unit: Unit, reviewed: bool) -> None:
        if unit.stage == "intake":
            self._check_no_open_blocking_gaps()
        hashes = self._current_hashes()
        rec = self.record(unit.name)
        rec["status"] = APPROVED
        rec["approved_at"] = now_iso()
        rec["reviewed"] = reviewed
        rec["approval"] = {
            "input_hashes": {d: hashes[d] for d in unit.deps},
            "output_hash": hashes[unit.name],
        }
        rec.pop("stale_reasons", None)
        self.refresh()

    def set_auto_mode(self, on: bool) -> None:
        self.data["options"]["auto_mode"] = on

    # ------------------------------------------------------------------ checks
    def _check_outputs(self, unit: Unit) -> None:
        missing = [p for p in unit.outputs if "*" not in p and not (self.dir / p).is_file()]
        if missing:
            raise StateError(f"{unit.name} is missing files: {', '.join(missing)}")
        problems = []
        for path in existing_outputs(self.dir, unit.outputs):
            rel = path.relative_to(self.dir).as_posix()
            if schema_for(rel):
                problems.extend(validate_file(path, base=self.dir))
        if problems:
            details = "\n".join(f"  - {p}" for p in problems)
            raise StateError(f"{unit.name} has files that don't match their schema:\n{details}")

    def _check_no_open_blocking_gaps(self) -> None:
        """FR-INT-03: blocking gaps must be answered or explicitly waived, even in auto mode."""
        context = load_yaml(self.dir / "launch-context.yaml")
        still_open = [g for g in context.get("gaps", []) if g["severity"] == "blocking" and g["status"] == "open"]
        if still_open:
            listed = "\n".join(f"  - {g['id']}: {g.get('question') or g['field']}" for g in still_open)
            raise StateError(
                "Intake can't be approved while blocking gaps are open. Answer them, or tell the agent "
                f"to waive them:\n{listed}"
            )

    def _strategy_items(self) -> tuple[Path, dict]:
        path = self.dir / "strategy-check.yaml"
        return path, load_yaml(path)

    def _check_strategy_responses(self) -> None:
        """FR-STR-05: the PMM must respond to every point before the strategy check is approved."""
        _, doc = self._strategy_items()
        missing = [
            item["id"]
            for item in doc.get("points", []) + doc.get("additions", [])
            if item.get("pmm_response", {}).get("decision") in (None, "not_reviewed")
        ]
        if missing:
            raise StateError(
                "The strategy check needs your response (accept, reject or adjust) to every point "
                f"before it can be approved. Still open: {', '.join(missing)}"
            )
        if not str(doc.get("resolved_direction", "")).strip():
            raise StateError("The strategy check needs a resolved direction before it can be approved.")

    def _mark_strategy_not_reviewed(self) -> None:
        path, doc = self._strategy_items()
        doc["auto_mode"] = True
        for item in doc.get("points", []) + doc.get("additions", []):
            item.setdefault("pmm_response", {"decision": "not_reviewed"})
        dump_yaml(doc, path)

    # ------------------------------------------------------------------ reporting
    def summary_rows(self) -> list[tuple[str, str, str, str]]:
        """(unit, stage label, status, note) for every unit, in pipeline order."""
        rows = []
        for name, unit in self.units.items():
            rec = self.record(name)
            note = "; ".join(rec.get("stale_reasons", []))
            if rec["status"] == APPROVED and rec.get("reviewed") is False:
                note = "not reviewed by PMM (auto mode)"
            rows.append((name, STAGE_LABELS[unit.stage], rec["status"], note))
        return rows

    def affected_by(self, name: str) -> list[str]:
        return downstream_of(self.units, name)
