# QA report: My Product Launch · RelayCX is a fictional test product, not a real product

_Generated 2026-10-19 by Industry Launch Accelerator. Draft: verify before external use._

**Ready for PMM review.** 0 error(s), 28 warning(s).

Errors must be fixed (or accepted by the PMM) before field use. Warnings are worth a look and may be fine.

| Check | Result | Errors | Warnings | Summary |
|---|---|---|---|---|
| FR-QA-01 Structure: every YAML file matches its schema | ✅ pass | 0 | 0 | All files match their schemas. |
| FR-QA-02 Citations: every factual claim is cited or labeled | ⚠️ warnings | 0 | 2 | 116 of 118 detectable claims cited or labeled (98%; target 95%). |
| FR-QA-03 Sources: registered, dated, recent and of the right tier | ⚠️ warnings | 0 | 9 | 36 registered source(s), 36 cited. |
| FR-QA-04 Brand: palette, fonts and terms | ✅ pass | 0 | 0 | Checked 22 Word/Excel file(s) against 5 brand color(s) and 1 font name(s); checked terms in the content. |
| FR-QA-05 Layout: no empty sections, placeholders or broken tables; within length | ⚠️ warnings | 0 | 9 | Checked 21 rendered Markdown file(s). |
| FR-QA-06 Industry-specific and value-first | ✅ pass | 0 | 0 | Compared 36 persona pair(s) across industries; checked 25 message(s). |
| FR-QA-07 Completeness: every industry and competitor has every asset | ⚠️ warnings | 0 | 8 | 2 industries, 8 competitor(s) checked. |
| FR-OUT-03 Cross-asset rules: customer copy, pricing, proof | ✅ pass | 0 | 0 | Checked customer-facing copy and pricing language. |

## FR-QA-02: Citations: every factual claim is cited or labeled

- **warning** competitive-overview.yaml (generic_objections[10].response.acknowledge): Uncited regulatory statement: "Regulators are watching AI in service channels."
- **warning** web/financial-services.yaml (sections[1].copy): Uncited regulatory statement: "Regulators expect any AI channel to give customers a path to a person, and fraudsters are using deepfakes to get past ID checks."

## FR-QA-03: Sources: registered, dated, recent and of the right tier

- **warning** research/industry-financial-services.yaml: T-financial-services-2 cites S9, published 2023-06-06 (older than 24 months)
- **warning** research/industry-financial-services.yaml: T-financial-services-4 needs at least 2 independent sources
- **warning** research/industry-financial-services.yaml: T-financial-services-5 cites S14, published 2023-06-09 (older than 24 months)
- **warning** research/industry-financial-services.yaml: T-financial-services-5 cites S15, published 2024-05-07 (older than 24 months)
- **warning** research/industry-financial-services.yaml: T-financial-services-5 has no source from the last 24 months
- **warning** research/industry-healthcare-life-sciences.yaml: T-healthcare-life-sciences-4 has no source from the last 24 months
- **warning** research/industry-healthcare-life-sciences.yaml: T-healthcare-life-sciences-4 needs at least 2 independent sources
- **warning** research/industry-healthcare-life-sciences.yaml: T-healthcare-life-sciences-4 needs at least one Tier 1 or 2 source
- **warning** research/industry-healthcare-life-sciences.yaml: T-healthcare-life-sciences-6 has no source from the last 24 months

## FR-QA-05: Layout: no empty sections, placeholders or broken tables; within length

- **warning** outputs/02-battlecard-build-in-house.md: Section "Recent moves (last 12 months)" has nothing in it ("None found.")
- **warning** outputs/02-battlecard-competitor-a.md: Section "Recent moves (last 12 months)" has nothing in it ("None found.")
- **warning** outputs/02-battlecard-competitor-b.md: Section "Recent moves (last 12 months)" has nothing in it ("None found.")
- **warning** outputs/02-battlecard-competitor-c.md: Section "Recent moves (last 12 months)" has nothing in it ("None found.")
- **warning** outputs/02-battlecard-competitor-d.md: Section "Recent moves (last 12 months)" has nothing in it ("None found.")
- **warning** outputs/02-battlecard-competitor-e.md: Section "Recent moves (last 12 months)" has nothing in it ("None found.")
- **warning** outputs/02-battlecard-incumbent-platform.md: Section "Recent moves (last 12 months)" has nothing in it ("None found.")
- **warning** outputs/02-battlecard-status-quo.md: Section "Recent moves (last 12 months)" has nothing in it ("None found.")
- **warning** outputs/03-strategy-check.md: 2753 words; the limit for this asset is 2500

## FR-QA-07: Completeness: every industry and competitor has every asset

- **warning** competitors/build-in-house.yaml: 1 objections (expected the top 5)
- **warning** competitors/competitor-a.yaml: 3 objections (expected the top 5)
- **warning** competitors/competitor-b.yaml: 3 objections (expected the top 5)
- **warning** competitors/competitor-c.yaml: 3 objections (expected the top 5)
- **warning** competitors/competitor-d.yaml: 2 objections (expected the top 5)
- **warning** competitors/competitor-e.yaml: 2 objections (expected the top 5)
- **warning** competitors/incumbent-platform.yaml: 2 objections (expected the top 5)
- **warning** competitors/status-quo.yaml: 1 objections (expected the top 5)
