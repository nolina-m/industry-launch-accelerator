"""Checks that the repo scaffold and its guardrails are in place (M0)."""

import socket
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent


def test_network_is_blocked_in_tests():
    with pytest.raises(RuntimeError):
        socket.create_connection(("example.org", 80), timeout=1)


@pytest.mark.parametrize(
    "path",
    [
        "README.md",
        "AGENTS.md",
        "CLAUDE.md",
        "LICENSE",
        "CONTRIBUTING.md",
        "setup.sh",
        "setup.ps1",
        "requirements.txt",
        ".gitignore",
        "docs/requirements-trace.md",
        "launches/.gitkeep",
    ],
)
def test_required_file_exists(path):
    assert (ROOT / path).is_file(), f"missing {path}"


def test_license_is_mit_with_owner():
    text = (ROOT / "LICENSE").read_text()
    assert text.startswith("MIT License")
    assert "Copyright (c) 2026 Nolina Mishra" in text


def test_claude_md_imports_agents_md():
    # Claude Code reads CLAUDE.md instead of AGENTS.md when both exist,
    # so CLAUDE.md must import AGENTS.md rather than just mention it.
    assert (ROOT / "CLAUDE.md").read_text().strip() == "@AGENTS.md"


def _is_ignored(rel_path: str) -> bool:
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", rel_path],
        cwd=ROOT,
        capture_output=True,
    )
    return result.returncode == 0


@pytest.mark.parametrize(
    "path",
    [
        "PRD_Industry_Launch_Accelerator_build.md",
        "PRD.md",
        "BUILD-NOTES.md",
        ".env",
        "launches/my-launch/launch.yaml",
        "launches/my-launch/research/cache/x.json",
        ".venv/bin/python",
    ],
)
def test_private_files_are_git_ignored(path):
    assert _is_ignored(path), f"{path} should be git-ignored"


def test_launch_placeholder_is_not_ignored():
    assert not _is_ignored("launches/.gitkeep")
