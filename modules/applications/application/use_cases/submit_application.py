
from datetime import datetime, timezone
from uuid import uuid4
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.reservations.domain.enums import ReservationStatus
from modules.applications.api.schemas import SubmitApplicationDTO
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.applications.domain.repositories.event_repository import EventRepository
from modules.applications.domain.entities.event import Event
from modules.reservations.domain.repositories.reservation_repository import ReservationRepository
from modules.applications.domain.policies.submit_application_policy import SubmitApplicationPolicy
from core.database.unit_of_work import UnitOfWork
from modules.auth.domain.entities.user import User
from modules.applications.application.services.application_form_service import ApplicationFormService

class SubmitApplicationUseCase:

    def __init__(
        self,
        application_form_service: ApplicationFormService,
        application_repository: ApplicationRepository,
        reservation_repository: ReservationRepository,
        event_repository: EventRepository,
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

        self.event_repository = (
            event_repository
        )

        self.uow = uow


    def execute(
        self,
        dto: SubmitApplicationDTO,
        current_user: User,
    ):

        try:

            # =========================
            # SAVE FORM
            # =========================

            result = (
                self.application_form_service.save(
                    dto=dto,
                    current_user=current_user,
                )
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

            application.status = (
                ApplicationStatus.SUBMITTED
            )

            application.previous_status = (
                ApplicationStatus.DRAFT
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

            self.event_repository.save(
                Event(
                    id=str(uuid4()),
                    application_id=application.id,
                    user_id=current_user.id,
                    type=EventType.APPLICATION_SUBMITTED,
                    message="Dossier soumis.",
                    created_at=datetime.now(
                        timezone.utc
                    ),
                )
            )


            # =========================
            # COMMIT
            # =========================

            self.uow.commit()


            return application


        except Exception:

            self.uow.rollback()
            raise