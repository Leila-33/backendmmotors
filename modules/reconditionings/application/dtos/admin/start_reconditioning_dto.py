from dataclasses import dataclass


@dataclass
class StartReconditioningDTO:

    vehicle_id: str
    admin_id: str