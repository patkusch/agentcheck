"""Command line: `agentcheck [folder]`."""
from __future__ import annotations

import argparse
import os
import sys

from . import __version__, report
from .runners import ORDER
from .scan import run_all


def _names(text):
    names = [n.strip() for n in text.split(",") if n.strip()]
    unknown = [n for n in names if n not in ORDER]
    if unknown:
        raise argparse.ArgumentTypeError(f"unknown tool {', '.join(unknown)}. Choose from {', '.join(ORDER)}")
    return names


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="agentcheck", description="One page about how safe a repo is to hand to a coding agent.")
    p.add_argument("--version", action="version", version=f"agentcheck {__version__}")
    p.add_argument("path", nargs="?", default=".", help="the project folder (default: this one)")
    p.add_argument("--json", action="store_true", help="print the result as JSON")
    p.add_argument("--all", action="store_true", help="also show the notes (small things, hidden by default)")
    p.add_argument("--only", type=_names, metavar="TOOLS", help="run only these tools, for example leash,mandata")
    p.add_argument("--skip", type=_names, default=[], metavar="TOOLS", help="do not run these tools")
    p.add_argument("--fail-on", choices=["fix", "check", "never"], default="fix",
                   help="when to exit with 1: when there is something to fix first (default), or to check as well, or never")
    args = p.parse_args(argv)
    if not os.path.isdir(args.path):
        print(f"agentcheck: {args.path} is not a folder", file=sys.stderr)
        return 2
    result = run_all(args.path, only=args.only, skip=args.skip)
    print(report.as_json(result) if args.json else report.text(result, show_notes=args.all))
    if not result.ran():
        return 2
    if args.fail_on == "never":
        return 0
    if result.items("fix") or (args.fail_on == "check" and result.items("check")):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
