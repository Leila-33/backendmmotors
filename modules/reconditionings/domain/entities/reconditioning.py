from dataclasses import dataclass
from datetime import datetime
from modules.core.enums import ReconditioningStatus

@dataclass
class Reconditioning:
    id: str
    vehicle_id: str

    status: ReconditioningStatus

    cost: float
    duration_days: int

    tasks: list[str]

    started_at: datetime | None
    completed_at: datetime | None