from models.transaction import Transaction
class Income(Transaction):
    def __init__(self, amount: float, description: str,
                 source: str, is_taxable: bool = True, date: str = None):

        # Call parent __init__ first — this handles id, amount, desc, date
        super().__init__(amount, description, date)

        # Income-specific private attributes
        self.__source = ""
        self.__is_taxable = True

        # Use setters for validation
        self.set_source(source)
        self.set_is_taxable(is_taxable)


    def get_source(self):
        return self.__source

    def get_is_taxable(self):
        return self.__is_taxable

    

    def set_source(self, source: str):
        """Source must be a non-empty string."""
        if not isinstance(source, str) or source.strip() == "":
            raise ValueError("Source cannot be empty.")
        self.__source = source.strip()

    def set_is_taxable(self, is_taxable):
        """is_taxable must be True or False."""
        if not isinstance(is_taxable, bool):
            raise ValueError("is_taxable must be True or False.")
        self.__is_taxable = is_taxable

   
    def display_details(self):
        """
        OVERRIDES Transaction.display_details().
        Adds source and taxable status to the output.
        """
        base = super().display_details()   
        taxable_str = "Taxable" if self.__is_taxable else "Non-taxable"
        return f"{base} | INCOME | Source: {self.__source} | {taxable_str}"

    

    def to_dict(self):
        """Extends parent to_dict() with Income-specific fields."""
        data = super().to_dict()
        data["source"] = self.__source
        data["is_taxable"] = self.__is_taxable
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Recreate Income from a saved dictionary."""
        obj = cls(
            amount=data["amount"],
            description=data["description"],
            source=data["source"],
            is_taxable=data["is_taxable"],
            date=data["date"]
        )
        obj._Transaction__id = data["id"]   # Restore original ID
        return obj