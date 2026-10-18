# Orchestrator: how to run a launch

Read this file before any launch work. It explains the pipeline, the checkpoints, the shared rules for every stage, and how state is tracked. Each stage has its own instruction file. Read it when you start that stage.

In commands, `PY` means the project's Python: `.venv/bin/python` (macOS/Linux) or `.venv\Scripts\python.exe` (Windows). `<slug>` is the launch's folder name under `launches/`.

## The pipeline

| Stage | Unit name(s) | Instructions | Writes (in `launches/<slug>/`) |
|---|---|---|---|
| 0 Intake and gap check | `intake` | `01-intake.md` | `launch-context.yaml`, `brand.yaml`, `gap-report.md` |
| 1 Industry research | `research:<industry>` | `02-industry-research.md` | `research/industry-<industry>.yaml` |
| 2 Competitive | `competitive` | `03-competitive.md` | `competitors/<id>.yaml`, `competitive-overview.yaml` |
| 3 Strategy check | `strategy` | `04-strategy-check.md` | `strategy-check.yaml` |
| 4 Personas | `personas:<industry>` | `05-personas.md` | `personas/<industry>.yaml` |
| 5 Messaging | `messaging` | `06-messaging.md` | `messaging.yaml` |
| 6a Industry playbook | `playbook:<industry>` | `07-playbook.md` | `playbooks/<industry>.yaml` |
| 6b Demo storyline | `demo:<industry>` | `08-demo-storyline.md` | `demos/<industry>.yaml` |
| 6c Webpage copy brief | `web:<industry>` | `09-web-copy.md` | `web/<industry>.yaml` |
| 7 QA and packaging | `qa` | `10-qa-packaging.md` | `qa-report.md`, `LAUNCH-KIT.md` |

Order: 0 → {1, 2} → 3 → 4 → 5 → {6a, 6b, 6c} → 7. Stages 1 and 2 depend only on intake. 6a–6c depend only on messaging and that industry's personas (6a also uses the battlecards). Every research source goes into the shared register `research/sources.json`.

**Parallel work is optional (FR-PIP-01).** If you can run subagents, you may run Stage 1 (one per industry) and Stage 2 at the same time, and 6a–6c at the same time. Each subagent reads the same instruction file and writes only its own files. If you can't, run them one after another. The result must be the same either way.

## Every stage follows the same loop

1. **Check state.** `PY scripts/launch.py status <slug>`. If anything is `stale`, see "When something upstream changes" below before doing new work.
2. **Start.** `PY scripts/launch.py start <slug> <unit>`. This is refused until every upstream unit is approved; that is the checkpoint rule (FR-STA-02). Don't work around it.
3. **Do the work** in the stage's instruction file. Write the YAML file(s) the stage owns. Register every source with `scripts/sources.py add` and cite it.
4. **Validate.** `PY scripts/validate.py --launch <slug>` and fix every problem.
5. **Submit.** `PY scripts/launch.py submit <slug> <unit>`. This checks that the files exist and match their schema, then sets the unit to `awaiting_approval`.
6. **Render a preview.** `PY scripts/launch.py render <slug>` so the PMM can read the asset in `outputs/`.
7. **Checkpoint: stop and post a short summary** (see below). Wait for the PMM.
8. **Approve only when the PMM says so.** `PY scripts/launch.py approve <slug> <unit>`, then render again.

### The checkpoint summary

Keep it short and scannable:

- **Key findings:** 3–6 bullets, the things the PMM most needs to know.
- **Assumptions:** what you labeled `[ASSUMPTION]` and why.
- **Open questions / to verify:** anything marked `[VERIFY]` or `[PROOF NEEDED]` that the PMM could resolve.
- **Where to read it:** the file(s) in `outputs/`.
- **Your options:** **approve**, **edit** (tell me what to change, or edit the YAML yourself), **redo** (with direction), or **cut** (name the items to remove).

On **edit** or **cut**, change the YAML, re-validate, re-render, and summarize what changed. On **redo**, run `start` again and redo the stage with the PMM's direction. The unit stays unapproved until the PMM approves.

### Auto mode (FR-STA-03)

If the PMM asks to skip checkpoints, run `PY scripts/launch.py auto <slug> on`. `submit` then approves each unit straight away, and every asset is labeled "Not reviewed by PMM". The strategy check still records your view; its PMM responses are marked `not_reviewed`. Two things still stop the run, because "ask, don't invent" comes first:

- intake can't be approved while a blocking gap is open;
- schema problems must still be fixed.

## Rules for every stage

1. **Accuracy over completeness (FR-GRD-01).** An empty field marked `[VERIFY]` beats a plausible invention. If you can't find evidence, say so.
2. **Cite or label every claim (principle 2):**
   - `[S12]`: a source in `research/sources.json`. Put it right after the claim it supports.
   - `[ASSUMPTION]`: your reasoned inference, not a sourced fact.
   - `[VERIFY]`: plausible but not confirmed. Add how to verify it, for example "[VERIFY] check their pricing page".
   - `[PROOF NEEDED]`: a slot for customer proof the PMM hasn't supplied.
   - `[FROM CUSTOMER DATA]`: anonymized content from transcripts or win/loss notes the PMM provided.
3. **Never invent proof (FR-GRD-02).** No made-up customer names, logos, quotes or metrics. Proof comes only from the PMM's inputs, with permission noted.
4. **Sources (FR-WEB-R-02, FR-WEB-R-04).** Use your web search and web fetch tools. Grade each source:
   - **Tier 1:** primary sources (company sites and docs, regulators, government data, filings).
   - **Tier 2:** reputable press and public analyst summaries.
   - **Tier 3:** vendor blogs, review sites, forums.

   Trend and regulatory claims need at least one Tier 1 or 2 source. Competitor pricing claims need Tier 1, or they become `[VERIFY]`. Respect site terms: no paywall workarounds and no automated logins. Never use non-public information.
5. **Register sources as you go:**

   ```
   PY scripts/sources.py add <slug> --url "<url>" --title "<title>" --publisher "<publisher>" --tier <1|2|3> --published <YYYY-MM-DD> --excerpt "<the sentence that supports the claim>"
   ```

   It prints the ID to cite (for example `S7`). Use the page's real publish date; leave `--published` out if there isn't one. The excerpt must be text from the page, not your summary. `PY scripts/sources.py check <slug>` lists citations that aren't registered.
6. **Recency (FR-GRD-07).** Trend evidence prefers the last 24 months. Competitor moves cover the last 12 months.
7. **Regulatory content is "Not legal advice" (FR-GRD-08).**
8. **Follow the resolved direction.** From Stage 4 on, use `resolved_direction` in `strategy-check.yaml`: the launch POV as adjusted by the PMM's responses. Never use a strategy point the PMM rejected (FR-STR-06).
9. **Customer-facing copy** (demo storyline, webpage copy) doesn't name competitors unless `options.name_competitors_in_customer_copy` is `true` in `launch.yaml`.
10. **Messaging is value-first (FR-OUT-03).** Customer outcome → capability → proof. Never open with a feature.
11. **Pricing models, never prices.** Never recommend a price anywhere.
12. **Brand.** Apply `brand.yaml` voice, banned and preferred terms, and product-name capitalization to everything you write.
13. **Industry-specific (G1).** Each industry gets its own trends, buyers, pains and story. Swapping the industry name into the same text is a failure.
14. **Don't edit the PMM's input files.** Especially `inputs/launch-pov.md`.

## Writing YAML safely

Square brackets, `?`, `:` and `#` mean something in YAML. Text containing labels like `[S12]` or `[VERIFY]` will break a file if it's written carelessly. So:

- Write lists **one item per line** with `- ` rather than `[a, b, c]`.
- **Put any text that contains `[`, `]`, `?`, `: ` or `#` in double quotes**, for example `- "Rules change often [VERIFY] ask IT"`.
- Run `PY scripts/validate.py --launch <slug>` after every edit. It names the file and line of any problem.

## IDs and references

Use these ID patterns so the scripts and later stages can link items:

| Item | Pattern | Example |
|---|---|---|
| Trend | `T-<industry>-<n>` | `T-technology-3` |
| Imperative | `I-<industry>-<n>` | `I-technology-1` |
| Regulation | `R-<industry>-<n>` | `R-technology-2` |
| Market data point | `MD-<industry>-<n>` | `MD-technology-1` |
| Objection | `O-<competitor>-<n>`, generic `O-gen-<n>` | `O-comp-a-2` |
| Strategy point / addition | `SC-<n>` / `SA-<n>` | `SC-4` |
| Persona | `P-<industry>-<role>` | `P-technology-cfo` |
| A persona's pain | `<persona id>#<n>` (1 = first pain) | `P-technology-cfo#2` |
| Value pillar | `PL-<n>` | `PL-2` |
| Demo moment | `DM-<n>` | `DM-3` |
| Web section | `WS-<n>` | `WS-1` |

## When something upstream changes (FR-STA-04)

`launch.py status` recalculates staleness from file contents every time. If a unit shows `stale`:

1. Tell the PMM exactly which assets are affected (status lists them) and why.
2. Ask before regenerating anything.
3. Regenerate only what is affected, and only the parts that depend on what changed. For example, one persona change means that persona's grid rows and the matching playbook sections, not the whole playbook.
4. If the PMM says the change doesn't matter, approve the stale unit as it is: `PY scripts/launch.py approve <slug> <unit>`.

If the PMM edited an approved YAML file, that unit goes back to `awaiting_approval`. Confirm the edit with them, then approve it.

## Rendered files

`PY scripts/launch.py render <slug>` writes Markdown and Word files to `outputs/` from the YAML. The YAML is the source of truth. If the PMM edits a rendered Markdown file, tell them you'll copy the edit back into the YAML before the next stage. Edits to Word files are not copied back.

## Starting a new launch

When the PMM says "start a new launch called <name>":

1. `PY scripts/launch.py new <slug> --name "<name>"` (the slug is lowercase with hyphens).
2. Tell them which files to fill in: `inputs/product-brief.md`, `inputs/launch-pov.md`, and optionally `inputs/brand-questionnaire.md`. Also tell them where to put supporting files: `inputs/brief/`, `inputs/brand/`, `inputs/optional/<type>/`.
3. When they say the inputs are ready, run Stage 0 (`01-intake.md`).
