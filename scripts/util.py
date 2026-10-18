"""Small helpers shared by all scripts: paths, YAML in/out, timestamps."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SCHEMAS_DIR = REPO_ROOT / "schemas"
LAUNCHES_DIR = REPO_ROOT / "launches"
TEMPLATES_DIR = REPO_ROOT / "templates"
TOOLKIT_VERSION = "0.1.0"


class _Loader(yaml.SafeLoader):
    """SafeLoader that keeps dates as plain strings.

    PyYAML turns `2026-10-18` into a date object by default, which then fails
    JSON Schema "string" checks. Artifacts store dates as text, so we drop the
    timestamp rule.
    """


_Loader.yaml_implicit_resolvers = {
    key: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


class _Dumper(yaml.SafeDumper):
    pass


def _str_presenter(dumper: yaml.SafeDumper, data: str) -> yaml.Node:
    # Multi-line text is written as a readable block instead of one long quoted line.
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


_Dumper.add_representer(str, _str_presenter)


def load_yaml(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, Loader=_Loader)


def loads_yaml(text: str) -> Any:
    return yaml.load(text, Loader=_Loader)


def dump_yaml(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=_Dumper, sort_keys=False, allow_unicode=True, width=100)


def load_data(path: Path) -> Any:
    """Load a .yaml/.yml or .json artifact."""
    if path.suffix == ".json":
        return json.loads(path.read_text(encoding="utf-8"))
    return load_yaml(path)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today() -> str:
    return datetime.now(timezone.utc).date().isoformat()
