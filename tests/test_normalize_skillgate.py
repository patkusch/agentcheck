import unittest

from agentcheck import normalize
from agentcheck.model import CHECK, FIX, NOTE

ROOT = "/repo"


def skill(name, verdict, findings, path="/repo/skills/demo"):
    return {"skill": name, "path": path, "verdict": verdict, "findings": findings, "files": {}}


def finding(severity, message="Tells the AI to hide something from you.", file="SKILL.md", line=8, snippet="do not tell the user"):
    return {"rule": "r", "severity": severity, "capability": "injection", "file": file, "line": line, "snippet": snippet, "message": message}


class Skillgate(unittest.TestCase):
    def test_high_is_fix_first_medium_is_check_and_low_is_a_note(self):
        items, _ = normalize.skillgate([skill("s", "block", [finding("high"), finding("medium"), finding("low")])], ROOT)
        self.assertEqual([i.tier for i in items], [FIX, CHECK, NOTE])

    def test_the_place_is_the_file_and_line_from_the_repo_root(self):
        (item,), _ = normalize.skillgate([skill("demo", "block", [finding("high", file="scripts/run.sh", line=3)])], ROOT)
        self.assertEqual(item.where, "skills/demo/scripts/run.sh:3")

    def test_the_title_names_the_skill_the_problem_and_the_line_it_found(self):
        (item,), _ = normalize.skillgate([skill("format-helper", "block", [finding("high")])], ROOT)
        self.assertEqual(item.title, "skill \"format-helper\": Tells the AI to hide something from you. ('do not tell the user')")

    def test_a_long_snippet_is_cut_and_a_missing_one_is_left_out(self):
        (long,), _ = normalize.skillgate([skill("s", "block", [finding("high", snippet="x" * 300)])], ROOT)
        self.assertLess(len(long.title), 200)
        (none,), _ = normalize.skillgate([skill("s", "block", [finding("high", snippet="")])], ROOT)
        self.assertNotIn("(", none.title)

    def test_only_fix_first_items_carry_advice(self):
        a, b = normalize.skillgate([skill("s", "block", [finding("high"), finding("medium")])], ROOT)[0]
        self.assertIn("Do not let an agent use the skill", a.fix)
        self.assertEqual(b.fix, "")

    def test_a_line_number_of_zero_or_none_is_not_shown(self):
        (item,), _ = normalize.skillgate([skill("s", "review", [finding("medium", line=0)])], ROOT)
        self.assertEqual(item.where, "skills/demo/SKILL.md")

    def test_the_summary_counts_skills_by_verdict(self):
        _, text = normalize.skillgate([skill("a", "block", []), skill("b", "review", []), skill("c", "ok", []), skill("d", "ok", [])], ROOT)
        self.assertEqual(text, "checked 4 skills: 1 blocked, 1 need review, 2 fine")
        _, text = normalize.skillgate([skill("a", "ok", [])], ROOT)
        self.assertEqual(text, "checked 1 skill: 1 fine")

    def test_an_answer_that_is_not_a_list_gives_nothing_instead_of_crashing(self):
        self.assertEqual(normalize.skillgate({"unexpected": True}, ROOT), ([], "checked 0 skills"))


if __name__ == "__main__":
    unittest.main()
