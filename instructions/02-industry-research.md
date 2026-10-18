# Stage 1: Industry research → Industry brief (asset 1)

**One unit per industry:** `research:<industry>`. **Writes:** `research/industry-<industry>.yaml` (schema `schemas/industry-research.schema.json`). **Needs:** `intake` approved.

> **Accuracy over completeness.** An empty field marked `[VERIFY]` beats a plausible invention. Five well-sourced trends beat eight thin ones.

## Read first

- `launch-context.yaml`: what the product does, for whom, and its capabilities. Trends must matter to this product's problem space.
- `inputs/launch-pov.md`: the PMM's direction.
- The industry pack, if there is one (if not, build it first with `instructions/12-custom-industry.md`): `industries/<industry>/pack.yaml` (or `launches/<slug>/industries/<industry>/pack.yaml` for a custom industry). It lists regulators, sources, search seeds and data connectors. **The pack is scaffolding, not findings (FR-IND-03).** Every trend comes from fresh research.
- The industry's focus in `launch.yaml` (sub-segments, regions, company size). Respect it throughout (FR-TRD-06).

## What to produce

### Trends (FR-TRD-01, FR-TRD-05): 5 to 8

For each trend:
- `headline`: short and specific to this industry.
- `summary`: what's happening, in 2–3 sentences, with citations inline.
- `evidence`: **at least 2 independent sources** (different publishers), and **at least 1 from the last 24 months**. At least one must be Tier 1 or 2. Each item: `source_id` plus a short `excerpt` from the source.
- `impact`: the business impact on companies in this industry.
- `so_what`: what this means for *this* product, linked to its capabilities.
- `relevance`: `rating` (`High` | `Med` | `Low`) plus a one-sentence `rationale`. Low-rated trends stay in the brief but are left out of messaging by default.

If you can only find one solid source for a trend, keep it only if it's clearly important; label the gap `[VERIFY] second source needed`. If you can't reach 5 well-sourced trends, stop at what you have and say so at the checkpoint.

### Imperatives (FR-TRD-02): 3 to 5

What leaders in this industry must do in the next 12–24 months. Each one has a `statement`, the `trend_ids` it follows from, and `capability_refs`: which product capabilities (from the brief) help. Use the brief's own wording for capabilities.

### Regulatory landscape (FR-TRD-03)

Set `regulatory.disclaimer: "Not legal advice"`. List the regulations and rules relevant to *this product* in *this industry* and its regions: `name`, `jurisdiction`, `status` (`in_force`, `proposed`, `pending`, `repealed`, `other`), a plain `summary`, why it's `relevant`, and `evidence`. Prefer the regulator's own site or the official journal (Tier 1). If none apply, leave `items` empty and say so at the checkpoint. Never guess.

### Using the data connectors (FR-API-03, FR-API-04)

The pack's `connectors` list says which public data sources fit this industry, with suggested queries and series IDs. Query them like this:

```
PY scripts/connectors/query.py <slug> <connector> search "<query>" [--opt since=2025-01-01] --register
PY scripts/connectors/query.py <slug> <connector> fetch "<series id>" --register
```

`--register` adds each result to the source register and prints the ID to cite. Every number shows its source, series ID and retrieval date. Run `PY scripts/connectors/check.py --offline` to see which connectors are switched on. If a connector isn't available (no key, offline, rate-limited), the tool says so. Carry on with web search, and mention the gap at the checkpoint. Never let a missing connector stop the stage.

### Market data (FR-TRD-04): 3 to 6 data points

Numbers that size or describe the industry: employment, spending, number of firms, growth. Prefer public data: government statistics, regulators, filings. Every number shows its source (`source_id`), its `series_id` (the dataset or table ID; use `null` only if the source has none), and its `retrieved_at` date. If you used a data connector, set `connector` to its id (from `connectors/registry.yaml`). Never round, combine or extrapolate numbers without labeling it `[ASSUMPTION]` in the `note`.

## IDs

`T-<industry>-<n>`, `I-<industry>-<n>`, `R-<industry>-<n>`, `MD-<industry>-<n>`. Set `industry` on every trend and imperative, and set `researched_at` to today.

## Checkpoint

Submit, render, and summarize:
- the top 3 trends and why they matter for this product;
- any trend you rated Low;
- regulatory items to watch;
- the data points found and any missing;
- anything marked `[VERIFY]`.

The industry brief is in `outputs/01-industry-brief-<industry>.md` and `.docx`.
