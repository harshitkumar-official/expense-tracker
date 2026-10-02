import unittest

import expenses


class ExpenseTests(unittest.TestCase):
    def setUp(self):
        self.conn = expenses.connect(":memory:")

    def test_add_and_list(self):
        i = expenses.add_expense(self.conn, 120.5, "Food", "lunch", "2026-09-03")
        rows = expenses.list_expenses(self.conn)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], i)
        self.assertEqual(rows[0]["category"], "food")

    def test_rejects_non_positive_amount(self):
        with self.assertRaises(Exception):
            expenses.add_expense(self.conn, -5, "food", day="2026-09-03")

    def test_rejects_bad_date(self):
        with self.assertRaises(ValueError):
            expenses.add_expense(self.conn, 5, "food", day="03-09-2026")

    def test_edit(self):
        i = expenses.add_expense(self.conn, 10, "food", day="2026-09-03")
        self.assertTrue(expenses.edit_expense(self.conn, i, amount=15, note="fixed"))
        row = expenses.list_expenses(self.conn)[0]
        self.assertEqual((row["amount"], row["note"]), (15, "fixed"))
        self.assertFalse(expenses.edit_expense(self.conn, 999, amount=1))

    def test_delete(self):
        i = expenses.add_expense(self.conn, 10, "food", day="2026-09-03")
        self.assertTrue(expenses.delete_expense(self.conn, i))
        self.assertFalse(expenses.delete_expense(self.conn, i))
        self.assertEqual(expenses.list_expenses(self.conn), [])

    def test_month_filter(self):
        expenses.add_expense(self.conn, 10, "food", day="2026-09-03")
        expenses.add_expense(self.conn, 20, "food", day="2026-10-01")
        self.assertEqual(len(expenses.list_expenses(self.conn, "2026-09")), 1)

    def test_monthly_summary_sorted_and_grouped(self):
        expenses.add_expense(self.conn, 100, "rent", day="2026-09-01")
        expenses.add_expense(self.conn, 30, "food", day="2026-09-02")
        expenses.add_expense(self.conn, 20, "food", day="2026-09-05")
        expenses.add_expense(self.conn, 999, "food", day="2026-10-05")
        summary = [(r["category"], r["total"]) for r in expenses.monthly_summary(self.conn, "2026-09")]
        self.assertEqual(summary, [("rent", 100.0), ("food", 50.0)])

    def test_cli_round_trip(self):
        import os, tempfile
        path = os.path.join(tempfile.mkdtemp(), "t.db")
        self.assertEqual(expenses.main(["--db", path, "add", "40", "travel", "--date", "2026-09-10"]), 0)
        self.assertEqual(expenses.main(["--db", path, "summary", "2026-09"]), 0)
        self.assertEqual(expenses.main(["--db", path, "add", "-3", "x"]), 1)


if __name__ == "__main__":
    unittest.main()
