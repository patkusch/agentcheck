"""Command line: `agentcheck [folder]`."""
from __future__ import annotations

import argparse
import sys

from . import __version__


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="agentcheck", description="One page about how safe a repo is to hand to a coding agent.")
    p.add_argument("--version", action="version", version=f"agentcheck {__version__}")
    p.add_argument("path", nargs="?", default=".", help="the project folder (default: this one)")
    p.parse_args(argv)
    print("agentcheck is being built.", file=sys.stderr)
    return 2
