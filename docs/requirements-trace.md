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
| FR-INP-01 | ✅ | `templates/inputs/product-brief.md` (Appendix A fields + "Anything else"), `scripts/intake/fields.py` | `tests/test_intake.py::test_every_brief_field_has_a_heading_in_the_template` |
| FR-INP-02 | ✅ | `scripts/extract/extract.py` (reads all of `inputs/`, incl. `inputs/brief/`) | `tests/test_extract.py` |
| FR-INP-03 | ✅ | `scripts/intake/run_intake.py::merge_field` (template wins); conflicts logged via `instructions/01-intake.md` | `tests/test_intake.py::test_template_wins_over_agent_value_but_agent_value_fills_gaps` |
| FR-INP-04 | ✅ | `templates/inputs/launch-pov.md` | `tests/test_intake.py::test_pov_text_and_industries_are_read` |
| FR-INP-05 | 🟡 | `AGENTS.md` rule 8, `instructions/01-intake.md` (never edit the POV); downstream use in M3 | Manual read |
| FR-INP-06 | 🟡 | POV "Target industries" section, `launch.py add-industry` (sub-segments, regions, size) | `tests/test_intake.py::test_pov_text_and_industries_are_read` |
| FR-INP-08 | ✅ | `scripts/brand/extract_brand.py` (questionnaire, brand docs, URL via agent, PNG logos, .docx/.dotx template) | `tests/test_brand.py` |
| FR-INP-09 | ✅ | `scripts/brand/extract_brand.py` → `brand.yaml` (Appendix C) | `tests/test_brand.py::test_questionnaire_answers_are_used` |
| FR-INP-10 | 🟡 | `inspect_template.py` style map stored in `brand.yaml`; neutral theme `scripts/brand/theme.py`; applied by renderers in M3 | `tests/test_brand.py::test_word_template_styles_fonts_and_colors` |
| FR-INP-11 | 🟡 | `extract_brand.py` (`unbranded: true`, neutral theme), `gap_report.py` (non-blocking G-brand); label applied by renderers in M3 | `tests/test_brand.py::test_no_brand_input_means_unbranded_neutral_theme`, `tests/test_intake.py::test_no_brand_input_is_a_non_blocking_gap` |
| FR-INP-12 | ✅ | `run_intake.py::optional_inputs` (classified by folder, permission `unknown` until stated), agent classification step in `01-intake.md` | `tests/test_intake.py::test_optional_inputs_are_classified_by_folder` |
| FR-INT-01 | ✅ | `scripts/extract/extract.py` (MD, TXT, DOCX incl. tables, PDF with scanned-image warning, PPTX incl. notes) | `tests/test_extract.py` |
| FR-INT-02 | ✅ | `run_intake.py` (value + `source_file` + status per field), `schemas/launch-context.schema.json` | `tests/test_intake.py::test_filled_brief_records_values_and_source` |
| FR-INT-03 | ✅ | `gap_report.py` (required missing/thin → blocking; recommended → `[ASSUMPTION]`), `launch_state.py::_check_no_open_blocking_gaps` | `tests/test_intake.py::test_required_fields_block_and_recommended_fields_become_assumptions`, `test_intake_cannot_be_approved_with_open_blocking_gaps` |
| FR-INT-04 | ✅ | `gap_report.py::questions_this_round` (≤7, by impact), specific default questions in `fields.py`, agent rewording kept | `tests/test_intake.py::test_at_most_seven_questions_blocking_first`, `test_agent_wording_waivers_and_own_gaps_survive_a_rerun` |
| FR-INT-05 | ✅ | `conflicts:` in launch-context (agent), turned into blocking questions by `gap_report.py` | `tests/test_intake.py::test_contradictions_become_blocking_questions` |
| FR-INT-06 | ✅ | `gap_report.py` (G-launch-pov) | `tests/test_intake.py::test_missing_pov_and_industries_are_blocking` |
| FR-INT-07 | ✅ | `scripts/brand/extract_brand.py`, `scripts/brand/inspect_template.py` (.docx and .dotx) | `tests/test_brand.py::test_inspector_lists_styles`, `test_word_template_styles_fonts_and_colors` |
| FR-INT-08 | ✅ | `gap_report.py` → `gap-report.md` (blocking, assumptions, contradictions, questions, files read) | `tests/test_intake.py::test_gap_report_lists_blocking_and_non_blocking` |
| FR-GRD-01 | 🟡 | Stated in `instructions/01-intake.md`; other stage files in M3–M4 | Manual read |
| M2 acceptance | ✅ | — | `tests/test_intake.py::test_acceptance_inputs_to_valid_context_brand_and_gap_report` |
