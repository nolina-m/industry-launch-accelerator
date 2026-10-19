# Compatibility

What the toolkit has been run on, and what's still untested (FR-CMPT-01..03). Last updated 2026-10-19.

## Coding agents

The toolkit needs only an agent that can read files, run shell commands, and search and fetch web pages (FR-CMPT-01). Instructions refer to these generically ("use your web search tool"). `AGENTS.md` is the entry point. `CLAUDE.md` contains only `@AGENTS.md`, because Claude Code reads `CLAUDE.md` instead of `AGENTS.md` when both exist.

| Agent | Status | Notes |
|---|---|---|
| Claude Code | ✅ Run end to end (private test runs during the build, 2026-10-18) | Web tools: `WebSearch`, `WebFetch`. Reads `AGENTS.md` through the `CLAUDE.md` import. |
| Codex | ⬜ Not yet tested | Web search is controlled by `web_search` in `~/.codex/config.toml`. The default `"cached"` uses an index rather than live pages; set `web_search = "live"` for current research. |
| Cursor | ⬜ Not yet tested | Use **Agent** mode. The agent searches the web when it needs to; `@Web` forces a search. Check that the web search tool is enabled in settings. |

Agent features checked against official documentation on 2026-10-18. They change often; if your agent behaves differently, please [open an issue](https://github.com/nolina-m/industry-launch-accelerator/issues/new/choose).

## Operating systems

| System | Status | Notes |
|---|---|---|
| macOS | ✅ Tested | `setup.sh` from a clean environment; Python 3.13. |
| Linux | 🟡 Automated tests only | Runs in GitHub Actions (Ubuntu) on Python 3.10 and 3.13. |
| Windows | ⬜ Not yet tested | `setup.ps1` is written but hasn't been run on Windows. Reports welcome. |

Python 3.10 or newer is the only runtime required (FR-CMPT-02).

## Output files

| Opened in | Status |
|---|---|
| Microsoft Word, Excel (Mac) | ✅ Checked 2026-10-18 |
| Google Docs, Google Sheets | ✅ Checked 2026-10-18 |
| macOS Quick Look | ✅ |

The files use only features that survive import into Google Docs and Sheets: built-in styles, simple tables, inline PNG images, plain headers and footers. There are no macros, embedded fonts or SmartArt.

## Help us test

If you run the toolkit in another agent or on Windows, please share how it went using the [feedback issue form](https://github.com/nolina-m/industry-launch-accelerator/issues/new/choose). Include the agent and its version.
