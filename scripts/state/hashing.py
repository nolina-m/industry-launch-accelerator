"""Content fingerprints (hashes) used to notice when a file has changed (FR-STA-01, FR-STA-04)."""

from __future__ import annotations

import hashlib
from pathlib import Path

EMPTY = "empty"


def _iter_files(base: Path, patterns: list[str]) -> list[Path]:
    files: set[Path] = set()
    for pattern in patterns:
        if pattern.endswith("/"):
            root = base / pattern
            if root.is_dir():
                files |= {p for p in root.rglob("*") if p.is_file()}
        else:
            files |= {p for p in base.glob(pattern) if p.is_file()}
    return sorted(f for f in files if f.name != ".DS_Store" and f.name != ".gitkeep")


def hash_files(base: Path, patterns: list[str]) -> str:
    """One fingerprint for all files matching `patterns` under `base`.

    File names are included, so adding, removing or renaming a file counts as a change.
    Returns "empty" when nothing matches.
    """
    files = _iter_files(base, patterns)
    if not files:
        return EMPTY
    h = hashlib.sha256()
    for f in files:
        h.update(f.relative_to(base).as_posix().encode())
        h.update(b"\0")
        h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()


def existing_outputs(base: Path, patterns: list[str]) -> list[Path]:
    return _iter_files(base, patterns)
