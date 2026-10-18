"""Rendering YAML to Markdown and Word (FR-RND-01..06, FR-GRD-06, FR-INP-10, FR-INP-11, FR-STA-03)."""

import zipfile

import pytest
from docx import Document

from scripts.render.render import FOOTER, Renderer, cited_in, labels_in
from scripts.sources import add as add_source
from scripts.state.launch_state import LaunchState
from scripts.util import dump_yaml, load_yaml
from tests import factories as f
from tests.docbuilders import make_word_template
from tests.test_state import INDUSTRIES, write_outputs

THIN_SLICE = ["intake", "research:ind-a", "research:ind-b", "competitive", "strategy",
              "personas:ind-a", "personas:ind-b", "messaging", "playbook:ind-a"]


@pytest.fixture
def launch(tmp_path):
    s = LaunchState.create(tmp_path / "r", "r", "Render test")
    for i in INDUSTRIES:
        s.data["industries"].append({"id": i, "name": i.upper()})
    s.data["competitors"].append({"id": "comp-a", "name": "Competitor A", "suggested": False})
    s.refresh()
    for unit in THIN_SLICE:
        s.start(unit)
        write_outputs(s.dir, unit)
        s.submit(unit)
        s.approve(unit)
    s.save()
    add_source(s.dir, url="https://example.org/a", title="Source title", publisher="Publisher", tier=1,
               excerpt="supporting text", published="2026-01-01")
    return s


def render(launch):
    return Renderer(launch.dir).render_all()


def test_assets_one_to_six_render_in_both_formats(launch):
    results = render(launch)
    names = sorted(r.markdown.name for r in results)
    assert names == sorted([
        "01-industry-brief-ind-a.md", "01-industry-brief-ind-b.md", "02-competitive-overview.md",
        "02-battlecard-comp-a.md", "03-strategy-check.md", "04-personas-ind-a.md", "04-personas-ind-b.md",
        "05-messaging-framework.md", "06-playbook-ind-a.md",
    ])
    for r in results:
        assert r.docx.is_file()
        Document(str(r.docx))  # opens without error
    assert (launch.dir / "outputs" / "images" / "positioning-map.png").is_file()
    assert (launch.dir / "outputs" / "images" / "committee-ind-a.png").is_file()


def test_every_asset_has_status_footer_and_verify_section(launch):
    for r in render(launch):
        md = r.markdown.read_text()
        assert "_Draft · Unbranded draft · Approved by PMM" in md
        assert FOOTER.format(date=load_yaml(launch.dir / "launch.yaml")["created_at"][:10]) in md
        assert "## Before you use this" in md and "## Sources" in md
        doc = Document(str(r.docx))
        footer = " ".join(p.text for p in doc.sections[0].footer.paragraphs)
        assert "Verify items marked [VERIFY] before external use." in footer
        header = " ".join(p.text for p in doc.sections[0].header.paragraphs)
        assert "Unbranded draft" in header


def test_markdown_tables_and_headings_become_word_structure(launch):
    render(launch)
    doc = Document(str(launch.dir / "outputs" / "01-industry-brief-ind-a.docx"))
    styles = [p.style.name for p in doc.paragraphs]
    assert styles[0] == "Title"
    assert "Heading 2" in styles and "List Bullet" in styles
    assert doc.tables, "the 'At a glance' table should be a real Word table"
    assert doc.tables[0].rows[0].cells[0].text == "Trend"
    assert len(doc.inline_shapes) == 0  # no image in the industry brief
    personas = Document(str(launch.dir / "outputs" / "04-personas-ind-a.docx"))
    assert len(personas.inline_shapes) == 1  # the committee diagram


def test_brand_fonts_and_colors_are_applied(launch):
    brand = f.brand()
    brand.update({"unbranded": False, "fonts": {"heading": "Georgia", "body": "Verdana",
                                                 "fallback_heading": "Arial", "fallback_body": "Arial"}})
    brand["colors"]["primary"] = "#123456"
    dump_yaml(brand, launch.dir / "brand.yaml")
    render(launch)
    doc = Document(str(launch.dir / "outputs" / "03-strategy-check.docx"))
    assert doc.styles["Normal"].font.name == "Verdana"
    assert doc.styles["Heading 1"].font.name == "Georgia"
    assert str(doc.styles["Heading 1"].font.color.rgb) == "123456"
    md = (launch.dir / "outputs" / "03-strategy-check.md").read_text()
    assert "Unbranded draft" not in md


def test_word_template_is_used_as_the_base(launch):
    make_word_template(launch.dir / "inputs" / "brand" / "brand.dotx", heading_font="Garamond")
    brand = f.brand()
    brand.update({"unbranded": False, "word_template": {
        "path": "inputs/brand/brand.dotx", "style_map": {"heading1": "Heading 1", "body": "Normal"}}})
    dump_yaml(brand, launch.dir / "brand.yaml")
    render(launch)
    doc = Document(str(launch.dir / "outputs" / "05-messaging-framework.docx"))
    assert doc.styles["Heading 1"].font.name == "Garamond"  # the template's style, untouched


def test_logo_goes_in_the_header(launch, tmp_path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(1, 0.4))
    fig.savefig(launch.dir / "inputs" / "brand" / "logo.png")
    plt.close(fig)
    brand = f.brand()
    brand.update({"unbranded": False, "logo": {"light_bg": "inputs/brand/logo.png", "placement": "header-left"}})
    dump_yaml(brand, launch.dir / "brand.yaml")
    render(launch)
    doc = Document(str(launch.dir / "outputs" / "05-messaging-framework.docx"))
    header_xml = doc.sections[0].header._element.xml
    assert "graphicData" in header_xml


def test_auto_mode_assets_say_not_reviewed(tmp_path):
    s = LaunchState.create(tmp_path / "a", "a")
    s.data["industries"].append({"id": "ind-a", "name": "A"})
    s.set_auto_mode(True)
    s.refresh()
    for unit in ["intake", "research:ind-a"]:
        s.start(unit)
        write_outputs(s.dir, unit)
        s.submit(unit)
    s.save()
    md = Renderer(s.dir).render_all()[0].markdown.read_text()
    assert "Not reviewed by PMM" in md


def test_awaiting_approval_is_labeled(tmp_path):
    s = LaunchState.create(tmp_path / "w", "w")
    s.data["industries"].append({"id": "ind-a", "name": "A"})
    s.refresh()
    s.start("intake")
    write_outputs(s.dir, "intake")
    s.submit("intake")
    s.approve("intake")
    s.start("research:ind-a")
    write_outputs(s.dir, "research:ind-a")
    s.submit("research:ind-a")
    s.save()
    md = Renderer(s.dir).render_all()[0].markdown.read_text()
    assert "Awaiting PMM approval" in md


def test_verify_items_and_sources_are_listed(launch):
    doc = f.industry_research("ind-a")
    doc["trends"][0]["impact"] = "Costs may rise [VERIFY] check the regulator's estimate"
    doc["trends"][0]["so_what"] = "Placeholder [ASSUMPTION]"
    dump_yaml(doc, launch.dir / "research" / "industry-ind-a.yaml")
    render(launch)
    md = (launch.dir / "outputs" / "01-industry-brief-ind-a.md").read_text()
    assert "**[VERIFY]:** 1 · **[ASSUMPTION]:** 1" in md
    assert "- Costs may rise [VERIFY] check the regulator's estimate" in md
    assert "**[S1]** Source title, Publisher (2026-01-01" in md


def test_unregistered_citation_is_flagged(launch):
    doc = f.industry_research("ind-a")
    doc["trends"][0]["summary"] = "Claim [S99]"
    dump_yaml(doc, launch.dir / "research" / "industry-ind-a.yaml")
    render(launch)
    md = (launch.dir / "outputs" / "01-industry-brief-ind-a.md").read_text()
    assert "**[S99]** [VERIFY] not found in the source register" in md


def test_strategy_check_shows_agent_view_and_pmm_response(launch):
    doc = f.strategy_check()
    doc["points"][0]["pmm_response"] = {"decision": "adjust", "adjusted_direction": "Lead with the second buyer",
                                        "reason": "field feedback"}
    doc["resolved_direction"] = "Resolved placeholder direction"
    dump_yaml(doc, launch.dir / "strategy-check.yaml")
    render(launch)
    md = (launch.dir / "outputs" / "03-strategy-check.md").read_text()
    assert "**Agent's stance:** agree" in md
    assert "**PMM decision:** adjust" in md
    assert "**Adjusted direction:** Lead with the second buyer" in md
    assert "Resolved placeholder direction" in md


def test_rendering_is_deterministic(launch):
    first = {r.markdown.name: (r.markdown.read_text(), _docx_parts(r.docx)) for r in render(launch)}
    second = {r.markdown.name: (r.markdown.read_text(), _docx_parts(r.docx)) for r in render(launch)}
    assert first == second


def _docx_parts(path):
    with zipfile.ZipFile(path) as z:
        return {n: z.read(n) for n in z.namelist()}


def test_png_diagrams_are_deterministic(launch):
    render(launch)
    a = (launch.dir / "outputs" / "images" / "positioning-map.png").read_bytes()
    render(launch)
    assert (launch.dir / "outputs" / "images" / "positioning-map.png").read_bytes() == a


def test_label_and_citation_helpers():
    data = {"a": "x [VERIFY] y [S3]", "b": [{"source_id": "S10"}, "[PROOF NEEDED]"]}
    assert labels_in(data)["counts"] == {"verify": 1, "assumption": 0, "proof": 1}
    assert cited_in(data) == ["S3", "S10"]


def test_cli_render(launch, monkeypatch, capsys):
    from scripts import launch as cli

    monkeypatch.setattr(cli, "LAUNCHES_DIR", launch.dir.parent)
    assert cli.main(["render", launch.dir.name, "--unit", "messaging"]) == 0
    assert "05-messaging-framework.md" in capsys.readouterr().out
