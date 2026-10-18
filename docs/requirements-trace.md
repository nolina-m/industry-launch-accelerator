# Requirements trace

Maps each requirement ID to the files that implement it and the test or check that proves it.
Status: ✅ done · 🟡 partial · ⬜ not started.

| ID | Status | Implemented in | Proved by |
|---|---|---|---|
| FR-USR-01 | 🟡 | `setup.sh`, `setup.ps1` (plain-language messages); README quickstart pending (M8) | Manual read |
| FR-CMPT-01 | 🟡 | `AGENTS.md` (plain Markdown, read files + run shell only) | Manual read; full check M8 |
| FR-CMPT-02 | 🟡 | `setup.sh` (macOS/Linux), `setup.ps1` (Windows, written, not tested by owner decision), `pyproject.toml` (`requires-python >=3.10`) | `setup.sh` run on macOS; CI on Linux (M9) |
| FR-TST-01 | 🟡 | `.github/workflows/ci.yml` (lint + tests), `tests/conftest.py` (blocks network) | `tests/test_scaffold.py::test_network_is_blocked_in_tests`; CI green pending repo (M9) |
| FR-DOC-04 | ✅ | `README.md` "Example runs" placeholder | Manual read |
| FR-DOC-05 | 🟡 | `README.md` "About the author" draft | Owner to edit wording |
| §13.1 AGENTS.md / CLAUDE.md | ✅ | `AGENTS.md`, `CLAUDE.md` (`@AGENTS.md` import) | `tests/test_scaffold.py::test_claude_md_imports_agents_md` |
| §13.2 Repo layout | 🟡 | Top-level folders created; filled in later milestones | `tests/test_scaffold.py::test_required_file_exists` |
| Read-first #3 (PRD never committed) | ✅ | `.gitignore` | `tests/test_scaffold.py::test_private_files_are_git_ignored` |
