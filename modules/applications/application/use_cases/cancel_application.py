from uuid import uuid4
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.payments.domain.enums import SubscriptionStatus
from modules.applications.domain.entities.event import Event
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.applications.domain.policies.cancel_application_policy import CancelApplicationPolicy
from modules.auth.domain.enums import UserRole
from modules.applications.domain.repositories.application_repository import ApplicationRepository
from modules.applications.application.services.event_service import EventService
from modules.reservations.application.use_cases.cancel_reservation import CancelReservationUseCase
from modules.financing.domain.repositories.financing_contract_repository import FinancingContractRepository
from modules.applications.domain.entities.application import Application
from core.database.unit_of_work import UnitOfWork


class CancelApplicationUseCase:

    def __init__(
        self,
        application_repository: ApplicationRepository,
        financing_contract_repository: FinancingContractRepository,
        event_service: EventService,
        cancel_reservation_uc: CancelReservationUseCase,
        unit_of_work: UnitOfWork,
    ):
        self.application_repository = application_repository
        self.financing_contract_repository = financing_contract_repository
        self.event_service = event_service
        self.cancel_reservation_uc = cancel_reservation_uc
        self.unit_of_work = unit_of_work

    def execute(
        self,
        application_id: str,
        role: str,
        user_id: str,
    ) -> Application:

        try:

            # =========================
            # LOAD
            # =========================
            application = self.application_repository.get_by_id(
                application_id
            )

            if application is None:
                raise ApplicationNotFound()

            # =========================
            # POLICY
            # =========================
            CancelApplicationPolicy.validate(
                application=application
            )

            # =========================
            # CANCEL FINANCING CONTRACT
            # =========================
            contract = application.financing_contract

            if contract is not None:

                contract.subscription_status = (
                    SubscriptionStatus.CANCELLED
                )

                self.financing_contract_repository.update(
                    contract
                )

            # =========================
            # CANCEL RESERVATION
            # =========================
            if application.reservation is not None:

                self.cancel_reservation_uc.execute(
                    reservation_id=application.reservation.id,
                    role=role,
                    user_id=user_id,
                )

            # =========================
            # CANCEL APPLICATION
            # =========================
            application.previous_status = application.status
            application.status = ApplicationStatus.CANCELLED

            self.application_repository.update(
                application
            )

            # =========================
            # EVENT
            # =========================
            self.event_service.log(
                    application_id=application.id,
                    user_id=user_id,
                    type=EventType.APPLICATION_CANCELLED,
                    message=(
                        "Dossier annulé par "
                        f"{'administrateur' if role == UserRole.ADMIN else 'client'}."
                    ),
                    event_metadata={
                        "role": role,
                    },
                )

            # =========================
            # COMMIT
            # =========================
            self.unit_of_work.commit()

            return application

        except Exception:
            self.unit_of_work.rollback()
            raise