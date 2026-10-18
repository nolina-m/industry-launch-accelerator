"""Stage transitions, checkpoints and staleness (FR-STA-01..04, FR-STR-05)."""

from pathlib import Path

import pytest

from scripts import launch as cli
from scripts.state.launch_state import LaunchState, StateError
from scripts.state.pipeline import build_units, downstream_of
from scripts.util import dump_yaml, load_yaml
from tests import factories as f

INDUSTRIES = ["ind-a", "ind-b"]


def write_outputs(d: Path, unit: str) -> None:
    """Write minimal valid files for one stage unit."""
    stage, _, ind = unit.partition(":")
    if stage == "intake":
        dump_yaml(f.launch_context(INDUSTRIES), d / "launch-context.yaml")
        dump_yaml(f.brand(), d / "brand.yaml")
        (d / "gap-report.md").write_text("# Gap report\n")
    elif stage == "research":
        dump_yaml(f.industry_research(ind), d / f"research/industry-{ind}.yaml")
    elif stage == "competitive":
        dump_yaml(f.competitor(), d / "competitors/comp-a.yaml")
        dump_yaml(f.competitive_overview(), d / "competitive-overview.yaml")
    elif stage == "strategy":
        dump_yaml(f.strategy_check(), d / "strategy-check.yaml")
    elif stage == "personas":
        dump_yaml(f.personas(ind), d / f"personas/{ind}.yaml")
    elif stage == "messaging":
        dump_yaml(f.messaging(INDUSTRIES), d / "messaging.yaml")
    elif stage == "playbook":
        dump_yaml(f.playbook(ind), d / f"playbooks/{ind}.yaml")
    elif stage == "demo":
        dump_yaml(f.demo(ind), d / f"demos/{ind}.yaml")
    elif stage == "web":
        dump_yaml(f.web(ind), d / f"web/{ind}.yaml")
    elif stage == "qa":
        (d / "qa-report.md").write_text("# QA\n")
        (d / "LAUNCH-KIT.md").write_text("# Kit\n")


def complete(state: LaunchState, unit: str) -> None:
    state.start(unit)
    write_outputs(state.dir, unit)
    state.submit(unit)
    if not state.auto_mode:
        state.approve(unit)


@pytest.fixture
def state(tmp_path):
    s = LaunchState.create(tmp_path / "t", "t")
    for i in INDUSTRIES:
        s.data["industries"].append({"id": i, "name": i})
    (s.dir / "inputs" / "product-brief.md").write_text("brief v1")
    s.refresh()
    return s


@pytest.fixture
def approved_state(state):
    for name in state.units:
        complete(state, name)
    return state


def statuses(state):
    return {name: state.status(name) for name in state.units}


# ------------------------------------------------------------------ pipeline shape
def test_units_follow_the_pipeline():
    units = build_units(["x"])
    assert list(units) == [
        "intake", "research:x", "competitive", "strategy", "personas:x",
        "messaging", "playbook:x", "demo:x", "web:x", "qa",
    ]
    assert units["research:x"].deps == ("intake",)
    assert units["competitive"].deps == ("intake",)
    assert set(units["strategy"].deps) == {"research:x", "competitive"}


def test_downstream_of_personas_is_only_that_industry_plus_shared_stages():
    units = build_units(INDUSTRIES)
    assert downstream_of(units, "personas:ind-a") == [
        "messaging", "playbook:ind-a", "playbook:ind-b", "demo:ind-a", "demo:ind-b",
        "web:ind-a", "web:ind-b", "qa",
    ]


# ------------------------------------------------------------------ transitions
def test_new_launch_starts_everything_not_started(state):
    assert set(statuses(state).values()) == {"not_started"}
    assert (state.dir / "inputs" / "brief").is_dir()


def test_invalid_slug_is_refused(tmp_path):
    with pytest.raises(StateError):
        LaunchState.create(tmp_path / "x", "My Launch!")


def test_downstream_refuses_to_start_until_upstream_approved(state):
    with pytest.raises(StateError, match="intake"):
        state.start("research:ind-a")
    state.start("intake")
    write_outputs(state.dir, "intake")
    state.submit("intake")
    assert state.status("intake") == "awaiting_approval"
    with pytest.raises(StateError, match="awaiting approval"):
        state.start("research:ind-a")
    state.approve("intake")
    state.start("research:ind-a")
    assert state.status("research:ind-a") == "in_progress"


def test_stages_one_and_two_only_need_intake(state):
    complete(state, "intake")
    state.start("research:ind-a")
    state.start("competitive")  # parallel-capable


def test_strategy_needs_every_industry_researched(state):
    complete(state, "intake")
    complete(state, "research:ind-a")
    complete(state, "competitive")
    with pytest.raises(StateError, match="research:ind-b"):
        state.start("strategy")


def test_submit_requires_outputs(state):
    state.start("intake")
    with pytest.raises(StateError, match="missing files"):
        state.submit("intake")


def test_submit_rejects_invalid_files(state):
    state.start("intake")
    write_outputs(state.dir, "intake")
    bad = f.brand()
    bad["colors"]["primary"] = "red"
    dump_yaml(bad, state.dir / "brand.yaml")
    with pytest.raises(StateError, match="schema"):
        state.submit("intake")


def test_cannot_approve_work_in_progress(state):
    state.start("intake")
    with pytest.raises(StateError, match="in progress"):
        state.approve("intake")


def test_redo_an_approved_stage(state):
    complete(state, "intake")
    state.start("intake")
    assert state.status("intake") == "in_progress"


def test_strategy_check_needs_a_pmm_response_for_every_point(state):
    for u in ["intake", "research:ind-a", "research:ind-b", "competitive"]:
        complete(state, u)
    state.start("strategy")
    dump_yaml(f.strategy_check(responded=False), state.dir / "strategy-check.yaml")
    state.submit("strategy")
    with pytest.raises(StateError, match="SC-1"):
        state.approve("strategy")
    dump_yaml(f.strategy_check(responded=True), state.dir / "strategy-check.yaml")
    state.approve("strategy")
    stored = load_yaml(state.dir / "strategy-check.yaml")
    assert stored["points"][0]["pmm_response"]["decision"] == "accept"


def test_auto_mode_approves_without_review(state):
    state.set_auto_mode(True)
    complete(state, "intake")
    rec = state.record("intake")
    assert rec["status"] == "approved" and rec["reviewed"] is False


def test_auto_mode_marks_strategy_responses_not_reviewed(state):
    state.set_auto_mode(True)
    for u in ["intake", "research:ind-a", "research:ind-b", "competitive"]:
        complete(state, u)
    state.start("strategy")
    dump_yaml(f.strategy_check(responded=False), state.dir / "strategy-check.yaml")
    state.submit("strategy")
    assert state.status("strategy") == "approved"
    doc = load_yaml(state.dir / "strategy-check.yaml")
    assert doc["points"][0]["pmm_response"]["decision"] == "not_reviewed"


def test_full_pipeline_approves(approved_state):
    assert set(statuses(approved_state).values()) == {"approved"}


def test_launch_yaml_round_trips_and_validates(approved_state):
    approved_state.save()
    reloaded = LaunchState.load(approved_state.dir)
    assert statuses(reloaded) == statuses(approved_state)


# ------------------------------------------------------------------ staleness
def test_persona_edit_marks_only_affected_assets_stale(approved_state):
    s = approved_state
    dump_yaml(f.personas("ind-a", pain="changed pain"), s.dir / "personas/ind-a.yaml")
    s.refresh()
    st = statuses(s)
    assert st["personas:ind-a"] == "awaiting_approval"  # edited after approval
    for name in ["messaging", "playbook:ind-a", "demo:ind-a", "web:ind-a", "qa"]:
        assert st[name] == "stale", name
    # Everything upstream, and the other industry's personas, are untouched.
    for name in ["intake", "research:ind-a", "research:ind-b", "competitive", "strategy", "personas:ind-b"]:
        assert st[name] == "approved", name


def test_reapproving_upstream_names_the_changed_input(approved_state):
    s = approved_state
    dump_yaml(f.personas("ind-a", pain="changed pain"), s.dir / "personas/ind-a.yaml")
    s.approve("personas:ind-a")
    assert s.status("messaging") == "stale"
    assert s.record("messaging")["stale_reasons"] == ["personas:ind-a changed"]
    # Sales assets for the other industry depend on messaging, so they wait on it.
    assert s.status("playbook:ind-b") == "stale"


def test_undoing_a_change_clears_staleness(approved_state):
    s = approved_state
    original = (s.dir / "research/industry-ind-b.yaml").read_text()
    (s.dir / "research/industry-ind-b.yaml").write_text(original + "# note\n")
    s.refresh()
    assert s.status("strategy") == "stale"
    (s.dir / "research/industry-ind-b.yaml").write_text(original)
    s.refresh()
    assert set(statuses(s).values()) == {"approved"}


def test_changing_an_input_file_makes_everything_stale(approved_state):
    s = approved_state
    (s.dir / "inputs" / "product-brief.md").write_text("brief v2")
    s.refresh()
    st = statuses(s)
    assert st["intake"] == "stale"
    assert all(v == "stale" for k, v in st.items() if k != "intake")


def test_stale_stage_can_be_approved_as_is(approved_state):
    s = approved_state
    (s.dir / "inputs" / "product-brief.md").write_text("brief v2")
    s.refresh()
    assert s.status("research:ind-a") == "stale"
    # The PMM reviews intake and keeps it as is: its files did not change, so the
    # research built on them is valid again without being redone.
    s.approve("intake")
    assert set(statuses(s).values()) == {"approved"}


def test_adding_an_industry_makes_shared_stages_stale(approved_state):
    s = approved_state
    s.data["industries"].append({"id": "ind-c", "name": "ind-c"})
    s.refresh()
    assert s.status("research:ind-c") == "not_started"
    assert s.status("strategy") == "stale"
    assert "research:ind-c is not started" in s.record("strategy")["stale_reasons"]


def test_removing_an_industry_drops_its_stages(approved_state):
    s = approved_state
    s.data["industries"] = [i for i in s.data["industries"] if i["id"] != "ind-b"]
    changes = s.refresh()
    assert "research:ind-b" not in s.data["stages"]
    assert any(c.unit == "research:ind-b" and c.new == "removed" for c in changes)


# ------------------------------------------------------------------ command line
@pytest.fixture
def cli_home(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "LAUNCHES_DIR", tmp_path)
    return tmp_path


def test_cli_new_status_and_approve(cli_home, capsys):
    assert cli.main(["new", "demo-run", "--name", "Demo run"]) == 0
    assert (cli_home / "demo-run" / "launch.yaml").exists()
    assert cli.main(["add-industry", "demo-run", "ind-a"]) == 0
    assert cli.main(["start", "demo-run", "research:ind-a"]) == 1
    assert "need to be approved first" in capsys.readouterr().out
    assert cli.main(["start", "demo-run", "intake"]) == 0
    write_outputs(cli_home / "demo-run", "intake")
    assert cli.main(["submit", "demo-run", "intake"]) == 0
    assert cli.main(["status", "demo-run"]) == 0
    out = capsys.readouterr().out
    assert "AWAITING YOUR APPROVAL" in out and "review intake" in out
    assert cli.main(["approve", "demo-run", "intake"]) == 0
    assert cli.main(["new", "demo-run"]) == 1  # already exists


def test_cli_options_and_competitors(cli_home):
    cli.main(["new", "x"])
    assert cli.main(["set-option", "x", "name_competitors_in_customer_copy", "true"]) == 0
    assert cli.main(["set-option", "x", "nonsense", "true"]) == 1
    assert cli.main(["add-competitor", "x", "comp-a", "--name", "Competitor A", "--suggested"]) == 0
    assert cli.main(["auto", "x", "on"]) == 0
    data = load_yaml(cli_home / "x" / "launch.yaml")
    assert data["options"] == {"name_competitors_in_customer_copy": True, "auto_mode": True}
    assert data["competitors"] == [{"id": "comp-a", "name": "Competitor A", "suggested": True}]
