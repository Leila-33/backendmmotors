from dataclasses import dataclass
from modules.applications.domain.enums import TradeInVehicleCondition

@dataclass
class ApplicationTradeIn:

    application_id: str

    brand: str

    model: str

    year: int

    mileage: int

    condition: TradeInVehicleCondition

    estimated_value: float