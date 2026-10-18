# Stage 6c: Webpage copy brief (asset 8)

**One unit per industry:** `web:<industry>`. **Writes:** `web/<industry>.yaml` (schema `web.schema.json`). **Needs:** `messaging` and `personas:<industry>` approved. Can run at the same time as 6a and 6b.

> **Accuracy over completeness.** An empty field marked `[VERIFY]` beats a plausible invention. This is a copy brief: structure and draft copy only, with no HTML or visual design (FR-WEB-02).

## Read first

- `messaging.yaml`: the positioning, pillars and this industry's grid rows. Every section draws on them.
- The industry's personas (their language: words to use and avoid).
- The industry research: why-now context.
- `brand.yaml`: voice, banned and preferred terms, product names.
- `options.name_competitors_in_customer_copy` in `launch.yaml`. A webpage is customer-facing, so don't name competitors unless it's `true`.

## What to produce (FR-WEB-01)

- **`page_goal`:** what the page must achieve, in one sentence.
- **`primary_cta`:** the single main call to action.
- **`target_personas`:** persona IDs, primary first.
- **`hero`:** a `headline` (outcome-led, industry-specific) and a `subhead`.
- **`sections`:** the page structure, top to bottom. Each has:
  - `id` (`WS-1`, `WS-2`, ...), `name`, and `purpose`;
  - draft `copy`;
  - `messaging_refs`: which pillar IDs, persona IDs or grid rows it draws on (FR-WEB-01 "links to the messaging").

  A typical page: problem and why now, how it works, value by role, proof, objections or FAQ, and a closing CTA.
- **`proof_section`:** draft copy using only proof the PMM supplied with permission. Otherwise write it as `[PROOF NEEDED]` with what kind of proof would fit.
- **`cta`:** the closing call to action copy.
- **`headline_variants`:** 2 to 3 alternative hero headlines to test, each from a different angle (outcome, pain, proof).
- **`keywords`:** suggested search terms for this industry. Each has `label: "[VERIFY]"`, because search volume is not checked.
- **`imagery_direction`:** what images or illustrations should show, in plain words.
- **`demo_embed_direction`:** which demo moment to embed or link, and where (refer to the demo storyline's `DM-` IDs if it exists).

## Rules

- Value first: outcome → capability → proof. No feature-list opening.
- Use the persona's language; respect banned terms, preferred terms and product-name capitalization.
- No competitor names unless the PMM opted in.
- Respect "Claims we can't make" and the POV's "Claims this launch must not make".

## Checkpoint

Submit, render, and summarize: the hero headline and its variants, the section list, the CTA, and what proof is still needed. The asset is `outputs/08-web-copy-<industry>.*`.
