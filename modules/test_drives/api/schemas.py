from pydantic import BaseModel
from datetime import datetime
from modules.test_drives.domain.enums import TestDriveStatus
from typing import Optional, List

class CreateTestDriveDTO(BaseModel):

    vehicle_id: str

    appointment_date: datetime

    comment: str | None = None




class TestDriveAdminDTO(BaseModel):

    id: str

    user_id: str
    user_name: str

    vehicle_id: str
    vehicle_name: str

    appointment_date: datetime

    status: str

    comment: str | None = None

    created_at: datetime


class UpdateTestDriveStatusDTO(BaseModel):
    status: TestDriveStatus





class TestDriveUserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str


class TestDriveVehicleResponse(BaseModel):
    id: str
    brand: str
    model: str
    year: int
    images: list[str]


class TestDriveEventResponse(BaseModel):
    id: str
    type: str
    message: str
    created_at: datetime


class TestDriveFullResponse(BaseModel):

    id: str

    user: Optional[TestDriveUserResponse]

    vehicle: Optional[TestDriveVehicleResponse]

    appointment_date: datetime

    status: TestDriveStatus

    comment: Optional[str]

    events: List[TestDriveEventResponse]

    created_at: datetime