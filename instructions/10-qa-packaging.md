# Stage 7: QA and packaging

**Unit:** `qa`. **Writes:** `qa-report.md`, `LAUNCH-KIT.md`, and every rendered file in `outputs/`. **Needs:** every playbook, demo storyline and webpage copy brief approved.

> **Accuracy over completeness.** QA finds problems; it never invents content to make a check pass. Fix a missing citation with a real source or a label (`[VERIFY]`, `[ASSUMPTION]`), never with a plausible-looking one.

## 1. Run the checks

```
PY scripts/launch.py start <slug> qa
PY scripts/launch.py qa <slug>
```

This renders every asset, runs all the checks, and writes `qa-report.md` and `LAUNCH-KIT.md`. Add `--check-links` to re-open every source link as well (needs internet; slower).

| Check | What it looks for |
|---|---|
| FR-QA-01 Structure | Every YAML file matches its schema |
| FR-QA-02 Citations | Numbers, dates, named-company claims and regulatory statements without `[S#]`, `[ASSUMPTION]` or `[VERIFY]`; target 95% coverage |
| FR-QA-03 Sources | Citations missing from the register; trend sources older than 24 months, or fewer than 2 independent ones; tier rules; list prices without a Tier 1 source |
| FR-QA-04 Brand | Colors outside the palette and undeclared fonts in the Word and Excel files; banned terms; avoided terms; product-name capitalization |
| FR-QA-05 Layout | Empty sections, placeholder text, broken tables, assets over the length limit (`scripts/qa/limits.yaml`; override per launch in `qa-limits.yaml`) |
| FR-QA-06 Sameness | Persona pains more than 70% alike across industries; near-identical headlines; messages that open with a feature instead of an outcome |
| FR-QA-07 Completeness | A missing asset for any industry or competitor; grid rows missing for a persona; strategy points without a PMM response; counts outside the recommended ranges |
| FR-OUT-03 Rules | Competitors named in customer-facing copy without opt-in; anything that reads like a price recommendation |

## 2. Fix what you can

Work through `qa-report.md`, errors first:
- **Uncited claims:** cite a registered source, or label the claim `[VERIFY]` (saying how to check it) or `[ASSUMPTION]`. If a claim can't be supported, rewrite or remove it.
- **Brand terms:** replace banned or avoided terms; fix product-name capitalization.
- **Sameness:** rewrite near-identical personas or headlines so they're specific to the industry. Rewrite feature-first messages to lead with the customer outcome.
- **Layout:** fill or remove empty sections; tighten assets that run over their length limit.
- **Completeness:** missing assets mean an earlier stage isn't done. Go back to it; don't fill the gap here.

Each fix edits an approved YAML file, so that unit goes back to `awaiting_approval` and everything downstream becomes stale. Group your fixes, then show the PMM what changed, unit by unit, and ask them to approve. Downstream units that only went stale because of an edit can be approved as they are once the PMM agrees (`PY scripts/launch.py approve <slug> <unit>`).

Run `PY scripts/launch.py qa <slug>` again until no errors remain, or until the PMM explicitly accepts the ones left.

Warnings are judgment calls. Fix the clear ones and list the rest for the PMM.

## 3. Checkpoint

```
PY scripts/launch.py submit <slug> qa
```

Summarize for the PMM:
- **The verdict:** errors and warnings left, and the citation coverage.
- **What you fixed.**
- **What needs their call:** remaining warnings, and errors they'd have to accept.
- **The top 10 things to verify before field use**, from `LAUNCH-KIT.md`.
- **Where everything is:** `LAUNCH-KIT.md` links every asset in Markdown and Word (plus the Excel messaging grid).

Approve only when the PMM says so. After approval, run `PY scripts/launch.py qa <slug>` once more, so `LAUNCH-KIT.md` shows the final statuses.
