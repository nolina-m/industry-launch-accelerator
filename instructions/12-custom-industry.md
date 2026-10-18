# Building a pack for an industry without one (FR-INP-07)

Use this when the PMM targets an industry that has no folder in `industries/` (for example public sector, manufacturing, energy or education). The pack is built during Stage 1 for that industry, before its research.

> **Accuracy over completeness.** An empty field marked `[VERIFY]` beats a plausible invention. A pack is scaffolding: where to look and what words to use. It is not findings, and nothing in it is cited as evidence.

## Steps

1. **Pick an id**: short, lowercase, hyphens (for example `public-sector`). It must match the id in `launch.yaml`.
2. **Research the scaffolding** with your web search tool. Prefer official and association sources:
   - `sub_segments`: how the industry splits (4–8).
   - `buying_committee_roles`: the roles that usually buy, use, approve or block software like this product.
   - `kpis`: what leaders in this industry are measured on.
   - `regulators`: name, jurisdiction and official URL, for the PMM's regions.
   - `regulations`: name, jurisdiction, a one-line plain summary and an official URL (the regulator's page, the official journal, eCFR or EUR-Lex). Only include ones you have confirmed exist.
   - `analyst_sources`: free public sources (government statistics, regulators, research institutes). Note that paywalled reports can only be cited through their public summaries.
   - `associations`: the main industry and professional associations.
   - `connectors`: which data connectors apply (see `connectors/registry.yaml`), with suggested queries or series IDs. Only list a series ID after checking it returns data:
     `PY scripts/connectors/query.py <slug> <connector> fetch "<series id>"`
   - `search_seeds`: 4–6 search patterns, using `<problem>`, `<year>` and similar placeholders.
   - `typical_objections`: what buyers in this industry usually push back on.
   - `vocabulary`: words to `use` and `avoid` with this audience.
3. **Save** it as `launches/<slug>/industries/<id>/pack.yaml` with `generated: true` and the same fields as the default packs. Copy the shape of any file in `industries/`.
4. **Validate**: `PY scripts/validate.py --launch <slug>`.
5. **Show the PMM** a short summary (sub-segments, regulators, the connectors you'll use) as part of the Stage 1 checkpoint for that industry.
6. **Offer to reuse it**: ask whether to copy it into `industries/<id>/` so future launches can use it. If they say yes, copy it, set `generated: false` only if they've reviewed it, and add a `notes.md` like the default packs have.

The industry brief for this industry says the pack was generated for this launch.
