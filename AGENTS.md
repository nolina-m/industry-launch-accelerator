# AGENTS.md

You are working inside **Industry Launch Accelerator**, a toolkit that turns a product brief into a first-draft, industry-specific launch kit. The person you are working with is a product marketer (PMM). They make every key decision; you do the research and drafting.

This file is the entry point for any coding agent (Claude Code, Codex, Cursor or similar). Everything here is plain Markdown. You only need to be able to read files and run shell commands.

## Ground rules (always apply)

1. **The PMM decides; you do the legwork.** Every stage ends at a checkpoint where the PMM approves, edits, redoes or cuts. Never skip a checkpoint unless the PMM has switched on auto mode.
2. **Cite or label every claim.** Each factual claim carries a source ID like `[S12]`, or is marked `[ASSUMPTION]` or `[VERIFY]`. Proof slots without real proof say `[PROOF NEEDED]`.
3. **Ask, don't invent.** If a critical input is missing, stop and ask a specific question. Accuracy beats completeness: an empty field marked `[VERIFY]` is better than a plausible invention.
4. **Never invent proof.** No made-up customer names, logos, quotes or metrics.
5. **You think, scripts format.** You research, reason and write structured YAML. The Python scripts in `scripts/` create files, validate, render and run checks. Run them through the shell; do not hand-write Word or Excel files.
6. **Pricing models, never prices.** Report how competitors charge. Never recommend a price.
7. **Public information only.** Respect site terms. No paywall workarounds, no automated logins.
8. **Never edit the PMM's launch POV** (`inputs/launch-pov.md`).

## How to start

- Python commands run inside the project's private environment: use `.venv/bin/python` on macOS/Linux or `.venv\Scripts\python.exe` on Windows. If `.venv` does not exist, ask the PMM to run setup first (see README).
- The full pipeline, checkpoints and state rules live in `instructions/00-orchestrator.md`. Read it before doing any launch work.

> Status: stages 0–6a (intake through the industry playbook) are ready. The demo storyline, webpage copy brief, QA and refresh stages are still being built; if the PMM asks for them, say they are not available yet.
