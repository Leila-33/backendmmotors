from dataclasses import dataclass


@dataclass(frozen=True)
class TradeInEstimateDTO:
    brand: str
    model: str
    year: int
    mileage: int
    condition: str