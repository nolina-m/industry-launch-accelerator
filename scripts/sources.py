"""The source register: every source a launch cites, in research/sources.json (FR-WEB-R-02, FR-WEB-R-03).

Usage:
    python scripts/sources.py add <slug> --url URL --title T --publisher P --tier 1|2|3
                                  --excerpt "supporting text" [--published YYYY-MM-DD] [--connector ID]
        Adds a source (or returns the existing ID if the URL is already registered)
        and prints its ID, e.g. S12. Cite it in YAML text as [S12].
    python scripts/sources.py list <slug>
    python scripts/sources.py check <slug>
        Lists cited IDs that are not in the register, and sources older than 24 months.

Tiers: 1 = primary (company sites and docs, regulators, government data, filings)
       2 = reputable press and public analyst summaries
       3 = vendor blogs, review sites, forums
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.util import LAUNCHES_DIR, load_data, today
from scripts.validate import validate_data

CITE_RE = re.compile(r"\[(S\d+)\]")
REGISTER = "research/sources.json"
RECENT_MONTHS = 24


def load(launch_dir: Path) -> dict:
    path = launch_dir / REGISTER
    if not path.exists():
        return {"sources": []}
    return json.loads(path.read_text(encoding="utf-8"))


def save(launch_dir: Path, register: dict) -> None:
    problems = validate_data(register, "sources.schema.json", REGISTER)
    if problems:
        raise ValueError("; ".join(map(str, problems)))
    path = launch_dir / REGISTER
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(register, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _norm_url(url: str) -> str:
    return url.strip().rstrip("/").lower()


def add(launch_dir: Path, *, url: str, title: str, publisher: str, tier: int, excerpt: str,
        published: str | None = None, connector: str | None = None) -> tuple[str, bool]:
    """Register a source. Returns (id, created). An already-registered URL returns its id."""
    register = load(launch_dir)
    for s in register["sources"]:
        if _norm_url(s["url"]) == _norm_url(url):
            return s["id"], False
    next_n = max((int(s["id"][1:]) for s in register["sources"]), default=0) + 1
    entry = {
        "id": f"S{next_n}",
        "url": url.strip(),
        "title": title,
        "publisher": publisher,
        "published_at": published,
        "retrieved_at": today(),
        "tier": tier,
        "excerpt": excerpt,
    }
    if connector:
        entry["connector"] = connector
    register["sources"].append(entry)
    save(launch_dir, register)
    return entry["id"], True


def cited_ids(launch_dir: Path) -> dict[str, set[str]]:
    """{source_id: {files citing it}} across every YAML artifact in the launch."""
    found: dict[str, set[str]] = {}
    for path in sorted(launch_dir.rglob("*.yaml")):
        rel = path.relative_to(launch_dir).as_posix()
        if rel.startswith(("inputs/", "intake/", "outputs/")) or rel == "launch.yaml":
            continue
        text = path.read_text(encoding="utf-8")
        ids = set(CITE_RE.findall(text)) | set(re.findall(r"source_id:\s*['\"]?(S\d+)", text))
        for sid in ids:
            found.setdefault(sid, set()).add(rel)
    return found


def months_between(earlier: str, later: str) -> int:
    a, b = date.fromisoformat(earlier), date.fromisoformat(later)
    return (b.year - a.year) * 12 + (b.month - a.month)


def check(launch_dir: Path) -> tuple[dict[str, set[str]], list[dict]]:
    """(cited IDs missing from the register, sources older than 24 months)."""
    register = {s["id"]: s for s in load(launch_dir)["sources"]}
    missing = {sid: files for sid, files in cited_ids(launch_dir).items() if sid not in register}
    old = [s for s in register.values()
           if s.get("published_at") and months_between(s["published_at"], today()) > RECENT_MONTHS]
    return missing, old


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sources.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    a = sub.add_parser("add")
    a.add_argument("slug")
    a.add_argument("--url", required=True)
    a.add_argument("--title", required=True)
    a.add_argument("--publisher", required=True)
    a.add_argument("--tier", type=int, choices=[1, 2, 3], required=True)
    a.add_argument("--excerpt", required=True)
    a.add_argument("--published")
    a.add_argument("--connector")
    for name in ("list", "check"):
        sub.add_parser(name).add_argument("slug")
    args = parser.parse_args(argv)
    launch_dir = LAUNCHES_DIR / args.slug
    if not (launch_dir / "launch.yaml").exists():
        print(f"[X] No launch called '{args.slug}'.")
        return 1

    if args.command == "add":
        if args.published and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", args.published):
            print("[X] --published must look like 2026-03-31")
            return 1
        sid, created = add(launch_dir, url=args.url, title=args.title, publisher=args.publisher, tier=args.tier,
                           excerpt=args.excerpt, published=args.published, connector=args.connector)
        print(sid if created else f"{sid} (already registered)")
        return 0
    if args.command == "list":
        for s in load_data(launch_dir / REGISTER)["sources"] if (launch_dir / REGISTER).exists() else []:
            print(f"{s['id']}  tier {s['tier']}  {s['published_at'] or 'undated'}  {s['title']} ({s['publisher']})")
        return 0
    missing, old = check(launch_dir)
    for sid, files in sorted(missing.items()):
        print(f"[X] {sid} is cited in {', '.join(sorted(files))} but is not in the source register")
    for s in old:
        print(f"[!] {s['id']} was published {s['published_at']}, more than {RECENT_MONTHS} months ago")
    if not missing and not old:
        print("[OK] Every cited source is registered and recent.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
