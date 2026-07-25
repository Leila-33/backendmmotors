from dataclasses import dataclass

@dataclass
class QuoteTradeIn:
    quote_id: str

    brand: str
    model: str

    year: int
    mileage: int

    condition: str

    estimated_value: float

    def update(
        self,
        brand: str,
        model: str,
        year: int,
        mileage: int,
        condition: str,
        estimated_value: float,
    ):

        self.brand = brand

        self.model = model

        self.year = year

        self.mileage = mileage

        self.condition = condition

        self.estimated_value = estimated_value