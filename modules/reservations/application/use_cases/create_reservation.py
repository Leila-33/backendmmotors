import logging
from uuid import uuid4

from modules.reservations.domain.entities.reservation import (
    Reservation,
)

from modules.reservations.domain.enums import (
    ReservationStatus,
)

from modules.reservations.domain.repositories.reservation_repository import (
    ReservationRepository,
)

from modules.vehicles.domain.exceptions import (
    VehicleNotAvailable,
)

from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)

from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository,
)

from modules.applications.domain.enums import (
    EventType,
)

from modules.applications.application.services.event_service import (
    EventService,
)

from modules.reservations.application.dtos.create_reservation_dto import (
    CreateReservationDTO,
)

from core.database.unit_of_work import UnitOfWork


logger = logging.getLogger(__name__)


class CreateReservationUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        reservation_repository: ReservationRepository,
        event_service: EventService,
        unit_of_work: UnitOfWork,
    ):
        self.application_repository = (
            application_repository
        )

        self.reservation_repository = (
            reservation_repository
        )

        self.event_service = event_service

        self.unit_of_work = unit_of_work

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        dto: CreateReservationDTO,
    ) -> Reservation:

        try:

            # =================================================
            # APPLICATION
            # =================================================

            application = (
                self.application_repository
                .get_by_id(
                    dto.application_id
                )
            )

            if application is None:
                raise ApplicationNotFound()

            # =================================================
            # VEHICLE AVAILABILITY
            # =================================================

            overlapping = (
                self.reservation_repository
                .exists_overlap(
                    vehicle_id=application.vehicle_id,
                    start_date=dto.start_date,
                    end_date=dto.end_date,
                )
            )

            if overlapping:
                raise VehicleNotAvailable()

            # =================================================
            # CREATE RESERVATION
            # =================================================

            reservation = Reservation(

                id=str(uuid4()),

                application_id=application.id,

                vehicle_id=application.vehicle_id,

                start_date=dto.start_date,

                end_date=dto.end_date,

                status=ReservationStatus.ACTIVE,
            )
            reservation.validate_for_creation()

            # =================================================
            # PERSIST
            # =================================================

            reservation = (
                self.reservation_repository
                .create(
                    reservation
                )
            )

            # =================================================
            # EVENT
            # =================================================

            self.event_service.log(

                type=EventType.RENTAL_CREATED,

                message="Réservation créée",

                user_id=application.user_id,

                vehicle_id=reservation.vehicle_id,

                application_id=application.id,

                event_metadata={
                    "reservation_id": reservation.id,
                    "start_date": (
                        reservation.start_date.isoformat()
                    ),
                    "end_date": (
                        reservation.end_date.isoformat()
                    ),
                    "status": (
                        reservation.status.value
                    ),
                },
            )

            # =================================================
            # COMMIT
            # =================================================

            self.unit_of_work.commit()

            # =================================================
            # SUCCESS LOG
            # =================================================

            logger.info(
                "Réservation créée",
                extra={
                    "reservation_id": reservation.id,
                    "application_id": application.id,
                    "user_id": application.user_id,
                    "vehicle_id": reservation.vehicle_id,
                },
            )

            return reservation

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création réservation",
                extra={
                    "application_id": dto.application_id,
                },
            )

            raise