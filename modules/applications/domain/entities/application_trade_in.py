from dataclasses import dataclass


@dataclass
class ApplicationTradeIn:

    brand: str

    model: str

    year: int

    mileage: int

    condition: str  # ex: excellent / good / average / poor

    estimated_value: int