"""Run each tool on a repo and collect what they found."""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from . import model, normalize
from .model import TIERS, ToolRun
from .runners import ORDER, TOOLS, subprocess_runner, run_tool

NORMALIZERS = {"leash": normalize.leash, "skillgate": normalize.skillgate, "mandata": normalize.mandata}
NOTHING_TEXT = {
    "leash": "found no agent permission files to read",
    "skillgate": "found no skills (no SKILL.md files) to check",
    "mandata": "found no instruction files (CLAUDE.md, AGENTS.md and the like)",
}


@dataclass
class Report:
    root: str
    runs: list = field(default_factory=list)

    def items(self, tier=None):
        """Every item, most urgent first; within a tier, in tool order and then by place."""
        order = {name: i for i, name in enumerate(ORDER)}
        out = [i for run in self.runs for i in run.items if tier in (None, i.tier)]
        return sorted(out, key=lambda i: (TIERS.index(i.tier), order.get(i.tool, 99), i.where))

    def ran(self):
        return [r for r in self.runs if r.status in (model.OK, model.NOTHING)]


def run_all(path, only=None, skip=(), runner=subprocess_runner, commands=None) -> Report:
    root = os.path.abspath(path)
    report = Report(root=root)
    commands = commands or {}
    for name in ORDER:
        tool = TOOLS[name]
        if (only and name not in only) or name in skip:
            report.runs.append(ToolRun(name, model.SKIPPED, note="you asked not to run it"))
            continue
        status, version, data, note = run_tool(tool, root, runner=runner, command=commands.get(name))
        run = ToolRun(name, status, version=version, note=note)
        if status == model.OK:
            run.items, run.summary = NORMALIZERS[name](data, root)
        elif status == model.NOTHING:
            run.summary = NOTHING_TEXT[name]
        report.runs.append(run)
    return report
