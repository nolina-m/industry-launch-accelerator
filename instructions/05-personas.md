# Stage 4: Personas and buying committee (asset 4)

**One unit per industry:** `personas:<industry>`. **Writes:** `personas/<industry>.yaml` (schema `personas.schema.json`). **Needs:** `strategy` and `research:<industry>` approved.

> **Accuracy over completeness.** An empty field marked `[VERIFY]` beats a plausible invention. Personas are research-derived archetypes, not real people.

## Read first

- `research/industry-<industry>.yaml`: trends and imperatives (pains must link to them).
- `strategy-check.yaml`: the `resolved_direction`, especially the priority buyers.
- `launch-context.yaml`: buyer roles from the brief.
- The industry pack's `buying_committee_roles`, `kpis` and `vocabulary`.
- Any call transcripts or win/loss notes in `optional_inputs`.

## What to produce

### 4 to 6 personas (FR-PER-01)

Cover the whole buying committee: an **economic buyer**, a **champion**, a **technical evaluator**, an **end user or operator**, and a likely **blocker** (security, procurement or compliance). Add an `influencer` if one matters. Set `buying_role` accordingly.

For each persona (FR-PER-02), fill in:
- `role`, common `titles`, `reports_to`;
- `responsibilities` and `kpis`;
- `pains`: the **top 3**, specific to this industry. Each is linked to the `trend_ids` (and `imperative_ids`) it comes from (FR-PER-03);
- `goals`, buying `triggers`, `objections`, `info_sources` (where they learn: associations, publications, peers);
- `language`: words they `use` and words that put them off (`avoid`);
- `beliefs_to_buy`: what they must believe to say yes;
- `discovery_questions`: exactly **5**, open-ended, for this persona in this industry.

**Provenance (FR-PER-04).**
- With transcripts or win/loss notes, you may add short **anonymized** quotes under `quotes`, labeled `[FROM CUSTOMER DATA]`, with the source file. Remove names, companies and anything identifying. Set `provenance` to `from-customer-data` or `mixed`.
- Otherwise set `provenance: research-derived`.
- Never invent a quote.

**Different by industry (FR-PER-05).** A CISO in healthcare and a CISO in financial services have different pains, regulators, KPIs and vocabulary. Write them that way. QA flags persona pairs across industries whose pains are more than 70% alike.

### Buying committee map (FR-PER-06)

`committee_map`: `edges` (who influences whom: `from` → `to`, with `influence` `high`, `medium` or `low`) and the typical `decision_sequence` (persona IDs in the order they usually engage). Mark anything that is a reasoned guess `[ASSUMPTION]` in the persona's text. The renderer draws the map as a table and a diagram.

## IDs

Personas are `P-<industry>-<role>` (for example `P-healthcare-life-sciences-ciso`). A pain is referred to as `<persona id>#<n>`.

## Checkpoint

Submit, render, and summarize:
- the committee in one line: who signs, who champions, who can block;
- the sharpest pain per persona;
- what's assumed versus taken from customer data.

The asset is `outputs/04-personas-<industry>.*`.
