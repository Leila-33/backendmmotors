from dataclasses import dataclass


@dataclass(frozen=True)
class ActivateVehicleWarrantyDTO:

    vehicle_id: str
    mileage: int
    user_id: str