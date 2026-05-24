from dataclasses import dataclass

from modules.core.enums import (
    TradeInVehicleCondition
)


@dataclass
class TradeInInput:
    brand: str
    model: str
    year: int
    mileage: int

    condition: TradeInVehicleCondition