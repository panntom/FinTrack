from models.transaction import Transaction
from datetime import datetime, timedelta
class RecurringBill(Transaction):
    VALID_FREQUENCIES = ("weekly", "monthly", "yearly")
    def __init__(self, amount: float, description: str,
                 frequency: str, next_due_date: str, date: str = None):
        super().__init__(amount, description, date)
        self.__frequency = ""
        self.__next_due_date = ""
        self.set_frequency(frequency)
        self.set_next_due_date(next_due_date)
    def get_frequency(self):
        return self.__frequency
    def get_next_due_date(self):
        return self.__next_due_date
    def set_frequency(self, frequency: str):
        if frequency not in self.VALID_FREQUENCIES:
            raise ValueError(
                f"Frequency must be one of: {self.VALID_FREQUENCIES}"
            )
        self.__frequency = frequency
    def set_next_due_date(self, date_str: str):
        try:
            datetime.strptime(date_str, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Next due date must be in DD/MM/YYYY format.")
        self.__next_due_date = date_str
    def advance_due_date(self):
        current = datetime.strptime(self.__next_due_date, "%d/%m/%Y")
        if self.__frequency == "weekly":
            next_date = current + timedelta(days=7)
        elif self.__frequency == "monthly":
            next_date = current + timedelta(days=30)
        else:  # yearly
            next_date = current + timedelta(days=365)
        self.__next_due_date = next_date.strftime("%d/%m/%Y")
    def is_due_within_days(self, days: int) -> bool:   
        today = datetime.today()
        due = datetime.strptime(self.__next_due_date, "%d/%m/%Y")
        diff = (due - today).days
        return 0 <= diff <= days
    def display_details(self):
        """OVERRIDES Transaction.display_details()."""
        base = super().display_details()
        return (
            f"{base} | RECURRING | "
            f"Every {self.__frequency} | "
            f"Next due: {self.__next_due_date}"
        )
    def to_dict(self):
        data = super().to_dict()
        data["frequency"] = self.__frequency
        data["next_due_date"] = self.__next_due_date
        return data
    @classmethod
    def from_dict(cls, data: dict):
        obj = cls(
            amount=data["amount"],
            description=data["description"],
            frequency=data["frequency"],
            next_due_date=data["next_due_date"],
            date=data["date"]
        )
        obj._Transaction__id = data["id"]
        return obj