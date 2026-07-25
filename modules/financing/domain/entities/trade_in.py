from dataclasses import dataclass

from modules.applications.domain.enums import TradeInVehicleCondition


@dataclass
class TradeInInput:
    brand: str
    model: str
    year: int
    mileage: int

    condition: TradeInVehicleCondition