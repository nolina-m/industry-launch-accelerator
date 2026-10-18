"""Industry packs (FR-IND-01, FR-IND-02, FR-API-02)."""

from pathlib import Path

import pytest

from connectors import registry
from scripts.util import REPO_ROOT, load_yaml
from scripts.validate import validate_file

PACKS = sorted((REPO_ROOT / "industries").glob("*/pack.yaml"))
DEFAULT_IDS = ["financial-services", "healthcare-life-sciences", "retail-consumer-goods", "technology",
               "telecom-media", "travel-hospitality"]


def test_the_six_default_packs_exist():
    assert [p.parent.name for p in PACKS] == DEFAULT_IDS


@pytest.mark.parametrize("path", PACKS, ids=lambda p: p.parent.name)
def test_pack_is_valid_and_complete(path: Path):
    assert validate_file(path, "industry-pack.schema.json") == []
    pack = load_yaml(path)
    assert pack["id"] == path.parent.name
    assert pack["generated"] is False
    assert (path.parent / "notes.md").is_file()
    for field in ("sub_segments", "buying_committee_roles", "kpis", "regulators", "regulations", "connectors",
                  "search_seeds", "typical_objections"):
        assert pack[field], f"{pack['id']}: {field} is empty"
    for item in pack["regulators"] + pack["regulations"]:
        assert item["url"].startswith("https://"), item["name"]


@pytest.mark.parametrize("path", PACKS, ids=lambda p: p.parent.name)
def test_pack_connectors_exist_and_name_series_ids(path: Path):
    pack = load_yaml(path)
    known = registry.entries()
    for c in pack["connectors"]:
        assert c["id"] in known, f"{pack['id']}: unknown connector {c['id']}"
        assert c.get("queries") or c.get("series_ids"), f"{pack['id']}: {c['id']} has no queries or series"
    assert any(c.get("series_ids") for c in pack["connectors"]), "at least one data series per pack"


def test_packs_name_no_vendors():
    """Packs are scaffolding: no competitor or vendor names (only regulators, associations, public sources)."""
    text = " ".join(p.read_text() for p in PACKS).lower()
    for word in ("gartner", "forrester", "salesforce", "oracle", "epic systems", "microsoft"):
        assert word not in text
