# Refresh (on demand)

**When:** the PMM asks to "refresh the launch" (FR-REF-01). Refresh is never scheduled. **Writes:** `refresh/<date>/what-changed.md`, `changes.yaml` and `snapshot.json`. It never edits an approved asset (FR-REF-04).

> **Accuracy over completeness.** Report what actually changed, with its source and date. If you can't confirm something, list it as `[VERIFY]` rather than assuming.

## 1. Run the connector checks

```
PY scripts/launch.py refresh <slug>
```

This re-checks, with the data connectors:
- **Competitors:** news (GDELT, Hacker News, Currents if keyed) and new SEC filings (if `ILA_CONTACT_EMAIL` is set).
- **Regulation:** new or proposed rules for the regulations in each industry brief (Federal Register, EUR-Lex, Regulations.gov if keyed).
- **Market data:** a newer value for every data point that came from a connector (BLS, FRED, World Bank).
- **Source health:** every link in the register (moved or offline), and sources older than 24 months.

It compares the results with the previous refresh, or the first time, with the research date. Add `--no-links` to skip re-opening every source link.

## 2. Add what web search finds (FR-REF-02)

The connectors don't cover everything. Use your web search tool for each competitor (last 12 months, or since the last refresh) and look for:
- product launches;
- pricing or packaging changes (check their pricing page);
- funding and acquisitions;
- leadership changes;
- notable hiring;
- new filings.

For each target industry, look for new or proposed regulation that the connectors may have missed (other regions, state laws, regulator guidance).

Register each new source with `scripts/sources.py add`. Add each finding to `refresh/<date>/what-changed.md`, under the matching heading, in the same format:
- **Source:** publisher, date and link.
- **Affects:** the assets and sections.
- **Suggested action.**

Remove connector items that turn out to be irrelevant (for example, news about a different company with the same name). Say why in one line.

## 3. Report to the PMM

Summarize the changes that matter, grouped by asset. For each one: what changed, the source, which assets and sections it affects, and your suggested update. Ask which updates to make. Don't change anything yet.

## 4. Update, asset by asset (FR-REF-04)

For each update the PMM approves:
1. `PY scripts/launch.py start <slug> <unit>` for the affected unit (for example `competitive` for a battlecard's recent moves, `research:<industry>` for a regulation or data point).
2. Edit only the affected items in the YAML, cite the new sources, validate, `submit`, render, and checkpoint as usual.
3. After approval, `PY scripts/launch.py status <slug>` shows which downstream assets went stale, and exactly which items in them refer to what changed. Regenerate only those items, after asking (see "When something upstream changes" in `00-orchestrator.md`).

Finally, run `PY scripts/launch.py qa <slug>`. `LAUNCH-KIT.md` then links the latest what-changed report.
