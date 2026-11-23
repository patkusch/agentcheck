import unittest

from agentcheck import model
from agentcheck.model import CHECK, FIX, NOTE, Item, ToolRun


class Model(unittest.TestCase):
    def test_tiers_run_from_most_to_least_urgent(self):
        self.assertEqual(model.TIERS, (FIX, CHECK, NOTE))

    def test_a_tool_run_counts_its_items_by_tier(self):
        run = ToolRun("leash", model.OK, items=[Item("leash", FIX, "a", "x"), Item("leash", FIX, "b", "y"), Item("leash", NOTE, "c", "z")])
        self.assertEqual((run.count(FIX), run.count(CHECK), run.count(NOTE)), (2, 0, 1))

    def test_two_runs_do_not_share_their_item_lists(self):
        a, b = ToolRun("a", model.OK), ToolRun("b", model.OK)
        a.items.append(Item("a", FIX, "x", "y"))
        self.assertEqual(b.items, [])


if __name__ == "__main__":
    unittest.main()
