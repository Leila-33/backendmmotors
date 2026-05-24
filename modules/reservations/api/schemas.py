from pydantic import BaseModel, Field, model_validator
from datetime import date, datetime
from typing import Optional
from modules.core.enums import ReservationStatus


# =========================
# BASE
# =========================
class ReservationBase(BaseModel):
    vehicle_id: int = Field(..., description="ID du véhicule réservé")
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


# =========================
# CREATE
# =========================
class ReservationCreate(ReservationBase):
    user_id: Optional[int] = None


# =========================
# UPDATE
# =========================
class ReservationUpdate(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[ReservationStatus] = None

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValueError("start_date must be before end_date")
        return self


# =========================
# RESPONSE
# =========================
class ReservationResponse(BaseModel):
    id: int

    vehicle_id: int
    user_id: Optional[int]

    start_date: date
    end_date: date

    status: ReservationStatus

    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# =========================
# LIST RESPONSE
# =========================
class ReservationListResponse(BaseModel):
    items: list[ReservationResponse]
    total: int


# =========================
# CHECK
# =========================
class ReservationCheck(BaseModel):
    vehicle_id: str

    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_dates(self):

        today = date.today()

        # =========================
        # START >= TODAY
        # =========================
        if self.start_date < today:
            raise ValueError(
                "La date de début doit être aujourd'hui ou ultérieure"
            )

        # =========================
        # START <= END
        # =========================
        if self.start_date > self.end_date:
            raise ValueError(
                "La date de début doit être avant la date de fin"
            )

        return self