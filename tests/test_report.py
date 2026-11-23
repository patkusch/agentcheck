import json
import unittest

from agentcheck import model, report as page
from agentcheck.model import CHECK, FIX, NOTE, Item, ToolRun
from agentcheck.scan import Report


def build(*runs):
    return Report(root="/repo", runs=list(runs))


LEASH = ToolRun("leash", model.OK, "0.4.2", [Item("leash", FIX, ".claude/settings.local.json", "reads ~/.aws", "remove the rule"),
                                             Item("leash", NOTE, "x.json", "a small thing")], "read 1 permission file: 1 high")
SKILL = ToolRun("skillgate", model.NOTHING, "0.1.0", [], "found no skills (no SKILL.md files) to check")
MAND = ToolRun("mandata", model.OK, "0.1.0", [Item("mandata", CHECK, "CLAUDE.md:3", "src/x.ts: that is not in the project.")], "read 1 instruction file: 0 wrong now, 1 probably stale")


class Text(unittest.TestCase):
    def test_the_top_says_in_one_sentence_how_many_things_to_fix_and_check(self):
        self.assertIn("1 thing to fix first, and 1 to check.", page.text(build(LEASH, SKILL, MAND)))
        self.assertIn("Nothing to fix first. 1 thing to check.", page.text(build(SKILL, MAND)))
        self.assertIn("Nothing to fix first, and nothing to check.", page.text(build(SKILL)))

    def test_fix_first_comes_before_check_and_each_item_has_its_tool_place_and_words(self):
        out = page.text(build(LEASH, SKILL, MAND))
        self.assertLess(out.index("FIX THESE FIRST (1)"), out.index("CHECK THESE (1)"))
        self.assertIn("  1. [leash] .claude/settings.local.json\n     reads ~/.aws\n     To fix: remove the rule", out)
        self.assertIn("  1. [mandata] CLAUDE.md:3\n     src/x.ts: that is not in the project.", out)

    def test_notes_are_counted_but_hidden_unless_asked_for(self):
        self.assertIn("1 note not shown. Add --all to see it.", page.text(build(LEASH)))
        self.assertNotIn("a small thing", page.text(build(LEASH)))
        shown = page.text(build(LEASH), show_notes=True)
        self.assertIn("NOTES (1)", shown)
        self.assertIn("a small thing", shown)

    def test_it_names_the_tools_that_ran_with_versions_and_the_ones_that_did_not_with_why(self):
        missing = ToolRun("mandata", model.MISSING, note="not installed. Install it with: pip install x")
        out = page.text(build(LEASH, SKILL, missing))
        self.assertIn("Checked with leash 0.4.2, skillgate 0.1.0.", out)
        self.assertIn("Not run: mandata (not installed. Install it with: pip install x).", out)

    def test_each_tool_gets_a_line_saying_what_it_saw_or_that_it_did_not_run(self):
        failed = ToolRun("mandata", model.FAILED, note="its answer could not be read (boom)")
        out = page.text(build(LEASH, SKILL, failed))
        self.assertIn("  leash      read 1 permission file: 1 high", out)
        self.assertIn("  skillgate  found no skills (no SKILL.md files) to check", out)
        self.assertIn("  mandata    did not run", out)

    def test_when_nothing_could_run_it_says_nothing_was_checked_instead_of_looking_clean(self):
        out = page.text(build(ToolRun("leash", model.MISSING, note="n"), ToolRun("mandata", model.MISSING, note="n")))
        self.assertIn("No tool could run, so nothing was checked.", out)
        self.assertNotIn("nothing to check.", out)

    def test_the_page_always_ends_by_saying_what_it_cannot_tell_you(self):
        out = page.text(build(SKILL))
        self.assertTrue(out.rstrip().endswith("or judge advice such as \"write clean code\"."))
        self.assertIn("An empty list does not mean the repo is safe.", out)


class Json(unittest.TestCase):
    def test_json_has_the_counts_the_tools_and_every_item(self):
        data = json.loads(page.as_json(build(LEASH, SKILL, MAND)))
        self.assertEqual((data["fix_first"], data["check"], data["notes"]), (1, 1, 1))
        self.assertEqual([t["name"] for t in data["tools"]], ["leash", "skillgate", "mandata"])
        self.assertEqual(data["tools"][0]["fix_first"], 1)
        self.assertEqual(data["tools"][1]["status"], "nothing")
        self.assertEqual([i["tier"] for i in data["items"]], ["fix", "check", "note"])
        self.assertEqual(set(data["items"][0]), {"tool", "tier", "where", "title", "fix"})


if __name__ == "__main__":
    unittest.main()
