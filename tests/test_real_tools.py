"""The real tools on the example projects. Skipped when leash, skillgate and mandata are not installed."""
import json
import unittest
from pathlib import Path

from agentcheck import model, report, runners, scan

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"
INSTALLED = all(runners.find_command(runners.TOOLS[n]) for n in runners.ORDER)


@unittest.skipUnless(INSTALLED, "leash, skillgate and mandata are not all installed")
class RealTools(unittest.TestCase):
    def test_the_healthy_example_has_nothing_to_fix_and_every_tool_ran(self):
        result = scan.run_all(str(EXAMPLES / "healthy"))
        self.assertEqual([r.status for r in result.runs], [model.OK, model.OK, model.OK])
        self.assertEqual(result.items("fix"), [])
        self.assertEqual(result.items("check"), [])
        self.assertTrue(all(r.version for r in result.runs))

    def test_the_risky_example_has_something_from_every_tool_in_fix_first(self):
        result = scan.run_all(str(EXAMPLES / "risky"))
        tools = {i.tool for i in result.items("fix")}
        self.assertEqual(tools, {"leash", "skillgate", "mandata"})

    def test_the_planted_problems_are_each_found(self):
        titles = " ".join(i.title for i in scan.run_all(str(EXAMPLES / "risky")).items("fix"))
        self.assertIn("a password or key set as an environment variable", titles)
        self.assertIn("Tells the AI to drop its own rules", titles)
        self.assertIn('package.json has no "check" script', titles)
        self.assertIn("package.json says it needs Node 22 or newer", titles)

    def test_the_page_and_the_json_both_come_out_of_real_output(self):
        result = scan.run_all(str(EXAMPLES / "risky"))
        self.assertIn("FIX THESE FIRST", report.text(result))
        self.assertGreater(json.loads(report.as_json(result))["fix_first"], 10)

    def test_a_folder_with_none_of_the_things_they_read_is_nothing_to_check_for_each(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            result = scan.run_all(d)
        self.assertEqual([r.status for r in result.runs][1], model.NOTHING)
        self.assertEqual(result.items(), [])


if __name__ == "__main__":
    unittest.main()
