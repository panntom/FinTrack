import json
import os
from models.transaction import Transaction
from models.income import Income
from models.expense import Expense
from models.recurring_bill import RecurringBill
DATA_FILE = "./data/transactions.json"
BUDGET_FILE = "./data/budgets.json"
class FinanceManager:
    def __init__(self):
        self.__transactions = []
        self.__budgets = {}
        os.makedirs("./data", exist_ok=True)
        self.load_transactions()
        self.load_budgets()
    def add_transaction(self, transaction: Transaction):
        if not isinstance(transaction, Transaction):
            raise TypeError("Must be a Transaction object.")
        self.__transactions.append(transaction)
        self.save_transactions()
    def get_all_transactions(self):
        return list(self.__transactions)
    def get_by_type(self, transaction_type):
        return [t for t in self.__transactions
                if isinstance(t, transaction_type)]
    def get_by_category(self, category: str):
        return [t for t in self.__transactions
                if isinstance(t, Expense)
                and t.get_category().lower() == category.lower()]
    def delete_transaction(self, transaction_id: str):
        original_count = len(self.__transactions)
        self.__transactions = [
            t for t in self.__transactions
            if t.get_id() != transaction_id
        ]
        if len(self.__transactions) < original_count:
            self.save_transactions()
            return True
        return False
    def get_total_income(self) -> float:
        """Sum of all Income transaction amounts."""
        return sum(t.get_amount() for t in self.get_by_type(Income))
    def get_total_expenses(self) -> float:
        """Sum of all Expense transaction amounts."""
        return sum(t.get_amount() for t in self.get_by_type(Expense))
    def get_current_balance(self) -> float:
        """Current balance = total income minus total expenses."""
        return round(self.get_total_income() - self.get_total_expenses(), 2)
    def set_budget(self, category: str, limit: float):
        """Set a spending limit for a category."""
        try:
            limit = float(limit)
        except (TypeError, ValueError):
            raise ValueError("Budget limit must be a number.")
        if limit <= 0:
            raise ValueError("Budget limit must be greater than zero.")
        self.__budgets[category.title()] = round(limit, 2)
        self.save_budgets()
    def get_budgets(self):
        return dict(self.__budgets)
    def get_spent_in_category(self, category: str) -> float:
        return round(
            sum(t.get_amount() for t in self.get_by_category(category)), 2
        )

    def check_budget_alert(self, category: str) -> dict:
        category = category.title()
        spent = self.get_spent_in_category(category)

        if category not in self.__budgets:
            return {"has_budget": False, "spent": spent}

        limit = self.__budgets[category]
        remaining = round(limit - spent, 2)
        percent = round((spent / limit) * 100, 1) if limit > 0 else 0

        return {
            "has_budget": True,
            "limit": limit,
            "spent": spent,
            "remaining": remaining,
            "over_budget": spent > limit,
            "percent_used": percent,
        }
    def get_needs_vs_wants(self) -> dict:
        needs = sum(
            t.get_amount() for t in self.get_by_type(Expense)
            if t.get_importance() == "Need"
        )
        wants = sum(
            t.get_amount() for t in self.get_by_type(Expense)
            if t.get_importance() == "Want"
        )
        total = needs + wants
        return {
            "needs": round(needs, 2),
            "wants": round(wants, 2),
            "total": round(total, 2),
        }

    def get_spending_by_category(self) -> dict:
        result = {}
        for t in self.get_by_type(Expense):
            cat = t.get_category()
            result[cat] = round(result.get(cat, 0) + t.get_amount(), 2)
        return result
    def save_transactions(self):
        data = [t.to_dict() for t in self.__transactions]
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except IOError as e:
            raise IOError(f"Could not save transactions: {e}")

    def load_transactions(self):
        if not os.path.exists(DATA_FILE):
            
            self.__transactions = []
            return

        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            # File is corrupted or unreadable
            print("[WARNING] Transaction file is corrupted. Starting fresh.")
            self.__transactions = []
            return

        self.__transactions = []
        for item in data:
            try:
                t_type = item.get("type", "")
                if t_type == "Income":
                    self.__transactions.append(Income.from_dict(item))
                elif t_type == "Expense":
                    self.__transactions.append(Expense.from_dict(item))
                elif t_type == "RecurringBill":
                    self.__transactions.append(RecurringBill.from_dict(item))
            except (KeyError, ValueError):
                # Skip corrupted individual records
                continue

    def save_budgets(self):
        try:
            with open(BUDGET_FILE, "w") as f:
                json.dump(self.__budgets, f, indent=2)
        except IOError as e:
            raise IOError(f"Could not save budgets: {e}")

    def load_budgets(self):
        if not os.path.exists(BUDGET_FILE):
            self.__budgets = {}
            return
        try:
            with open(BUDGET_FILE, "r") as f:
                self.__budgets = json.load(f)
        except (json.JSONDecodeError, IOError):
            print("[WARNING] Budget file is corrupted. Starting fresh.")
            self.__budgets = {}