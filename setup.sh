#!/usr/bin/env bash
# Industry Launch Accelerator: one-time setup for macOS and Linux.
# What it does: finds Python 3.10 or newer, creates a private Python
# environment in .venv/, installs the libraries, and checks which data
# sources are available.
#
# Usage:  ./setup.sh          (normal setup)
#         ./setup.sh --dev    (also installs test tools, for contributors)

set -euo pipefail

cd "$(dirname "$0")"

say()  { printf '%s\n' "$*"; }
fail() { printf '\n[X] %s\n' "$*" >&2; exit 1; }

say "Industry Launch Accelerator setup"
say "---------------------------------"

# 1. Find a Python that is 3.10 or newer.
PYTHON=""
for candidate in python3.14 python3.13 python3.12 python3.11 python3.10 python3 python; do
  if command -v "$candidate" >/dev/null 2>&1; then
    if "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' 2>/dev/null; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  fail "Python 3.10 or newer was not found.
    Install it from https://www.python.org/downloads/ (click the yellow Download button,
    open the file and follow the installer). On a Mac, also double-click
    'Install Certificates.command' in the window that opens at the end.
    Then run ./setup.sh again."
fi
say "[1/4] Found $("$PYTHON" --version) ($(command -v "$PYTHON"))"

# 2. Create the private environment (.venv) if it does not exist yet.
if [ ! -x ".venv/bin/python" ]; then
  say "[2/4] Creating a private Python environment in .venv/ ..."
  "$PYTHON" -m venv .venv || fail "Could not create .venv. On Linux you may need: sudo apt install python3-venv"
else
  say "[2/4] Private Python environment already exists (.venv/)"
fi
VENV_PY=".venv/bin/python"

# 3. Install libraries.
say "[3/4] Installing libraries (this can take a minute the first time) ..."
"$VENV_PY" -m pip install --quiet --upgrade pip
if [ "${1:-}" = "--dev" ]; then
  "$VENV_PY" -m pip install --quiet -r requirements-dev.txt
else
  "$VENV_PY" -m pip install --quiet -r requirements.txt
fi

# 4. Check which data sources are available.
if [ -f "scripts/connectors/check.py" ]; then
  say "[4/4] Checking data sources ..."
  "$VENV_PY" scripts/connectors/check.py || say "    (Some data sources could not be reached. That is OK; research continues without them.)"
else
  say "[4/4] Data source check not available yet (skipped)"
fi

say ""
say "[OK] Setup complete."
say "Next: open this folder in your coding agent (Claude Code, Codex, Cursor or similar)"
say "and say: start a new launch called <name>"
