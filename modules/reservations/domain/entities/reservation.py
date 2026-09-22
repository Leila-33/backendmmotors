from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from modules.reservations.domain.enums import ReservationStatus
from modules.reservations.domain.exceptions import (
    InvalidReservationDates,
)

@dataclass
class Reservation:

    id: str

    vehicle_id: str

    application_id: str

    start_date: date
    end_date: date

    status: ReservationStatus = ReservationStatus.ACTIVE

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """
        Validation structurelle de l'entité.

        Cette validation est appliquée lors de la création
        et lors de la reconstruction depuis la base de données.
        """

        if self.start_date > self.end_date:

            raise InvalidReservationDates(
                "La date de début doit être antérieure "
                "ou égale à la date de fin."
            )

    def validate_for_creation(self):
        """
        Vérifie les règles métier applicables
        à une nouvelle réservation.
        """

        today = date.today()

        if self.start_date < today:

            raise InvalidReservationDates(
                "La date de début doit être supérieure "
                "ou égale à aujourd'hui."
            )

        if self.end_date < today:

            raise InvalidReservationDates(
                "La date de fin doit être supérieure "
                "ou égale à aujourd'hui."
            )