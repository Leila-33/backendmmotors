from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from modules.inspections.domain.enums import InspectionStatus
from modules.inspections.domain.exceptions import InspectionCannotBeStarted

@dataclass
class Inspection:

    id: str

    vehicle_id: str


    # =========================
    # STATUS
    # =========================

    status: InspectionStatus


    # =========================
    # SCORES
    # =========================

    engine_score: int = 0

    brakes_score: int = 0

    tires_score: int = 0

    electronics_score: int = 0

    safety_score: int = 0


    overall_score: int = 0


    # =========================
    # RESULTS
    # =========================

    failures: list[str] = field(
        default_factory=list
    )

    recommended_repairs: list[str] = field(
        default_factory=list
    )


    # =========================
    # DATES
    # =========================

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None


    created_at: datetime = field(
        default_factory=lambda:
            datetime.now(timezone.utc)
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
    
    def start(self):

        if self.status != InspectionStatus.PENDING:
            raise InspectionCannotBeStarted()


        self.status = (
            InspectionStatus.IN_PROGRESS
        )

        self.started_at = (
            datetime.now(timezone.utc)
        )

    def complete(self, result):

        self.engine_score = result.engine_score
        self.brakes_score = result.brakes_score
        self.tires_score = result.tires_score
        self.electronics_score = result.electronics_score
        self.safety_score = result.safety_score

        self.failures = result.failures or []

        self.recommended_repairs = (
            result.recommended_repairs or []
        )

        self.overall_score = (
            sum([
                self.engine_score,
                self.brakes_score,
                self.tires_score,
                self.electronics_score,
                self.safety_score
            ])
            // 5
        )

        self.status = (
            InspectionStatus.COMPLETED
        )

        self.completed_at = (
            datetime.now(timezone.utc)
        )