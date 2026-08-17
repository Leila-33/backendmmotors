from dataclasses import dataclass
from datetime import datetime

from modules.inspections.domain.enums import InspectionStatus


@dataclass
class InspectionResult:
    id: str
    vehicle_id: str
    status: InspectionStatus

    engine_score: float | None
    brakes_score: float | None
    tires_score: float | None
    electronics_score: float | None
    safety_score: float | None

    overall_score: float | None

    failures: list[str]
    recommended_repairs: list[str]

    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime