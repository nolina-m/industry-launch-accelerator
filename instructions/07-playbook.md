# Stage 6a: Industry playbook (asset 6)

**One unit per industry:** `playbook:<industry>`. **Writes:** `playbooks/<industry>.yaml` (schema `playbook.schema.json`). **Needs:** `messaging`, `personas:<industry>` and `competitive` approved. Can run at the same time as 6b and 6c.

> **Accuracy over completeness.** An empty field marked `[VERIFY]` beats a plausible invention. This is for the field; anything uncertain must be visibly labeled.

## Read first

The industry's research, its personas and committee map, `messaging.yaml` (this industry's grid rows), the battlecards and competitive overview, and the `resolved_direction`.

## What to produce (FR-PBK-01)

- `targeting`:
  - `segments`: which companies to go after first, using the industry focus (sub-segments, region, size);
  - `committee_summary`: one paragraph on the buying committee, drawn from the map.
- `why_now`: one entry per imperative (`imperative_id` and the talk-track `text`), citing the trend evidence.
- `value_story`: one entry per persona (`persona_id`, the `message` from the grid, the `pillar_id`).
- `discovery`: per persona, the questions to ask, each with **what good sounds like**: the answer that signals a real opportunity. Start from the persona's discovery questions.
- `qualification`: `signals` that a deal is real, and `disqualifiers` that say walk away.
- `objections`: the top objections for this industry, from the battlecards and generic objections (`objection_id`, a one-line `summary`, and the short `response`).
- `competitive_quick_ref`: per competitor active in this industry, how to win (`win_with`) and what to `watch_out` for.
- `next_steps`: recommended offers (`workshop`, `demo`, `pilot`, `other`), with a description and when to use each.
- `proof_library`: every proof point available for this industry. Mark `status: available` only for proof the PMM supplied with permission; everything else is `[PROOF NEEDED]`.

Keep it field-ready: short sentences, scannable, and no claims that go beyond the messaging framework.

## Checkpoint

Submit, render, and summarize:
- the first segment to target;
- the top 3 discovery questions;
- the top objection and its response;
- the gaps in the proof library.

The asset is `outputs/06-playbook-<industry>.*`.
