"""Turn each tool's own JSON into the same plain list of items."""
from __future__ import annotations

import os

from . import model
from .model import CHECK, FIX, NOTE, Item


def _relative(path, root):
    if not path:
        return ""
    try:
        rel = os.path.relpath(path, root)
    except ValueError:
        return path
    return path if rel.startswith("..") else rel


def _plural(n, word):
    return f"{n} {word}{'' if n == 1 else 's'}"


LEASH_TIER = {"critical": FIX, "high": FIX, "medium": CHECK, "low": NOTE, "info": NOTE}


def leash(data, root):
    """leash prints {"files_checked", "summary", "findings": [{"level", "title", "fix", "path", ...}]}."""
    items = []
    for f in data.get("findings", []):
        tier = LEASH_TIER.get(f.get("level"), NOTE)
        items.append(Item("leash", tier, _relative(f.get("path"), root) or "agent permissions", f.get("title", ""), f.get("fix", "")))
    checked = int(data.get("files_checked", 0) or 0)
    summary = data.get("summary", {})
    counts = ", ".join(f"{summary[k]} {k}" for k in ("critical", "high", "medium") if summary.get(k))
    if checked == 0 and not items:
        text = "found no agent permission files to read"
    else:
        text = f"read {_plural(checked, 'permission file')}" + (f": {counts}" if counts else ", nothing serious")
    return items, text


SKILLGATE_TIER = {"high": FIX, "medium": CHECK, "low": NOTE}
SKILLGATE_FIX = "Read this line. Do not let an agent use the skill until you are sure it is meant to be there."


def skillgate(data, root):
    """skillgate prints a list of {"skill", "path", "verdict", "findings": [{"severity", "file", "line", "message", "snippet"}]}."""
    items = []
    skills = data if isinstance(data, list) else []
    verdicts = {"ok": 0, "review": 0, "block": 0}
    for skill in skills:
        verdicts[skill.get("verdict")] = verdicts.get(skill.get("verdict"), 0) + 1
        folder = _relative(skill.get("path"), root)
        for f in skill.get("findings", []):
            tier = SKILLGATE_TIER.get(f.get("severity"), NOTE)
            where = f"{folder}/{f.get('file', '')}".replace("//", "/").strip("/")
            if f.get("line"):
                where += f":{f['line']}"
            title = f"skill \"{skill.get('skill', folder)}\": {f.get('message', '')}"
            snippet = (f.get("snippet") or "").strip()
            if snippet:
                title += f" ({snippet[:70]!r})"
            items.append(Item("skillgate", tier, where, title, SKILLGATE_FIX if tier == FIX else ""))
    parts = [f"{n} {word}" for word, n in (("blocked", verdicts["block"]), ("need review", verdicts["review"]), ("fine", verdicts["ok"])) if n]
    return items, f"checked {_plural(len(skills), 'skill')}" + (": " + ", ".join(parts) if parts else "")


def mandata(data, root):
    """mandata prints {"files", "errors", "warnings", "findings": [{"level", "file", "line", "said", "message"}]}."""
    items = []
    for f in data.get("findings", []):
        tier = FIX if f.get("level") == "error" else CHECK
        where = f"{f.get('file', '')}:{f['line']}" if f.get("line") else f.get("file", "")
        items.append(Item("mandata", tier, where, f"{f.get('said', '')}: {f.get('message', '')}"))
    files = data.get("files", [])
    if not files:
        return items, "found no instruction files (CLAUDE.md, AGENTS.md and the like)"
    wrong = sum(1 for i in items if i.tier == FIX)
    stale = sum(1 for i in items if i.tier == CHECK)
    if not items:
        return items, f"read {_plural(len(files), 'instruction file')}, everything it could test is still true"
    return items, f"read {_plural(len(files), 'instruction file')}: {wrong} wrong now, {stale} probably stale"
