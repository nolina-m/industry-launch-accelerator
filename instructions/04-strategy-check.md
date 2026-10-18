# Stage 3: Strategy check (asset 3)

**Unit:** `strategy`. **Writes:** `strategy-check.yaml` (schema `strategy-check.schema.json`). **Needs:** every `research:<industry>` and `competitive` approved (FR-STR-01).

This is where you give the PMM your honest, evidence-based view of their launch POV. The PMM has the final say. A disagreement never blocks the run (FR-STR-07).

> **Accuracy over completeness.** Every stance rests on evidence already in the research, the battlecards or the market data. Don't introduce unsourced claims here.

## 1. Break the POV into points

Read `inputs/launch-pov.md`. Split it into separate claims or choices: each industry choice, each priority buyer, each competitor emphasis, each element of the winning story, each claim to avoid. Quote each one exactly in `pov_quote`. Use IDs `SC-1`, `SC-2`, and so on.

## 2. Give your view on each point (FR-STR-02)

- `stance`:
  - `agree`: the evidence supports it.
  - `disagree`: the evidence points elsewhere.
  - `partly agree`: right in part, wrong or incomplete in part.
  - `add`: right, but the evidence suggests an important extension.
- `reasoning`: 2–4 sentences.
- `evidence`: the source IDs (and trend, competitor or data IDs in the reasoning text) that back your stance.
- `confidence`: `high`, `medium` or `low`, with a one-line `reason`. For example: "low: only one Tier 3 source".

**Tone (FR-STR-04).** Direct and respectful. When you disagree, say so plainly and show the evidence. Never soften a disagreement into agreement, and never agree just to be agreeable.

## 3. Additions (FR-STR-03): up to 5

Opportunities, risks or industries the POV didn't mention but the evidence supports. Each has `text`, `evidence` and `confidence`. Use IDs `SA-1`, `SA-2`, and so on. Leave the list empty if there's nothing worth adding.

## 4. Checkpoint: the PMM responds to every point (FR-STR-05)

Submit and render, then present each point and addition in turn: the POV quote, your stance and reasoning, the evidence, and your confidence. Ask the PMM to respond to each one with:

- **accept**: use your view;
- **reject**: keep their original direction (your point is never used downstream);
- **adjust**: they give the adjusted direction in their own words.

They can add a one-line reason. Record each response in the YAML:

```yaml
pmm_response:
  decision: adjust          # accept | reject | adjust
  adjusted_direction: "..." # required for adjust, in the PMM's words
  reason: "..."             # optional
  responded_at: "2026-10-18T15:04:00Z"
```

Then write `resolved_direction`: the launch POV as adjusted by the PMM's responses, as a short paragraph or bullets. This is what every later stage follows (FR-STR-06). It must:
- keep every rejected point as the PMM originally wrote it;
- include accepted views and adjusted directions;
- include only the additions the PMM accepted.

Approval is refused until every point and addition has a response and `resolved_direction` is filled in. In auto mode, responses are recorded as `not_reviewed`, and you write `resolved_direction` from the original POV plus your accepted-by-default views, labeled "Not reviewed by PMM".

The asset is `outputs/03-strategy-check.*`. It shows your view and the PMM's response side by side.
