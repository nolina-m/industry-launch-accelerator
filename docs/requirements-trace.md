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
| FR-STA-02 | ✅ | `launch_state.py` (`start`/`submit`/`approve`; downstream refuses to start until upstream approved); agent checkpoint wording in instructions (M3) | `tests/test_state.py::test_downstream_refuses_to_start_until_upstream_approved` |
| FR-STA-03 | ✅ | `launch_state.py` (auto mode approves with `reviewed: false`; strategy responses set to `not_reviewed`); asset labels at render (M3) | `tests/test_state.py::test_auto_mode_*` |
| FR-STA-04 | ✅ | `scripts/state/hashing.py`, `launch_state.py::refresh`, `launch.py status` (lists affected assets) ; item-level selective regeneration in M7 | `tests/test_state.py::test_persona_edit_marks_only_affected_assets_stale` and other staleness tests |
| FR-STA-06 | ✅ | `LaunchState.create` (self-contained `launches/<slug>/`) | `tests/test_state.py::test_new_launch_starts_everything_not_started` |
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
| FR-TRD-01..06 | 🟡 | `instructions/02-industry-research.md`, `schemas/industry-research.schema.json`, `templates/docs/industry-brief.md.j2`; min counts → QA warnings (M6) | M3 smoke run; `tests/test_render.py` |
| FR-CMP-01..06 | 🟡 | `instructions/03-competitive.md`, competitor + overview schemas, `battlecard.md.j2`, `competitive-overview.md.j2`, `launch.py add-competitor --suggested` | M3 smoke run; `tests/test_render.py` |
| FR-STR-01..07 | ✅ | `instructions/04-strategy-check.md`, `strategy-check.schema.json`, `launch_state.py` (gate: all upstream approved; every point answered), `strategy-check.md.j2` (agent view + PMM response side by side) | `tests/test_state.py::test_strategy_check_needs_a_pmm_response_for_every_point`, `tests/test_render.py::test_strategy_check_shows_agent_view_and_pmm_response`; M3 smoke run |
| FR-PER-01..06 | 🟡 | `instructions/05-personas.md`, `personas.schema.json`, `personas.md.j2`, committee diagram `scripts/render/diagrams.py::committee_map`; sameness check M6 | `tests/test_render.py`; M3 smoke run |
| FR-MSG-01..05 | 🟡 | `instructions/06-messaging.md`, `messaging.schema.json`, `messaging.md.j2`; XLSX grid M4; feature-first check M6 | `tests/test_render.py`; M3 smoke run |
| FR-PBK-01 | ✅ | `instructions/07-playbook.md`, `playbook.schema.json`, `playbook.md.j2` | `tests/test_render.py`; M3 smoke run |
| FR-WEB-R-01 | ✅ | Generic "use your web search / web fetch tool" in `instructions/00-orchestrator.md`; tool names verified 2026-10-18 (Claude Code `WebSearch`/`WebFetch`; Codex `web_search` config, default `cached`; Cursor agent web search / `@Web`), to be recorded in `docs/compatibility.md` (M8) | Manual read |
| FR-WEB-R-02 / -03 / -04 | ✅ | `scripts/sources.py` (register, tiers, dedupe, `check`), rules in `00-orchestrator.md` | `tests/test_sources.py` |
| FR-STA-02 | ✅ | + checkpoint loop and summary format in `instructions/00-orchestrator.md` | M3 smoke run (research refused before intake approval; strategy refused before stages 1–2 approved) |
| FR-STA-03 | ✅ | + "Not reviewed by PMM" label in rendered assets | `tests/test_render.py::test_auto_mode_assets_say_not_reviewed` |
| FR-RND-01 | ✅ | `scripts/render/docx_writer.py` (python-docx; brand theme or the PMM's Word template) | `tests/test_render.py::test_brand_fonts_and_colors_are_applied`, `test_word_template_is_used_as_the_base` |
| FR-RND-03 | ✅ | `scripts/render/render.py` + `templates/docs/*.md.j2` (Jinja2) | `tests/test_render.py` |
| FR-RND-04 | ✅ | `scripts/render/diagrams.py` (matplotlib PNG; data also as tables) | `tests/test_render.py::test_assets_one_to_six_render_in_both_formats` |
| FR-RND-05 | ✅ | Fixed render date in core properties; PNG without metadata | `tests/test_render.py::test_rendering_is_deterministic`, `test_png_diagrams_are_deterministic` |
| FR-RND-06 | ✅ | `scripts/brand/theme.py` (Arial), fonts set on built-in styles | `tests/test_render.py::test_brand_fonts_and_colors_are_applied` |
| FR-OUT-02 | ✅ | Only built-in styles, simple tables with explicit borders, inline PNG, plain header/footer | Files opened via macOS Quick Look/textutil in smoke run; manual Word/Google check at M4 |
| FR-OUT-03 (rules) | ✅ | Rules in `00-orchestrator.md`, `06-messaging.md`, `08`, `09` | Manual read |
| FR-GRD-03..08 | 🟡 | Stated in stage instructions; footer (FR-GRD-06) on every asset | `tests/test_render.py::test_every_asset_has_status_footer_and_verify_section` |
| FR-INP-11 | ✅ | + "Unbranded draft" in every asset's status line and Word header | `tests/test_render.py::test_every_asset_has_status_footer_and_verify_section` |
| M3 acceptance | ✅ | Private smoke run 2026-10-18 outside the repo (deleted): assets 1–6 for one industry rendered; checkpoints blocked correctly; strategy check stored PMM responses | Smoke run log in BUILD-NOTES |
| FR-DMO-01 / FR-DMO-02 | ✅ | `instructions/08-demo-storyline.md`, `schemas/demo.schema.json`, `templates/docs/demo.md.j2` (moments table, aha, 5- and 20-minute versions, data, environment, [VERIFY] per moment) | `tests/test_render.py::test_demo_storyline_content` |
| FR-WEB-01 / FR-WEB-02 | ✅ | `instructions/09-web-copy.md`, `schemas/web.schema.json`, `templates/docs/web.md.j2` (structure, copy, variants, [VERIFY] keywords, messaging links; no HTML) | `tests/test_render.py::test_web_copy_content` |
| FR-MSG-03 (XLSX) / FR-RND-02 | ✅ | `scripts/render/xlsx_writer.py` (one row per industry × persona, autofilter, frozen header, brand fill and font, footer + About sheet) | `tests/test_render.py::test_excel_grid_has_filters_frozen_header_and_one_row_per_persona`, `test_excel_grid_uses_brand_font` |
| FR-OUT-03 (competitors in customer copy) | ✅ | Rule in `08-demo-storyline.md`, `09-web-copy.md`, `00-orchestrator.md`; automated check in M6 | Manual read |
| Multi-industry | ✅ | Per-industry units for every per-industry asset; grid grouped by industry | `tests/test_render.py::test_all_eight_assets_render_for_two_industries` |
| M4 acceptance | ✅ | All 8 assets render for 2 industries (automated). Owner opened the files in Word, Excel, Google Docs and Google Sheets on 2026-10-18: all fine | `tests/test_render.py::test_all_eight_assets_render_for_two_industries` |
| FR-INP-07 | ✅ | `instructions/12-custom-industry.md` (pack saved in `launches/<slug>/industries/<id>/pack.yaml`, `generated: true`, offer to copy), `launch.py add-industry` (detects packs) | `tests/test_schemas.py::test_schema_lookup_by_path` (launch-local pack validated) |
| FR-IND-01 | ✅ | `schemas/industry-pack.schema.json`, `industries/*/pack.yaml` + `notes.md` | `tests/test_packs.py::test_pack_is_valid_and_complete` |
| FR-IND-02 | ✅ | `industries/` financial-services, healthcare-life-sciences, retail-consumer-goods, technology, telecom-media, travel-hospitality | `tests/test_packs.py::test_the_six_default_packs_exist` |
| FR-IND-03 | ✅ | Pack header comments, `notes.md`, `02-industry-research.md` | `tests/test_packs.py::test_packs_name_no_vendors`; manual read |
| §11.2 connectors | ✅ | `connectors/base.py` (common interface `search`/`fetch`, Record), 28 connector modules, `connectors/registry.yaml`, `connectors/registry.py`. Source list changed with owner approval (see `docs/data-sources.md`) | `tests/connectors/test_connectors.py` |
| FR-API-01 | ✅ | `scripts/connectors/check.py` (key present, live probe, `--offline`); run by setup | `tests/connectors/test_connectors.py::test_check_reports_ready_needs_setup_and_unreachable`; live run 2026-10-18 |
| FR-API-02 | ✅ | `connectors:` in every pack with queries and verified series IDs (BLS, World Bank, FRED) | `tests/test_packs.py::test_pack_connectors_exist_and_name_series_ids` |
| FR-API-03 | ✅ | `connectors/base.py` (rate-limit spacing, User-Agent, cache in `research/cache/` with retrieval time and previous copy, fail soft), `scripts/connectors/query.py` | `tests/connectors/test_connectors.py` (fail-soft, cache, rate limit tests) |
| FR-API-04 | ✅ | `Record` (connector, series_id, retrieved_at), `query.py` output and `--register` excerpt | `tests/connectors/test_connectors.py::test_connector_reads_its_recorded_response`, `test_query_tool_registers_sources_with_series_and_connector` |
| FR-API-05 | ✅ | `docs/adding-a-data-source.md` | Manual read |
| §11.2 docs | ✅ | `docs/data-sources.md` (verification date, access, limits, changes with reasons), `.env.example` (step-by-step, sign-up links) | Manual read |
| M5 acceptance | ✅ | Packs validate; every connector has a recorded-response test; missing keys degrade gracefully | `tests/test_packs.py`, `tests/connectors/test_connectors.py::test_every_registered_connector_has_a_recorded_response`, `test_missing_key_means_off_and_fails_soft` |
| FR-QA-01 | ✅ | `scripts/qa/content_checks.py::check_structure` | `tests/test_qa.py::test_structure_catches_schema_error` |
| FR-QA-02 | ✅ | `scripts/qa/content_checks.py::check_citations` (numbers/dates, named companies, regulatory statements; inline labels or structured source; 95% target; lists uncovered) | `tests/test_qa.py::test_citations_catch_an_uncited_claim`, `test_labels_and_structured_sources_count_as_cited`, `test_citations_catch_named_company_and_regulatory_claims` |
| FR-QA-03 | ✅ | `check_sources` (unregistered citations, URL + retrieval date, trend sources >24 months, ≥2 independent, tier rules, list prices Tier 1, optional `--check-links`) | `tests/test_qa.py::test_sources_*`, `test_link_check_reports_dead_links` |
| FR-QA-04 | ✅ | `scripts/qa/output_checks.py::check_brand` (reads DOCX/XLSX: resolves used styles incl. theme fonts/colors; palette, fonts; banned/preferred terms; product-name caps) | `tests/test_qa.py::test_brand_catches_off_palette_color`, `test_brand_catches_undeclared_font`, `test_brand_catches_banned_term_preferred_term_and_product_caps`, `test_brand_passes_on_rendered_files` |
| FR-QA-05 | ✅ | `check_layout` (empty sections, filler-only sections, placeholders, broken tables, length limits in `scripts/qa/limits.yaml` + per-launch `qa-limits.yaml`) | `tests/test_qa.py::test_layout_catches_empty_section`, `test_layout_catches_placeholder_broken_table_and_length` |
| FR-QA-06 | ✅ | `check_sameness` (persona pains >70% alike across industries; near-identical headlines; feature-first messages) | `tests/test_qa.py::test_sameness_catches_near_identical_personas`, `test_sameness_catches_feature_first_message`, `test_feature_first_heuristic` |
| FR-QA-07 | ✅ | `check_completeness` (per-industry assets, grid rows per persona, battlecards per competitor, strategy responses; recommended counts as warnings) | `tests/test_qa.py::test_completeness_*` |
| FR-QA-08 | ✅ | `scripts/qa/run.py` (render all, `qa-report.md`), `scripts/qa/kit.py` (`LAUNCH-KIT.md`: assets with links/status/open items, top 10 to verify, gap report, QA summary, source register, latest what-changed) | `tests/test_qa.py::test_run_writes_report_and_kit`, `test_qa_stage_can_be_approved_and_kit_rebuilt_without_going_stale` |
| FR-OUT-03 / FR-CMP-04 (checks) | ✅ | `check_rules` (competitors in customer copy without opt-in; price-recommendation language) | `tests/test_qa.py::test_rules_*` |
| FR-OUT-03 | ✅ | + automated check above | as above |
| FR-MSG-04 | ✅ | Feature-first flag in `check_sameness` | `tests/test_qa.py::test_sameness_catches_feature_first_message` |
| FR-INP-10 / FR-RND-06 (fix) | ✅ | `docx_writer.py` removes Word theme fonts/colors from branded styles; title rule in brand primary; XLSX base font = brand font | `tests/test_qa.py::test_brand_passes_on_rendered_files` |
| M6 acceptance | ✅ | Each check catches its seeded defect (uncited claim, banned term, off-palette color, empty section, near-identical personas, feature-first message, and more) | `tests/test_qa.py` |
| FR-REF-01 | ✅ | `launch.py refresh <slug>` + `instructions/11-refresh.md` (on demand only; no scheduling) | `tests/test_iteration.py::test_first_refresh_reports_changes_since_research`; live run 2026-10-19 |
| FR-REF-02 | ✅ | `scripts/refresh/refresh.py` (competitor news + filings, regulation per industry, market data via BLS/FRED/World Bank, source health: link status + age); web-search checks for launches, pricing, funding, acquisitions, leadership, hiring in `11-refresh.md` | `tests/test_iteration.py::test_first_refresh_*`, `test_refresh_checks_source_health` |
| FR-REF-03 | ✅ | Compares with the previous refresh snapshot, else the research date; `refresh/<date>/what-changed.md` (source, date, affected assets/sections, suggested action), `changes.yaml`, `snapshot.json` | `tests/test_iteration.py::test_second_refresh_reports_only_what_is_new` |
| FR-REF-04 | ✅ | Refresh writes only under `refresh/` and the cache; updates go through checkpoints (`11-refresh.md` step 4) | `tests/test_iteration.py::test_refresh_never_changes_approved_assets` |
| FR-STA-04 (item level) | ✅ | `scripts/state/impact.py` (copy of each approval in `.approved/`, diff by item id, references in downstream files), `LaunchState.impact`, `launch.py status` lists parts to redo; orchestrator instructions | `tests/test_iteration.py::test_one_persona_change_points_to_its_grid_rows_and_playbook_items`, `test_status_prints_the_parts_to_redo` |
| FR-STA-05 | ✅ | `scripts/state/edits.py` (rendered copies in `outputs/.rendered/`), render keeps hand edits, `launch.py edits` (diff + source YAML, `--discard`), `render --force`, warnings in `status`/`start`; DOCX/XLSX not synced (documented in orchestrator; README in M8) | `tests/test_iteration.py::test_hand_edits_are_detected_protected_and_synced`, `test_discard_puts_back_the_rendered_version` |
| FR-API-03 (fail soft in refresh) | ✅ | Unavailable connectors listed in the report for web search | `tests/test_iteration.py::test_refresh_fails_soft_when_everything_is_offline` |
| M7 acceptance | ✅ | Changing cached data yields a correct what-changed report; an upstream edit marks only affected assets stale (and names the affected items) | `tests/test_iteration.py` |
