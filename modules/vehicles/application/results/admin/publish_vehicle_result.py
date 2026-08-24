from dataclasses import dataclass

@dataclass(frozen=True)
class PublishVehicleResult:
    vehicle_id: str
    status: str
    message: str