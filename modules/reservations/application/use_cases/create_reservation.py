from modules.reservations.domain.entities.reservation import Reservation
from modules.reservations.domain.enums import ReservationStatus
from modules.vehicles.domain.exceptions import VehicleNotAvailable
from uuid import uuid4
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.reservations.api.schemas import CreateReservationDTO
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository
from core.database.unit_of_work import UnitOfWork

class CreateReservationUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        reservation_repository: ReservationRepository,
        unit_of_work: UnitOfWork,
    ):
        self.application_repository = application_repository
        self.reservation_repository = reservation_repository
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: CreateReservationDTO,
        application_id: str,
    ) -> Reservation:

        try:

            # =========================
            # APPLICATION
            # =========================
            application = (
                self.application_repository.get_by_id(
                    application_id
                )
            )

            if application is None:
                raise ApplicationNotFound()

            # =========================
            # VEHICLE AVAILABILITY
            # =========================
            if self.reservation_repository.exists_overlap(
                vehicle_id=application.vehicle_id,
                start_date=dto.start_date,
                end_date=dto.end_date,
            ):
                raise VehicleNotAvailable()

            # =========================
            # CREATE RESERVATION
            # =========================
            reservation = Reservation(
                id=str(uuid4()),
                application_id=application.id,
                vehicle_id=application.vehicle_id,
                start_date=dto.start_date,
                end_date=dto.end_date,
                status=ReservationStatus.ACTIVE,
            )

            reservation = self.reservation_repository.create(
                reservation
            )

            self.unit_of_work.commit()

            return reservation

        except Exception:
            self.unit_of_work.rollback()
            raise
