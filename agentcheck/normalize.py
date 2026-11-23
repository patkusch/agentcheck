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
