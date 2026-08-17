from pydantic import BaseModel, model_validator
from datetime import date, datetime
from modules.reservations.domain.enums import ReservationStatus

from datetime import date

# =========================
# CHECK
# =========================
class CheckAvailabilityRequest(BaseModel):
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


class CheckAvailabilityResponse(BaseModel):

    available: bool

# reservation response

class ReservationResponse(BaseModel):

    id: str

    vehicle_id: str

    application_id: str | None

    start_date: date

    end_date: date

    status: ReservationStatus

    created_at: datetime

    updated_at: datetime | None = None

    class Config:
        from_attributes = True
