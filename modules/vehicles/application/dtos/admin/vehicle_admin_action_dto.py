from dataclasses import dataclass


@dataclass(frozen=True)
class VehicleAdminActionDTO:
    vehicle_id: str
    admin_id: str