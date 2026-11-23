"""Find the three tools, run them, and read what they print. Nothing here judges the results."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable

from . import model

TIMEOUT_SECONDS = 180


@dataclass
class Tool:
    name: str
    module: str
    exe: str
    install: str
    args: Callable          # path -> the arguments that make it print JSON and never fail the run
    nothing_text: tuple = ()  # words on stderr that mean "this repo has nothing of the kind I look at"


TOOLS = {
    "leash": Tool(
        "leash", "leash", "leash", "pip install git+https://github.com/patkusch/leash",
        lambda path: [path, "--json", "--no-user", "--no-gh", "--fail-on", "never"]),
    "skillgate": Tool(
        "skillgate", "skillgate", "skillgate", "pip install git+https://github.com/patkusch/skillgate",
        lambda path: ["scan", path, "--json", "--fail-on", "never"],
        nothing_text=("No SKILL.md found",)),
    "mandata": Tool(
        "mandata", "mandata", "mandata", "pip install git+https://github.com/patkusch/mandata",
        lambda path: [path, "--json", "--fail-on", "never"]),
}
ORDER = ("leash", "skillgate", "mandata")


def subprocess_runner(argv):
    """Run a command and return (exit code, what it printed, what it complained about)."""
    try:
        done = subprocess.run(argv, capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, "", str(e)
    return done.returncode, done.stdout, done.stderr


def find_command(tool: Tool):
    """The words that start the tool, or None when it is not installed here."""
    try:
        if importlib.util.find_spec(tool.module) is not None:
            return [sys.executable, "-m", tool.module]
    except (ImportError, ValueError):
        pass
    exe = shutil.which(tool.exe)
    return [exe] if exe else None


def _version(command, runner) -> str:
    code, out, err = runner(command + ["--version"])
    m = re.search(r"\d+\.\d+\.\d+", out + err) if code == 0 else None
    return m.group(0) if m else ""


def run_tool(tool: Tool, path: str, runner=subprocess_runner, command=None):
    """Return (status, version, data, note). `command` lets a test say where the tool is."""
    command = command if command is not None else find_command(tool)
    if command is None:
        return model.MISSING, "", None, f"not installed. Install it with: {tool.install}"
    version = _version(command, runner)
    code, out, err = runner(command + tool.args(path))
    if any(text in (out + err) for text in tool.nothing_text):
        return model.NOTHING, version, None, ""
    try:
        data = json.loads(out)
    except ValueError:
        first = (err.strip().splitlines() or out.strip().splitlines() or ["no output"])[0]
        return model.FAILED, version, None, f"its answer could not be read ({first[:120]})"
    return model.OK, version, data, ""
