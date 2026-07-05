from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class InspectionDTO(BaseModel):
    id: str
    vehicle_id: str

    status: str

    engine_score: int
    brakes_score: int
    tires_score: int
    electronics_score: int
    safety_score: int
    overall_score: int

    failures: Optional[List[str]] = []
    recommended_repairs: Optional[List[str]] = []

    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None