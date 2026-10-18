# Stage 2: Competitive → Battlecards (asset 2)

**Unit:** `competitive`. **Writes:** one `competitors/<id>.yaml` per competitor (schema `competitor.schema.json`) and `competitive-overview.yaml` (schema `competitive-overview.schema.json`). **Needs:** `intake` approved. Can run at the same time as Stage 1.

> **Accuracy over completeness.** An empty field marked `[VERIFY]` beats a plausible invention. Every claim about a named company must come from a public source (FR-CMP-06).

## Read first

- `launch.yaml`: competitors already registered by the PMM.
- `launch-context.yaml`: known competitors, differentiation, `is_ai_product`.
- `inputs/launch-pov.md` and any `optional_inputs` of type `competitors` or `win_loss`.

## 1. The competitor set (FR-CMP-01)

1. Start with every competitor the PMM named.
2. Add **up to 3 more** that research suggests, including the **status quo** (doing nothing, or spreadsheets) and **build in-house** when they're real alternatives. Register each suggestion with `--suggested` so the PMM can accept or remove it at the checkpoint:

   ```
   PY scripts/launch.py add-competitor <slug> <id> --name "<Name>" --suggested
   ```

## 2. One battlecard per competitor (FR-CMP-03)

Research each competitor from public sources: their site and docs, filings, press releases, reputable press, public reviews. Fill in:

- `category`: `direct`, `adjacent`, `platform`, `status-quo` or `build-in-house`. Set `suggested`.
- `overview`: what they do, with citations.
- `positioning_quote`: how they describe themselves, **in their own words**, with the source. Leave it out for status-quo and build-in-house.
- `strengths` and `weaknesses`: honest and fair. Real strengths, no disparaging language (FR-GRD-03). Each one cited, or labeled `[VERIFY]`.
- `win_themes` / `loss_themes`: where we win and where we lose against them. Use the PMM's win/loss notes when there are some. Otherwise label these `[ASSUMPTION]`.
- `landmines`: questions to plant in discovery that expose their weak spots, fairly.
- `traps`: things they may say or do that pull a deal off course, and how to stay clear.
- `objections`: the **top 5** objections when this competitor is in the deal (see "Objections" below).
- `pricing`: see below.
- `recent_moves`: launches, pricing changes, funding, acquisitions and leadership changes from the **last 12 months**, each with a date and source.
- `sources`: every source ID used. Set `researched_at` to today.

Claims that aren't sourced aren't allowed. Turn them into `[VERIFY]` with a suggested way to check, for example "[VERIFY] confirm in their latest 10-K".

### Pricing model (FR-CMP-04): never prices to copy

- `model`: `seat`, `consumption`, `outcome-based`, `platform fee + usage`, `tiered bundle`, `hybrid` (list its `components`), or `unknown`.
- `value_metric`: what they charge by (users, conversations, transactions...).
- `tiers`: editions or plans, and `add_ons`.
- `free_tier`: free trial or freemium details, or "none found".
- `contract_signals`: public signals such as annual commitments, minimums or marketplace listings.
- `list_prices`: **only** if openly published on their own site (Tier 1). Each one must carry `label: "list; enterprise deals typically differ"`. Otherwise leave it out.
- Pricing claims without a Tier 1 source become `[VERIFY]`.
- **Never recommend a price, anywhere.**

## 3. Objections (FR-CMP-05)

Each objection needs:
- `text`;
- the likely `personas` and `industries`;
- the `underlying_concern`;
- a `response` in four parts: **acknowledge → reframe → evidence → question back**;
- a `proof_slot`: the proof that would answer it, or `[PROOF NEEDED]`.

Put competitor-specific objections in each battlecard (top 5). Put the generic ones in `competitive-overview.yaml` under `generic_objections`. Cover budget, status quo, build vs buy, security and compliance, integration effort, change management, and vendor viability.

**If `is_ai_product` is true,** also add these to the generic objections:
- accuracy and hallucination;
- brand and tone control;
- data privacy and training on customer data;
- compliance in regulated industries;
- workforce impact;
- "we'll build it ourselves on an LLM API".

Use IDs `O-<competitor>-<n>` and `O-gen-<n>`.

## 4. Competitive overview (FR-CMP-02): one page

- `categories`: which competitors fall into direct, adjacent, platform, status quo and build-in-house.
- `positioning_map`: two axes that matter to buyers in the target industries. Give each axis a label, what low and high mean, and a `rationale` for choosing it. Place every competitor and our product (`competitor_id: null`) on a 0–10 scale, each with a one-line rationale. Mark placements without evidence `[ASSUMPTION]`.
- `industry_strength`: for each target industry, who is strongest and why (cited).
- `generic_objections`: see above.

## Checkpoint

Submit, render, and summarize:
- the competitor set, saying which ones you **suggested** (the PMM accepts or removes them);
- the biggest threat per industry;
- our clearest win theme;
- the chosen positioning-map axes;
- anything marked `[VERIFY]`, especially pricing.

If the PMM removes a suggested competitor, run `PY scripts/launch.py remove-competitor <slug> <id>`, delete its file, and remove it from the overview. Battlecards are in `outputs/02-battlecard-<id>.*` and the overview in `outputs/02-competitive-overview.*`.
