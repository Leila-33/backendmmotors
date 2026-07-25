from dataclasses import dataclass, field
from datetime import datetime, timezone
from modules.reconditionings.domain.enums import ReconditioningStatus
from modules.reconditionings.domain.exceptions import (
    ReconditioningCannotStart,
    ReconditioningCannotComplete,
    ReconditioningCannotBeApproved
)
@dataclass
class Reconditioning:

    id: str
    vehicle_id: str

    status: ReconditioningStatus

    cost: float = 0
    duration_days: int = 0

    tasks: list[str] = field(
        default_factory=list
    )

    started_at: datetime | None = None
    completed_at: datetime | None = None

    @classmethod
    def create(
        cls,
        id: str,
        vehicle_id: str,
    ):

        return cls(
            id=id,
            vehicle_id=vehicle_id,
            status=ReconditioningStatus.PENDING,
            started_at=datetime.now(timezone.utc),
        )
    
    def start(self):

        if self.status != ReconditioningStatus.PENDING:
            raise ReconditioningCannotStart()

        self.status = ReconditioningStatus.IN_PROGRESS

    def apply_result(
    self,
    cost: float,
    duration_days: int,
    tasks: list[str],
):

        self.cost = cost
        self.duration_days = duration_days
        self.tasks = tasks

    def complete(self):

        if self.status != ReconditioningStatus.IN_PROGRESS:
            raise ReconditioningCannotComplete()

        self.status = ReconditioningStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)

    def approve(self):

        if self.status != ReconditioningStatus.COMPLETED:
            raise ReconditioningCannotBeApproved()

        self.status = ReconditioningStatus.APPROVED
