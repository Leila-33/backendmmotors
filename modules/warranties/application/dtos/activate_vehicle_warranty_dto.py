from dataclasses import dataclass


@dataclass(frozen=True)
class ActivateVehicleWarrantyDTO:
    vehicle_id: str
    user_id: str
    mileage: int | None = None