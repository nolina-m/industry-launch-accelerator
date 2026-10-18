# Requirements trace

Maps each requirement ID to the files that implement it and the test or check that proves it.
Status: ✅ done · 🟡 partial · ⬜ not started.

| ID | Status | Implemented in | Proved by |
|---|---|---|---|
| FR-USR-01 | 🟡 | `setup.sh`, `setup.ps1` (plain-language messages); README quickstart pending (M8) | Manual read |
| FR-CMPT-01 | 🟡 | `AGENTS.md` (plain Markdown, read files + run shell only) | Manual read; full check M8 |
| FR-CMPT-02 | 🟡 | `setup.sh` (macOS/Linux), `setup.ps1` (Windows, written, not tested by owner decision), `pyproject.toml` (`requires-python >=3.10`) | `setup.sh` run on macOS; CI on Linux (M9) |
| FR-TST-01 | 🟡 | `.github/workflows/ci.yml` (lint + tests), `tests/conftest.py` (blocks network) | `tests/test_scaffold.py::test_network_is_blocked_in_tests`; CI green pending repo (M9) |
| FR-DOC-04 | ✅ | `README.md` "Example runs" placeholder | Manual read |
| FR-DOC-05 | 🟡 | `README.md` "About the author" draft | Owner to edit wording |
| §13.1 AGENTS.md / CLAUDE.md | ✅ | `AGENTS.md`, `CLAUDE.md` (`@AGENTS.md` import) | `tests/test_scaffold.py::test_claude_md_imports_agents_md` |
| §13.2 Repo layout | 🟡 | Top-level folders created; filled in later milestones | `tests/test_scaffold.py::test_required_file_exists` |
| Read-first #3 (PRD never committed) | ✅ | `.gitignore` | `tests/test_scaffold.py::test_private_files_are_git_ignored` |
| FR-PIP-01 | 🟡 | `scripts/state/pipeline.py` (dependency graph: stages 1 and 2 need only intake; 6a–6c need only messaging + that industry's personas) | `tests/test_state.py::test_units_follow_the_pipeline`, `test_stages_one_and_two_only_need_intake` |
| FR-STA-01 | ✅ | `scripts/state/launch_state.py`, `schemas/launch.schema.json` (industries, competitors, options, stage status, approval timestamps, input hashes) | `tests/test_state.py::test_launch_yaml_round_trips_and_validates` |
| FR-STA-02 | 🟡 | `launch_state.py` (`start`/`submit`/`approve`; downstream refuses to start until upstream approved); agent checkpoint wording in instructions (M3) | `tests/test_state.py::test_downstream_refuses_to_start_until_upstream_approved` |
| FR-STA-03 | 🟡 | `launch_state.py` (auto mode approves with `reviewed: false`; strategy responses set to `not_reviewed`); asset labels at render (M3) | `tests/test_state.py::test_auto_mode_*` |
| FR-STA-04 | 🟡 | `scripts/state/hashing.py`, `launch_state.py::refresh`, `launch.py status` (lists affected assets) ; item-level selective regeneration in M7 | `tests/test_state.py::test_persona_edit_marks_only_affected_assets_stale` and other staleness tests |
| FR-STA-06 | 🟡 | `LaunchState.create` (self-contained `launches/<slug>/`) | `tests/test_state.py::test_new_launch_starts_everything_not_started` |
| FR-STR-05 | 🟡 | `schemas/strategy-check.schema.json` (`pmm_response`), `launch_state.py::_check_strategy_responses` (approval refused until every point has a response) | `tests/test_state.py::test_strategy_check_needs_a_pmm_response_for_every_point`, `tests/test_schemas.py::test_adjust_response_requires_adjusted_direction` |
| FR-QA-01 | 🟡 | `schemas/*.schema.json` (all artifacts), `scripts/validate.py` (file, launch-wide, CLI); used on submit/approve | `tests/test_schemas.py` |
| FR-CMP-04 | 🟡 | `schemas/competitor.schema.json` (pricing model enum, list-price label required) | `tests/test_schemas.py::test_list_price_must_carry_the_enterprise_label` |
| FR-TRD-03 / FR-GRD-08 | 🟡 | `schemas/industry-research.schema.json` (`disclaimer: "Not legal advice"` required) | `tests/test_schemas.py::test_regulatory_section_must_say_not_legal_advice` |
| FR-IND-01 | 🟡 | `schemas/industry-pack.schema.json` | `tests/test_schemas.py::test_minimal_documents_pass` |
| FR-WEB-R-03 | 🟡 | `schemas/sources.schema.json` | `tests/test_schemas.py::test_minimal_documents_pass` |
| Appendix B | ✅ | One schema per artifact in `schemas/` | `tests/test_schemas.py` |
| Appendix C | ✅ | `schemas/brand.schema.json` | `tests/test_schemas.py::test_brand_colors_must_be_hex` |
