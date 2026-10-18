"""The source register (FR-WEB-R-02, FR-WEB-R-03, FR-QA-03 groundwork)."""

import pytest

from scripts import sources
from scripts.state.launch_state import LaunchState
from scripts.util import dump_yaml
from scripts.validate import validate_file
from tests import factories as f


@pytest.fixture
def launch_dir(tmp_path):
    return LaunchState.create(tmp_path / "s", "s").dir


def _add(d, url, published="2026-01-01"):
    return sources.add(d, url=url, title="t", publisher="p", tier=2, excerpt="e", published=published)


def test_ids_count_up_and_duplicates_return_the_existing_id(launch_dir):
    assert _add(launch_dir, "https://example.org/a") == ("S1", True)
    assert _add(launch_dir, "https://example.org/b") == ("S2", True)
    assert _add(launch_dir, "https://EXAMPLE.org/a/") == ("S1", False)
    assert validate_file(launch_dir / "research" / "sources.json", "sources.schema.json") == []


def test_check_finds_unregistered_citations_and_old_sources(launch_dir):
    _add(launch_dir, "https://example.org/old", published="2020-01-01")
    doc = f.industry_research()
    doc["trends"][0]["summary"] = "claim [S1] and [S7]"
    dump_yaml(doc, launch_dir / "research" / "industry-ind-a.yaml")
    missing, old = sources.check(launch_dir)
    assert set(missing) == {"S7"}
    assert [s["id"] for s in old] == ["S1"]


def test_cli_add_prints_the_id(launch_dir, monkeypatch, capsys):
    monkeypatch.setattr(sources, "LAUNCHES_DIR", launch_dir.parent)
    args = ["add", "s", "--url", "https://example.org/x", "--title", "T", "--publisher", "P", "--tier", "1",
            "--excerpt", "E", "--published", "2026-02-02"]
    assert sources.main(args) == 0
    assert capsys.readouterr().out.strip() == "S1"
    assert sources.main(args[:-2] + ["--published", "Feb 2026"]) == 1
