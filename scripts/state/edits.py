"""Notice when the PMM edits a rendered Markdown file, so the edit can be copied back (FR-STA-05).

The YAML files are the source of truth. Every render keeps a private copy of each
Markdown file in outputs/.rendered/. If a Markdown file no longer matches its copy,
the PMM edited it:
- the next render leaves that file alone (and its Word version) instead of
  overwriting the edit;
- `launch.py status` and `launch.py start` point it out;
- `launch.py edits <slug>` shows exactly what changed, so the agent can copy the
  change into the YAML, re-validate and re-render with --force.

Edits made in Word or Excel files are not copied back (documented in the README).
"""

from __future__ import annotations

import difflib
import re
from pathlib import Path

RENDERED = ".rendered"

# Rendered file name -> the YAML it comes from.
SOURCES = [
    (r"01-industry-brief-(?P<x>.+)", "research/industry-{x}.yaml"),
    (r"02-competitive-overview", "competitive-overview.yaml"),
    (r"02-battlecard-(?P<x>.+)", "competitors/{x}.yaml"),
    (r"03-strategy-check", "strategy-check.yaml"),
    (r"04-personas-(?P<x>.+)", "personas/{x}.yaml"),
    (r"05-messaging-framework", "messaging.yaml"),
    (r"06-playbook-(?P<x>.+)", "playbooks/{x}.yaml"),
    (r"07-demo-storyline-(?P<x>.+)", "demos/{x}.yaml"),
    (r"08-web-copy-(?P<x>.+)", "web/{x}.yaml"),
]


def copy_path(out_dir: Path, md_name: str) -> Path:
    return out_dir / RENDERED / md_name


def remember(out_dir: Path, md_name: str, text: str) -> None:
    path = copy_path(out_dir, md_name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def is_edited(out_dir: Path, md_name: str) -> bool:
    md, copy = out_dir / md_name, copy_path(out_dir, md_name)
    return md.exists() and copy.exists() and md.read_text(encoding="utf-8") != copy.read_text(encoding="utf-8")


def edited_outputs(launch_dir: Path) -> list[str]:
    out = launch_dir / "outputs"
    if not out.is_dir():
        return []
    return [p.name for p in sorted(out.glob("*.md")) if is_edited(out, p.name)]


def source_yaml(md_name: str) -> str | None:
    stem = Path(md_name).stem
    for pattern, template in SOURCES:
        m = re.fullmatch(pattern, stem)
        if m:
            return template.format(**m.groupdict())
    return None


def show_diff(launch_dir: Path, md_name: str) -> str:
    out = launch_dir / "outputs"
    before = copy_path(out, md_name).read_text(encoding="utf-8").splitlines()
    after = (out / md_name).read_text(encoding="utf-8").splitlines()
    return "\n".join(difflib.unified_diff(before, after, f"as rendered/{md_name}", f"as edited/{md_name}",
                                          lineterm="", n=2))


def discard(launch_dir: Path, md_name: str) -> None:
    """Undo a hand edit: put back the last rendered version."""
    out = launch_dir / "outputs"
    (out / md_name).write_text(copy_path(out, md_name).read_text(encoding="utf-8"), encoding="utf-8")
