"""Which data sources can the toolkit use right now? (FR-API-01)

Usage:
    python scripts/connectors/check.py            # check keys and try each source once
    python scripts/connectors/check.py --offline  # check keys only, no network

For each source it reports: ready, needs a key (with where to get one), or
unreachable right now. Nothing here is required: research continues with web
search for any source that isn't available.
"""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from connectors import registry  # noqa: E402
from scripts.connectors.env import load_env  # noqa: E402

# One small, cheap request per source, used only to see if it answers.
PROBES: dict[str, tuple[str, list, dict]] = {
    "sec-edgar": ("fetch", ["320193"], {"limit": 1}),
    "wikipedia": ("search", ["economy"], {"limit": 1}),
    "github": ("search", ["data"], {"limit": 1}),
    "arbeitnow": ("search", [""], {"limit": 1}),
    "gdelt": ("search", ["economy"], {"limit": 1}),
    "hackernews": ("search", ["data"], {"limit": 1}),
    "currents": ("search", ["economy"], {"limit": 1}),
    "federal-register": ("search", ["data"], {"limit": 1}),
    "eurlex": ("search", ["data"], {"since": "2025-01-01", "limit": 1}),
    "regulations-gov": ("search", ["data"], {"limit": 1}),
    "congress-gov": ("search", [""], {"limit": 1}),
    "bls": ("fetch", ["CES0000000001"], {"limit": 1}),
    "census": ("fetch", ["2022/cbp"], {"get": "ESTAB", "NAICS2017": "00"}),
    "datausa": ("fetch", ["acs_yg_total_population_1"], {"measures": "Population"}),
    "worldbank": ("fetch", ["NY.GDP.MKTP.CD"], {"limit": 1}),
    "oecd": ("fetch", ["OECD.SDD.NAD,DSD_NAMAIN1@DF_QNA,"],
             {"key": "Q..USA.S1..B1GQ._Z...USD_PPP.LR.LA.T0102", "start": "2025-Q1", "limit": 1}),
    "fred": ("fetch", ["GDP"], {"limit": 1}),
    "usaspending": ("search", ["software"], {"limit": 1}),
    "sam-gov": ("search", ["software"], {"days": 30, "limit": 1}),
    "nppes": ("search", ["hospital"], {"limit": 1}),
    "openfda": ("search", ["reason_for_recall:software"], {"limit": 1}),
    "cms": ("search", ["hospital"], {"limit": 1}),
    "clinicaltrials": ("search", ["health"], {"limit": 1}),
    "healthdata": ("search", ["hospital"], {"limit": 1}),
    "fdic": ("search", [""], {"limit": 1}),
    "cfpb": ("search", ["account"], {"limit": 1}),
    "fcc": ("search", ["broadband"], {"limit": 1}),
    "us-dot": ("search", ["airline"], {"limit": 1}),
}


def check(offline: bool = False, env: dict | None = None, transport=None) -> list[dict]:
    env = env if env is not None else load_env()
    results = []
    for cid, entry in registry.entries().items():
        kwargs = {"env": env}
        if transport:
            kwargs["transport"] = transport
        c = registry.get(cid, **kwargs)
        ok, reason = c.available()
        row = {"id": cid, "name": entry["name"], "access": entry["access"], "status": "ready", "note": reason}
        if not ok:
            row["status"] = "needs setup"
            if entry.get("signup_url"):
                row["note"] = f"{reason} (free sign-up: {entry['signup_url']})"
        elif not offline:
            method, args, kw = PROBES[cid]
            getattr(c, method)(*args, **kw)
            if c.last_error:
                row["status"] = "unreachable"
                row["note"] = c.last_error
        results.append(row)
    return results


def main(argv: list[str]) -> int:
    offline = "--offline" in argv
    print("Checking data sources" + (" (keys only, no network)" if offline else "") + " ...")
    results = check(offline)
    width = max(len(r["name"]) for r in results)
    marks = {"ready": "[OK]", "needs setup": "[ -]", "unreachable": "[!!]"}
    for r in results:
        print(f"  {marks[r['status']]} {r['name'].ljust(width)}  {r['note']}")
    ready = sum(r["status"] == "ready" for r in results)
    print(f"\n{ready} of {len(results)} sources ready. Sources marked [ -] switch on when you add a free key to .env;")
    print("sources marked [!!] didn't answer just now. Research continues with web search either way.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
