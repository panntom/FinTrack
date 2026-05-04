

from models.transaction import Transaction


class Expense(Transaction):
    """
    Represents an expense — money spent.
    Inherits from Transaction and adds:
      - category: e.g. "Food", "Transport", "Entertainment"
      - importance: "Need" or "Want"
    """

    VALID_IMPORTANCE = ("Need", "Want")

    def __init__(self, amount: float, description: str,
                 category: str, importance: str, date: str = None):
        """
        Initialise an Expense transaction.

        Args:
            amount (float): How much was spent.
            description (str): Short description.
            category (str): e.g. "Food", "Rent", "Entertainment"
            importance (str): Must be "Need" or "Want"
            date (str): DD/MM/YYYY. Defaults to today.
        """
        super().__init__(amount, description, date)

        self.__category = ""
        self.__importance = ""

        self.set_category(category)
        self.set_importance(importance)


    def get_category(self):
        return self.__category

    def get_importance(self):
        return self.__importance

 

    def set_category(self, category: str):
        """Category must be a non-empty string."""
        if not isinstance(category, str) or category.strip() == "":
            raise ValueError("Category cannot be empty.")
        self.__category = category.strip().title()  # "food" → "Food"

    def set_importance(self, importance: str):
        """Importance must be exactly 'Need' or 'Want'."""
        if importance not in self.VALID_IMPORTANCE:
            raise ValueError(
                f"Importance must be one of: {self.VALID_IMPORTANCE}"
            )
        self.__importance = importance

    

    def display_details(self):
        """OVERRIDES Transaction.display_details()."""
        base = super().display_details()
        return (
            f"{base} | EXPENSE | "
            f"Category: {self.__category} | "
            f"{self.__importance}"
        )
    def to_dict(self):
        data = super().to_dict()
        data["category"] = self.__category
        data["importance"] = self.__importance
        return data

    @classmethod
    def from_dict(cls, data: dict):
        obj = cls(
            amount=data["amount"],
            description=data["description"],
            category=data["category"],
            importance=data["importance"],
            date=data["date"]
        )
        obj._Transaction__id = data["id"]
        return obj