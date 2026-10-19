"""Which parts of downstream assets depend on what changed upstream (FR-STA-04).

Every approval saves a copy of the unit's files in `.approved/<unit>/<fingerprint>/`.
When a unit goes stale, its approval record says which fingerprint of each upstream
unit it was built on. Comparing that copy with the current files gives the exact
items that changed (a persona, a pillar, a trend), and searching the stale unit's
files for references to those IDs gives the parts to regenerate.

Example: one persona's pains change -> in messaging.yaml only that persona's grid
rows depend on it; in playbooks/<industry>.yaml only its value story and discovery
questions.
"""

from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from scripts.state.hashing import existing_outputs
from scripts.util import load_data

SNAPSHOT_DIR = ".approved"


def _unit_dir(launch_dir: Path, unit: str) -> Path:
    return launch_dir / SNAPSHOT_DIR / unit.replace(":", "__")


def save_snapshot(launch_dir: Path, unit: str, patterns: list[str], output_hash: str) -> None:
    """Keep a copy of a unit's files as approved (one copy per distinct content)."""
    target = _unit_dir(launch_dir, unit) / output_hash[:16]
    if target.exists():
        return
    for path in existing_outputs(launch_dir, patterns):
        dest = target / path.relative_to(launch_dir)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    target.mkdir(parents=True, exist_ok=True)


def snapshot_files(launch_dir: Path, unit: str, output_hash: str | None) -> dict[str, object] | None:
    """{relative path: parsed data} of an approved copy, or None if there is no copy."""
    if not output_hash:
        return None
    base = _unit_dir(launch_dir, unit) / output_hash[:16]
    if not base.is_dir():
        return None
    return {p.relative_to(base).as_posix(): _load(p) for p in sorted(base.rglob("*")) if p.is_file()}


def current_files(launch_dir: Path, patterns: list[str]) -> dict[str, object]:
    return {p.relative_to(launch_dir).as_posix(): _load(p) for p in existing_outputs(launch_dir, patterns)}


def _load(path: Path):
    if path.suffix in (".yaml", ".yml", ".json"):
        try:
            return load_data(path)
        except Exception:
            return None
    return path.read_text(encoding="utf-8", errors="replace")


# ---------------------------------------------------------------------- what changed


def _items_by_id(value, found=None) -> dict[str, str]:
    """{id: canonical JSON} for every object with an `id` field, at any depth."""
    found = {} if found is None else found
    if isinstance(value, dict):
        if isinstance(value.get("id"), str):
            found[value["id"]] = json.dumps(value, sort_keys=True, default=str)
        for v in value.values():
            _items_by_id(v, found)
    elif isinstance(value, list):
        for v in value:
            _items_by_id(v, found)
    return found


def _without_ided(value):
    """The object with every id-carrying child removed (to spot changes outside those items)."""
    if isinstance(value, dict):
        if isinstance(value.get("id"), str):
            return "<item>"
        return {k: _without_ided(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_without_ided(v) for v in value]
    return value


@dataclass
class Change:
    file: str
    changed: list[str] = field(default_factory=list)  # item ids whose content changed
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)  # top-level fields that changed outside items
    whole_file: bool = False  # added/removed file, or not structured data

    @property
    def ids(self) -> list[str]:
        return self.changed + self.added + self.removed

    def describe(self) -> str:
        if self.whole_file:
            return f"{self.file} (whole file)"
        parts = []
        if self.changed:
            parts.append("changed " + ", ".join(self.changed))
        if self.added:
            parts.append("added " + ", ".join(self.added))
        if self.removed:
            parts.append("removed " + ", ".join(self.removed))
        if self.fields:
            parts.append("edited " + ", ".join(self.fields))
        return f"{self.file}: " + "; ".join(parts)


def diff(old: dict[str, object], new: dict[str, object]) -> list[Change]:
    changes = []
    for rel in sorted(set(old) | set(new)):
        a, b = old.get(rel), new.get(rel)
        if a == b:
            continue
        if a is None or b is None or not isinstance(a, dict | list) or not isinstance(b, dict | list):
            changes.append(Change(rel, whole_file=True))
            continue
        ia, ib = _items_by_id(a), _items_by_id(b)
        c = Change(rel,
                   changed=sorted(k for k in ia.keys() & ib.keys() if ia[k] != ib[k]),
                   added=sorted(ib.keys() - ia.keys()),
                   removed=sorted(ia.keys() - ib.keys()))
        sa, sb = _without_ided(a), _without_ided(b)
        if isinstance(sa, dict) and isinstance(sb, dict):
            c.fields = sorted(k for k in sa.keys() | sb.keys() if sa.get(k) != sb.get(k))
        elif sa != sb:
            c.fields = ["(structure)"]
        # An item whose child item changed also "changed"; keep only the innermost ids.
        c.changed = [i for i in c.changed if not any(j != i and j in ia.get(i, "") for j in c.ids)] or c.changed
        changes.append(c)
    return changes


# ---------------------------------------------------------------------- where it's used


def _mentions(text: str, item_id: str) -> bool:
    """True if `text` refers to `item_id`: the id itself, a pain ref like P-x#2, or the id inside prose."""
    return re.search(rf"(?<![\w-]){re.escape(item_id)}(?![\w-])", text) is not None


def find_references(files: dict[str, object], ids: list[str]) -> list[tuple[str, str, str]]:
    """[(file, item path, id)]: the smallest list item in each file that refers to a changed id."""
    out: list[tuple[str, str, str]] = []
    if not ids:
        return out
    for rel, data in files.items():
        if not isinstance(data, dict | list):
            continue
        found: list[tuple[str, str]] = []

        def capture(value, path, owner, found=found):
            if isinstance(value, dict):
                for k, v in value.items():
                    capture(v, f"{path}.{k}" if path else k, owner)
            elif isinstance(value, list):
                for i, v in enumerate(value):
                    child = f"{path}[{i}]"
                    capture(v, child, child if isinstance(v, dict) else owner)
            elif isinstance(value, str):
                for item_id in ids:
                    if _mentions(value, item_id):
                        found.append((owner or path, item_id))

        capture(data, "", "")
        out += [(rel, item_path, item_id) for item_path, item_id in dict.fromkeys(found)]
    return out
