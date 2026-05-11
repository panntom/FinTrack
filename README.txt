════════════════════════════════════════════════════════
  FinTrack — Personal Finance & Budget Forecaster
  CIS1703 Coursework 2 | Group [Your Group Name]
════════════════════════════════════════════════════════

GROUP MEMBERS
─────────────
  - Phan Duy [26749467] 
  - Ng Tr My Hoa [26749491]

HOW TO RUN
──────────
  Requirements: Python 3.8 or higher (Tkinter is included by default)

  1. Open a terminal / command prompt
  2. Navigate to this folder:
       cd path/to/FinTrack
  3. Run the application:
       python main.py

  No external libraries are required.
  All data is saved automatically to the ./data/ folder.

PROJECT STRUCTURE
─────────────────
  main.py               — Entry point
  models/
    transaction.py      — Base class (Abstraction, Encapsulation)
    income.py           — Income subclass (Inheritance, Polymorphism)
    expense.py          — Expense subclass (Inheritance, Polymorphism)
    recurring_bill.py   — RecurringBill subclass (Inheritance, Polymorphism)
  logic/
    finance_manager.py  — Data management and persistence (JSON)
    forecaster.py       — Smart 30-day forecasting logic
  ui/
    app.py              — Full Tkinter GUI application
  data/
    transactions.json   — Auto-created on first run (gitignored)
    budgets.json        — Auto-created on first run (gitignored)

FEATURES
────────
  ✓ Add Income, Expenses, and Recurring Bills
  ✓ View all transactions on the Dashboard
  ✓ Delete transactions
  ✓ Set budget limits per category with live progress bars
  ✓ Budget alerts when adding an expense over the limit
  ✓ 30-day financial forecast based on recurring bills
  ✓ Needs vs Wants spending breakdown
  ✓ Category spending histogram
  ✓ Data saved automatically between sessions (JSON persistence)
  ✓ Crash-proof: all inputs validated before processing

OOP DESIGN
──────────
  Inheritance:   Income, Expense, RecurringBill all inherit from Transaction
  Encapsulation: All class attributes are private (__attr) with getters/setters
  Polymorphism:  display_details() and to_dict() behave differently per subclass
  Abstraction:   Transaction hides ID generation and date handling from subclasses

GITHUB REPOSITORY
─────────────────
https://github.com/panntom/FinTrack.git