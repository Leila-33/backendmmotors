from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class FinalCheckResult:
    vehicle_id: str
    vehicle_status: str
    reconditioning_status: str
    final_check_at: datetime