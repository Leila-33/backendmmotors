from dataclasses import dataclass


@dataclass
class StartInspectionResult:
    inspection_id: str
    vehicle_id: str
    status: str
    message: str