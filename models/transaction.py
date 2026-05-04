import uuid
from datetime import datetime
class Transaction:
    def __init__(self, amount: float, description: str, date: str = None):
        self.__id = str(uuid.uuid4())[:8]   
        self.__description = ""
        self.__amount = 0.0
        self.__date = ""
        self.set_description(description)
        self.set_amount(amount)
        if date is None:
            self.__date = datetime.today().strftime("%d/%m/%Y")
        else:
            self.set_date(date)
    def get_id(self):
        return self.__id

    def get_description(self):
        return self.__description

    def get_amount(self):
        return self.__amount

    def get_date(self):
        return self.__date
    def set_description(self, description: str):
        """Description must be a non-empty string."""
        if not isinstance(description, str) or description.strip() == "":
            raise ValueError("Description cannot be empty.")
        self.__description = description.strip()

    def set_amount(self, amount):
        """Amount must be a positive number."""
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ValueError("Amount must be a number.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        self.__amount = round(amount, 2)

    def set_date(self, date: str):
        """Date must be in DD/MM/YYYY format."""
        try:
            datetime.strptime(date, "%d/%m/%Y")
        except ValueError:
            raise ValueError("Date must be in DD/MM/YYYY format.")
        self.__date = date
    def display_details(self):
        """
        Returns a formatted string of this transaction's details.
        Subclasses will OVERRIDE this method to add extra fields.
        This is Polymorphism in action.
        """
        return (
            f"[ID: {self.__id}] "
            f"{self.__date} | "
            f"£{self.__amount:.2f} | "
            f"{self.__description}"
        )
    def to_dict(self):
        """
        Convert this object to a dictionary so it can be saved as JSON.
        Subclasses will override this and call super().to_dict() first.
        """
        return {
            "id": self.__id,
            "type": self.__class__.__name__,  
            "amount": self.__amount,
            "description": self.__description,
            "date": self.__date,
        }
    @classmethod
    def from_dict(cls, data: dict):
        """
        Recreate a Transaction object from a dictionary (loaded from JSON).
        """
        obj = cls.__new__(cls)  
        obj._Transaction__id = data["id"]
        obj._Transaction__amount = data["amount"]
        obj._Transaction__description = data["description"]
        obj._Transaction__date = data["date"]
        return obj