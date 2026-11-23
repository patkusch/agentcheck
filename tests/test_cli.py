import contextlib
import io
import json
import unittest
from unittest import mock

from agentcheck import __version__, model
from agentcheck.cli import main
from agentcheck.model import CHECK, FIX, NOTE, Item, ToolRun
from agentcheck.scan import Report


def call(argv, report=None):
    out, err = io.StringIO(), io.StringIO()
    patch = mock.patch("agentcheck.cli.run_all", return_value=report) if report is not None else contextlib.nullcontext()
    with patch as fake, contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as e:
            code = e.code
    return code, out.getvalue(), err.getvalue(), fake


def report(*items, status=model.OK):
    return Report(root="/repo", runs=[ToolRun("leash", status, "1.0.0", list(items), "read 1 permission file")])


FIXME = Item("leash", FIX, "a.json", "bad")
CHECKME = Item("leash", CHECK, "b.json", "odd")
NOTEME = Item("leash", NOTE, "c.json", "tiny")


class Cli(unittest.TestCase):
    def test_version_and_help(self):
        code, out, _, _ = call(["--version"])
        self.assertEqual((code, out.strip()), (0, f"agentcheck {__version__}"))
        code, out, _, _ = call(["--help"])
        self.assertEqual(code, 0)
        self.assertIn("how safe a repo is to hand to a coding agent", out)

    def test_a_folder_that_does_not_exist_is_a_plain_message_and_exit_2(self):
        code, out, err, _ = call(["/no/such/folder"])
        self.assertEqual((code, out), (2, ""))
        self.assertIn("is not a folder", err)

    def test_something_to_fix_first_exits_1_and_nothing_wrong_exits_0(self):
        self.assertEqual(call(["."], report(FIXME))[0], 1)
        self.assertEqual(call(["."], report(CHECKME, NOTEME))[0], 0)
        self.assertEqual(call(["."], report())[0], 0)

    def test_fail_on_check_also_fails_on_things_to_check_and_never_never_fails(self):
        self.assertEqual(call([".", "--fail-on", "check"], report(CHECKME))[0], 1)
        self.assertEqual(call([".", "--fail-on", "check"], report(NOTEME))[0], 0)
        self.assertEqual(call([".", "--fail-on", "never"], report(FIXME))[0], 0)

    def test_when_no_tool_could_run_it_exits_2_not_0_so_a_clean_looking_page_is_never_a_pass(self):
        code, out, _, _ = call(["."], report(status=model.MISSING))
        self.assertEqual(code, 2)
        self.assertIn("No tool could run", out)

    def test_json_prints_the_result_as_data(self):
        code, out, _, _ = call([".", "--json"], report(FIXME))
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out)["fix_first"], 1)

    def test_notes_are_hidden_unless_all_is_given(self):
        self.assertNotIn("tiny", call(["."], report(NOTEME))[1])
        self.assertIn("tiny", call([".", "--all"], report(NOTEME))[1])

    def test_only_and_skip_are_passed_on_as_lists_of_tool_names(self):
        _, _, _, fake = call([".", "--only", "leash,mandata", "--skip", "mandata"], report())
        fake.assert_called_once()
        self.assertEqual(fake.call_args.kwargs, {"only": ["leash", "mandata"], "skip": ["mandata"]})

    def test_an_unknown_tool_name_is_refused_with_the_choices(self):
        code, _, err, _ = call([".", "--only", "nope"])
        self.assertEqual(code, 2)
        self.assertIn("unknown tool nope", err)
        self.assertIn("leash, skillgate, mandata", err)

    def test_the_folder_is_passed_to_the_scan(self):
        _, _, _, fake = call(["."], report())
        self.assertEqual(fake.call_args.args, (".",))


if __name__ == "__main__":
    unittest.main()
