# Design decisions

> **✍️ Author's note: placeholder.** This paragraph is reserved for Nolina Mishra to write in her own voice: why this toolkit exists, and what a PMM should expect from it. *(Replace this block.)*

The choices below shape how the toolkit behaves. Each one trades some speed or polish for something PMMs need more: drafts they can trust and check quickly, with their own judgment in charge.

## Cite or label every claim

A generic AI draft is fast to produce and slow to trust. You have to re-check every sentence, because nothing tells you which parts are grounded. So every factual claim here carries a source ID (`[S12]`) from a register that records the URL, the publisher, the date and the exact supporting text. Anything that isn't a sourced fact is labeled `[ASSUMPTION]`, `[VERIFY]` or `[PROOF NEEDED]`.

The labels turn checking from "re-research everything" into "work through the flagged items". QA counts them, and `LAUNCH-KIT.md` lists the top 10 to verify before field use. The rule behind it, in every stage's instructions: **an empty field marked `[VERIFY]` beats a plausible invention.** Customer names, quotes and metrics are never invented.

## Checkpoints, and a strategy check that can disagree

The PMM's judgment is the valuable part of a launch, so the agent stops after every stage: approve, edit, redo with direction, or cut. Downstream stages can't start until upstream ones are approved. This is enforced by the scripts, not left to the agent's good behavior.

The strategy check goes one step further. After research and competitive analysis, the agent gives its own evidence-based view on the PMM's launch POV, point by point: agree, disagree, partly agree, or add. It states disagreement plainly, with sources and a confidence level. The PMM responds to every point, and everything after follows the resolved direction. A disagreement never blocks the run; the PMM has the final say. The point is to make the reasoning visible, both to the PMM and to anyone reviewing the launch later.

## Data first, documents second

Each stage writes structured YAML that's checked against a schema. Word, Excel and Markdown are generated from it. This makes several things possible that a pile of documents can't do:
- **Partial updates.** Change one persona and only that persona's messaging rows and playbook sections need redoing. The toolkit can name them.
- **Real checks.** Citations, brand terms, sameness across industries and completeness are checked mechanically.
- **Consistent formats.** One layout produces both the Markdown and the Word file, so they never drift apart.

Because the data is the source of truth, edits to the Markdown files are detected and copied back into it. Edits in Word aren't, which is why the README suggests polishing in Word at the very end.

## Pricing models, not prices

Battlecards describe how each competitor charges: seat, consumption, outcome-based, platform fee plus usage, tiered bundles, or hybrids. They also cover the value metric, tiers, add-ons, free trials and contract signals. They show list prices only when the competitor publishes them openly, always labeled "list; enterprise deals typically differ".

The toolkit never recommends a price. Pricing decisions depend on costs, strategy and deal data that public research can't see. A confident-looking number from an AI draft is exactly the kind of plausible invention the toolkit is built to avoid.

## Plain instructions for any agent

The toolkit is a set of plain Markdown instructions (`AGENTS.md`, then one file per stage) plus ordinary Python scripts. There are no plugins, slash commands or tool-specific adapters. Any coding agent that can read files and run shell commands can follow them: Claude Code, Codex, Cursor, or the next one. PMMs keep using the tool they already have, and the toolkit doesn't break when one vendor changes its extension format.

The split is deliberate: **the agent thinks, the scripts format.** The agent researches, reasons and writes. Deterministic scripts handle files, validation, data calls, rendering, state and QA, so the same data always produces the same documents.

## Only sources a PMM can use at work

Many "free" data APIs are free for personal or non-commercial use only. A product marketer using this toolkit for their company's launch is doing business work. So the toolkit includes only public sources whose free access allows that, and it never bypasses paywalls or logs in automatically. The full list, with the evidence for each source included or left out, is in [data-sources.md](data-sources.md).

## No slides in v1

Slides are where launch content gets finalized, styled and argued over. They depend heavily on each company's templates and storytelling conventions. Generating them would add a lot of formatting work and push the toolkit toward "finished assets", which it deliberately isn't.

The kit gives you what slides are built from: positioning, pillars, the persona grid, proof, demo moments and talk tracks. All of it comes as Word, Excel and Markdown, which travel cleanly into Google Docs and Sheets.
