import logging

from core.database.unit_of_work import UnitOfWork

from modules.applications.application.services.application_form_service import (
    ApplicationFormService,
)
from modules.applications.application.services.event_service import (
    EventService,
)

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.applications.domain.policies.submit_application_policy import (
    SubmitApplicationPolicy,
)
from modules.applications.domain.repositories.application_repository import (
    ApplicationRepository,
)
from modules.applications.application.dtos.submit_application_dto import (
    SubmitApplicationDTO,
)

from modules.reservations.domain.enums import (
    ReservationStatus,
)
from modules.reservations.domain.repositories.reservation_repository import (
    ReservationRepository,
)


logger = logging.getLogger(__name__)

class SubmitApplicationUseCase:

    def __init__(
        self,
        application_form_service: ApplicationFormService,
        application_repository: ApplicationRepository,
        reservation_repository: ReservationRepository,
        event_service: EventService,
        uow: UnitOfWork,
    ):
        self.application_form_service = (
            application_form_service
        )

        self.application_repository = (
            application_repository
        )

        self.reservation_repository = (
            reservation_repository
        )

        self.event_service = (
            event_service
        )

        self.uow = uow


    def execute(
        self,
        dto: SubmitApplicationDTO,
        current_user_id: str,
    ):

        application = None

        try:

            # =========================
            # SAVE FORM
            # =========================

            result = self.application_form_service.save(
                dto=dto,
                current_user_id=current_user_id,
            )

            application = result.application

            # =========================
            # VALIDATE BEFORE SUBMIT
            # =========================

            SubmitApplicationPolicy.validate(
                application
            )

            # =========================
            # STATUS
            # =========================

            application.previous_status = (
                application.status
            )

            application.status = (
                ApplicationStatus.SUBMITTED
            )

            self.application_repository.update(
                application
            )

            # =========================
            # RESERVATION
            # =========================

            if application.reservation:

                application.reservation.status = (
                    ReservationStatus.PENDING
                )

                self.reservation_repository.update(
                    application.reservation
                )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                application_id=application.id,
                user_id=current_user_id,
                vehicle_id=application.vehicle_id,
                type=EventType.APPLICATION_SUBMITTED,
                message="Dossier soumis.",
            )

            # =========================
            # COMMIT
            # =========================

            self.uow.commit()

            # =========================
            # LOG
            # =========================

            logger.info(
                "Application soumise",
                extra={
                    "application_id": application.id,
                    "user_id": current_user_id,
                    "vehicle_id": application.vehicle_id,
                    "status": application.status.value,
                },
            )

            return application

        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur soumission application",
                extra={
                    "application_id": (
                        application.id
                        if application
                        else None
                    ),
                    "user_id": current_user_id,
                },
            )

            raise