import unittest

from agentcheck import normalize
from agentcheck.model import CHECK, FIX, NOTE

ROOT = "/repo"


def finding(level, title="t", path="/repo/.claude/settings.local.json", fix="do this"):
    return {"level": level, "kind": "rule", "title": title, "fix": fix, "path": path, "project": "/repo", "rule": None}


class Leash(unittest.TestCase):
    def test_critical_and_high_are_fix_first_medium_is_check_and_the_rest_are_notes(self):
        data = {"files_checked": 1, "summary": {"critical": 1, "high": 1, "medium": 1, "low": 1, "info": 1},
                "findings": [finding(level) for level in ("critical", "high", "medium", "low", "info")]}
        items, _ = normalize.leash(data, ROOT)
        self.assertEqual([i.tier for i in items], [FIX, FIX, CHECK, NOTE, NOTE])

    def test_the_file_is_shown_from_the_repo_root_and_the_title_and_fix_are_kept(self):
        (item,), _ = normalize.leash({"files_checked": 1, "summary": {}, "findings": [finding("high", "may read ~/.aws", fix="remove it")]}, ROOT)
        self.assertEqual((item.tool, item.where, item.title, item.fix), ("leash", ".claude/settings.local.json", "may read ~/.aws", "remove it"))

    def test_a_file_outside_the_repo_keeps_its_full_path_and_a_missing_path_gets_a_name(self):
        (a, b), _ = normalize.leash({"findings": [finding("high", path="/elsewhere/x.json"), finding("high", path=None)]}, ROOT)
        self.assertEqual(a.where, "/elsewhere/x.json")
        self.assertEqual(b.where, "agent permissions")

    def test_an_unknown_level_is_only_a_note_rather_than_an_alarm(self):
        (item,), _ = normalize.leash({"findings": [finding("weird")]}, ROOT)
        self.assertEqual(item.tier, NOTE)

    def test_the_summary_line_says_how_many_files_and_what_was_serious(self):
        _, text = normalize.leash({"files_checked": 2, "summary": {"critical": 3, "high": 1, "medium": 0}, "findings": []}, ROOT)
        self.assertEqual(text, "read 2 permission files: 3 critical, 1 high")
        _, text = normalize.leash({"files_checked": 1, "summary": {}, "findings": []}, ROOT)
        self.assertEqual(text, "read 1 permission file, nothing serious")

    def test_a_repo_with_no_permission_files_says_so(self):
        items, text = normalize.leash({"files_checked": 0, "summary": {}, "findings": []}, ROOT)
        self.assertEqual((items, text), ([], "found no agent permission files to read"))

    def test_an_empty_or_odd_answer_does_not_crash(self):
        self.assertEqual(normalize.leash({}, ROOT)[0], [])


if __name__ == "__main__":
    unittest.main()
