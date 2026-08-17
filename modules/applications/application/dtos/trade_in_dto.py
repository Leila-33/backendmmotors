from dataclasses import dataclass
from modules.applications.domain.enums import TradeInVehicleCondition

@dataclass
class TradeInDTO:
    enabled: bool
    brand: str | None
    model: str | None
    year: int | None
    mileage: int | None
    condition: TradeInVehicleCondition