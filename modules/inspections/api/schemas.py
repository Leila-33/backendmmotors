from pydantic import BaseModel
from datetime import datetime
from pydantic import Field

# get inspection
class InspectionResponse(BaseModel):

    id: str

    vehicle_id: str

    status: str


    engine_score: int

    brakes_score: int

    tires_score: int

    electronics_score: int

    safety_score: int


    overall_score: int

    failures: list[str] = Field(default_factory=list)

    recommended_repairs: list[str] = Field(default_factory=list)


    started_at: datetime | None = None

    completed_at: datetime | None = None

    created_at: datetime | None = None


# start inspection

class StartInspectionResponse(BaseModel):

    inspection_id: str

    vehicle_id: str

    status: str

    message: str