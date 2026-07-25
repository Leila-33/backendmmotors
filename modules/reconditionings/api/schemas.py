from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
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



class ReconditioningResult(BaseModel):
    cost: float = Field(ge=0)
    duration_days: int = Field(ge=0)
    tasks: List[str] = Field(default_factory=list)

# start_reconditioning
class StartReconditioningResponse(BaseModel):

    reconditioning_id: str

    vehicle_id: str

    status: str

    message: str