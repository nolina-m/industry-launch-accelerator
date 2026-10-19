"""Stage 7: run every QA check, write qa-report.md, render all files and build LAUNCH-KIT.md (§9.8).

Usage:
    python scripts/launch.py qa <slug>                  # checks + render + kit
    python scripts/launch.py qa <slug> --check-links    # also re-open every source link
    python scripts/launch.py qa <slug> --no-render      # checks only

Exit code is 1 while any error-level finding remains.
"""

from __future__ import annotations

from pathlib import Path

from scripts.qa.common import ERROR, CheckResult
from scripts.qa.content_checks import (
    check_citations,
    check_completeness,
    check_rules,
    check_sameness,
    check_sources,
    check_structure,
)
from scripts.qa.kit import write_kit
from scripts.qa.output_checks import check_brand, check_layout
from scripts.util import load_yaml, today

MAX_LISTED = 40  # per check, in the report; the rest are counted


def http_link_checker(url: str) -> int | None:
    import requests

    try:
        r = requests.get(url, timeout=20, allow_redirects=True, stream=True,
                         headers={"User-Agent": "Mozilla/5.0 (compatible; IndustryLaunchAccelerator link check)"})
        r.close()
        return r.status_code
    except Exception:
        return None


def run_checks(launch_dir: Path, check_links: bool = False, link_checker=None) -> list[CheckResult]:
    checker = link_checker or (http_link_checker if check_links else None)
    return [
        check_structure(launch_dir),
        check_citations(launch_dir),
        check_sources(launch_dir, checker),
        check_brand(launch_dir),
        check_layout(launch_dir),
        check_sameness(launch_dir),
        check_completeness(launch_dir),
        check_rules(launch_dir),
    ]


def render_report(launch_dir: Path, results: list[CheckResult]) -> str:
    launch = load_yaml(launch_dir / "launch.yaml")
    errors = sum(r.errors for r in results)
    warnings = sum(r.warnings for r in results)
    verdict = "Ready for PMM review" if not errors else "Not ready: fix the errors below, or accept them explicitly"
    lines = [
        f"# QA report: {launch['name']}",
        "",
        f"_Generated {today()} by Industry Launch Accelerator. Draft: verify before external use._",
        "",
        f"**{verdict}.** {errors} error(s), {warnings} warning(s).",
        "",
        "Errors must be fixed (or accepted by the PMM) before field use. Warnings are worth a look and may be fine.",
        "",
        "| Check | Result | Errors | Warnings | Summary |",
        "|---|---|---|---|---|",
    ]
    for r in results:
        mark = {"pass": "✅ pass", "warn": "⚠️ warnings", "fail": "❌ errors"}[r.status]
        lines.append(f"| {r.check} {r.title} | {mark} | {r.errors} | {r.warnings} | {r.summary} |")
    for r in results:
        if not r.findings:
            continue
        lines += ["", f"## {r.check}: {r.title}", ""]
        ordered = sorted(r.findings, key=lambda f: (f.severity != ERROR, f.file))
        for f in ordered[:MAX_LISTED]:
            where = f"{f.file}{' (' + f.location + ')' if f.location else ''}"
            lines.append(f"- **{f.severity}** {where}: {f.message}")
        if len(ordered) > MAX_LISTED:
            lines.append(f"- ...and {len(ordered) - MAX_LISTED} more")
    lines.append("")
    return "\n".join(lines)


def run(launch_dir: Path, check_links: bool = False, render: bool = True, link_checker=None) -> list[CheckResult]:
    if render:
        from scripts.render.render import Renderer

        Renderer(launch_dir).render_all()  # brand and layout checks read the rendered files
    results = run_checks(launch_dir, check_links, link_checker)
    (launch_dir / "qa-report.md").write_text(render_report(launch_dir, results), encoding="utf-8")
    write_kit(launch_dir, results)
    return results


def summary_line(results: list[CheckResult]) -> str:
    errors = sum(r.errors for r in results)
    warnings = sum(r.warnings for r in results)
    cov = next((getattr(r, "coverage", None) for r in results if r.check == "FR-QA-02"), None)
    extra = f"; citation coverage {cov:.0%}" if cov is not None else ""
    return f"{errors} error(s), {warnings} warning(s){extra}"

