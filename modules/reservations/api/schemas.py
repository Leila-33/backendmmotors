from pydantic import BaseModel, model_validator
from datetime import date
from modules.reservations.domain.enums import ReservationStatus



class CreateReservationDTO(BaseModel):

    vehicle_id: str
    application_id: str

    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date must be before end_date")
        return self


class CancelReservationDTO(BaseModel):
    reservation_id: str



class ReservationResponseDTO(BaseModel):

    id: str
    status: str
    message: str



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