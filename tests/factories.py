"""Minimal valid artifacts for tests (FR-TST-02).

These are the smallest documents that pass each schema, with placeholder text.
They are not examples of a launch and contain no company, product or brief.
"""

from __future__ import annotations

OBJECTION = {
    "id": "O-1",
    "text": "placeholder objection",
    "underlying_concern": "placeholder concern",
    "response": {"acknowledge": "a", "reframe": "b", "evidence": "c", "question": "d"},
    "proof_slot": "[PROOF NEEDED]",
}


def launch_context(industries=("ind-a",)):
    field = {"value": "x", "source_file": "inputs/product-brief.md", "status": "provided"}
    return {
        "product_brief": {
            "basics": {"product_name": field},
            "problem": {"problem_statement": field},
            "solution": {"what_it_is": field},
            "target": {"primary_buyer_roles": field},
        },
        "launch_pov": {"text": "placeholder point of view", "source_file": "inputs/launch-pov.md"},
        "industries": [{"id": i, "name": i} for i in industries],
        "gaps": [],
    }


def brand():
    return {
        "colors": {"primary": "#112233", "text": "#000000", "background": "#FFFFFF"},
        "fonts": {"heading": "Arial", "body": "Arial", "fallback_heading": "Arial", "fallback_body": "Arial"},
        "logo": {"placement": "none"},
        "voice": {},
        "terms": {},
        "unbranded": True,
    }


def industry_research(industry="ind-a"):
    return {
        "industry": industry,
        "researched_at": "2026-01-01",
        "trends": [
            {
                "id": "T-1",
                "industry": industry,
                "headline": "h",
                "summary": "s [S1]",
                "evidence": [{"source_id": "S1"}],
                "impact": "i",
                "so_what": "w",
                "relevance": {"rating": "High", "rationale": "r"},
            }
        ],
        "imperatives": [
            {"id": "I-1", "industry": industry, "statement": "s", "trend_ids": ["T-1"], "capability_refs": []}
        ],
        "regulatory": {"disclaimer": "Not legal advice", "items": []},
        "market_data": [],
    }


def competitor(cid="comp-a"):
    return {
        "id": cid,
        "name": "Competitor A",
        "category": "direct",
        "suggested": False,
        "overview": "o",
        "strengths": [],
        "weaknesses": [],
        "win_themes": [],
        "loss_themes": [],
        "landmines": [],
        "traps": [],
        "objections": [OBJECTION],
        "pricing": {
            "model": "seat",
            "components": [],
            "value_metric": "per user",
            "tiers": [],
            "free_tier": "none found",
            "contract_signals": "",
        },
        "recent_moves": [],
        "sources": [],
        "researched_at": "2026-01-01",
    }


def competitive_overview():
    axis = {"label": "l", "low": "lo", "high": "hi", "rationale": "r"}
    return {
        "categories": [],
        "positioning_map": {"x_axis": axis, "y_axis": axis, "points": []},
        "industry_strength": [],
        "generic_objections": [],
    }


def strategy_check(responded=True):
    point = {
        "id": "SC-1",
        "pov_quote": "q",
        "stance": "agree",
        "reasoning": "r",
        "evidence": [{"source_id": "S1"}],
        "confidence": {"level": "high", "reason": "r"},
    }
    doc = {"points": [point], "additions": []}
    if responded:
        point["pmm_response"] = {"decision": "accept", "responded_at": "2026-01-01T00:00:00Z"}
        doc["resolved_direction"] = "placeholder resolved direction"
    return doc


def personas(industry="ind-a", pain="placeholder pain"):
    return {
        "industry": industry,
        "personas": [
            {
                "id": "P-1",
                "industry": industry,
                "role": "r",
                "titles": [],
                "reports_to": "x",
                "buying_role": "champion",
                "responsibilities": [],
                "kpis": [],
                "pains": [{"text": pain, "trend_ids": ["T-1"]}],
                "goals": [],
                "triggers": [],
                "objections": [],
                "info_sources": [],
                "language": {"use": [], "avoid": []},
                "beliefs_to_buy": [],
                "discovery_questions": [],
                "provenance": "research-derived",
            }
        ],
        "committee_map": {"industry": industry, "edges": [], "decision_sequence": ["P-1"]},
    }


def messaging(industries=("ind-a",)):
    return {
        "positioning": {k: "x" for k in ("for", "who", "product", "category", "that", "unlike", "we")},
        "elevator_pitch": "e",
        "boilerplate": "b",
        "pillars": [
            {"id": "PL-1", "headline": "h", "outcome": "o", "capabilities": [], "proof": [], "differentiator": "d"}
        ],
        "grid": [
            {
                "industry": i,
                "persona_id": "P-1",
                "headline": "h",
                "pain_ref": "P-1.pain-1",
                "pillar_id": "PL-1",
                "value_hypothesis": {"text": "t", "label": "[ASSUMPTION]"},
                "proof": "[PROOF NEEDED]",
            }
            for i in industries
        ],
    }


def playbook(industry="ind-a"):
    return {
        "industry": industry,
        "targeting": {"segments": [], "committee_summary": "c"},
        "why_now": [],
        "value_story": [],
        "discovery": [],
        "qualification": {"signals": [], "disqualifiers": []},
        "objections": [],
        "competitive_quick_ref": [],
        "next_steps": [],
        "proof_library": [],
    }


def demo(industry="ind-a"):
    return {
        "industry": industry,
        "scenario": "s",
        "cast": [],
        "moments": [],
        "aha": {"moment_id": "M-1", "description": "d"},
        "data_needed": [],
        "environment": [],
        "versions": {"five_minute": {"moment_ids": ["M-1"]}, "twenty_minute": {"moment_ids": ["M-1"]}},
    }


def web(industry="ind-a"):
    return {
        "industry": industry,
        "page_goal": "g",
        "primary_cta": "c",
        "target_personas": [],
        "hero": {"headline": "h", "subhead": "s"},
        "sections": [],
        "proof_section": "p",
        "cta": "c",
        "headline_variants": [],
        "keywords": [{"term": "t", "label": "[VERIFY]"}],
        "imagery_direction": "i",
        "demo_embed_direction": "d",
    }


def sources():
    return {
        "sources": [
            {
                "id": "S1",
                "url": "https://example.org/a",
                "title": "t",
                "publisher": "p",
                "published_at": None,
                "retrieved_at": "2026-01-01",
                "tier": 1,
                "excerpt": "e",
            }
        ]
    }


def industry_pack(pid="ind-a"):
    return {
        "id": pid,
        "display_name": "Industry A",
        "sub_segments": [],
        "buying_committee_roles": [],
        "kpis": [],
        "regulators": [],
        "regulations": [],
        "analyst_sources": [],
        "associations": [],
        "connectors": [],
        "search_seeds": [],
        "typical_objections": [],
        "vocabulary": {"use": [], "avoid": []},
    }
