from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from modules.core.enums import InspectionStatus

@dataclass
class Inspection:
    id: str
    vehicle_id: str

    status: InspectionStatus

    engine_score: int = 0
    brakes_score: int = 0
    tires_score: int = 0
    electronics_score: int = 0
    safety_score: int = 0

    overall_score: int = 0

    failures: list[str] | None = None
    recommended_repairs: list[str] | None = None

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # =========================
    # FACTORY
    # =========================
    @staticmethod
    def create(id: str, vehicle_id: str) -> "Inspection":
        return Inspection(
            id=id,
            vehicle_id=vehicle_id,
            status=InspectionStatus.PENDING,
            engine_score=0,
            brakes_score=0,
            tires_score=0,
            electronics_score=0,
            safety_score=0,
            overall_score=0,
            failures=[],
            recommended_repairs=[],
            started_at=None,
            completed_at=None,
        )