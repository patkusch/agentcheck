"""Write the page."""
from __future__ import annotations

import json
from dataclasses import asdict

from . import model
from .model import CHECK, FIX, NOTE

HEADINGS = {FIX: "FIX THESE FIRST", CHECK: "CHECK THESE", NOTE: "NOTES"}
LIMITS = (
    "An empty list does not mean the repo is safe. It means these tools found nothing.",
    "They read files. They do not run your code, look at your dependencies, scan your servers or judge advice such as \"write clean code\".",
)


def _plural(n, word):
    return f"{n} {word}{'' if n == 1 else 's'}"


def _verdict(report):
    fix = len(report.items(FIX))
    check = len(report.items(CHECK))
    if not report.ran():
        return "No tool could run, so nothing was checked."
    if fix:
        return f"{_plural(fix, 'thing')} to fix first" + (f", and {check} to check." if check else ".")
    if check:
        return f"Nothing to fix first. {_plural(check, 'thing')} to check."
    return "Nothing to fix first, and nothing to check."


def text(report, show_notes=False) -> str:
    lines = [f"agentcheck: {report.root}", "", _verdict(report), ""]
    ran = [r for r in report.runs if r.status in (model.OK, model.NOTHING)]
    if ran:
        lines.append("Checked with " + ", ".join(f"{r.name} {r.version}".strip() for r in ran) + ".")
    for r in report.runs:
        if r.status not in (model.OK, model.NOTHING):
            lines.append(f"Not run: {r.name} ({r.note}).")
    for tier in (FIX, CHECK, NOTE):
        items = report.items(tier)
        if not items:
            continue
        if tier == NOTE and not show_notes:
            lines += ["", f"{_plural(len(items), 'note')} not shown. Add --all to see {'it' if len(items) == 1 else 'them'}."]
            continue
        lines += ["", f"{HEADINGS[tier]} ({len(items)})"]
        first_with = {}
        for n, item in enumerate(items, 1):
            lines.append(f"  {n}. [{item.tool}] {item.where}")
            lines.append(f"     {item.title}")
            if item.fix:
                earlier = first_with.setdefault(item.fix, n)
                lines.append(f"     To fix: {item.fix}" if earlier == n else f"     To fix: same as {earlier}.")
    lines += ["", "WHAT EACH TOOL SAW"]
    width = max(len(r.name) for r in report.runs)
    for r in report.runs:
        said = r.summary if r.status in (model.OK, model.NOTHING) else "did not run"
        lines.append(f"  {r.name.ljust(width)}  {said}")
    lines += ["", "WHAT THIS PAGE DOES NOT TELL YOU"] + [f"  {t}" for t in LIMITS]
    return "\n".join(lines)


def as_json(report) -> str:
    return json.dumps({
        "root": report.root,
        "fix_first": len(report.items(FIX)),
        "check": len(report.items(CHECK)),
        "notes": len(report.items(NOTE)),
        "tools": [{"name": r.name, "status": r.status, "version": r.version, "summary": r.summary, "note": r.note,
                   "fix_first": r.count(FIX), "check": r.count(CHECK), "notes": r.count(NOTE)} for r in report.runs],
        "items": [asdict(i) for i in report.items()],
    }, indent=2)
