from datetime import datetime, timedelta
from models.recurring_bill import RecurringBill


class Forecaster:

    def __init__(self, finance_manager):

        self.__manager = finance_manager

    def forecast_30_days(self) -> dict:
        current_balance = self.__manager.get_current_balance()
        running_balance = current_balance
        events = []
        today = datetime.today()

        # Get all RecurringBill objects
        recurring_bills = self.__manager.get_by_type(RecurringBill)

        # Check each bill for the next 30 days
        for bill in recurring_bills:
            due_str = bill.get_next_due_date()
            due_date = datetime.strptime(due_str, "%d/%m/%Y")
            diff_days = (due_date - today).days

            if 0 <= diff_days <= 30:
                running_balance -= bill.get_amount()
                running_balance = round(running_balance, 2)
                events.append({
                    "date": due_str,
                    "days_away": diff_days,
                    "description": bill.get_description(),
                    "amount": -bill.get_amount(),      # negative = outgoing
                    "balance_after": running_balance,
                })

        # Sort events by date (soonest first)
        events.sort(key=lambda e: datetime.strptime(e["date"], "%d/%m/%Y"))

        return {
            "current_balance": current_balance,
            "projected_balance": running_balance,
            "events": events,
            "warning": running_balance < 0,
            "warning_low": 0 <= running_balance < 50,  # Low balance warning
        }

    def get_upcoming_bills(self, days: int = 7) -> list:
        bills = self.__manager.get_by_type(RecurringBill)
        upcoming = []
        for bill in bills:
            if bill.is_due_within_days(days):
                upcoming.append(bill)
        return upcoming

    def get_monthly_summary(self) -> dict:
        from models.income import Income
        from models.expense import Expense

        total_income = self.__manager.get_total_income()
        total_expenses = self.__manager.get_total_expenses()

        # Get distinct months that appear in transactions
        all_tx = self.__manager.get_all_transactions()
        months = set()
        for t in all_tx:
            date_str = t.get_date()
            month_key = date_str[3:]   # "DD/MM/YYYY" → "MM/YYYY"
            months.add(month_key)

        num_months = max(len(months), 1)   # Avoid division by zero

        avg_income = round(total_income / num_months, 2)
        avg_expenses = round(total_expenses / num_months, 2)

        return {
            "avg_monthly_income": avg_income,
            "avg_monthly_expenses": avg_expenses,
            "monthly_surplus": round(avg_income - avg_expenses, 2),
        }