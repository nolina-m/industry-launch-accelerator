"""Manage launches: create them, see where each stage stands, and record approvals.

Run with the project's Python, for example on macOS/Linux:
    .venv/bin/python scripts/launch.py status my-launch

Commands
    new <slug> [--name "Display name"]     Create launches/<slug>/ with input templates
    status <slug>                          Show every stage, what is stale and what to do next
    start <slug> <stage>                   Begin (or redo) a stage; refused until upstream is approved
    submit <slug> <stage>                  Agent finished a stage: check files, post for review
    approve <slug> <stage>                 PMM approves a stage at its checkpoint
    add-industry <slug> <id> [--name N] [--sub-segments a,b] [--regions a,b] [--company-size S]
    remove-industry <slug> <id>
    add-competitor <slug> <id> --name N [--suggested]
    remove-competitor <slug> <id>
    set-option <slug> <option> <true|false>
    auto <slug> <on|off>                   Switch checkpoints off/on for this launch (auto mode)
    refresh <slug> [--no-links]            Pull fresh data and write refresh/<date>/what-changed.md
    render <slug> [--unit <stage>] [--force] Build Markdown and Word files in outputs/
    edits <slug> [--discard FILE]          Show hand edits to rendered Markdown, to copy into the YAML
    qa <slug> [--check-links] [--no-render] Run quality checks, render everything, build LAUNCH-KIT.md

Stage names look like: intake, research:<industry>, competitive, strategy,
personas:<industry>, messaging, playbook:<industry>, demo:<industry>, web:<industry>, qa
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.state.launch_state import (
    APPROVED,
    AWAITING,
    IN_PROGRESS,
    STALE,
    LaunchState,
    StateError,
)
from scripts.util import LAUNCHES_DIR, REPO_ROOT, TEMPLATES_DIR

STATUS_TEXT = {
    "not_started": "not started",
    "in_progress": "in progress",
    "awaiting_approval": "AWAITING YOUR APPROVAL",
    "approved": "approved",
    "stale": "STALE",
}


def launch_dir(slug: str) -> Path:
    return LAUNCHES_DIR / slug


def _csv(value: str | None) -> list[str]:
    return [v.strip() for v in value.split(",") if v.strip()] if value else []


# ---------------------------------------------------------------------- commands
def cmd_new(args) -> int:
    path = launch_dir(args.slug)
    state = LaunchState.create(path, args.slug, args.name)
    copied = []
    inputs_templates = TEMPLATES_DIR / "inputs"
    if inputs_templates.is_dir():
        for tpl in sorted(inputs_templates.glob("*.md")):
            target = path / "inputs" / tpl.name
            if not target.exists():
                shutil.copy(tpl, target)
                copied.append(tpl.name)
    shown = path.relative_to(REPO_ROOT) if path.is_relative_to(REPO_ROOT) else path
    print(f"[OK] Created launch '{state.data['name']}' in {shown}/")
    if copied:
        print("Fill in these files in inputs/: " + ", ".join(copied))
    print("Put supporting documents in inputs/brief/, brand files in inputs/brand/,")
    print("and anything else useful in inputs/optional/.")
    return 0


def cmd_status(args) -> int:
    state = LaunchState.load(launch_dir(args.slug))
    changes = state.refresh()
    state.save()
    d = state.data
    print(f"Launch: {d['name']} ({d['slug']})")
    print(f"Auto mode: {'ON (checkpoints off)' if state.auto_mode else 'off'}")
    print("Industries: " + (", ".join(f"{i['name']} [{i['id']}]" for i in d["industries"]) or "none yet"))
    comps = [f"{c['name']}{' (suggested)' if c['suggested'] else ''}" for c in d["competitors"]]
    print("Competitors: " + (", ".join(comps) or "none yet"))
    print()
    rows = state.summary_rows()
    width = max(len(r[0]) for r in rows)
    for name, _label, status, note in rows:
        line = f"  {name.ljust(width)}  {STATUS_TEXT[status]}"
        if note:
            line += f"  ({note})"
        print(line)

    if changes:
        print("\nWhat changed since last time:")
        for c in changes:
            why = f": {'; '.join(c.reasons)}" if c.reasons else ""
            print(f"  - {c.unit}: {STATUS_TEXT.get(c.old, c.old)} -> {STATUS_TEXT.get(c.new, c.new)}{why}")

    stale = [r[0] for r in rows if r[2] in (STALE, AWAITING)]
    if stale:
        print("\nWhat changed, and which parts depend on it (only these need redoing, after you agree):")
        for name in stale:
            details = state.impact(name)
            if not details and state.status(name) != STALE:
                continue
            print(f"  - {state.asset_label(name)} [{name}]")
            for d in details:
                for c in d["changes"]:
                    who = "its own files" if d["source"] == name else d["source"]
                    print(f"      {who}: {c.describe()}")
                for file, item, item_id in d["refs"]:
                    print(f"        -> {file}: {item} (uses {item_id})")
                if d["source"] != name and not d["refs"] and any(c.ids for c in d["changes"]):
                    print("        -> nothing in this asset refers to the changed items directly; review it as a whole")
            if not details:
                print("      (no approved copy to compare with: review the whole asset)")
    edited = _edited_outputs(launch_dir(args.slug))
    if edited:
        print("\nRendered files edited by hand (copy the edits into the YAML before the next stage):")
        for name in edited:
            print(f"  - outputs/{name}   (see: launch.py edits {args.slug})")

    print("\nNext: " + _next_step(state, rows))
    return 0


def _next_step(state: LaunchState, rows) -> str:
    for name, _, status, _ in rows:
        if status == AWAITING:
            return f"review {name} and approve, edit, redo or cut items."
    for name, _, status, _ in rows:
        if status == STALE:
            return f"{name} is stale. Ask the agent to redo it, or approve it as is."
    for name, _, status, _ in rows:
        if status == IN_PROGRESS:
            return f"{name} is being worked on."
    if not state.industry_ids:
        return "add inputs and industries, then run intake."
    for name in state.units:
        if state.status(name) != APPROVED:
            return f"start {name}."
    return "everything is approved."


def _edited_outputs(path: Path) -> list[str]:
    from scripts.state.edits import edited_outputs

    return edited_outputs(path)


def cmd_start(args) -> int:
    state = LaunchState.load(launch_dir(args.slug))
    state.start(args.stage)
    state.save()
    print(f"[OK] {args.stage} is now in progress.")
    edited = _edited_outputs(state.dir)
    if edited:
        print(f"[!] The PMM edited {len(edited)} rendered file(s): {', '.join(edited)}.")
        print(f"    Copy those edits into the YAML first: launch.py edits {args.slug}")
    return 0


def cmd_edits(args) -> int:
    from scripts.state import edits

    path = launch_dir(args.slug)
    LaunchState.load(path)
    if args.discard:
        edits.discard(path, args.discard)
        print(f"[OK] Put back the last rendered version of outputs/{args.discard}.")
        return 0
    edited = edits.edited_outputs(path)
    if not edited:
        print("No rendered files have been edited by hand.")
        return 0
    for name in edited:
        print(f"=== outputs/{name}  (source of truth: {edits.source_yaml(name) or 'unknown'})")
        print(edits.show_diff(path, name))
        print()
    print("Next: copy each change into the YAML file named above, run validate.py, then")
    print(f"      launch.py render {args.slug} --force   (or --discard <file> to drop an edit)")
    return 0


def cmd_submit(args) -> int:
    state = LaunchState.load(launch_dir(args.slug))
    messages = state.submit(args.stage)
    state.save()
    for m in messages:
        print(f"[OK] {m}")
    return 0


def cmd_approve(args) -> int:
    state = LaunchState.load(launch_dir(args.slug))
    state.approve(args.stage)
    state.save()
    print(f"[OK] {args.stage} approved.")
    return 0


def cmd_add_industry(args) -> int:
    state = LaunchState.load(launch_dir(args.slug))
    if args.id in state.industry_ids:
        raise StateError(f"Industry '{args.id}' is already in this launch.")
    pack_file = REPO_ROOT / "industries" / args.id / "pack.yaml"
    local_pack = state.dir / "industries" / args.id / "pack.yaml"
    entry = {
        "id": args.id,
        "name": args.name or args.id.replace("-", " ").title(),
        "pack": args.id if pack_file.exists() else None,
        "generated": local_pack.exists() and not pack_file.exists(),
    }
    if args.sub_segments:
        entry["sub_segments"] = _csv(args.sub_segments)
    if args.regions:
        entry["regions"] = _csv(args.regions)
    if args.company_size:
        entry["company_size"] = args.company_size
    state.data["industries"].append(entry)
    state.refresh()
    state.save()
    print(f"[OK] Added industry {entry['name']} [{args.id}]"
          + ("" if entry["pack"] else " (no default pack: the agent will build one)"))
    return 0


def cmd_remove_industry(args) -> int:
    state = LaunchState.load(launch_dir(args.slug))
    before = len(state.data["industries"])
    state.data["industries"] = [i for i in state.data["industries"] if i["id"] != args.id]
    if len(state.data["industries"]) == before:
        raise StateError(f"Industry '{args.id}' is not in this launch.")
    state.refresh()
    state.save()
    print(f"[OK] Removed industry {args.id}. Its files were left in place.")
    return 0


def cmd_add_competitor(args) -> int:
    state = LaunchState.load(launch_dir(args.slug))
    if any(c["id"] == args.id for c in state.data["competitors"]):
        raise StateError(f"Competitor '{args.id}' is already in this launch.")
    state.data["competitors"].append({"id": args.id, "name": args.name, "suggested": args.suggested})
    state.save()
    print(f"[OK] Added competitor {args.name}{' (suggested)' if args.suggested else ''}")
    return 0


def cmd_remove_competitor(args) -> int:
    state = LaunchState.load(launch_dir(args.slug))
    before = len(state.data["competitors"])
    state.data["competitors"] = [c for c in state.data["competitors"] if c["id"] != args.id]
    if len(state.data["competitors"]) == before:
        raise StateError(f"Competitor '{args.id}' is not in this launch.")
    state.save()
    print(f"[OK] Removed competitor {args.id}.")
    return 0


def cmd_set_option(args) -> int:
    state = LaunchState.load(launch_dir(args.slug))
    options = state.data["options"]
    if args.option not in options:
        raise StateError(f"Unknown option '{args.option}'. Options: {', '.join(options)}")
    value = args.value.lower()
    if value not in ("true", "false"):
        raise StateError("The value must be true or false.")
    options[args.option] = value == "true"
    state.save()
    print(f"[OK] {args.option} = {value}")
    return 0


def cmd_auto(args) -> int:
    state = LaunchState.load(launch_dir(args.slug))
    state.set_auto_mode(args.mode == "on")
    state.save()
    if args.mode == "on":
        print("[OK] Auto mode ON: stages are approved automatically and labeled 'Not reviewed by PMM'.")
    else:
        print("[OK] Auto mode off: the agent will stop for your approval after each stage.")
    return 0


def cmd_render(args) -> int:
    from scripts.render.render import Renderer

    renderer = Renderer(launch_dir(args.slug), force=args.force)
    results = renderer.render_all(args.unit)
    for name in renderer.kept:
        print(f"[!] Kept your edits in outputs/{name} (not overwritten). See: launch.py edits {args.slug}")
    if not results:
        print("Nothing to render yet." if not args.unit else f"Nothing to render for {args.unit} yet.")
        return 0
    for r in results:
        extra = f" and outputs/{r.xlsx.name}" if r.xlsx else ""
        print(f"[OK] {r.title}: outputs/{r.markdown.name}, outputs/{r.docx.name}{extra}")
    return 0


def cmd_qa(args) -> int:
    from scripts.qa.run import run, summary_line

    path = launch_dir(args.slug)
    LaunchState.load(path)  # friendly error if the launch doesn't exist
    results = run(path, check_links=args.check_links, render=not args.no_render)
    for r in results:
        mark = {"pass": "[OK]", "warn": "[! ]", "fail": "[X ]"}[r.status]
        print(f"{mark} {r.check} {r.title}: {r.summary}")
    print(f"\nQA: {summary_line(results)}")
    print("Wrote qa-report.md and LAUNCH-KIT.md")
    return 1 if any(r.errors for r in results) else 0


def cmd_refresh(args) -> int:
    from scripts.connectors.env import load_env
    from scripts.qa.run import http_link_checker
    from scripts.refresh.refresh import main_summary, refresh

    path = launch_dir(args.slug)
    LaunchState.load(path)
    print("Checking competitors, regulation, market data and sources (this can take a few minutes) ...")
    result = refresh(path, env=load_env(), link_checker=None if args.no_links else http_link_checker)
    print(f"[OK] {main_summary(result)}")
    if result.unavailable:
        print(f"    {len(result.unavailable)} check(s) couldn't run; they're listed in the report for web search.")
    return 0


# ---------------------------------------------------------------------- parser
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="launch.py", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("new")
    s.add_argument("slug")
    s.add_argument("--name")
    s.set_defaults(func=cmd_new)

    for name, func in (("status", cmd_status),):
        s = sub.add_parser(name)
        s.add_argument("slug")
        s.set_defaults(func=func)

    for name, func in (("start", cmd_start), ("submit", cmd_submit), ("approve", cmd_approve)):
        s = sub.add_parser(name)
        s.add_argument("slug")
        s.add_argument("stage")
        s.set_defaults(func=func)

    s = sub.add_parser("add-industry")
    s.add_argument("slug")
    s.add_argument("id")
    s.add_argument("--name")
    s.add_argument("--sub-segments")
    s.add_argument("--regions")
    s.add_argument("--company-size")
    s.set_defaults(func=cmd_add_industry)

    s = sub.add_parser("remove-industry")
    s.add_argument("slug")
    s.add_argument("id")
    s.set_defaults(func=cmd_remove_industry)

    s = sub.add_parser("add-competitor")
    s.add_argument("slug")
    s.add_argument("id")
    s.add_argument("--name", required=True)
    s.add_argument("--suggested", action="store_true")
    s.set_defaults(func=cmd_add_competitor)

    s = sub.add_parser("remove-competitor")
    s.add_argument("slug")
    s.add_argument("id")
    s.set_defaults(func=cmd_remove_competitor)

    s = sub.add_parser("set-option")
    s.add_argument("slug")
    s.add_argument("option")
    s.add_argument("value")
    s.set_defaults(func=cmd_set_option)

    s = sub.add_parser("auto")
    s.add_argument("slug")
    s.add_argument("mode", choices=["on", "off"])
    s.set_defaults(func=cmd_auto)

    s = sub.add_parser("render")
    s.add_argument("slug")
    s.add_argument("--unit")
    s.add_argument("--force", action="store_true", help="overwrite Markdown files edited by hand")
    s.set_defaults(func=cmd_render)

    s = sub.add_parser("edits")
    s.add_argument("slug")
    s.add_argument("--discard", metavar="FILE", help="put back the last rendered version of FILE")
    s.set_defaults(func=cmd_edits)

    s = sub.add_parser("qa")
    s.add_argument("slug")
    s.add_argument("--check-links", action="store_true")
    s.add_argument("--no-render", action="store_true")
    s.set_defaults(func=cmd_qa)

    s = sub.add_parser("refresh")
    s.add_argument("slug")
    s.add_argument("--no-links", action="store_true", help="skip re-opening every source link")
    s.set_defaults(func=cmd_refresh)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except StateError as exc:
        print(f"[X] {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
