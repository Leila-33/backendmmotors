from datetime import (
    datetime,
    timezone
)
from modules.core.exceptions import FinancingContractNotFound
from modules.core.enums import InstallmentStatus, SubscriptionStatus, EventType, ApplicationStatus
from modules.applications.domain.entities.event import Event
from uuid import uuid4
from modules.core.exceptions import ApplicationNotFound

class HandleSubscriptionPaymentUseCase:

    def __init__(
        self,
        db,
        installment_repository,
        financing_contract_repository,
        event_repository,
        application_repository
    ):
        self.db = db

        self.installment_repository = (
            installment_repository
        )

        self.financing_contract_repository = (
            financing_contract_repository
        )

        self.event_repository = (
            event_repository
        )
        self.application_repository = (
                    application_repository
                )
    # =========================
    # EXECUTE
    # =========================
    def execute(
        self,
        event: dict
    ):

        event_type = event["type"]

        invoice = event["data"]["object"]

        subscription_id = invoice.subscription if hasattr(invoice, "subscription") else None

        if not subscription_id:
            return None

        # =========================
        # CONTRACT
        # =========================
        contract = (
            self.financing_contract_repository
            .get_by_subscription_id(
                subscription_id
            )
        )

        if not contract:
            raise FinancingContractNotFound()


        application = (
                    self.application_repository
                    .get_by_id(
                        contract.application_id
                    )
                )

        if not application:
            raise ApplicationNotFound()
        # =========================
        # INSTALLMENT
        # =========================
        installment = (
            self.installment_repository
            .find_next_unpaid(
                contract.id
            )
        )

        if not installment:
            return None

        # =========================
        # PAYMENT SUCCESS
        # =========================
        if event_type == "invoice.paid":

            if installment.status == InstallmentStatus.PAID:
                return installment

            installment.status = InstallmentStatus.PAID
            installment.paid_at = datetime.now(timezone.utc)
            installment.stripe_invoice_id = invoice["id"]

            self.installment_repository.save(installment)

            # =========================
            # UPDATE CONTRACT
            # =========================
            contract.remaining_balance = max(
                0,
                contract.remaining_balance - installment.amount
            )

            # =========================
            # EVENT INSTALLMENT (TOUJOURS EN PREMIER)
            # =========================
            self.event_repository.save(
                Event(
                    id=str(uuid4()),
                    application_id=contract.application_id,
                    user_id=application.user_id,
                    type=EventType.INSTALLMENT_PAID,
                    message=(
                        f"Mensualité n°{installment.installment_number} "
                        f"/ {contract.duration_months} "
                        f"de {installment.amount:.2f} € payée."
                    ),
                    event_metadata={
                        "installment_number": installment.installment_number,
                        "contract_id": contract.id,
                        "installment_id": installment.id,
                        "invoice_id": invoice["id"]
                    }
                )
            )

            # =========================
            # CHECK FINISH
            # =========================
            if contract.remaining_balance == 0:

                contract.subscription_status = SubscriptionStatus.COMPLETED
                contract.updated_at = datetime.now(timezone.utc)

                application.status = ApplicationStatus.COMPLETED

                self.application_repository.update(application)

                self.financing_contract_repository.update(contract)
                self.event_repository.save(
                    Event(
                        id=str(uuid4()),
                        application_id=contract.application_id,
                        user_id=application.user_id,
                        type=EventType.FINANCING_COMPLETED,
                        message=(
                            "Financement intégralement remboursé."
                        ),
                        event_metadata={
                            "contract_id": contract.id,
                            "financed_amount": contract.financed_amount
                        }
                    )
                )

        # =========================
        # PAYMENT FAILED
        # =========================
        elif (
            event_type
            == "invoice.payment_failed"
        ):

            installment.status = (
                InstallmentStatus.FAILED
            )

            installment.stripe_invoice_id = (
                invoice["id"]
            )

            self.installment_repository.save(
                installment
            )

            self.event_repository.save(
                Event(
                    id=str(uuid4()),
                    application_id=contract.application_id,
                    user_id=application.user_id,
                    type=EventType.INSTALLMENT_FAILED,
                   message=(
    f"Le paiement de la mensualité "
    f"n°{installment.installment_number} "
    f"sur {contract.duration_months} "
    f"({installment.amount:.2f} €) a échoué."
),
                    event_metadata={
                        "installment_number": installment.installment_number,
                        "contract_id": contract.id,
                        "installment_id": installment.id,
                        "invoice_id": invoice["id"]
                    }
                )
            )

        self.event_repository.commit()
        return installment