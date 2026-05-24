from pydantic import BaseModel
from datetime import datetime
from typing import List

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


from modules.core.enums import TestDriveStatus

class UpdateTestDriveStatusDTO(BaseModel):
    status: TestDriveStatus