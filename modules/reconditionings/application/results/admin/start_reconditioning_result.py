from dataclasses import dataclass


@dataclass
class StartReconditioningResult:

    reconditioning_id: str
    vehicle_id: str
    status: str
    message: str