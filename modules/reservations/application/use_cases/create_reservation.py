from modules.reservations.domain.entities.reservation import Reservation
from modules.reservations.domain.enums import ReservationStatus
from modules.vehicles.domain.exceptions import VehicleNotAvailable
from uuid import uuid4
from modules.applications.domain.exceptions import ApplicationNotFound
class CreateReservationUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, data, application_id: str):

        # =========================
        # CHECK AVAILABILITY
        # =========================
        if self.repo.exists_overlap(
            data.vehicle_id,
            data.start_date,
            data.end_date
        ):
            raise VehicleNotAvailable()
        
        if not application_id:
            raise ApplicationNotFound()
        # =========================
        # CREATE RESERVATION
        # =========================
        reservation = Reservation(
            id=str(uuid4()),
            vehicle_id=data.vehicle_id,
            application_id=application_id,
            start_date=data.start_date,
            end_date=data.end_date,
            status=ReservationStatus.ACTIVE
        )

        # =========================
        # SAVE
        # =========================
        return self.repo.create(reservation)
