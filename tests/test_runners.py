import json
import unittest

from agentcheck import model, runners
from agentcheck.runners import TOOLS, run_tool


def fake(answers):
    """A stand-in for running a program: answers[(first word after the program)] -> (code, out, err)."""
    calls = []

    def run(argv):
        calls.append(argv)
        key = "--version" if argv[-1] == "--version" else "run"
        return answers[key]
    run.calls = calls
    return run


class Runners(unittest.TestCase):
    def test_every_tool_is_asked_for_json_and_told_never_to_fail_the_run(self):
        for name, tool in TOOLS.items():
            args = tool.args("/repo")
            self.assertIn("/repo", args, name)
            self.assertIn("--json", args, name)
            self.assertEqual(args[args.index("--fail-on") + 1], "never", name)

    def test_leash_is_told_not_to_read_the_home_folder_or_ask_github(self):
        args = TOOLS["leash"].args("/repo")
        self.assertIn("--no-user", args)
        self.assertIn("--no-gh", args)

    def test_skillgate_is_asked_to_scan_and_the_order_is_leash_skillgate_mandata(self):
        self.assertEqual(TOOLS["skillgate"].args("/repo")[0], "scan")
        self.assertEqual(runners.ORDER, ("leash", "skillgate", "mandata"))

    def test_a_tool_that_is_not_installed_says_how_to_install_it(self):
        absent = runners.Tool("ghost", "no_such_module_xyz", "no-such-exe-xyz", "pip install ghost", lambda p: [p])
        status, version, data, note = run_tool(absent, "/repo", runner=fake({}))
        self.assertEqual((status, version, data), (model.MISSING, "", None))
        self.assertEqual(note, "not installed. Install it with: pip install ghost")

    def test_a_working_tool_gives_its_version_and_its_json(self):
        run = fake({"--version": (0, "leash 0.4.2\n", ""), "run": (0, json.dumps({"findings": []}), "")})
        status, version, data, note = run_tool(TOOLS["leash"], "/repo", runner=run, command=["leash"])
        self.assertEqual((status, version, data, note), (model.OK, "0.4.2", {"findings": []}, ""))
        self.assertEqual(run.calls[0], ["leash", "--version"])
        self.assertEqual(run.calls[1][0], "leash")

    def test_an_answer_that_is_not_json_is_a_failure_with_the_first_line_of_the_complaint(self):
        run = fake({"--version": (0, "x 1.0.0", ""), "run": (1, "", "Traceback (most recent call last):\n  boom")})
        status, _, data, note = run_tool(TOOLS["mandata"], "/repo", runner=run, command=["mandata"])
        self.assertEqual((status, data), (model.FAILED, None))
        self.assertIn("could not be read", note)
        self.assertIn("Traceback", note)

    def test_skillgate_saying_there_are_no_skills_means_nothing_to_check_not_a_failure(self):
        run = fake({"--version": (0, "skillgate 0.1.0", ""), "run": (2, "", "No SKILL.md found under /repo")})
        status, version, data, _ = run_tool(TOOLS["skillgate"], "/repo", runner=run, command=["skillgate"])
        self.assertEqual((status, version, data), (model.NOTHING, "0.1.0", None))

    def test_a_missing_version_is_left_blank(self):
        run = fake({"--version": (2, "", "unknown option"), "run": (0, "[]", "")})
        self.assertEqual(run_tool(TOOLS["skillgate"], "/repo", runner=run, command=["skillgate"])[1], "")

    def test_a_program_that_cannot_start_is_reported_by_the_real_runner_without_crashing(self):
        code, out, err = runners.subprocess_runner(["/no/such/program"])
        self.assertEqual((code, out), (127, ""))
        self.assertTrue(err)

    def test_the_real_runner_returns_what_a_program_prints(self):
        import sys
        code, out, _ = runners.subprocess_runner([sys.executable, "-c", "print('hi')"])
        self.assertEqual((code, out.strip()), (0, "hi"))

    def test_find_command_prefers_an_importable_module_and_gives_none_when_neither_exists(self):
        found = runners.find_command(runners.Tool("t", "json", "no-such-exe", "", lambda p: []))
        self.assertEqual(found[1:], ["-m", "json"])
        self.assertIsNone(runners.find_command(runners.Tool("t", "no_such_module_xyz", "no-such-exe-xyz", "", lambda p: [])))


if __name__ == "__main__":
    unittest.main()
