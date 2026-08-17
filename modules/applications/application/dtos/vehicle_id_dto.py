from dataclasses import dataclass

@dataclass(frozen=True)
class VehicleIdDTO:
    vehicle_id: str