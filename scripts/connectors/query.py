"""Ask a data source for records during research (FR-API-03, FR-API-04).

Usage:
    python scripts/connectors/query.py <slug> <connector> search "<query>" [--opt name=value ...] [--register]
    python scripts/connectors/query.py <slug> <connector> fetch "<id>"     [--opt name=value ...] [--register]

Examples:
    ... query.py my-launch bls fetch CES6562000001 --opt limit=3 --register
    ... query.py my-launch federal-register search "prior authorization" --opt since=2026-01-01

Prints each record with its source, series ID and retrieval date. Responses are
cached in launches/<slug>/research/cache/. With --register, each record is added
to research/sources.json and its source ID (S12) is printed, ready to cite.

If the source isn't available (no key, offline, rate-limited), this says so and
exits normally: continue with web search and note the gap.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from connectors import registry  # noqa: E402
from scripts.connectors.env import load_env  # noqa: E402
from scripts.sources import add as add_source  # noqa: E402
from scripts.util import LAUNCHES_DIR  # noqa: E402


def _value(text: str):
    for cast in (int, float):
        try:
            return cast(text)
        except ValueError:
            pass
    return {"true": True, "false": False}.get(text.lower(), text)


def register(launch_dir: Path, connector_id: str, record) -> str:
    entry = registry.entries()[connector_id]
    if record.value is not None:
        excerpt = f"{record.series_id or record.title}: {record.value}{' ' + record.unit if record.unit else ''}" \
                  f"{' (' + record.period + ')' if record.period else ''}"
    else:
        excerpt = (record.summary or record.title)[:300]
    sid, _ = add_source(launch_dir, url=record.url, title=record.title[:200] or entry["name"],
                        publisher=entry["name"], tier=entry.get("tier", 2), excerpt=excerpt,
                        published=(record.published_at or None) if _is_date(record.published_at) else None,
                        connector=connector_id)
    return sid


def _is_date(value) -> bool:
    import re

    return bool(value) and bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(value)))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="query.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("slug")
    p.add_argument("connector", choices=sorted(registry.entries()))
    p.add_argument("method", choices=["search", "fetch"])
    p.add_argument("target")
    p.add_argument("--opt", action="append", default=[], help="extra option, e.g. --opt since=2026-01-01")
    p.add_argument("--register", action="store_true")
    p.add_argument("--fresh", action="store_true", help="ignore the cache and ask the source again")
    args = p.parse_args(argv)

    launch_dir = LAUNCHES_DIR / args.slug
    if not (launch_dir / "launch.yaml").exists():
        print(f"[X] No launch called '{args.slug}'.")
        return 1
    options = {}
    for opt in args.opt:
        name, _, value = opt.partition("=")
        options[name] = _value(value)

    c = registry.get(args.connector, cache_dir=launch_dir / "research" / "cache", env=load_env(),
                     use_cache=not args.fresh)
    records = getattr(c, args.method)(args.target, **options)
    if c.last_error:
        print(f"[!] {c.name} is not available: {c.last_error}")
        print("    Continue with web search and note the gap.")
        return 0
    if not records:
        print(f"No results from {c.name}.")
        return 0
    print(f"{len(records)} result(s) from {c.name}{' (cached)' if c.last_from_cache else ''}:")
    for r in records:
        sid = register(launch_dir, args.connector, r) if args.register else None
        line = f"- {r.title}"
        if r.value is not None:
            line += f" = {r.value}{' ' + r.unit if r.unit else ''}"
        if r.period:
            line += f" ({r.period})"
        print(line)
        print(f"    source: {c.name} | series: {r.series_id or 'n/a'} | retrieved: {r.retrieved_at[:10]}"
              f"{' | published: ' + r.published_at if r.published_at else ''}")
        print(f"    {r.url}{'  -> cite as [' + sid + ']' if sid else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
