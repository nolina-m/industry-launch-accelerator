# Stage 0: Intake and gap check

**Goal:** understand everything the PMM has provided, find what is missing or contradictory, and ask a short round of specific questions. Nothing is researched or drafted at this stage.

**Writes:** `launch-context.yaml`, `brand.yaml`, `gap-report.md` (all in `launches/<slug>/`).

> **Accuracy over completeness.** An empty field marked `[VERIFY]` beats a plausible invention. Never fill a brief field with something the PMM did not say or a file does not contain.

In the commands below, `PY` means the project's Python: `.venv/bin/python` on macOS/Linux, `.venv\Scripts\python.exe` on Windows.

## Steps

### 1. Start the stage

```
PY scripts/launch.py start <slug> intake
```

### 2. Read the inputs

```
PY scripts/intake/run_intake.py <slug>
```

This extracts the text of every file in `inputs/` into `intake/extracted/` and drafts `launch-context.yaml` from the product brief template. For each field it records the value, the source file and a status (`provided`, `thin` or `missing`).

Then read every file in `intake/extracted/` yourself, plus `inputs/launch-pov.md`.

### 3. Complete `launch-context.yaml`

Edit `launch-context.yaml` directly:

- **Fill missing or thin fields from other files.** If a PRD, one-pager or other file in `inputs/brief/` answers a field the template left empty, copy the answer in. Set `source_file` to that file (for example `inputs/brief/prd.docx`) and `status: provided`. Use the file's own words where you can.
- **The template wins (FR-INP-03).** If the template and another file disagree, keep the template value and add an entry under `conflicts:` with both values and their files. Set `resolution: "template wins"`. If two files other than the template disagree (for example the target buyer is "CIO" in one and "VP Operations" in another), add a conflict with no `resolution`. The gap report turns it into a question.
- **Classify optional inputs.** Check each entry in `optional_inputs`. Set its `type` (`existing_messaging`, `win_loss`, `call_transcript`, `case_study`, `customer_metrics`, `pricing_packaging`, `analyst_report`, `competitors`, `other`). Set `permission` (`approved`, `internal_only`, `unknown`) from what the file or the PMM says. Never assume `approved`.
- **AI product?** Set `is_ai_product: true` if the product uses AI or agents. This adds the AI-specific questions and objections later.
- **Industries.** Read the "Target industries" section of the launch POV. For each industry, add it to `launch-context.yaml` under `industries` and register it:

  ```
  PY scripts/launch.py add-industry <slug> <id> --name "<Display name>" [--sub-segments "a,b"] [--regions "a,b"] [--company-size "..."]
  ```

  Use a default pack id when the industry matches one: `financial-services` (includes insurance), `healthcare-life-sciences`, `retail-consumer-goods`, `technology`, `telecom-media`, `travel-hospitality`. Otherwise make a short lowercase id (for example `public-sector`). A pack will be built for it (see `instructions/12-custom-industry.md`).
- **Competitors.** Register every competitor the PMM names in the POV or the brief:

  ```
  PY scripts/launch.py add-competitor <slug> <id> --name "<Name>"
  ```

  Don't add suggestions of your own yet; that happens in Stage 2.
- **Never edit `inputs/launch-pov.md`** or any other file the PMM wrote.

### 4. Brand

```
PY scripts/brand/extract_brand.py <slug>
```

This builds `brand.yaml` from the brand questionnaire, any Word template and logo files in `inputs/brand/`, and the neutral theme. It also lists colors and fonts it spotted in brand documents (`intake/brand-candidates.yaml`), plus any brand page URL the PMM gave.

If there is a brand book, style guide or brand page:

1. Read it (for a URL, use your web fetch tool).
2. Note colors (hex), heading and body fonts, tone of voice, do's and don'ts, banned and preferred terms, and product-name capitalization.
3. Write what you found to `intake/brand-notes.yaml`, using the same fields as `brand.yaml` (only the ones you found).
4. Run `extract_brand.py` again.

The PMM's questionnaire answers always win over your notes. Logos must be PNG; if only SVG is available, ask the PMM for a PNG.

To check a Word template on its own: `PY scripts/brand/inspect_template.py inputs/brand/<file>`.

With no brand input at all, that's fine. `brand.yaml` gets `unbranded: true`, every document will be labeled "Unbranded draft", and a non-blocking gap is logged.

### 5. Gaps and questions

```
PY scripts/intake/gap_report.py <slug>
```

This writes `gap-report.md` and the `gaps:` list in `launch-context.yaml`:

- **Blocking:** a required field is missing or too thin, there is no launch POV, there are no industries, or two inputs contradict each other. Research can't start until each one is answered or waived.
- **Non-blocking:** a recommended field is missing. The run continues; related content is labeled `[ASSUMPTION]`.

**Make the questions specific (FR-INT-04).** The generated questions are a starting point. Rewrite any of them in `launch-context.yaml` (the `question` field of the gap) so it is specific to this product and answerable in a line or two. For example, "Which 3 capabilities would a CFO notice first?", not "Tell me more about the solution." You can also add gaps of your own (use ids like `G-agent-1`). Then re-run `gap_report.py`. Ask **at most 7 questions per round**, most important first. The report already orders and caps them.

### 6. Checkpoint

```
PY scripts/launch.py submit <slug> intake
```

Then stop and post a short summary to the PMM:

- what you read (files, and any that couldn't be read);
- the industries and competitors you registered;
- brand: branded or unbranded, Word template yes or no;
- the questions from `gap-report.md` (numbered, at most 7);
- the main assumptions you will make if they don't answer the optional ones.

Offer the four responses: **approve**, **edit** (in chat or in the files), **redo** with direction, or **cut** items.

**When the PMM answers:**

1. Record each answer in `inputs/intake-answers.md`. Append, never overwrite: the question, the answer and the date.
2. Copy the answer into the matching field of `launch-context.yaml` with `source_file: inputs/intake-answers.md` and `status: answered`.
3. Set that gap's `status: answered`.
4. If the PMM says to skip a blocking question, set the gap's `status: waived` and note it in `inputs/intake-answers.md`. Downstream content that depends on it must be labeled `[ASSUMPTION]`.
5. Re-run `gap_report.py` and show the PMM what is still open, if anything. The stage stays awaiting approval while you update files; there's no need to restart it.

Approve only when the PMM says so:

```
PY scripts/launch.py approve <slug> intake
```

Approval is refused while any blocking gap is still open.
