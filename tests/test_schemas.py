"""Schema validation (FR-QA-01, FR-TST-02)."""

import json

import pytest
from jsonschema import Draft202012Validator

from scripts.util import SCHEMAS_DIR, loads_yaml
from scripts.validate import schema_for, validate_data
from tests import factories as f

VALID = [
    ("launch-context.schema.json", f.launch_context()),
    ("brand.schema.json", f.brand()),
    ("industry-research.schema.json", f.industry_research()),
    ("competitor.schema.json", f.competitor()),
    ("competitive-overview.schema.json", f.competitive_overview()),
    ("strategy-check.schema.json", f.strategy_check()),
    ("personas.schema.json", f.personas()),
    ("messaging.schema.json", f.messaging()),
    ("playbook.schema.json", f.playbook()),
    ("demo.schema.json", f.demo()),
    ("web.schema.json", f.web()),
    ("sources.schema.json", f.sources()),
    ("industry-pack.schema.json", f.industry_pack()),
]


@pytest.mark.parametrize("path", sorted(SCHEMAS_DIR.glob("*.schema.json")), ids=lambda p: p.name)
def test_every_schema_is_valid_json_schema(path):
    Draft202012Validator.check_schema(json.loads(path.read_text()))


@pytest.mark.parametrize("schema,doc", VALID, ids=[v[0] for v in VALID])
def test_minimal_documents_pass(schema, doc):
    assert validate_data(doc, schema) == []


def _errors(schema, doc):
    return [p.message for p in validate_data(doc, schema)]


def test_adjust_response_requires_adjusted_direction():
    doc = f.strategy_check()
    doc["points"][0]["pmm_response"] = {"decision": "adjust"}
    assert any("adjusted_direction" in e for e in _errors("strategy-check.schema.json", doc))


def test_bad_source_id_is_rejected():
    doc = f.industry_research()
    doc["trends"][0]["evidence"] = [{"source_id": "source-one"}]
    assert _errors("industry-research.schema.json", doc)


def test_list_price_must_carry_the_enterprise_label():
    doc = f.competitor()
    doc["pricing"]["list_prices"] = [{"item": "Pro", "price": "$10", "source_id": "S1", "label": "list"}]
    assert _errors("competitor.schema.json", doc)


def test_unknown_pricing_model_is_rejected():
    doc = f.competitor()
    doc["pricing"]["model"] = "per-widget"
    assert _errors("competitor.schema.json", doc)


def test_more_than_eight_trends_is_rejected():
    doc = f.industry_research()
    doc["trends"] = doc["trends"] * 9
    assert _errors("industry-research.schema.json", doc)


def test_more_than_six_personas_is_rejected():
    doc = f.personas()
    doc["personas"] = doc["personas"] * 7
    assert _errors("personas.schema.json", doc)


def test_more_than_five_strategy_additions_is_rejected():
    doc = f.strategy_check()
    addition = {"id": "A-1", "text": "t", "evidence": [], "confidence": {"level": "low", "reason": "r"}}
    doc["additions"] = [addition] * 6
    assert _errors("strategy-check.schema.json", doc)


def test_brand_colors_must_be_hex():
    doc = f.brand()
    doc["colors"]["primary"] = "blue"
    assert _errors("brand.schema.json", doc)


def test_regulatory_section_must_say_not_legal_advice():
    doc = f.industry_research()
    doc["regulatory"]["disclaimer"] = "FYI"
    assert _errors("industry-research.schema.json", doc)


def test_misspelled_field_is_caught():
    doc = f.web()
    doc["headline_variant"] = []
    assert _errors("web.schema.json", doc)


def test_yaml_dates_stay_text():
    # PyYAML would normally turn this into a date object and fail the schema.
    doc = loads_yaml("researched_at: 2026-01-01\n")
    assert doc["researched_at"] == "2026-01-01"


@pytest.mark.parametrize(
    "rel,schema",
    [
        ("research/industry-technology.yaml", "industry-research.schema.json"),
        ("competitors/comp-a.yaml", "competitor.schema.json"),
        ("personas/technology.yaml", "personas.schema.json"),
        ("industries/custom/pack.yaml", "industry-pack.schema.json"),
        ("research/sources.json", "sources.schema.json"),
        ("gap-report.md", None),
    ],
)
def test_schema_lookup_by_path(rel, schema):
    assert schema_for(rel) == schema
