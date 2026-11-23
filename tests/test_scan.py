import json
import unittest

from agentcheck import model, scan
from agentcheck.model import CHECK, FIX, NOTE

LEASH = {"files_checked": 1, "summary": {"high": 1}, "findings": [{"level": "high", "title": "reads keys", "fix": "remove", "path": "/repo/.claude/settings.local.json"}]}
SKILLGATE = [{"skill": "s", "path": "/repo/skills/s", "verdict": "block", "findings": [{"severity": "high", "file": "SKILL.md", "line": 2, "message": "bad", "snippet": ""}]}]
MANDATA = {"files": ["CLAUDE.md"], "findings": [{"level": "warn", "file": "CLAUDE.md", "line": 1, "said": "src/x.ts", "message": "gone"}]}
ANSWERS = {"leash": LEASH, "skillgate": SKILLGATE, "mandata": MANDATA}


def fake_runner(answers=ANSWERS, nothing=(), broken=()):
    def run(argv):
        name = next(n for n in ("leash", "skillgate", "mandata") if n in argv[0])
        if argv[-1] == "--version":
            return 0, f"{name} 1.2.3", ""
        if name in nothing:
            return 2, "", "No SKILL.md found under /repo"
        if name in broken:
            return 1, "", "Traceback\nboom"
        return 0, json.dumps(answers[name]), ""
    return run


COMMANDS = {"leash": ["leash"], "skillgate": ["skillgate"], "mandata": ["mandata"]}


class Scan(unittest.TestCase):
    def go(self, **kw):
        return scan.run_all("/repo", runner=fake_runner(**kw.pop("r", {})), commands=kw.pop("commands", COMMANDS), **kw)

    def test_all_three_tools_run_in_order_and_their_items_are_collected(self):
        report = self.go()
        self.assertEqual([r.name for r in report.runs], ["leash", "skillgate", "mandata"])
        self.assertEqual([r.status for r in report.runs], [model.OK] * 3)
        self.assertEqual([r.version for r in report.runs], ["1.2.3"] * 3)
        self.assertEqual(len(report.items()), 3)

    def test_items_come_most_urgent_first_then_in_tool_order(self):
        tiers_and_tools = [(i.tier, i.tool) for i in self.go().items()]
        self.assertEqual(tiers_and_tools, [(FIX, "leash"), (FIX, "skillgate"), (CHECK, "mandata")])

    def test_items_can_be_filtered_by_tier(self):
        report = self.go()
        self.assertEqual(len(report.items(FIX)), 2)
        self.assertEqual(len(report.items(CHECK)), 1)
        self.assertEqual(report.items(NOTE), [])

    def test_a_tool_that_is_not_installed_is_reported_with_how_to_install_it_and_the_others_still_run(self):
        from unittest import mock
        with mock.patch("agentcheck.runners.find_command", return_value=None):
            report = scan.run_all("/repo", runner=fake_runner(), commands={"leash": ["leash"], "skillgate": ["skillgate"]})
        self.assertEqual([r.status for r in report.runs], [model.OK, model.OK, model.MISSING])
        self.assertIn("pip install git+https://github.com/patkusch/mandata", report.runs[2].note)
        self.assertNotIn(report.runs[2], report.ran())

    def test_a_repo_with_no_skills_is_nothing_to_check_not_a_failure(self):
        report = self.go(r={"nothing": ("skillgate",)})
        run = report.runs[1]
        self.assertEqual(run.status, model.NOTHING)
        self.assertEqual(run.summary, "found no skills (no SKILL.md files) to check")
        self.assertIn(run, report.ran())

    def test_a_tool_that_breaks_is_reported_as_failed_and_counted_as_not_run(self):
        report = self.go(r={"broken": ("mandata",)})
        run = report.runs[2]
        self.assertEqual(run.status, model.FAILED)
        self.assertNotIn(run, report.ran())
        self.assertEqual(run.items, [])

    def test_only_and_skip_choose_which_tools_run(self):
        report = self.go(only=["leash"])
        self.assertEqual([r.status for r in report.runs], [model.OK, model.SKIPPED, model.SKIPPED])
        report = self.go(skip=("leash",))
        self.assertEqual([r.status for r in report.runs], [model.SKIPPED, model.OK, model.OK])
        self.assertEqual(report.runs[0].note, "you asked not to run it")

    def test_the_root_is_made_absolute(self):
        import os
        self.assertEqual(scan.run_all(".", runner=fake_runner(), commands=COMMANDS).root, os.path.abspath("."))


if __name__ == "__main__":
    unittest.main()
