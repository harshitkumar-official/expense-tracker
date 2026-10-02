# Expense Tracker (Python + SQLite)

Command-line expense tracker using the standard library only (`sqlite3`, `argparse`).

## Features
- add, edit, delete and list expenses; filter by month
- monthly summary: total per category, largest first
- input validation (positive amounts, valid dates) enforced in code and by a SQL `CHECK` constraint
- 8 automated tests

## Run
Needs Python 3.9+.
```
python expenses.py add 250 food --note lunch --date 2026-09-03
python expenses.py add 900 rent --date 2026-09-01
python expenses.py list --month 2026-09
python expenses.py summary 2026-09
python expenses.py edit 1 --amount 275
python expenses.py delete 2
python -m unittest -v
```

## Design notes
- All SQL uses `?` placeholders, which prevents SQL injection.
- Tests run against an in-memory database (`:memory:`) so they never touch real data.
- Next steps: CSV export, budgets per category.
