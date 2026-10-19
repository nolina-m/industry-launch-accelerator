"""Shared pieces for the QA checks (§9.8): findings, the artifacts of a launch, and text helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from scripts.util import load_data

ERROR = "error"  # must be fixed (or explicitly accepted by the PMM) before field use
WARNING = "warning"  # worth a look; may be fine

LABEL_RE = re.compile(r"\[(S\d+|ASSUMPTION|VERIFY|PROOF NEEDED|FROM CUSTOMER DATA)\]")
SENTENCE_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(\[])")


@dataclass
class Finding:
    check: str  # e.g. "FR-QA-02"
    severity: str
    file: str
    message: str
    location: str = ""


@dataclass
class CheckResult:
    check: str
    title: str
    findings: list[Finding] = field(default_factory=list)
    summary: str = ""

    @property
    def errors(self) -> int:
        return sum(f.severity == ERROR for f in self.findings)

    @property
    def warnings(self) -> int:
        return sum(f.severity == WARNING for f in self.findings)

    @property
    def status(self) -> str:
        return "fail" if self.errors else "warn" if self.warnings else "pass"


# Artifacts the checks read, by path pattern relative to the launch folder.
ARTIFACT_GLOBS = [
    "research/industry-*.yaml",
    "competitors/*.yaml",
    "competitive-overview.yaml",
    "strategy-check.yaml",
    "personas/*.yaml",
    "messaging.yaml",
    "playbooks/*.yaml",
    "demos/*.yaml",
    "web/*.yaml",
]


def artifacts(launch_dir: Path) -> dict[str, object]:
    """{relative path: parsed YAML} for every content artifact that exists."""
    out = {}
    for pattern in ARTIFACT_GLOBS:
        for path in sorted(launch_dir.glob(pattern)):
            try:
                out[path.relative_to(launch_dir).as_posix()] = load_data(path)
            except Exception:
                continue  # unreadable files are reported by the structure check
    return out


def walk(value, path: str = ""):
    """Yield (path, parent, key, text) for every string in a YAML structure."""
    if isinstance(value, dict):
        for k, v in value.items():
            p = f"{path}.{k}" if path else str(k)
            if isinstance(v, str):
                yield p, value, k, v
            else:
                yield from walk(v, p)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            p = f"{path}[{i}]"
            if isinstance(v, str):
                yield p, value, i, v
            else:
                yield from walk(v, p)


def sentences(text: str) -> list[str]:
    return [s.strip() for s in SENTENCE_RE.split(text.strip()) if s.strip()]


def words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())
