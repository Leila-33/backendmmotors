from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class DeleteVehicleResult:
    vehicle_id: str
    action: Literal["ARCHIVED", "DELETED"]