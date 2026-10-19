# Requirements trace

Every requirement ID → the files that implement it → the test or check that proves it.

**Status:** ✅ done · 🟡 partly done (the note says what's left) · ⏸️ waived by the owner

Test paths are under `tests/`. "Smoke run" means a private end-to-end run outside the repo (deleted afterwards, nothing committed); see FR-TST-03.

## Users and inputs

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-USR-01 | Non-developer can set up and use it | ✅ | `README.md` quickstart (copy-paste, no Git/Python knowledge), `setup.sh`, `setup.ps1`, plain messages in all scripts | `test_repo_hygiene.py::test_readme_first_screen_and_sections`; owner ran setup on macOS |
| FR-INP-01 | Product brief template (Appendix A) | ✅ | `templates/inputs/product-brief.md`, `scripts/intake/fields.py` | `test_intake.py::test_every_brief_field_has_a_heading_in_the_template` |
| FR-INP-02 | Free-form brief files read | ✅ | `scripts/extract/extract.py` (MD, TXT, DOCX, PDF, PPTX) | `test_extract.py` |
| FR-INP-03 | Template wins; conflicts logged | ✅ | `scripts/intake/run_intake.py::merge_field`, `conflicts` in launch-context, `gap_report.py` | `test_intake.py::test_template_wins_over_agent_value_but_agent_value_fills_gaps`, `test_contradictions_become_blocking_questions` |
| FR-INP-04 | Launch POV template | ✅ | `templates/inputs/launch-pov.md` | `test_intake.py::test_pov_text_and_industries_are_read` |
| FR-INP-05 | POV drives every stage; never edited by the agent | ✅ | `AGENTS.md` rule 8, `instructions/00-orchestrator.md`, `04-strategy-check.md` (resolved direction) | Manual read; `test_state.py::test_strategy_check_needs_a_pmm_response_for_every_point` |
| FR-INP-06 | Industries from packs or free; focus options | ✅ | POV "Target industries", `launch.py add-industry` (sub-segments, regions, size) | `test_intake.py::test_pov_text_and_industries_are_read`, `test_state.py::test_cli_new_status_and_approve` |
| FR-INP-07 | Custom industry pack built and offered for reuse | ✅ | `instructions/12-custom-industry.md`, launch-local `industries/<id>/pack.yaml` validated | `test_schemas.py::test_schema_lookup_by_path` |
| FR-INP-08 | Brand inputs accepted | ✅ | `scripts/brand/extract_brand.py` (questionnaire, brand docs, URL via agent, PNG logos, .docx/.dotx) | `test_brand.py` |
| FR-INP-09 | `brand.yaml` extracted | ✅ | `extract_brand.py`, `schemas/brand.schema.json` | `test_brand.py::test_questionnaire_answers_are_used` |
| FR-INP-10 | Word template styles used; neutral theme otherwise | ✅ | `scripts/brand/inspect_template.py`, `scripts/render/docx_writer.py`, `scripts/brand/theme.py` | `test_render.py::test_word_template_is_used_as_the_base`, `test_brand_fonts_and_colors_are_applied`, `test_qa.py::test_brand_passes_on_rendered_files` |
| FR-INP-11 | No brand → neutral theme, "Unbranded draft", gap logged | ✅ | `extract_brand.py`, `gap_report.py`, renderer status line and header | `test_brand.py::test_no_brand_input_means_unbranded_neutral_theme`, `test_render.py::test_every_asset_has_status_footer_and_verify_section` |
| FR-INP-12 | Optional inputs classified | ✅ | `run_intake.py::optional_inputs`, `01-intake.md` | `test_intake.py::test_optional_inputs_are_classified_by_folder` |

## Outputs and pipeline

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-OUT-01 | No PDF export | ✅ | README "Working with the kit" (save as PDF from Word/Docs) | Manual read |
| FR-OUT-02 | Files open cleanly in Word, Excel, Google Docs, Google Sheets | ✅ | Built-in styles, explicit table borders and widths, inline PNG, no macros/fonts/SmartArt | Owner check in all four apps, 2026-10-18; `test_render.py` (files open) |
| FR-OUT-03 | Value-first; proof stays `[PROOF NEEDED]`; no competitor names in customer copy unless opted in | ✅ | `00-orchestrator.md`, `06`/`08`/`09` instructions, `scripts/qa/content_checks.py::check_rules`, feature-first check | `test_qa.py::test_rules_*`, `test_sameness_catches_feature_first_message` |
| FR-PIP-01 | Parallel is optional; sequential equivalent | ✅ | `scripts/state/pipeline.py` (dependency graph), `00-orchestrator.md` | `test_state.py::test_units_follow_the_pipeline`, `test_stages_one_and_two_only_need_intake` |

## Stage 0: Intake

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-INT-01 | Extract text from all inputs | ✅ | `scripts/extract/extract.py` | `test_extract.py` |
| FR-INT-02 | `launch-context.yaml` with source per field | ✅ | `scripts/intake/run_intake.py`, `schemas/launch-context.schema.json` | `test_intake.py::test_filled_brief_records_values_and_source` |
| FR-INT-03 | Blocking vs non-blocking gaps | ✅ | `scripts/intake/gap_report.py`, `launch_state.py::_check_no_open_blocking_gaps` | `test_intake.py::test_required_fields_block_and_recommended_fields_become_assumptions`, `test_intake_cannot_be_approved_with_open_blocking_gaps` |
| FR-INT-04 | Specific questions, max 7, by impact | ✅ | `gap_report.py::questions_this_round`, `fields.py` | `test_intake.py::test_at_most_seven_questions_blocking_first`, `test_empty_brief_asks_once_instead_of_field_by_field` |
| FR-INT-05 | Contradictions raised as questions | ✅ | `conflicts` → `gap_report.py` | `test_intake.py::test_contradictions_become_blocking_questions` |
| FR-INT-06 | Missing POV is blocking | ✅ | `gap_report.py` | `test_intake.py::test_missing_pov_and_industries_are_blocking` |
| FR-INT-07 | `brand.yaml` + Word template inspector | ✅ | `extract_brand.py`, `inspect_template.py` | `test_brand.py::test_inspector_lists_styles`, `test_word_template_styles_fonts_and_colors` |
| FR-INT-08 | `gap-report.md` | ✅ | `gap_report.py::render` | `test_intake.py::test_gap_report_lists_blocking_and_non_blocking` |

## Stage 1: Industry research

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-TRD-01 | 5–8 trends, ≥2 independent sources, ≥1 recent | ✅ | `02-industry-research.md`, schema (max), QA counts/sources | `test_qa.py::test_sources_flag_old_and_single_source_trends`, `test_completeness_counts_are_warnings_only` |
| FR-TRD-02 | 3–5 imperatives linked to trends and capabilities | ✅ | `02-industry-research.md`, schema | `test_schemas.py`; QA count check |
| FR-TRD-03 | Regulatory landscape, "Not legal advice" | ✅ | Schema `disclaimer` const, `industry-brief.md.j2` | `test_schemas.py::test_regulatory_section_must_say_not_legal_advice` |
| FR-TRD-04 | 3–6 market data points with source, series ID, date | ✅ | Schema, connectors, `query.py --register` | `test_schemas.py`, `connectors/test_connectors.py::test_query_tool_registers_sources_with_series_and_connector` |
| FR-TRD-05 | Relevance rating; Low excluded downstream | ✅ | Schema, `06-messaging.md` | `test_schemas.py`; manual read |
| FR-TRD-06 | Respect sub-segment, region, size focus | ✅ | `launch.yaml` industries, `02-industry-research.md`, brief "Focus" line | `test_render.py`; manual read |

## Stage 2: Competitive

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-CMP-01 | PMM-named first, up to 3 suggested, marked | ✅ | `03-competitive.md`, `launch.py add-competitor --suggested`, battlecard label | `test_state.py::test_cli_options_and_competitors` |
| FR-CMP-02 | One-page overview with positioning map | ✅ | `competitive-overview.schema.json`, `competitive-overview.md.j2`, `diagrams.py::positioning_map` | `test_render.py::test_all_eight_assets_render_for_two_industries` |
| FR-CMP-03 | Battlecard contents | ✅ | `competitor.schema.json`, `battlecard.md.j2` | `test_render.py` |
| FR-CMP-04 | Pricing model, list prices labeled, no recommendations | ✅ | Schema (model enum, required label), QA tier and price-advice checks | `test_schemas.py::test_list_price_must_carry_the_enterprise_label`, `test_qa.py::test_sources_require_tier_1_for_list_prices`, `test_rules_catch_competitor_in_customer_copy_and_price_advice` |
| FR-CMP-05 | Objections incl. AI-specific; acknowledge→reframe→evidence→question | ✅ | `common.schema.json#objection`, `03-competitive.md` | `test_schemas.py` |
| FR-CMP-06 | Named-company claims from public sources or `[VERIFY]` | ✅ | `03-competitive.md`, QA citation check (named companies) | `test_qa.py::test_citations_catch_named_company_and_regulatory_claims` |

## Stage 3: Strategy check

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-STR-01 | After stages 1 and 2 approved | ✅ | Pipeline dependencies | `test_state.py::test_strategy_needs_every_industry_researched` |
| FR-STR-02 | Point, stance, reasoning, evidence, confidence | ✅ | `strategy-check.schema.json`, `04-strategy-check.md` | `test_schemas.py` |
| FR-STR-03 | Up to 5 additions | ✅ | Schema (max 5) | `test_schemas.py::test_more_than_five_strategy_additions_is_rejected` |
| FR-STR-04 | Direct, respectful tone | ✅ | `04-strategy-check.md` | Manual read |
| FR-STR-05 | PMM responds to every point; both rendered | ✅ | Schema `pmm_response`, approval gate, `strategy-check.md.j2` | `test_state.py::test_strategy_check_needs_a_pmm_response_for_every_point`, `test_render.py::test_strategy_check_shows_agent_view_and_pmm_response` |
| FR-STR-06 | Downstream uses resolved direction | ✅ | `resolved_direction` required at approval; stage 4+ instructions | `test_state.py`; manual read |
| FR-STR-07 | Disagreement never blocks | ✅ | No gate on stance | `test_state.py` |

## Stages 4–6: Personas, messaging, sales assets

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-PER-01 | 4–6 personas covering the committee | ✅ | Schema (max 6), QA count, `05-personas.md` | `test_schemas.py::test_more_than_six_personas_is_rejected`; QA count |
| FR-PER-02 | Persona fields incl. 5 discovery questions | ✅ | `personas.schema.json` | `test_schemas.py`; QA count |
| FR-PER-03 | Pains link to trend/imperative IDs | ✅ | Schema `trend_ids` required | `test_schemas.py` |
| FR-PER-04 | `[FROM CUSTOMER DATA]` quotes or research-derived | ✅ | Schema `provenance`, `quotes.label` const | `test_schemas.py` |
| FR-PER-05 | Personas differ by industry | ✅ | `check_sameness` | `test_qa.py::test_sameness_catches_near_identical_personas` |
| FR-PER-06 | Committee map as table and diagram | ✅ | `personas.md.j2`, `diagrams.py::committee_map` | `test_render.py::test_markdown_tables_and_headings_become_word_structure` |
| FR-MSG-01 | Positioning, pitch, boilerplate | ✅ | `messaging.schema.json`, `messaging.md.j2` | `test_render.py` |
| FR-MSG-02 | 3–4 pillars with proof or `[PROOF NEEDED]` | ✅ | Schema (max 4), template | `test_render.py`; QA count |
| FR-MSG-03 | Industry × persona grid, XLSX with filters and frozen headers | ✅ | Schema, `xlsx_writer.py` | `test_render.py::test_excel_grid_has_filters_frozen_header_and_one_row_per_persona` |
| FR-MSG-04 | Value-based; feature-first flagged | ✅ | `06-messaging.md`, `check_sameness` | `test_qa.py::test_sameness_catches_feature_first_message`, `test_feature_first_heuristic` |
| FR-MSG-05 | Brand tone and terms; resolved direction | ✅ | `06-messaging.md`, `check_brand` terms | `test_qa.py::test_brand_catches_banned_term_preferred_term_and_product_caps` |
| FR-PBK-01 | Industry playbook contents | ✅ | `playbook.schema.json`, `07-playbook.md`, `playbook.md.j2` | `test_render.py` |
| FR-DMO-01 | Demo storyline contents | ✅ | `demo.schema.json`, `08-demo-storyline.md`, `demo.md.j2` | `test_render.py::test_demo_storyline_content` |
| FR-DMO-02 | Spec; assumed capabilities `[VERIFY]` | ✅ | `08-demo-storyline.md`, `verify` per moment | `test_render.py::test_demo_storyline_content` |
| FR-WEB-01 | Webpage copy brief contents | ✅ | `web.schema.json`, `09-web-copy.md`, `web.md.j2` | `test_render.py::test_web_copy_content` |
| FR-WEB-02 | Copy and structure only | ✅ | `09-web-copy.md`, template note | Manual read |

## Stage 7: QA and packaging

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-QA-01 | Schemas validate | ✅ | `content_checks.py::check_structure`, `scripts/validate.py` | `test_qa.py::test_structure_catches_schema_error`, `test_schemas.py` |
| FR-QA-02 | Citation coverage ≥95%, uncovered listed | ✅ | `check_citations` | `test_qa.py::test_citations_catch_an_uncited_claim` |
| FR-QA-03 | Sources resolve, dated, recent | ✅ | `check_sources`, `--check-links` | `test_qa.py::test_sources_*`, `test_link_check_reports_dead_links` |
| FR-QA-04 | Palette, fonts, banned terms, product names | ✅ | `output_checks.py::check_brand` | `test_qa.py::test_brand_*` |
| FR-QA-05 | Empty sections, placeholders, tables, length | ✅ | `check_layout`, `scripts/qa/limits.yaml` | `test_qa.py::test_layout_*` |
| FR-QA-06 | Sameness >70%; feature-first | ✅ | `check_sameness` | `test_qa.py::test_sameness_*` |
| FR-QA-07 | Completeness | ✅ | `check_completeness` | `test_qa.py::test_completeness_*` |
| FR-QA-08 | Render all; `LAUNCH-KIT.md` with top 10 | ✅ | `scripts/qa/run.py`, `scripts/qa/kit.py` | `test_qa.py::test_run_writes_report_and_kit` |

## State, checkpoints and refresh

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-STA-01 | `launch.yaml` state | ✅ | `launch_state.py`, `launch.schema.json` | `test_state.py::test_launch_yaml_round_trips_and_validates` |
| FR-STA-02 | Checkpoints; downstream refuses until approved | ✅ | `launch_state.py`, `00-orchestrator.md` | `test_state.py::test_downstream_refuses_to_start_until_upstream_approved`; M3 smoke run |
| FR-STA-03 | Auto mode labels "Not reviewed by PMM" | ✅ | `launch.py auto`, renderer status | `test_state.py::test_auto_mode_*`, `test_render.py::test_auto_mode_assets_say_not_reviewed` |
| FR-STA-04 | Staleness by hash; regenerate only what's affected | ✅ | `hashing.py`, `launch_state.py::refresh`, `impact.py` | `test_state.py::test_persona_edit_marks_only_affected_assets_stale`, `test_iteration.py::test_one_persona_change_points_to_its_grid_rows_and_playbook_items` |
| FR-STA-05 | Markdown edits detected and synced; DOCX not | ✅ | `scripts/state/edits.py`, `launch.py edits`, `render --force` | `test_iteration.py::test_hand_edits_are_detected_protected_and_synced` |
| FR-STA-06 | Launches coexist, self-contained | ✅ | `launches/<slug>/` | `test_state.py::test_new_launch_starts_everything_not_started` |
| FR-REF-01 | On-demand refresh command | ✅ | `launch.py refresh`, `11-refresh.md` | `test_iteration.py::test_first_refresh_reports_changes_since_research` |
| FR-REF-02 | Re-checks competitors, regulation, data, source health | ✅ | `scripts/refresh/refresh.py` + web search in `11-refresh.md` | `test_iteration.py::test_first_refresh_*`, `test_refresh_checks_source_health` |
| FR-REF-03 | Compare with previous; `what-changed.md` | ✅ | `refresh.py` snapshots and report | `test_iteration.py::test_second_refresh_reports_only_what_is_new` |
| FR-REF-04 | Never overwrites approved assets | ✅ | Refresh writes only under `refresh/` and the cache | `test_iteration.py::test_refresh_never_changes_approved_assets` |

## Industry packs and data sources

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-IND-01 | Pack contents and schema | ✅ | `industries/*/pack.yaml`, `notes.md`, schema | `test_packs.py::test_pack_is_valid_and_complete` |
| FR-IND-02 | Six default packs | ✅ | `industries/` | `test_packs.py::test_the_six_default_packs_exist` |
| FR-IND-03 | Packs are scaffolding | ✅ | Pack headers, `notes.md`, research instructions | `test_packs.py::test_packs_name_no_vendors` |
| FR-WEB-R-01 | Host agent's web tools, named generically | ✅ | `00-orchestrator.md`; tool names verified 2026-10-18 in `docs/compatibility.md` | Manual read |
| FR-WEB-R-02 | Source tiers and tier rules | ✅ | `scripts/sources.py`, registry tiers, `check_sources` | `test_sources.py`, `test_qa.py::test_sources_*` |
| FR-WEB-R-03 | Source register | ✅ | `research/sources.json`, `sources.schema.json` | `test_sources.py` |
| FR-WEB-R-04 | Site terms, no paywalls or logins | ✅ | `00-orchestrator.md`; only sources allowing business use (`docs/data-sources.md`) | Manual read |
| FR-API-01 | `check.py` | ✅ | `scripts/connectors/check.py`, run by setup | `connectors/test_connectors.py::test_check_reports_ready_needs_setup_and_unreachable` |
| FR-API-02 | Packs list connectors and series | ✅ | Pack `connectors` (series IDs checked live) | `test_packs.py::test_pack_connectors_exist_and_name_series_ids` |
| FR-API-03 | Rate limits, User-Agent, cache, fail soft | ✅ | `connectors/base.py` | `connectors/test_connectors.py` |
| FR-API-04 | Numbers show source, series, date | ✅ | `Record`, `query.py` | `connectors/test_connectors.py::test_connector_reads_its_recorded_response` |
| FR-API-05 | How to add a connector | ✅ | `docs/adding-a-data-source.md` | Manual read |

## Quality bar and guardrails

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-GRD-01 | Accuracy over completeness, in every stage file | ✅ | Every file in `instructions/` | Manual read |
| FR-GRD-02 | No made-up proof | ✅ | Instructions; `[PROOF NEEDED]` defaults in schemas and templates | Manual read |
| FR-GRD-03 | Fair competitive content | ✅ | `03-competitive.md` | Manual read |
| FR-GRD-04 | Public information only | ✅ | Instructions; `CONTRIBUTING.md`; no launches tracked | `test_repo_hygiene.py::test_no_launches_or_sample_outputs_are_tracked` |
| FR-GRD-05 | No brand assets bundled | ✅ | `.gitignore`, contributing rules | `test_repo_hygiene.py::test_no_brand_assets_or_binary_samples_are_bundled` |
| FR-GRD-06 | Draft footer on every asset | ✅ | `render.py` (Markdown + Word footer), XLSX footer, kit | `test_render.py::test_every_asset_has_status_footer_and_verify_section` |
| FR-GRD-07 | Recency rules | ✅ | Instructions, `check_sources` | `test_qa.py::test_sources_flag_old_and_single_source_trends` |
| FR-GRD-08 | Regulatory content "Not legal advice" | ✅ | Schema const, template, pack notes | `test_schemas.py::test_regulatory_section_must_say_not_legal_advice` |

## Rendering and compatibility

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-RND-01 | DOCX via python-docx, brand or Word template | ✅ | `docx_writer.py` (one Jinja layout per asset feeds both Markdown and Word; see `docs/design-decisions.md`) | `test_render.py` |
| FR-RND-02 | XLSX via openpyxl | ✅ | `xlsx_writer.py` | `test_render.py::test_excel_grid_*` |
| FR-RND-03 | Markdown via Jinja2 | ✅ | `render.py`, `templates/docs/*.md.j2` | `test_render.py` |
| FR-RND-04 | Diagrams as PNG plus tables | ✅ | `diagrams.py` | `test_render.py::test_all_eight_assets_render_for_two_industries` |
| FR-RND-05 | Deterministic renderers | ✅ | Fixed dates, PNG without metadata | `test_render.py::test_rendering_is_deterministic`, `test_png_diagrams_are_deterministic` |
| FR-RND-06 | Widely available fonts with fallbacks | ✅ | `theme.py` (Arial); theme fonts removed from styles | `test_qa.py::test_brand_passes_on_rendered_files` |
| FR-CMPT-01 | Works with read files + run shell | ✅ | Plain Markdown instructions, Python scripts | Claude Code end to end; `docs/compatibility.md` |
| FR-CMPT-02 | macOS, Linux, Windows; Python 3.10+ only | 🟡 | `setup.sh`, `setup.ps1`, CI on Python 3.10 and 3.13 | macOS tested; Linux tests green in CI; Windows written, not tested (owner decision) |
| FR-CMPT-03 | Run in Claude Code and one other agent | ⏸️ | `docs/compatibility.md` | Claude Code done; second agent waived by the owner (2026-10-18) |

## Docs and testing

| ID | Requirement | Status | Implemented in | Proved by |
|---|---|---|---|---|
| FR-DOC-01 | README first screen with diagram | ✅ | `README.md`, `docs/images/pipeline.svg` | `test_repo_hygiene.py::test_readme_first_screen_and_sections` |
| FR-DOC-02 | "How it works in 60 seconds" | ✅ | `README.md` | `test_repo_hygiene.py::test_readme_first_screen_and_sections` |
| FR-DOC-03 | Copy-paste quickstart (Mac, Windows, agents, keys) | ✅ | `README.md` Quickstart, `.env.example` | Owner review |
| FR-DOC-04 | Example runs placeholder | ✅ | `README.md` | `test_repo_hygiene.py::test_readme_first_screen_and_sections` |
| FR-DOC-05 | About the author with links | 🟡 | `README.md` | Draft wording; the owner will edit it |
| FR-DOC-06 | Design decisions with owner placeholder | ✅ | `docs/design-decisions.md` | `test_repo_hygiene.py::test_design_decisions_has_owner_placeholder_and_topics` |
| FR-DOC-07 | Customization; contributing | ✅ | `docs/customization.md`, `CONTRIBUTING.md` | Manual read; `test_repo_hygiene.py::test_markdown_links_to_repo_files_resolve` |
| FR-DOC-08 | Issue templates (bug, feedback 1–5, pack, data source) | ✅ | `.github/ISSUE_TEMPLATE/*.yml` | `test_repo_hygiene.py::test_feedback_form_has_the_1_to_5_rating` |
| FR-TST-01 | CI with lint and tests, no network | ✅ | `.github/workflows/ci.yml`, `tests/conftest.py` | `test_scaffold.py::test_network_is_blocked_in_tests`; GitHub Actions green on Python 3.10 and 3.13 (2026-10-19) |
| FR-TST-02 | Unit tests incl. seeded defects; no example launch | ✅ | `tests/` (inline placeholder data; recorded connector responses) | Full suite; `test_repo_hygiene.py` |
| FR-TST-03 | Private end-to-end smoke run before release | ✅ | Smoke runs at M3 (real sources), M4 (formats) and pre-release 2026-10-19 (every command end to end: intake, 15 stages, render, QA, edit sync, live refresh); all deleted | Build log |

## Other rules from the PRD

| Rule | Status | Proved by |
|---|---|---|
| Read-first #3: the PRD is never committed | ✅ | `.gitignore`; `test_scaffold.py::test_private_files_are_git_ignored`, `test_repo_hygiene.py::test_no_private_build_documents_are_tracked` |
| Read-first #4: no example launch, company, brief or outputs | ✅ | `test_repo_hygiene.py::test_no_launches_or_sample_outputs_are_tracked` |
| Read-first #6: no employer or job-application mentions | ✅ | `test_repo_hygiene.py::test_no_employer_or_job_application_mentions` |
| §13.1 `AGENTS.md` canonical; `CLAUDE.md` pointer | ✅ | `test_scaffold.py::test_claude_md_imports_agents_md` |
| §11.2 source list verified at build time | ✅ | `docs/data-sources.md` (changes approved by the owner 2026-10-18) |
| M0–M8 acceptance criteria | ✅ | Per milestone in the build log; M9 (release) in progress |
