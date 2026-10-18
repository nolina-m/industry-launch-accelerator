# Stage 5: Messaging framework (asset 5)

**Unit:** `messaging`. **Writes:** `messaging.yaml` (schema `messaging.schema.json`). **Needs:** `strategy`, `competitive` and every `personas:<industry>` approved.

> **Accuracy over completeness.** An empty field marked `[VERIFY]` beats a plausible invention. Proof slots stay `[PROOF NEEDED]` unless the PMM supplied real proof.

## Read first

- `strategy-check.yaml`: the `resolved_direction` is your brief (FR-MSG-05).
- `launch-context.yaml`: capabilities, outcomes, proof (with permission status), constraints and claims to avoid.
- Personas for every industry, the industry research (skip Low-relevance trends unless the PMM asked for them), and the battlecards for differentiation.
- `brand.yaml`: voice traits, do's and don'ts, banned and preferred terms, product-name capitalization.
- Existing messaging in `optional_inputs` (type `existing_messaging`), if any: **refine it, don't replace it** (FR-INP-12).

## What to produce

### Positioning (FR-MSG-01)

- `positioning`: **for** (target customer) / **who** (their need) / **product** (name) / **category** (is a...) / **that** (key benefit) / **unlike** (main alternative) / **we** (key differentiator).
- `elevator_pitch`: one line.
- `boilerplate`: about 50 words.

### Value pillars (FR-MSG-02): 3 to 4

Each pillar: `headline`, the customer `outcome`, the supporting `capabilities` (from the brief), `proof` (from the PMM's inputs with permission, otherwise `[PROOF NEEDED]`), and the `differentiator` versus competitors (cited to battlecards or sources).

### The grid (FR-MSG-03): every industry × persona

One row per persona in every industry:
- `industry`, `persona_id`;
- `headline`: the value message for that persona in that industry;
- `pain_ref`: the pain it addresses, as `<persona id>#<n>`;
- `pillar_id`: the pillar it emphasizes;
- `value_hypothesis`: a quantified hypothesis (for example "cuts month-end close by 2 days"). The `label` is always `[ASSUMPTION]` unless backed by the PMM's customer data, then `[FROM CUSTOMER DATA]`;
- `proof`: a proof point, or `[PROOF NEEDED]`.

## Rules

- **Value first (FR-MSG-04, FR-OUT-03):** customer outcome → capability → proof. A headline that opens with a feature ("Our AI engine...") is wrong; QA flags it.
- Apply the brand's voice and terms everywhere. Never use a banned term. Use preferred terms. Capitalize product names exactly as `brand.yaml` lists them.
- Respect the brief's "Claims we can't make" and the POV's "Claims this launch must not make".
- Every message must be specific to its industry and persona. The same headline with the industry name swapped is a failure.

## Checkpoint

Submit, render, and summarize: the positioning statement, the pillar headlines, two or three standout grid messages, and which proof slots are still `[PROOF NEEDED]`. The asset is `outputs/05-messaging-framework.*`.
