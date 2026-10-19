# Customization

Three things are designed to be customized: **industry packs**, **data sources** and **brand / Word templates**. None of them need code changes, except adding a data source.

## Add or improve an industry pack

An industry pack gives the agent a starting map for one industry: sub-segments, buying committee roles, KPIs, regulators and regulations, public sources, which data connectors to use, search starting points, typical objections, and vocabulary. It is **scaffolding, not findings**: every trend still comes from fresh, cited research.

**The easy way:** target an industry that has no pack. The agent builds one for that launch (`launches/<slug>/industries/<id>/pack.yaml`, following `instructions/12-custom-industry.md`) and offers to save it to `industries/` for future launches.

**By hand:**
1. Copy a folder in `industries/` (for example `industries/technology/`) to `industries/<your-id>/`. Use lowercase with hyphens, for example `public-sector`.
2. Edit `pack.yaml`. Every field is explained by the default packs. For regulations, link to an official page (the regulator, the official journal, eCFR or EUR-Lex). For data series, only list IDs you've checked return data:
   ```
   .venv/bin/python scripts/connectors/query.py <slug> bls fetch "<series id>"
   ```
3. Update `notes.md`.
4. Validate:
   ```
   .venv/bin/python scripts/validate.py industries/<your-id>/pack.yaml
   ```

Don't name vendors or competitors in a pack; that belongs in each launch's research. To share a pack, open a pull request (see [CONTRIBUTING.md](../CONTRIBUTING.md)).

## Add a data source

See [adding-a-data-source.md](adding-a-data-source.md). It takes one module, one test with a recorded response, and one registry row. The source must be free to use for business purposes.

## Use your brand

You can give brand guidance at intake in any mix of these. Later items win when they disagree:

1. **Nothing.** Documents use a clean neutral style (Arial, navy headings) and are labeled "Unbranded draft".
2. **A Word template** (`.dotx`, or a `.docx` with "template" in its name) in `inputs/brand/`. The toolkit uses it as the base for every Word file. It maps your styles (Heading 1, Normal, List Bullet, Table Grid, and so on) and takes your heading font and color from it. To see what it found:
   ```
   .venv/bin/python scripts/brand/inspect_template.py inputs/brand/<file>
   ```
3. **A brand book or style guide** (PDF, Word or Markdown) in `inputs/brand/`, or a brand page URL in the questionnaire. The agent reads it, confirms colors, fonts, voice and terms with you, and records them.
4. **The brand questionnaire** (`inputs/brand-questionnaire.md`): your direct answers always win.

**Logos** must be PNG (Word can't hold SVG). Name the dark-background version with "white", "dark" or "reverse" in the file name.

**Fonts:** fonts available in both Word and Google Docs (Arial, Roboto, Lato, Georgia and similar) look the same everywhere. A font that isn't installed will be substituted by Word or Google Docs.

**Terms:** banned terms, preferred terms ("use X instead of Y") and exact product-name capitalization are applied by the agent while writing, and checked by QA.

## Adjust QA limits

Length limits per asset are in `scripts/qa/limits.yaml`. To change them for one launch, create `launches/<slug>/qa-limits.yaml` with only the values you want to change:

```yaml
06-playbook: 5000
```
