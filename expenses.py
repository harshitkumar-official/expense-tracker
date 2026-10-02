"""Expense tracker: SQLite storage + argparse CLI. Standard library only."""
import argparse
import sqlite3
import sys
from datetime import date

DB_DEFAULT = "expenses.db"


def connect(path=DB_DEFAULT):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """CREATE TABLE IF NOT EXISTS expenses (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               day TEXT NOT NULL,
               category TEXT NOT NULL,
               amount REAL NOT NULL CHECK (amount > 0),
               note TEXT DEFAULT ''
           )"""
    )
    return conn


def add_expense(conn, amount, category, note="", day=None):
    day = day or date.today().isoformat()
    date.fromisoformat(day)  # raises ValueError on a bad date
    cur = conn.execute(
        "INSERT INTO expenses (day, category, amount, note) VALUES (?, ?, ?, ?)",
        (day, category.strip().lower(), amount, note),
    )
    conn.commit()
    return cur.lastrowid


def edit_expense(conn, expense_id, amount=None, category=None, note=None):
    row = conn.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,)).fetchone()
    if row is None:
        return False
    conn.execute(
        "UPDATE expenses SET amount = ?, category = ?, note = ? WHERE id = ?",
        (
            amount if amount is not None else row["amount"],
            category.strip().lower() if category else row["category"],
            note if note is not None else row["note"],
            expense_id,
        ),
    )
    conn.commit()
    return True


def delete_expense(conn, expense_id):
    cur = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    return cur.rowcount == 1


def list_expenses(conn, month=None):
    if month:
        return conn.execute(
            "SELECT * FROM expenses WHERE substr(day, 1, 7) = ? ORDER BY day, id", (month,)
        ).fetchall()
    return conn.execute("SELECT * FROM expenses ORDER BY day, id").fetchall()


def monthly_summary(conn, month):
    """Total per category for a month (YYYY-MM), largest first."""
    return conn.execute(
        """SELECT category, ROUND(SUM(amount), 2) AS total
           FROM expenses WHERE substr(day, 1, 7) = ?
           GROUP BY category ORDER BY total DESC""",
        (month,),
    ).fetchall()


def build_parser():
    p = argparse.ArgumentParser(description="Simple expense tracker")
    p.add_argument("--db", default=DB_DEFAULT)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("amount", type=float)
    a.add_argument("category")
    a.add_argument("--note", default="")
    a.add_argument("--date", default=None, help="YYYY-MM-DD (default: today)")

    e = sub.add_parser("edit")
    e.add_argument("id", type=int)
    e.add_argument("--amount", type=float)
    e.add_argument("--category")
    e.add_argument("--note")

    d = sub.add_parser("delete")
    d.add_argument("id", type=int)

    l = sub.add_parser("list")
    l.add_argument("--month", help="YYYY-MM")

    s = sub.add_parser("summary")
    s.add_argument("month", help="YYYY-MM")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    conn = connect(args.db)
    try:
        if args.cmd == "add":
            print("Added expense", add_expense(conn, args.amount, args.category, args.note, args.date))
        elif args.cmd == "edit":
            print("Updated." if edit_expense(conn, args.id, args.amount, args.category, args.note) else "No such id.")
        elif args.cmd == "delete":
            print("Deleted." if delete_expense(conn, args.id) else "No such id.")
        elif args.cmd == "list":
            for r in list_expenses(conn, args.month):
                print(f"{r['id']:>3}  {r['day']}  {r['category']:<12} {r['amount']:>9.2f}  {r['note']}")
        elif args.cmd == "summary":
            rows = monthly_summary(conn, args.month)
            for r in rows:
                print(f"{r['category']:<12} {r['total']:>9.2f}")
            print(f"{'TOTAL':<12} {sum(r['total'] for r in rows):>9.2f}")
    except (ValueError, sqlite3.IntegrityError) as err:
        print("Error:", err)
        return 1
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
