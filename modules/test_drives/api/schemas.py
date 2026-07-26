from pydantic import BaseModel
from datetime import datetime
from modules.test_drives.domain.enums import TestDriveStatus
from typing import Optional, List, Any

# CLIENT

# create test drive
class CreateTestDriveRequest(BaseModel):

    vehicle_id: str

    appointment_date: datetime

    comment: str | None = None


# get my test drives
class MyTestDriveResponse(BaseModel):

    id: str

    vehicle_id: str

    vehicle_name: str

    appointment_date: datetime

    status: TestDriveStatus

    comment: str | None = None

    created_at: datetime | None = None


# get test drive details client
class TestDriveVehicleResponse(BaseModel):

    id: str

    brand: str

    model: str

    images: list[str] = []


class TestDriveUserResponse(BaseModel):

    id: str

    name: str

    email: str


class TestDriveTimelineResponse(BaseModel):

    type: str

    message: str

    date: datetime

    metadata: Optional[dict[str, Any]] = None


class TestDriveDetailClientResponse(BaseModel):

    id: str

    vehicle: TestDriveVehicleResponse

    appointment_date: datetime

    status: TestDriveStatus

    comment: Optional[str] = None

    user: TestDriveUserResponse

    timeline: List[TestDriveTimelineResponse]

# get availability
class AvailabilityResponse(BaseModel):

    date: str

    timezone: str

    available_slots: list[datetime]


# testdrive response
class TestDriveResponse(BaseModel):

    id: str

    user_id: str

    vehicle_id: str

    appointment_date: datetime

    status: TestDriveStatus

    comment: str | None = None

    created_at: datetime | None = None

# ADMIN

# get test drive details admin
class TestDriveEventResponse(BaseModel):
    id: str
    type: str
    message: str
    created_at: datetime


class TestDriveDetailsAdminResponse(BaseModel):
    id: str

    # USER
    user_name: str
    user_email: str

    # VEHICLE
    vehicle_name: str
    vehicle_price: float
    vehicle_license_plate: str | None

    # APPOINTMENT
    appointment_date: datetime
    status: str
    comment: str | None

    # TIMELINE
    events: list[TestDriveEventResponse]


# get test drives admin
class TestDriveAdminListItemResponse(BaseModel):
    id: str
    user_name: str
    vehicle_name: str
    appointment_date: datetime
    status: str


class TestDriveAdminListResponse(BaseModel):
    items: list[TestDriveAdminListItemResponse]
    total: int
    page: int
    limit: int

# update test drive status
class UpdateTestDriveStatusRequest(BaseModel):

    status: TestDriveStatus

class TestDriveStatusResponse(BaseModel):

    id: str

    status: str

    appointment_date: datetime

    message: str

# pending count

class PendingTestDriveCountResponse(BaseModel):

    count: int