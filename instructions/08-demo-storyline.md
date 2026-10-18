# Stage 6b: Demo storyline (asset 7)

**One unit per industry:** `demo:<industry>`. **Writes:** `demos/<industry>.yaml` (schema `demo.schema.json`). **Needs:** `messaging` and `personas:<industry>` approved. Can run at the same time as 6a and 6c.

> **Accuracy over completeness.** An empty field marked `[VERIFY]` beats a plausible invention. This is a spec for whoever builds the demo. Every capability shown must exist in the product brief; anything assumed is `[VERIFY]` (FR-DMO-02).

## Read first

- The industry's personas and committee map.
- `messaging.yaml`: the pillars and this industry's grid rows.
- `launch-context.yaml`: capabilities and how it works. This is the only list of what the product can actually do.
- The `resolved_direction`.
- `options.name_competitors_in_customer_copy` in `launch.yaml`. The demo is customer-facing, so don't name competitors unless it's `true`.

## What to produce (FR-DMO-01)

- **`scenario`:** a realistic day-in-the-life situation in this industry, using the industry's own vocabulary. Use a fictional company, clearly described as fictional (for example "a regional hospital system"). Never use a real customer's name.
- **`cast`:** the personas in the room (`persona_id`) and their `role_in_demo` (what they watch for).
- **`moments`: 5 to 7 tell-show-tell moments.** Each has:
  - `title`;
  - `tell`: set up the pain;
  - `show`: what happens on screen;
  - `tell_back`: land the outcome;
  - `pillar_id`, and `pain_ref` (`<persona id>#<n>`);
  - `talk_track`: what the presenter says;
  - `verify`: anything assumed about the product (`[VERIFY] confirm the product can...`).

  Use IDs `DM-1` to `DM-7`.
- **`aha`:** the one moment that makes the room lean in (`moment_id`), and why.
- **`data_needed`:** the demo data to prepare (records, users, sample documents), all fictional.
- **`environment`:** the systems, integrations and accounts the demo environment needs.
- **`versions`:**
  - `five_minute`: which moments to keep (usually the aha plus one or two);
  - `twenty_minute`: the full arc;
  - optional `notes` for each.

## Rules

- **Outcome first:** each moment opens with the pain and ends with the outcome, not with a feature tour.
- Only show capabilities that are in the brief. Everything else is `[VERIFY]`.
- **No competitor names** unless the PMM opted in. "Your current process" or "manual review" is fine.
- No made-up customer results. Any number shown on screen is demo data, not a claim.

## Checkpoint

Submit, render, and summarize: the scenario in one line, the aha moment, the 5-minute cut, and every `[VERIFY]` about product capabilities. The asset is `outputs/07-demo-storyline-<industry>.*`.
