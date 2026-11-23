import unittest

from agentcheck import normalize
from agentcheck.model import CHECK, FIX


def finding(level, said="npm run lint", message="package.json has no \"lint\" script.", file="CLAUDE.md", line=3):
    return {"level": level, "file": file, "line": line, "code": "x", "said": said, "message": message}


class Mandata(unittest.TestCase):
    def test_a_wrong_claim_is_fix_first_and_a_probably_stale_one_is_check(self):
        data = {"files": ["CLAUDE.md"], "errors": 1, "warnings": 1, "findings": [finding("error"), finding("warn")]}
        items, _ = normalize.mandata(data, "/repo")
        self.assertEqual([i.tier for i in items], [FIX, CHECK])

    def test_the_place_is_the_file_and_line_and_the_title_joins_what_it_said_with_what_is_true(self):
        (item,), _ = normalize.mandata({"files": ["CLAUDE.md"], "findings": [finding("error")]}, "/repo")
        self.assertEqual((item.tool, item.where), ("mandata", "CLAUDE.md:3"))
        self.assertEqual(item.title, 'npm run lint: package.json has no "lint" script.')

    def test_a_finding_with_no_line_shows_just_the_file(self):
        (item,), _ = normalize.mandata({"files": ["CLAUDE.md"], "findings": [finding("warn", line=0)]}, "/repo")
        self.assertEqual(item.where, "CLAUDE.md")

    def test_the_summary_counts_wrong_and_stale(self):
        data = {"files": ["CLAUDE.md", "AGENTS.md"], "findings": [finding("error"), finding("error"), finding("warn")]}
        self.assertEqual(normalize.mandata(data, "/repo")[1], "read 2 instruction files: 2 wrong now, 1 probably stale")

    def test_a_clean_result_says_everything_it_could_test_is_true(self):
        self.assertEqual(normalize.mandata({"files": ["CLAUDE.md"], "findings": []}, "/repo")[1],
                         "read 1 instruction file, everything it could test is still true")

    def test_no_instruction_files_is_said_plainly(self):
        self.assertEqual(normalize.mandata({"files": [], "findings": []}, "/repo"), ([], "found no instruction files (CLAUDE.md, AGENTS.md and the like)"))


if __name__ == "__main__":
    unittest.main()
