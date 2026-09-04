from pydantic import BaseModel
from datetime import datetime
from modules.reconditionings.domain.enums import ReconditioningStatus


class ReconditioningResponse(BaseModel):

    id: str

    vehicle_id: str

    status: ReconditioningStatus

    cost: float

    duration_days: int

    tasks: list[str]

    started_at: datetime | None = None

    completed_at: datetime | None = None



# =========================
# START RECONDITIONING
# =========================
class StartReconditioningResponse(BaseModel):

    reconditioning_id: str

    vehicle_id: str

    status: str

    message: str