from uuid import uuid4
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.payments.domain.enums import SubscriptionStatus
from modules.applications.domain.entities.event import Event
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.applications.domain.policies.cancel_application_policy import CancelApplicationPolicy


class CancelApplicationUseCase:

    def __init__(
        self,
        application_repository,
        reservation_repository,
        financing_contract_repository,
        event_repository,
        cancel_reservation_uc
    ):
        self.application_repository = application_repository
        self.reservation_repository = reservation_repository
        self.financing_contract_repository = financing_contract_repository
        self.event_repository = event_repository
        self.cancel_reservation_uc=cancel_reservation_uc

    def execute(
        self,
        application_id: str,
        role: str,
        user_id
    ):

        application = self.application_repository.get_by_id(
            application_id
        )

        if not application:
            raise ApplicationNotFound()

        # =========================
        # POLICY VALIDATION (IMPORTANT)
        # =========================
        CancelApplicationPolicy.validate(
            application,
            role
        )

        # =========================
        # ALREADY CANCELLED (OPTIONAL SAFE GUARD)
        # =========================
        if application.status == ApplicationStatus.CANCELLED:
            return application

        # =========================
        # CANCEL FINANCING CONTRACT (ADMIN ONLY via policy)
        # =========================
        contract = application.financing_contract

        if contract:

            contract.subscription_status = (
                SubscriptionStatus.CANCELLED
            )

            self.financing_contract_repository.update(
                contract
            )

        # =========================
        # CANCEL RESERVATION
        # =========================
        if application.reservation:

            self.cancel_reservation_uc.execute(
                reservation_id=application.reservation.id,
                role=role,
                user_id=user_id
            )

        # =========================
        # CANCEL APPLICATION
        # =========================
        application.previous_status = application.status

        application.status = ApplicationStatus.CANCELLED

        self.application_repository.update(application)

        # =========================
        # EVENT
        # =========================
        self.event_repository.save(
            Event(
                id=str(uuid4()),
                application_id=application.id,
                user_id=application.user_id,
                type=EventType.APPLICATION_CANCELLED,
                message=(
                    "Dossier annulé par "
                    f"{'administrateur' if role == 'admin' else 'client'}."
                ),
                event_metadata={
                    "role": role
                }
            )
        )

        # =========================
        # COMMIT
        # =========================
        self.application_repository.commit()

        return application