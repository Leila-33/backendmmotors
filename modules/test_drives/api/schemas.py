from datetime import datetime, date as Date
from pydantic import BaseModel, Field, field_validator
from modules.test_drives.domain.enums import TestDriveStatus
from uuid import UUID


# =========================================================
# CLIENT — CREATE
# =========================================================

class CreateTestDriveRequest(BaseModel):

    vehicle_id: str

    appointment_date: datetime

    comment: str | None = None


# =========================================================
# CLIENT — MY TEST DRIVES
# =========================================================

class MyTestDriveResponse(BaseModel):

    id: str

    vehicle_id: str

    vehicle_name: str

    appointment_date: datetime

    status: TestDriveStatus

    comment: str | None = None

    created_at: datetime | None = None


# =========================================================
# CLIENT — AVAILABILITY
# =========================================================
class GetAvailabilityRequest(BaseModel):
    vehicle_id: str
    date: Date

    @field_validator("vehicle_id")
    @classmethod
    def validate_vehicle_id(cls, value: str) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "L'identifiant du véhicule est requis"
            )

        try:
            UUID(value)
        except ValueError:
            raise ValueError(
                "L'identifiant du véhicule est invalide"
            )

        return value

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: Date) -> Date:

        if value < Date.today():
            raise ValueError(
                "La date ne peut pas être dans le passé"
            )

        return value
    
class GetAvailabilityResponse(BaseModel):

    date: str

    timezone: str

    available_slots: list[datetime]


# =========================================================
# CLIENT — CREATE RESPONSE
# =========================================================

class TestDriveResponse(BaseModel):

    id: str

    user_id: str

    vehicle_id: str

    appointment_date: datetime

    status: TestDriveStatus

    comment: str | None = None

    created_at: datetime | None = None


# =========================================================
# SHARED — DETAIL
# =========================================================

class TestDriveUserResponse(BaseModel):

    id: str

    name: str

    email: str


class TestDriveVehicleResponse(BaseModel):

    id: str

    brand: str

    model: str

    images: list[str]

    price: float

    license_plate: str | None = None


class TestDriveTimelineItem(BaseModel):

    id: str

    type: str

    message: str

    date: datetime

    metadata: dict | None = None


class TestDriveDetailResponse(BaseModel):

    id: str

    appointment_date: datetime

    status: TestDriveStatus

    comment: str | None = None

    user: TestDriveUserResponse

    vehicle: TestDriveVehicleResponse

    timeline: list[TestDriveTimelineItem]


# =========================================================
# SHARED - STATUS
# =========================================================

class UpdateTestDriveStatusRequest(BaseModel):

    status: TestDriveStatus


class TestDriveStatusResponse(BaseModel):

    id: str

    status: TestDriveStatus

    appointment_date: datetime

    message: str



# =========================================================
# ADMIN — LIST QUERY
# =========================================================

class GetTestDrivesAdminQuery(BaseModel):

    status: TestDriveStatus | None = None

    search: str = ""

    page: int = Field(
        default=1,
        ge=1,
    )

    limit: int = Field(
        default=20,
        ge=1,
        le=100,
    )


# =========================================================
# ADMIN — LIST ITEM
# =========================================================

class TestDriveAdminItemResponse(BaseModel):

    id: str

    user_name: str

    vehicle_name: str

    appointment_date: datetime

    status: TestDriveStatus

    comment: str | None = None

# =========================================================
# ADMIN — PAGINATION
# =========================================================

class PaginatedTestDriveAdminResponse(BaseModel):

    items: list[TestDriveAdminItemResponse]

    page: int

    limit: int

    total: int
# =========================================================
# ADMIN - PENDING COUNT
# =========================================================

class PendingTestDriveCountResponse(BaseModel):

    count: int