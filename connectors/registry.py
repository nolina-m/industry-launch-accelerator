"""Load connectors from registry.yaml."""

from __future__ import annotations

import importlib
from functools import lru_cache
from pathlib import Path

import yaml

REGISTRY = Path(__file__).with_name("registry.yaml")


@lru_cache(maxsize=1)
def entries() -> dict[str, dict]:
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    return {e["id"]: e for e in data["connectors"]}


def connector_class(connector_id: str):
    module_name, class_name = entries()[connector_id]["class"].split(":")
    return getattr(importlib.import_module(module_name), class_name)


def get(connector_id: str, **kwargs):
    """A ready-to-use connector, e.g. get("bls", cache_dir=launch_dir / "research" / "cache")."""
    if connector_id not in entries():
        raise KeyError(f"Unknown connector '{connector_id}'. Known: {', '.join(entries())}")
    return connector_class(connector_id)(**kwargs)
