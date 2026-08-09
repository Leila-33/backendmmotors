from modules.reservations.domain.entities.reservation import Reservation
from modules.reservations.domain.enums import ReservationStatus
from modules.vehicles.domain.exceptions import VehicleNotAvailable
from uuid import uuid4
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.reservations.api.schemas import CreateReservationDTO
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository
from core.database.unit_of_work import UnitOfWork
from modules.applications.domain.enums import EventType
from modules.applications.application.services.event_service import EventService
import logging

logger = logging.getLogger(__name__)

class CreateReservationUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        reservation_repository: ReservationRepository,
        event_service: EventService,
        unit_of_work: UnitOfWork,
    ):
        self.application_repository = application_repository
        self.reservation_repository = reservation_repository
        self.event_service = event_service
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

            self.event_service.log(
    type=EventType.RENTAL_CREATED,
    message="Réservation créée",
    user_id=application.user_id,
    vehicle_id=reservation.vehicle_id,
    application_id=application_id,
    event_metadata={
        "reservation_id": reservation.id,
        "start_date": reservation.start_date.isoformat(),
        "end_date": reservation.end_date.isoformat(),
        "status": reservation.status.value,
    }
)

            self.unit_of_work.commit()

            logger.info(
    "Réservation créée",
    extra={
        "reservation_id": reservation.id,
        "user_id": application.user_id,
        "vehicle_id": reservation.vehicle_id,
    }
)
            return reservation

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création réservation",
                extra={
                    "user_id": application.user_id,
                    "vehicle_id": reservation.vehicle_id,
                }
            )

            raise
