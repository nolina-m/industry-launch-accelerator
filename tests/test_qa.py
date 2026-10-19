"""QA checks: each one catches its seeded defect (FR-QA-01..08, FR-TST-02).

Each test starts from a complete launch built from minimal inline data, plants one
defect, and checks that the right check reports it, and didn't before.
"""

import zipfile

import pytest

from scripts.qa import content_checks as cc
from scripts.qa import output_checks as oc
from scripts.qa.kit import write_kit
from scripts.qa.run import run
from scripts.render.render import Renderer
from scripts.sources import add as add_source
from scripts.state.launch_state import LaunchState
from scripts.util import dump_yaml, load_yaml
from tests.test_state import INDUSTRIES, write_outputs

ALL_BUT_QA = ["intake", "research:ind-a", "research:ind-b", "competitive", "strategy", "personas:ind-a",
              "personas:ind-b", "messaging", "playbook:ind-a", "playbook:ind-b", "demo:ind-a", "demo:ind-b",
              "web:ind-a", "web:ind-b"]


@pytest.fixture
def launch(tmp_path):
    s = LaunchState.create(tmp_path / "qa", "qa", "QA test")
    for i in INDUSTRIES:
        s.data["industries"].append({"id": i, "name": i.upper()})
    s.data["competitors"].append({"id": "comp-a", "name": "Competitor A", "suggested": False})
    s.refresh()
    for unit in ALL_BUT_QA:
        s.start(unit)
        write_outputs(s.dir, unit)
        s.submit(unit)
        s.approve(unit)
    s.save()
    add_source(s.dir, url="https://example.org/a", title="Source A", publisher="Publisher A", tier=1,
               excerpt="e", published="2026-01-01")
    add_source(s.dir, url="https://example.org/b", title="Source B", publisher="Publisher B", tier=2,
               excerpt="e", published="2026-02-01")
    return s.dir


def messages(result):
    return [x.message for x in result.findings]


def edit(launch_dir, rel, change):
    doc = load_yaml(launch_dir / rel)
    change(doc)
    dump_yaml(doc, launch_dir / rel)


# ------------------------------------------------------------------ FR-QA-01
def test_structure_catches_schema_error(launch):
    assert cc.check_structure(launch).status == "pass"
    edit(launch, "messaging.yaml", lambda d: d.pop("boilerplate"))
    assert any("boilerplate" in m for m in messages(cc.check_structure(launch)))


# ------------------------------------------------------------------ FR-QA-02
def test_citations_catch_an_uncited_claim(launch):
    before = cc.check_citations(launch)
    assert before.status == "pass"
    edit(launch, "research/industry-ind-a.yaml",
         lambda d: d["trends"][0].update(impact="Spending grew 42% in 2025 at hospitals."))
    after = cc.check_citations(launch)
    assert any("Uncited number or date" in m and "42%" in m for m in messages(after))
    assert after.errors == 1  # coverage fell below 95%


def test_labels_and_structured_sources_count_as_cited(launch):
    edit(launch, "research/industry-ind-a.yaml", lambda d: d["trends"][0].update(
        impact="Spending grew 42% in 2025 [S1]. Costs may double by 2030 [ASSUMPTION]. "
               "The new Act takes effect in 2027 [VERIFY] check the regulator's site."))
    assert cc.check_citations(launch).status == "pass"


def test_citations_catch_named_company_and_regulatory_claims():
    names = ["Competitor A"]
    assert "named company" in cc.claim_kinds("Competitor A leads the market.", names)
    assert "regulatory statement" in cc.claim_kinds("The regulation requires annual audits.", names)
    assert cc.claim_kinds("Teams want faster answers.", names) == []
    assert cc.claim_kinds("See T-ind-a-1 and PL-2.", names) == []  # IDs are not numbers
    assert cc.claim_kinds("Act on changes the same day", names) == []  # a verb, not a law
    assert "regulatory statement" in cc.claim_kinds("The Placeholder Act took effect.", names)
    assert "regulatory statement" in cc.claim_kinds("Regulation (EU) 2024/1689 applies.", names)


@pytest.mark.parametrize("sentence", [
    "Watches whether scheduling rules are followed and the reschedule finishes without staff.",
    "Clear exception categories that map to handoff rules.",
    "Strong internal engineering with a build mandate.",
    "Documented rules that could be configured, not tribal knowledge only.",
    "Approval is required before the agent acts.",
])
def test_everyday_words_are_not_regulatory_claims(sentence):
    assert "regulatory statement" not in cc.claim_kinds(sentence, [])


@pytest.mark.parametrize("sentence", [
    "The proposed rule would shorten decision timeframes.",
    "Regulators expect a documented risk assessment.",
    "State privacy laws differ on consent.",
    "The FTC Safeguards Rule applies to consumer lenders.",
    "New regulations take effect in 2027.",
])
def test_legal_language_is_still_a_regulatory_claim(sentence):
    assert "regulatory statement" in cc.claim_kinds(sentence, [])


# ------------------------------------------------------------------ FR-QA-03
def test_sources_catch_unregistered_citation(launch):
    assert not any("S99" in m for m in messages(cc.check_sources(launch)))
    edit(launch, "research/industry-ind-a.yaml", lambda d: d["trends"][0].update(summary="Claim [S99]."))
    assert any("S99 is cited but not in" in m for m in messages(cc.check_sources(launch)))


def test_sources_flag_old_and_single_source_trends(launch):
    add_source(launch, url="https://example.org/old", title="Old", publisher="Old Pub", tier=1, excerpt="e",
               published="2020-01-01")
    edit(launch, "research/industry-ind-a.yaml",
         lambda d: d["trends"][0].update(evidence=[{"source_id": "S3"}]))
    msgs = messages(cc.check_sources(launch))
    assert any("older than 24 months" in m for m in msgs)
    assert any("no source from the last 24 months" in m for m in msgs)
    assert any("2 independent sources" in m for m in msgs)


def test_sources_require_tier_1_for_list_prices(launch):
    edit(launch, "competitors/comp-a.yaml", lambda d: d["pricing"].update(list_prices=[
        {"item": "Pro", "price": "$10", "source_id": "S2", "label": "list; enterprise deals typically differ"}]))
    assert any("needs a Tier 1 source" in m for m in messages(cc.check_sources(launch)))


def test_link_check_reports_dead_links(launch):
    result = cc.check_sources(launch, link_checker=lambda url: 404 if url.endswith("/b") else 200)
    assert any("S2 link didn't answer (404)" in m for m in messages(result))


# ------------------------------------------------------------------ FR-QA-04
def test_brand_passes_on_rendered_files(launch):
    """Regression: Word theme fonts/colors and Excel's default Calibri must not leak into branded files."""
    Renderer(launch).render_all()
    assert oc.check_brand(launch).status == "pass"


def test_brand_catches_off_palette_color(launch):
    Renderer(launch).render_all()
    path = launch / "outputs" / "03-strategy-check.docx"
    with zipfile.ZipFile(path) as z:
        parts = {n: z.read(n) for n in z.namelist()}
    parts["word/document.xml"] = parts["word/document.xml"].replace(
        b"<w:r>", b'<w:r><w:rPr><w:color w:val="FF00FF"/></w:rPr>', 1)
    with zipfile.ZipFile(path, "w") as z:
        for n, data in parts.items():
            z.writestr(n, data)
    assert any("#FF00FF" in m for m in messages(oc.check_brand(launch)))


def test_brand_catches_undeclared_font(launch):
    Renderer(launch).render_all()
    brand = load_yaml(launch / "brand.yaml")
    brand["fonts"] = {k: "Georgia" for k in brand["fonts"]}  # the files still use Arial
    dump_yaml(brand, launch / "brand.yaml")
    assert any("Fonts not declared" in m and "Arial" in m for m in messages(oc.check_brand(launch)))


def test_brand_catches_banned_term_preferred_term_and_product_caps(launch):
    brand = load_yaml(launch / "brand.yaml")
    brand["terms"] = {"banned": ["synergy"], "preferred": {"AI-powered": "AI-native"},
                      "product_names": ["PlaceholderOne"]}
    dump_yaml(brand, launch / "brand.yaml")
    edit(launch, "messaging.yaml", lambda d: d.update(
        elevator_pitch="Real synergy for teams.", boilerplate="placeholderone is AI-powered."))
    msgs = messages(oc.check_brand(launch))
    assert any('Banned term "synergy"' in m for m in msgs)
    assert any('instead of "AI-powered"' in m for m in msgs)
    assert any('written "placeholderone"' in m for m in msgs)


# ------------------------------------------------------------------ FR-QA-05
def test_layout_catches_empty_section(launch):
    Renderer(launch).render_all()
    md = launch / "outputs" / "05-messaging-framework.md"
    md.write_text(md.read_text().replace("## Elevator pitch\n\ne\n", "## Elevator pitch\n\n"))
    assert any('Empty section "Elevator pitch"' in m for m in messages(oc.check_layout(launch)))


def test_layout_catches_placeholder_broken_table_and_length(launch, monkeypatch):
    Renderer(launch).render_all()
    md = launch / "outputs" / "06-playbook-ind-a.md"
    md.write_text(md.read_text() + "\nTODO write this\n\n<built-in method copy of dict object at 0x10ac99f80>\n"
                  "\n| a | b |\n|---|---|\n| 1 | 2 | 3 |\n")
    (launch / "qa-limits.yaml").write_text("06-playbook: 10\n")
    msgs = messages(oc.check_layout(launch))
    assert any("Placeholder text" in m and "TODO" in m for m in msgs)
    assert any("Placeholder text" in m and "built-in method" in m for m in msgs)  # template printed an object
    assert any("Broken table" in m for m in msgs)
    assert any("the limit for this asset is 10" in m for m in msgs)


# ------------------------------------------------------------------ FR-QA-06
def test_sameness_catches_near_identical_personas(launch):
    edit(launch, "personas/ind-a.yaml", lambda d: d["personas"][0]["pains"][0].update(
        text="Clinicians lose hours each week to prior authorization paperwork"))
    edit(launch, "personas/ind-b.yaml", lambda d: d["personas"][0]["pains"][0].update(
        text="Branch staff can't see a member's full relationship during onboarding"))
    assert not any("have pains" in m for m in messages(cc.check_sameness(launch)))
    pain = "Month-end close takes too long because data lives in spreadsheets"
    for i in INDUSTRIES:
        edit(launch, f"personas/{i}.yaml", lambda d, p=pain: d["personas"][0]["pains"][0].update(text=p))
    result = cc.check_sameness(launch)
    assert any("have pains 100% alike across industries" in m for m in messages(result))
    assert result.errors >= 1


def test_sameness_catches_feature_first_message(launch):
    edit(launch, "messaging.yaml", lambda d: d["grid"][0].update(headline="Our AI engine automates reconciliation"))
    assert any("Feature-first" in m and "Our AI engine" in m for m in messages(cc.check_sameness(launch)))


@pytest.mark.parametrize("text,flagged", [
    ("Close the books two days faster", False),
    ("Fewer denials, caught before the claim", False),
    ("Introducing the reconciliation platform", True),
    ("AI-powered workflows for finance", True),
    ("Dashboard views for every team", True),
    ("PlaceholderOne cuts close time", True),
])
def test_feature_first_heuristic(text, flagged):
    assert bool(cc.opens_with_feature(text, ["PlaceholderOne"])) is flagged


# ------------------------------------------------------------------ FR-QA-07
def test_completeness_catches_missing_asset_and_unanswered_strategy_point(launch):
    assert cc.check_completeness(launch).errors == 0
    (launch / "web" / "ind-b.yaml").unlink()
    edit(launch, "strategy-check.yaml", lambda d: d["points"][0].pop("pmm_response"))
    msgs = messages(cc.check_completeness(launch))
    assert any("IND-B: webpage copy brief is missing" in m for m in msgs)
    assert any("SC-1 has no PMM response" in m for m in msgs)


def test_completeness_catches_missing_grid_row_and_battlecard(launch):
    edit(launch, "messaging.yaml", lambda d: d.update(grid=[r for r in d["grid"] if r["industry"] != "ind-b"]))
    (launch / "competitors" / "comp-a.yaml").unlink()
    msgs = messages(cc.check_completeness(launch))
    assert any("No grid row for P-1 (IND-B)" in m for m in msgs)
    assert any("No battlecard for Competitor A" in m for m in msgs)


def test_completeness_counts_are_warnings_only(launch):
    result = cc.check_completeness(launch)
    assert any("trends (expected 5–8)" in x.message and x.severity == "warning" for x in result.findings)


# ------------------------------------------------------------------ FR-OUT-03 / FR-CMP-04
def test_rules_catch_competitor_in_customer_copy_and_price_advice(launch):
    assert cc.check_rules(launch).status == "pass"
    edit(launch, "web/ind-a.yaml", lambda d: d.update(page_goal="Win deals from Competitor A"))
    edit(launch, "competitors/comp-a.yaml", lambda d: d.update(overview="We recommend pricing at $40 per seat."))
    msgs = messages(cc.check_rules(launch))
    assert any("names competitor 'Competitor A'" in m for m in msgs)
    assert any("price recommendation" in m for m in msgs)


def test_rules_allow_competitor_names_when_opted_in(launch):
    launch_yaml = load_yaml(launch / "launch.yaml")
    launch_yaml["options"]["name_competitors_in_customer_copy"] = True
    dump_yaml(launch_yaml, launch / "launch.yaml")
    edit(launch, "web/ind-a.yaml", lambda d: d.update(page_goal="Win deals from Competitor A"))
    assert not any("names competitor" in m for m in messages(cc.check_rules(launch)))


# ------------------------------------------------------------------ FR-QA-08 packaging
def test_run_writes_report_and_kit(launch):
    edit(launch, "web/ind-a.yaml", lambda d: d.update(page_goal="Cut costs by 30% [VERIFY] confirm with finance"))
    results = run(launch)
    report = (launch / "qa-report.md").read_text()
    kit = (launch / "LAUNCH-KIT.md").read_text()
    assert "| FR-QA-02 Citations" in report and "error(s)" in report
    for asset in ("Industry brief: IND-A", "Battlecard: Competitor A", "Strategy check", "Messaging framework",
                  "Industry playbook: IND-B", "Demo storyline: IND-A", "Webpage copy brief: IND-B"):
        assert asset in kit, asset
    assert "[DOCX](outputs/05-messaging-framework.docx)" in kit and "[XLSX](outputs/05-messaging-grid.xlsx)" in kit
    assert "## Top 10 things to verify before field use" in kit
    assert "1. **Webpage copy brief: IND-A:** Cut costs by 30% [VERIFY]" in kit  # numeric, customer-facing first
    assert "| S1 | [Source A](https://example.org/a) |" in kit
    assert "Full report: [gap-report.md](gap-report.md)" in kit
    assert "No refresh run yet" in kit
    assert "Draft generated with Industry Launch Accelerator" in kit
    assert len(results) == 8


def test_qa_stage_can_be_approved_and_kit_rebuilt_without_going_stale(launch):
    s = LaunchState.load(launch)
    s.start("qa")
    run(launch)
    s.submit("qa")
    s.approve("qa")
    s.save()
    write_kit(launch)  # shows the new statuses; must not undo the approval
    s = LaunchState.load(launch)
    s.refresh()
    assert s.status("qa") == "approved"
    assert "approved" in (launch / "LAUNCH-KIT.md").read_text()


def test_cli_qa_exit_code(launch, monkeypatch, capsys):
    from scripts import launch as cli

    monkeypatch.setattr(cli, "LAUNCHES_DIR", launch.parent)
    code = cli.main(["qa", launch.name])
    out = capsys.readouterr().out
    assert "QA:" in out and "Wrote qa-report.md and LAUNCH-KIT.md" in out
    assert code == (1 if "[X ]" in out else 0)


def test_buyer_objections_and_resolved_direction_are_not_claims(launch):
    edit(launch, "competitors/comp-a.yaml", lambda d: d["objections"][0].update(
        text="Competitor A already integrates with our EHR and raised $50 million."))
    edit(launch, "strategy-check.yaml", lambda d: d.update(resolved_direction="Lead with 2 industries in 2027."))
    edit(launch, "competitive-overview.yaml", lambda d: d.update(generic_objections=[{
        "id": "O-gen-1", "text": "Regulators won't accept an AI agent here.",
        "underlying_concern": "c", "response": {"acknowledge": "a", "reframe": "r", "evidence": "e", "question": "q"},
        "proof_slot": "[PROOF NEEDED]"}]))
    msgs = messages(cc.check_citations(launch))
    locations = [f.location for f in cc.check_citations(launch).findings]
    assert not any(loc.endswith("objections[0].text") for loc in locations)  # battlecard and generic objections
    assert not any("resolved_direction" in m for m in msgs)
    # The objection's response is still checked.
    edit(launch, "competitors/comp-a.yaml", lambda d: d["objections"][0]["response"].update(
        evidence="Competitor A raised $50 million."))
    assert any(f.location.endswith("objections[0].response.evidence") for f in cc.check_citations(launch).findings)
