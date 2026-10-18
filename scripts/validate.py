"""Validate YAML/JSON artifacts against the JSON Schemas in schemas/ (FR-QA-01).

Usage:
    python scripts/validate.py <file> [<file> ...]
    python scripts/validate.py --launch <slug>      # every artifact in a launch
"""

from __future__ import annotations

import fnmatch
import json
import sys
from dataclasses import dataclass
from functools import cache, lru_cache
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from scripts.util import LAUNCHES_DIR, SCHEMAS_DIR, load_data

# Which schema applies to which artifact, by path relative to the launch folder.
ARTIFACT_SCHEMAS: list[tuple[str, str]] = [
    ("launch.yaml", "launch.schema.json"),
    ("launch-context.yaml", "launch-context.schema.json"),
    ("brand.yaml", "brand.schema.json"),
    ("research/sources.json", "sources.schema.json"),
    ("research/industry-*.yaml", "industry-research.schema.json"),
    ("competitors/*.yaml", "competitor.schema.json"),
    ("competitive-overview.yaml", "competitive-overview.schema.json"),
    ("strategy-check.yaml", "strategy-check.schema.json"),
    ("personas/*.yaml", "personas.schema.json"),
    ("messaging.yaml", "messaging.schema.json"),
    ("playbooks/*.yaml", "playbook.schema.json"),
    ("demos/*.yaml", "demo.schema.json"),
    ("web/*.yaml", "web.schema.json"),
    ("industries/*/pack.yaml", "industry-pack.schema.json"),
]


@dataclass
class Problem:
    file: str
    location: str
    message: str

    def __str__(self) -> str:
        return f"{self.file}: at {self.location}: {self.message}"


@lru_cache(maxsize=1)
def _registry() -> Registry:
    resources = []
    for path in sorted(SCHEMAS_DIR.glob("*.schema.json")):
        contents = json.loads(path.read_text(encoding="utf-8"))
        resources.append((contents["$id"], Resource.from_contents(contents)))
    return Registry().with_resources(resources)


@cache
def validator_for(schema_name: str) -> Draft202012Validator:
    schema = json.loads((SCHEMAS_DIR / schema_name).read_text(encoding="utf-8"))
    return Draft202012Validator(schema, registry=_registry())


def schema_for(rel_path: str) -> str | None:
    rel_path = rel_path.replace("\\", "/")
    for pattern, schema in ARTIFACT_SCHEMAS:
        if fnmatch.fnmatch(rel_path, pattern):
            return schema
    return None


def validate_data(data, schema_name: str, label: str = "<data>") -> list[Problem]:
    problems = []
    for err in sorted(validator_for(schema_name).iter_errors(data), key=lambda e: list(e.path)):
        location = "/".join(str(p) for p in err.path) or "(top level)"
        problems.append(Problem(label, location, err.message))
    return problems


def validate_file(path: Path, schema_name: str | None = None, base: Path | None = None) -> list[Problem]:
    label = str(path.relative_to(base)) if base else str(path)
    if schema_name is None:
        schema_name = schema_for(label if base else path.name)
    if schema_name is None:
        return [Problem(label, "(file)", "no schema is registered for this file")]
    try:
        data = load_data(path)
    except Exception as exc:  # unreadable YAML/JSON is a validation failure, not a crash
        return [Problem(label, "(file)", f"could not be read: {exc}")]
    return validate_data(data, schema_name, label)


def validate_launch(launch_dir: Path) -> list[Problem]:
    problems: list[Problem] = []
    for path in sorted(launch_dir.rglob("*")):
        if not path.is_file() or path.suffix not in (".yaml", ".yml", ".json"):
            continue
        rel = path.relative_to(launch_dir).as_posix()
        if rel.startswith(("inputs/", "outputs/", "refresh/")) or "/cache/" in rel:
            continue
        schema = schema_for(rel)
        if schema:
            problems.extend(validate_file(path, schema, base=launch_dir))
    return problems


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--launch":
        launch_dir = LAUNCHES_DIR / argv[1]
        problems = validate_launch(launch_dir)
    else:
        problems = []
        for arg in argv:
            path = Path(arg).resolve()
            problems.extend(validate_file(path, schema_for(_guess_rel(path))))
    if problems:
        print(f"[X] {len(problems)} problem(s) found:")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("[OK] All files match their schemas.")
    return 0


def _guess_rel(path: Path) -> str:
    """Path relative to its launch folder (or the repo for industry packs)."""
    parts = path.parts
    if "launches" in parts:
        i = parts.index("launches")
        return "/".join(parts[i + 2 :])
    if "industries" in parts:
        i = parts.index("industries")
        return "/".join(parts[i:])
    return path.name


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
