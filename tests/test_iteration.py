"""Refresh, item-level impact and edit sync (FR-REF-01..04, FR-STA-04, FR-STA-05, M7)."""

import json

import pytest

from connectors.base import Response
from scripts import launch as cli
from scripts.refresh.refresh import refresh
from scripts.render.render import Renderer
from scripts.sources import add as add_source
from scripts.state import edits
from scripts.state.hashing import hash_files
from scripts.state.launch_state import LaunchState
from scripts.util import dump_yaml, load_yaml
from tests import factories as f
from tests.test_state import write_outputs

IND = ["ind-a", "ind-b"]


def persona(pid, industry, pain):
    p = f.personas(industry)["personas"][0]
    p.update(id=pid, pains=[{"text": pain, "trend_ids": ["T-1"]}])
    return p


def write_unit(d, unit):
    """Like tests.test_state.write_outputs, with distinct persona ids per industry and richer research."""
    stage, _, ind = unit.partition(":")
    if stage == "research":
        doc = f.industry_research(ind)
        doc["regulatory"]["items"] = [{"id": "R-1", "name": "Placeholder Act (PA)", "jurisdiction": "US",
                                       "status": "in_force", "summary": "s [S1]", "relevance": "r",
                                       "evidence": [{"source_id": "S1"}]}]
        doc["market_data"] = [{"id": f"MD-{ind}-1", "label": "Employment", "value": 1000, "unit": "jobs",
                               "source_id": "S1", "connector": "bls", "series_id": "CES0000000001",
                               "retrieved_at": "2026-01-01"}]
        dump_yaml(doc, d / f"research/industry-{ind}.yaml")
    elif stage == "personas":
        doc = f.personas(ind)
        doc["personas"] = [persona(f"P-{ind}-cfo", ind, f"{ind} pain one"),
                           persona(f"P-{ind}-cio", ind, f"{ind} pain two")]
        doc["committee_map"]["decision_sequence"] = [f"P-{ind}-cfo"]
        dump_yaml(doc, d / f"personas/{ind}.yaml")
    elif stage == "messaging":
        doc = f.messaging(IND)
        doc["grid"] = [{**doc["grid"][0], "industry": i, "persona_id": f"P-{i}-{r}", "pain_ref": f"P-{i}-{r}#1"}
                       for i in IND for r in ("cfo", "cio")]
        dump_yaml(doc, d / "messaging.yaml")
    elif stage == "playbook":
        doc = f.playbook(ind)
        doc["value_story"] = [{"persona_id": f"P-{ind}-{r}", "message": "m", "pillar_id": "PL-1"}
                              for r in ("cfo", "cio")]
        dump_yaml(doc, d / f"playbooks/{ind}.yaml")
    else:
        write_outputs(d, unit)


@pytest.fixture
def launch(tmp_path):
    s = LaunchState.create(tmp_path / "it", "it", "Iteration test")
    for i in IND:
        s.data["industries"].append({"id": i, "name": i.upper()})
    s.data["competitors"].append({"id": "comp-a", "name": "Competitor A", "suggested": False})
    s.refresh()
    add_source(s.dir, url="https://example.org/a", title="Source A", publisher="Pub A", tier=1, excerpt="e",
               published="2026-01-01")
    for unit in [u for u in s.units if u != "qa"]:
        s.start(unit)
        write_unit(s.dir, unit)
        s.submit(unit)
        s.approve(unit)
    s.save()
    return s


# ------------------------------------------------------------------ item-level impact (FR-STA-04)
def test_one_persona_change_points_to_its_grid_rows_and_playbook_items(launch):
    d = launch.dir
    doc = load_yaml(d / "personas/ind-a.yaml")
    doc["personas"][0]["pains"][0]["text"] = "a sharper pain"
    dump_yaml(doc, d / "personas/ind-a.yaml")
    launch.approve("personas:ind-a")

    # Only assets downstream of that industry's personas are stale.
    assert launch.status("messaging") == "stale" and launch.status("playbook:ind-a") == "stale"
    assert launch.status("personas:ind-b") == "approved" and launch.status("research:ind-a") == "approved"

    [entry] = launch.impact("messaging")
    assert entry["source"] == "personas:ind-a"
    assert entry["changes"][0].changed == ["P-ind-a-cfo"]
    assert entry["refs"] == [("messaging.yaml", "grid[0]", "P-ind-a-cfo")]  # not ind-b rows, not the cio row
    playbook = {r[1] for e in launch.impact("playbook:ind-a") for r in e["refs"]}
    assert playbook == {"value_story[0]"}


def test_edited_unit_shows_what_was_edited(launch):
    d = launch.dir
    doc = load_yaml(d / "messaging.yaml")
    doc["elevator_pitch"] = "edited pitch"
    doc["pillars"][0]["headline"] = "edited pillar"
    dump_yaml(doc, d / "messaging.yaml")
    launch.refresh()
    [entry] = launch.impact("messaging")
    change = entry["changes"][0]
    assert change.changed == ["PL-1"] and change.fields == ["elevator_pitch"]


def test_status_prints_the_parts_to_redo(launch, monkeypatch, capsys):
    doc = load_yaml(launch.dir / "personas/ind-b.yaml")
    doc["personas"][1]["pains"][0]["text"] = "changed"
    dump_yaml(doc, launch.dir / "personas/ind-b.yaml")
    launch.approve("personas:ind-b")
    launch.save()
    monkeypatch.setattr(cli, "LAUNCHES_DIR", launch.dir.parent)
    cli.main(["status", launch.dir.name])
    out = capsys.readouterr().out
    assert "personas:ind-b: personas/ind-b.yaml: changed P-ind-b-cio" in out
    assert "-> messaging.yaml: grid[3] (uses P-ind-b-cio)" in out


def test_no_snapshot_means_review_whole_asset(launch):
    import shutil

    shutil.rmtree(launch.dir / ".approved")
    doc = load_yaml(launch.dir / "personas/ind-a.yaml")
    doc["personas"][0]["pains"][0]["text"] = "x"
    dump_yaml(doc, launch.dir / "personas/ind-a.yaml")
    launch.approve("personas:ind-a")
    assert launch.impact("messaging") == []


# ------------------------------------------------------------------ edit sync (FR-STA-05)
def test_hand_edits_are_detected_protected_and_synced(launch, monkeypatch, capsys):
    d = launch.dir
    Renderer(d).render_all()
    md = d / "outputs" / "05-messaging-framework.md"
    md.write_text(md.read_text().replace("## Elevator pitch\n\ne\n", "## Elevator pitch\n\nA sharper pitch.\n"))
    assert edits.edited_outputs(d) == ["05-messaging-framework.md"]

    renderer = Renderer(d)
    renderer.render_all()
    assert renderer.kept == ["05-messaging-framework.md"]
    assert "A sharper pitch." in md.read_text()  # not overwritten

    monkeypatch.setattr(cli, "LAUNCHES_DIR", d.parent)
    cli.main(["edits", d.name])
    out = capsys.readouterr().out
    assert "source of truth: messaging.yaml" in out and "+A sharper pitch." in out and "-e" in out
    cli.main(["start", d.name, "web:ind-a"])
    assert "edited 1 rendered file" in capsys.readouterr().out

    # The agent copies the edit into the YAML, then re-renders with --force.
    doc = load_yaml(d / "messaging.yaml")
    doc["elevator_pitch"] = "A sharper pitch."
    dump_yaml(doc, d / "messaging.yaml")
    cli.main(["render", d.name, "--force"])
    assert edits.edited_outputs(d) == []
    assert "A sharper pitch." in md.read_text()


def test_discard_puts_back_the_rendered_version(launch, monkeypatch):
    Renderer(launch.dir).render_all()
    md = launch.dir / "outputs" / "03-strategy-check.md"
    original = md.read_text()
    md.write_text(original + "\nstray edit\n")
    monkeypatch.setattr(cli, "LAUNCHES_DIR", launch.dir.parent)
    cli.main(["edits", launch.dir.name, "--discard", "03-strategy-check.md"])
    assert md.read_text() == original


# ------------------------------------------------------------------ refresh (FR-REF-01..04)
class FakeSources:
    """Answers connector requests from editable in-memory data."""

    def __init__(self):
        self.articles = [("https://news.example.org/old", "Old story", "20251201T000000Z"),
                         ("https://news.example.org/launch", "Competitor A launches a new tier", "20260301T000000Z")]
        self.rules = [("2026-00001", "Placeholder Act amendments (proposed)", "2026-04-01")]
        self.bls_value = "1,050"

    def __call__(self, method, url, params, headers, body, timeout):
        if "gdeltproject" in url:
            return Response(200, json.dumps({"articles": [{"url": u, "title": t, "seendate": s, "domain": "x"}
                                                          for u, t, s in self.articles]}))
        if "algolia" in url:
            return Response(200, json.dumps({"hits": []}))
        if "federalregister" in url:
            return Response(200, json.dumps({"results": [
                {"document_number": n, "title": t, "html_url": f"https://www.federalregister.gov/d/{n}",
                 "publication_date": p, "type": "Proposed Rule", "agencies": []} for n, t, p in self.rules]}))
        if "europa.eu" in url:
            return Response(200, json.dumps({"results": {"bindings": []}}))
        if "api.bls.gov" in url:
            return Response(200, json.dumps({"status": "REQUEST_SUCCEEDED", "message": [], "Results": {"series": [
                {"seriesID": "CES0000000001", "data": [{"year": "2026", "period": "M09", "periodName": "September",
                                                        "latest": "true", "value": self.bls_value}]}]}}))
        return Response(404, "not recorded")


def run_refresh(launch, fake, day, links=None):
    return refresh(launch.dir, env={}, transport=fake, link_checker=links, sleep=lambda s: None, day=day)


def test_first_refresh_reports_changes_since_research(launch):
    fake = FakeSources()
    result = run_refresh(launch, fake, "2026-10-18")
    titles = [c.title for c in result.changes]
    assert "Competitor A launches a new tier" in titles
    assert "Old story" not in titles  # published before the research date
    assert "Placeholder Act amendments (proposed)" in titles
    assert any(t.startswith("MD-ind-a-1: new value 1050") for t in titles)
    report = (result.folder / "what-changed.md").read_text()
    assert "## Competitor news" in report and "## Regulation" in report and "## Market data" in report
    assert "- **Affects:** Battlecards and competitive overview (Recent moves)" in report
    assert "- **Suggested action:**" in report and "The brief cites 1000" in report
    assert "## Not checked" in report  # keyed sources without a key, SEC without a contact email
    assert (result.folder / "changes.yaml").exists() and (result.folder / "snapshot.json").exists()


def test_second_refresh_reports_only_what_is_new(launch):
    fake = FakeSources()
    run_refresh(launch, fake, "2026-10-18")
    fake.articles.append(("https://news.example.org/funding", "Competitor A raises funding", "20261025T000000Z"))
    fake.bls_value = "1000"  # back to the cited value: no market change
    result = run_refresh(launch, fake, "2026-11-01")
    titles = [c.title for c in result.changes]
    assert titles == ["Competitor A raises funding"]
    assert result.baseline == "2026-10-18"
    assert "_Compared with 2026-10-18." in (result.folder / "what-changed.md").read_text()


def test_refresh_checks_source_health(launch):
    add_source(launch.dir, url="https://example.org/gone", title="Gone", publisher="P", tier=2, excerpt="e",
               published="2023-01-01")
    result = run_refresh(launch, FakeSources(), "2026-10-18",
                         links=lambda url: 404 if url.endswith("/gone") else 200)
    health = [c.title for c in result.changes if c.category == "source health"]
    assert any("S2 no longer answers (404)" in t for t in health)
    assert any("S2 is older than 24 months" in t for t in health)


def test_refresh_never_changes_approved_assets(launch):
    assets = ["research/industry-*.yaml", "research/sources.json", "competitors/", "personas/", "messaging.yaml",
              "playbooks/", "demos/", "web/", "strategy-check.yaml", "outputs/"]
    before = hash_files(launch.dir, assets)
    statuses = {u: launch.status(u) for u in launch.units}
    run_refresh(launch, FakeSources(), "2026-10-18")
    after = hash_files(launch.dir, assets)
    assert before == after
    state = LaunchState.load(launch.dir)
    state.refresh()
    assert {u: state.status(u) for u in state.units} == statuses


def test_refresh_fails_soft_when_everything_is_offline(launch):
    def offline(*args):
        raise ConnectionError("offline")

    result = refresh(launch.dir, env={}, transport=offline, sleep=lambda s: None, day="2026-10-18")
    assert result.changes == [] and result.unavailable
    assert "Nothing could be checked" in (result.folder / "what-changed.md").read_text()


def test_kit_links_the_latest_refresh(launch):
    from scripts.qa.kit import write_kit

    run_refresh(launch, FakeSources(), "2026-10-18")
    kit = write_kit(launch.dir).read_text()
    assert "[refresh/2026-10-18/what-changed.md](refresh/2026-10-18/what-changed.md)" in kit
