"""The few shapes everything else passes around."""
from __future__ import annotations

from dataclasses import dataclass, field

FIX = "fix"      # wrong or dangerous now: do this first
CHECK = "check"  # probably a problem: look at it
NOTE = "note"    # worth knowing, not worth acting on

TIERS = (FIX, CHECK, NOTE)

# What each status means for the page.
OK = "ok"                # the tool ran and gave an answer (which may be "nothing found")
MISSING = "missing"      # the tool is not installed
FAILED = "failed"        # the tool ran but its answer could not be read
NOTHING = "nothing"      # the tool ran and the repo has nothing of the kind it looks at
SKIPPED = "skipped"      # the person asked not to run it


@dataclass
class Item:
    tool: str
    tier: str
    where: str      # a file and line, or a short name for the thing
    title: str      # what is wrong, in a sentence
    fix: str = ""   # what to do about it, when the tool says


@dataclass
class ToolRun:
    name: str
    status: str
    version: str = ""
    items: list = field(default_factory=list)
    summary: str = ""   # one line: what this tool looked at and how it went
    note: str = ""      # why it did not run, or what went wrong

    def count(self, tier: str) -> int:
        return sum(1 for i in self.items if i.tier == tier)
