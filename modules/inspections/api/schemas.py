from pydantic import BaseModel, Field
from datetime import datetime

# get inspection

class InspectionResponse(BaseModel):

    id: str
    vehicle_id: str

    status: str

    engine_score: int | None = None
    brakes_score: int | None = None
    tires_score: int | None = None
    electronics_score: int | None = None
    safety_score: int | None = None

    overall_score: int | None = None

    failures: list[str] = Field(
        default_factory=list
    )

    recommended_repairs: list[str] = Field(
        default_factory=list
    )

    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None


# start inspection

class StartInspectionResponse(BaseModel):

    inspection_id: str

    vehicle_id: str

    status: str

    message: str