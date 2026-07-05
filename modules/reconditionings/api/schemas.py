from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from modules.core.enums import ReconditioningStatus


class ReconditioningDTO(BaseModel):
    id: str
    vehicle_id: str
    status: ReconditioningStatus

    cost: float
    duration_days: int

    tasks: List[str]

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None




class ReconditioningResult(BaseModel):
    cost: float = Field(ge=0)
    duration_days: int = Field(ge=0)
    tasks: List[str] = Field(default_factory=list)
