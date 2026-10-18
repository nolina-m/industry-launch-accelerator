"""Intake: templates, launch-context.yaml and the gap report (FR-INP-01..06, FR-INT-02..08).

Tests fill in the real templates with short placeholder answers; no example brief is stored.
"""

import re

import pytest

from scripts.intake import gap_report, run_intake
from scripts.intake import markdown_template as md
from scripts.intake.fields import FIELDS
from scripts.state.launch_state import LaunchState, StateError
from scripts.util import TEMPLATES_DIR, dump_yaml, load_yaml
from scripts.validate import validate_file

BRIEF_TPL = (TEMPLATES_DIR / "inputs" / "product-brief.md").read_text()
POV_TPL = (TEMPLATES_DIR / "inputs" / "launch-pov.md").read_text()

FULL_ANSWERS = {
    "Product name": "Placeholder Product",
    "Company name": "Placeholder Co",
    "Launch date": "2027-03",
    "Launch size": "Major",
    "Problem statement": "Teams spend hours each week reconciling records by hand, which delays decisions "
                         "and causes costly errors.",
    "Who has the problem": "Operations leads at mid-size companies",
    "Current workarounds": "Spreadsheets and email threads",
    "What it is": "A placeholder product that reconciles records automatically and flags exceptions "
                  "for a person to review before anything is changed.",
    "Top capabilities": "- Capability one\n- Capability two\n- Capability three",
    "How it works": "It connects to existing systems, compares records nightly, and sends a review queue.",
    "Company size": "Mid-market",
    "Regions": "North America",
    "Primary buyer roles": "VP Operations signs, operations lead champions",
}


def fill(template: str, answers: dict[str, str]) -> str:
    """Put each answer on the line after its heading in the template."""
    out = template
    for heading, answer in answers.items():
        pattern = re.compile(rf"^(#{{2,3}} {re.escape(heading)}[^\n]*\n)", re.M)
        assert pattern.search(out), f"heading not in template: {heading}"
        out = pattern.sub(lambda m, a=answer: m.group(1) + a + "\n", out, count=1)
    return out


@pytest.fixture
def launch(tmp_path):
    state = LaunchState.create(tmp_path / "l", "l", "Test launch")
    (state.dir / "inputs" / "product-brief.md").write_text(BRIEF_TPL)
    (state.dir / "inputs" / "launch-pov.md").write_text(POV_TPL)
    return state


def write_brief(launch, answers):
    (launch.dir / "inputs" / "product-brief.md").write_text(fill(BRIEF_TPL, answers))


def write_pov(launch, answers):
    (launch.dir / "inputs" / "launch-pov.md").write_text(fill(POV_TPL, answers))


def field(context, path):
    section, key = path.split(".")
    return context["product_brief"][section][key]


# ------------------------------------------------------------------ templates
def test_every_brief_field_has_a_heading_in_the_template():
    headings = {md.heading_key(h) for h in re.findall(r"^### (.+)$", BRIEF_TPL, re.M)}
    for f in FIELDS:
        if f.section != "free_form":
            assert md.heading_key(f.label) in headings, f.label


def test_blank_templates_have_no_content():
    assert not md.has_content(BRIEF_TPL)
    assert not md.has_content(POV_TPL)
    assert not md.has_content((TEMPLATES_DIR / "inputs" / "brand-questionnaire.md").read_text())


def test_new_launch_gets_the_templates(tmp_path, monkeypatch):
    from scripts import launch as cli

    monkeypatch.setattr(cli, "LAUNCHES_DIR", tmp_path)
    cli.main(["new", "x"])
    names = sorted(p.name for p in (tmp_path / "x" / "inputs").glob("*.md"))
    assert names == ["brand-questionnaire.md", "launch-pov.md", "product-brief.md"]


def test_parse_ignores_guidance_comments():
    parsed = md.parse("## Basics (required)\n### Product name\n<!-- hint -->\nWidget\n")
    assert parsed["basics"]["fields"]["product_name"] == "Widget"


# ------------------------------------------------------------------ launch-context.yaml
def test_blank_inputs_make_every_required_field_missing(launch):
    context, _, _ = run_intake.run(launch.dir)
    assert all(field(context, f.path)["status"] == "missing" for f in FIELDS if f.required)
    assert context["launch_pov"]["text"] == ""
    assert validate_file(launch.dir / "launch-context.yaml", "launch-context.schema.json") == []


def test_filled_brief_records_values_and_source(launch):
    write_brief(launch, FULL_ANSWERS)
    context, _, _ = run_intake.run(launch.dir)
    for f in FIELDS:
        if f.required:
            assert field(context, f.path)["status"] == "provided", f.label
    assert field(context, "basics.launch_size")["value"] == "major"
    assert field(context, "solution.capabilities")["value"] == ["Capability one", "Capability two", "Capability three"]
    assert field(context, "basics.product_name")["source_file"] == "inputs/product-brief.md"


def test_thin_answers_are_flagged(launch):
    write_brief(launch, {**FULL_ANSWERS, "Problem statement": "It is slow.", "Top capabilities": "- Only one",
                         "Launch size": "big"})
    context, _, _ = run_intake.run(launch.dir)
    assert field(context, "problem.problem_statement")["status"] == "thin"
    assert field(context, "solution.capabilities")["status"] == "thin"
    assert field(context, "basics.launch_size")["status"] == "thin"


def test_placeholder_answers_count_as_missing(launch):
    write_brief(launch, {**FULL_ANSWERS, "Regions": "TBD"})
    context, _, _ = run_intake.run(launch.dir)
    assert field(context, "target.regions")["status"] == "missing"


def test_template_wins_over_agent_value_but_agent_value_fills_gaps(launch):
    run_intake.run(launch.dir)
    path = launch.dir / "launch-context.yaml"
    context = load_yaml(path)
    context["product_brief"]["target"]["regions"] = {
        "value": "Europe", "source_file": "inputs/brief/prd.md", "status": "provided"}
    context["product_brief"]["basics"]["product_name"] = {
        "value": "Other Name", "source_file": "inputs/brief/prd.md", "status": "provided"}
    dump_yaml(context, path)
    write_brief(launch, {"Product name": "Placeholder Product"})
    context, _, _ = run_intake.run(launch.dir)
    assert field(context, "basics.product_name")["value"] == "Placeholder Product"  # template wins
    assert field(context, "target.regions")["value"] == "Europe"  # kept: template still empty


def test_pov_text_and_industries_are_read(launch):
    write_pov(launch, {"Target industries": "- Technology\n- Healthcare and life sciences: hospitals, US",
                       "The story we believe will win": "Placeholder story."})
    context, industries, _ = run_intake.run(launch.dir)
    assert "Placeholder story." in context["launch_pov"]["text"]
    assert industries == ["Technology", "Healthcare and life sciences: hospitals, US"]


def test_optional_inputs_are_classified_by_folder(launch):
    (launch.dir / "inputs" / "optional" / "win-loss").mkdir(parents=True)
    (launch.dir / "inputs" / "optional" / "win-loss" / "q1.md").write_text("notes")
    (launch.dir / "inputs" / "optional" / "misc.md").write_text("notes")
    context, _, _ = run_intake.run(launch.dir)
    kinds = {o["path"]: o["type"] for o in context["optional_inputs"]}
    assert kinds == {"inputs/optional/win-loss/q1.md": "win_loss", "inputs/optional/misc.md": "other"}
    assert all(o["permission"] == "unknown" for o in context["optional_inputs"])


def test_ai_product_first_guess(launch):
    write_brief(launch, {**FULL_ANSWERS, "What it is": "An AI agent platform that resolves tickets on its own "
                                                       "and hands off to a person when unsure."})
    context, _, _ = run_intake.run(launch.dir)
    assert context["is_ai_product"] is True


# ------------------------------------------------------------------ gaps
def gaps_after_intake(launch):
    run_intake.run(launch.dir)
    gaps, report = gap_report.run(launch.dir)
    return {g["id"]: g for g in gaps}, report


def test_missing_pov_and_industries_are_blocking(launch):
    write_brief(launch, FULL_ANSWERS)
    gaps, report = gaps_after_intake(launch)
    assert gaps["G-launch-pov"]["severity"] == "blocking"
    assert gaps["G-industries"]["severity"] == "blocking"
    assert "Blocking gaps still open:** 2" in report


def test_required_fields_block_and_recommended_fields_become_assumptions(launch):
    write_brief(launch, {k: v for k, v in FULL_ANSWERS.items() if k != "Regions"})
    write_pov(launch, {"The story we believe will win": "Placeholder story."})
    gaps, report = gaps_after_intake(launch)
    assert gaps["G-field-target-regions"]["severity"] == "blocking"
    value_gap = gaps["G-field-value-customer-outcomes"]
    assert value_gap["severity"] == "non_blocking" and value_gap["status"] == "assumed"
    assert "[ASSUMPTION]" in value_gap["assumption"]
    assert "## Assumptions" in report


def test_ai_questions_only_for_ai_products(launch):
    write_brief(launch, FULL_ANSWERS)
    gaps, _ = gaps_after_intake(launch)
    assert not any(g.startswith("G-field-ai-specifics") for g in gaps)


def test_no_brand_input_is_a_non_blocking_gap(launch):
    gaps, _ = gaps_after_intake(launch)
    assert gaps["G-brand"]["severity"] == "non_blocking"
    assert "Unbranded draft" in gaps["G-brand"]["assumption"]


def test_contradictions_become_blocking_questions(launch):
    run_intake.run(launch.dir)
    path = launch.dir / "launch-context.yaml"
    context = load_yaml(path)
    context["conflicts"] = [{"field": "target.primary_buyer_roles", "values": [
        {"value": "CIO", "source_file": "inputs/brief/a.md"},
        {"value": "VP Operations", "source_file": "inputs/brief/b.md"}]}]
    dump_yaml(context, path)
    gaps, report = gap_report.run(launch.dir)
    conflict = next(g for g in gaps if g["id"] == "G-conflict-1")
    assert conflict["severity"] == "blocking"
    assert "CIO" in conflict["question"] and "VP Operations" in conflict["question"]
    assert "## Contradictions" in report


def test_at_most_seven_questions_blocking_first(launch):
    write_brief(launch, {"Product name": "Placeholder Product"})
    gaps, report = gaps_after_intake(launch)
    questions = gap_report.questions_this_round(list(gaps.values()))
    assert len(questions) == 7
    assert all(q["severity"] == "blocking" for q in questions)
    assert questions[0]["id"] == "G-launch-pov"
    assert report.count("_(blocking:") == 7


def test_empty_brief_asks_once_instead_of_field_by_field(launch):
    gaps, report = gaps_after_intake(launch)
    questions = gap_report.questions_this_round(list(gaps.values()))
    assert [q["id"] for q in questions] == ["G-launch-pov", "G-industries", "G-brief-empty"] + [
        q["id"] for q in questions[3:]]
    assert not any(q["id"].startswith("G-field-basics") for q in questions)
    assert "G-field-basics-product-name" in report  # still listed as a blocking gap


def test_agent_wording_waivers_and_own_gaps_survive_a_rerun(launch):
    gaps_after_intake(launch)
    path = launch.dir / "launch-context.yaml"
    context = load_yaml(path)
    for g in context["gaps"]:
        if g["id"] == "G-field-target-regions":
            g["status"] = "waived"
        if g["id"] == "G-field-solution-capabilities":
            g["question"] = "Which 3 capabilities would an operations lead notice first?"
    context["gaps"].append({"id": "G-agent-1", "field": "proof.metrics", "severity": "non_blocking",
                            "status": "open", "question": "Can the pilot numbers be shared externally?"})
    dump_yaml(context, path)
    gaps, _ = gaps_after_intake(launch)
    assert gaps["G-field-target-regions"]["status"] == "waived"
    assert gaps["G-field-solution-capabilities"]["question"].startswith("Which 3 capabilities")
    assert gaps["G-agent-1"]["question"] == "Can the pilot numbers be shared externally?"


def test_answered_field_closes_its_gap(launch):
    gaps_after_intake(launch)
    path = launch.dir / "launch-context.yaml"
    context = load_yaml(path)
    context["product_brief"]["target"]["regions"] = {
        "value": "North America", "source_file": "inputs/intake-answers.md", "status": "answered"}
    dump_yaml(context, path)
    gaps, _ = gap_report.run(launch.dir)
    assert "G-field-target-regions" not in {g["id"] for g in gaps}


# ------------------------------------------------------------------ checkpoint
def test_intake_cannot_be_approved_with_open_blocking_gaps(launch):
    from scripts.brand import extract_brand

    launch.start("intake")
    write_brief(launch, FULL_ANSWERS)
    run_intake.run(launch.dir)
    extract_brand.run(launch.dir)
    gap_report.run(launch.dir)
    launch.submit("intake")
    with pytest.raises(StateError, match="G-launch-pov"):
        launch.approve("intake")


def test_acceptance_inputs_to_valid_context_brand_and_gap_report(launch):
    """M2 acceptance: inputs -> valid launch-context.yaml, brand.yaml, gap report with both gap kinds."""
    from scripts.brand import extract_brand

    launch.start("intake")
    write_brief(launch, FULL_ANSWERS)
    write_pov(launch, {"Target industries": "- Technology", "The story we believe will win": "Placeholder story."})
    run_intake.run(launch.dir)
    context = load_yaml(launch.dir / "launch-context.yaml")
    context["industries"] = [{"id": "technology", "name": "Technology"}]
    dump_yaml(context, launch.dir / "launch-context.yaml")
    extract_brand.run(launch.dir)
    gaps, report = gap_report.run(launch.dir)

    assert validate_file(launch.dir / "launch-context.yaml", "launch-context.schema.json") == []
    assert validate_file(launch.dir / "brand.yaml", "brand.schema.json") == []
    assert gap_report.open_blocking(gaps) == []
    assert any(g["severity"] == "non_blocking" for g in gaps)

    launch.submit("intake")
    launch.approve("intake")
    assert launch.status("intake") == "approved"


def test_gap_report_lists_blocking_and_non_blocking(launch):
    write_brief(launch, {k: v for k, v in FULL_ANSWERS.items() if k != "Regions"})
    _, report = gaps_after_intake(launch)
    assert "## Blocking gaps" in report and "G-field-target-regions" in report
    assert "## Assumptions" in report and "value.customer_outcomes" in report
