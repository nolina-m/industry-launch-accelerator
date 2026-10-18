"""Brand extraction and the Word template inspector (FR-INP-08..11, FR-INT-07)."""

import re

import pytest

from scripts.brand import extract_brand, inspect_template
from scripts.brand.theme import NEUTRAL_COLORS
from scripts.util import TEMPLATES_DIR, dump_yaml, load_yaml
from scripts.validate import validate_file
from tests.docbuilders import make_docx, make_word_template

Q_TPL = (TEMPLATES_DIR / "inputs" / "brand-questionnaire.md").read_text()


def fill(answers):
    out = Q_TPL
    for heading, answer in answers.items():
        pattern = re.compile(rf"^(#{{2,3}} {re.escape(heading)}[^\n]*\n)", re.M)
        assert pattern.search(out), heading
        out = pattern.sub(lambda m, a=answer: m.group(1) + a + "\n", out, count=1)
    return out


@pytest.fixture
def launch_dir(tmp_path):
    d = tmp_path / "l"
    (d / "inputs" / "brand").mkdir(parents=True)
    (d / "inputs" / "brand-questionnaire.md").write_text(Q_TPL)
    return d


def test_no_brand_input_means_unbranded_neutral_theme(launch_dir):
    brand, _, _ = extract_brand.run(launch_dir)
    assert brand["unbranded"] is True
    assert brand["colors"] == NEUTRAL_COLORS
    assert validate_file(launch_dir / "brand.yaml", "brand.schema.json") == []


def test_questionnaire_answers_are_used(launch_dir):
    (launch_dir / "inputs" / "brand-questionnaire.md").write_text(fill({
        "Company name": "Placeholder Co",
        "Primary color": "#0a2540",
        "Accent colors": "- #abc\n- #00FF00",
        "Heading font": "Lato",
        "Tone traits": "confident, plain-spoken",
        "Banned terms": "- synergy",
        "Preferred terms": "- AI-powered -> AI-native",
        "Product names": "- PlaceholderOne",
    }))
    brand, _, warnings = extract_brand.run(launch_dir)
    assert brand["unbranded"] is False
    assert brand["name"] == "Placeholder Co"
    assert brand["colors"]["primary"] == "#0A2540"
    assert brand["colors"]["accent"] == ["#AABBCC", "#00FF00"]
    assert brand["fonts"]["heading"] == "Lato"
    assert brand["fonts"]["body"] == "Arial"  # unchanged neutral default
    assert brand["voice"]["traits"] == ["confident", "plain-spoken"]
    assert brand["terms"] == {"banned": ["synergy"], "preferred": {"AI-powered": "AI-native"},
                              "product_names": ["PlaceholderOne"]}
    assert warnings == []


def test_bad_color_and_bad_preferred_term_warn_instead_of_failing(launch_dir):
    (launch_dir / "inputs" / "brand-questionnaire.md").write_text(fill({
        "Primary color": "navy blue", "Preferred terms": "- just one term"}))
    brand, _, warnings = extract_brand.run(launch_dir)
    assert brand["colors"]["primary"] == NEUTRAL_COLORS["primary"]
    assert any("not a hex color" in w for w in warnings)
    assert any("avoid this -> use this" in w for w in warnings)


def test_logos_are_found_and_svg_warns(launch_dir):
    (launch_dir / "inputs" / "brand" / "logo.png").write_bytes(b"\x89PNG")
    (launch_dir / "inputs" / "brand" / "logo-white.png").write_bytes(b"\x89PNG")
    (launch_dir / "inputs" / "brand" / "mark.svg").write_text("<svg/>")
    brand, _, warnings = extract_brand.run(launch_dir)
    assert brand["logo"] == {"light_bg": "inputs/brand/logo.png", "dark_bg": "inputs/brand/logo-white.png",
                             "placement": "header-right"}
    assert any("PNG" in w for w in warnings)


def test_missing_logo_file_named_in_questionnaire_warns(launch_dir):
    (launch_dir / "inputs" / "brand-questionnaire.md").write_text(fill({"Logo for light backgrounds": "nope.png"}))
    brand, _, warnings = extract_brand.run(launch_dir)
    assert brand["logo"]["light_bg"] is None
    assert any("not found" in w for w in warnings)


@pytest.mark.parametrize("name", ["brand-template.docx", "brand.dotx"])
def test_word_template_styles_fonts_and_colors(launch_dir, name):
    make_word_template(launch_dir / "inputs" / "brand" / name, heading_font="Georgia", heading_color="123456")
    brand, _, _ = extract_brand.run(launch_dir)
    assert brand["word_template"]["path"] == f"inputs/brand/{name}"
    style_map = brand["word_template"]["style_map"]
    assert style_map["heading1"] == "Heading 1" and style_map["body"] == "Normal"
    assert brand["fonts"]["heading"] == "Georgia"
    assert brand["colors"]["primary"] == "#123456"


def test_inspector_lists_styles(tmp_path):
    path = make_word_template(tmp_path / "t.dotx")
    result = inspect_template.inspect(path)
    names = {s["name"] for s in result["styles"]}
    assert {"Normal", "Heading 1", "Title"} <= names
    assert result["style_map"]["title"] == "Title"


def test_brand_document_colors_and_fonts_are_candidates_only(launch_dir):
    make_docx(launch_dir / "inputs" / "brand" / "guidelines.docx", "Colors",
              "Primary #FF5500, secondary #FF5500 and #222222. Headings use Montserrat.")
    brand, candidates, _ = extract_brand.run(launch_dir)
    assert candidates["colors"][0] == {"hex": "#FF5500", "mentions": 2}
    assert candidates["fonts"][0]["name"] == "Montserrat"
    assert brand["colors"]["primary"] == NEUTRAL_COLORS["primary"]  # not guessed into brand.yaml
    assert brand["unbranded"] is False
    assert load_yaml(launch_dir / "intake" / "brand-candidates.yaml")["documents_read"]


def test_layers_questionnaire_beats_agent_notes(launch_dir):
    dump_yaml({"colors": {"primary": "#111111", "secondary": "#222222"}, "fonts": {"body": "Roboto"}},
              launch_dir / "intake" / "brand-notes.yaml")
    (launch_dir / "inputs" / "brand-questionnaire.md").write_text(fill({"Primary color": "#333333"}))
    brand, _, _ = extract_brand.run(launch_dir)
    assert brand["colors"]["primary"] == "#333333"
    assert brand["colors"]["secondary"] == "#222222"
    assert brand["fonts"]["body"] == "Roboto"
