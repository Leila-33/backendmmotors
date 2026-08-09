from datetime import (
    datetime,
    timezone
)
from modules.financing.domain.exceptions import FinancingContractNotFound
from modules.payments.domain.enums import InstallmentStatus, SubscriptionStatus
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.financing.domain.exceptions import InstallmentNotFound
from modules.applications.domain.enums import (
    EventType
)
import logging

logger = logging.getLogger(__name__)

import logging

logger = logging.getLogger(__name__)


class HandleSubscriptionPaymentUseCase:

    def __init__(
        self,
        installment_repository,
        financing_contract_repository,
        application_repository,
        event_service,
        uow,
    ):
        self.installment_repository = (
            installment_repository
        )

        self.financing_contract_repository = (
            financing_contract_repository
        )

        self.application_repository = (
            application_repository
        )

        self.event_service = event_service

        self.uow = uow


    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        event: dict,
    ):

        event_type = None
        invoice = None
        installment = None
        contract = None

        try:

            event_type = event["type"]

            invoice = event["data"]["object"]


            # =============================================
            # INSTALLMENT
            # =============================================

            installment = (
                self.installment_repository
                .find_by_stripe_invoice_id(
                    invoice.id
                )
            )

            if not installment:
                raise InstallmentNotFound()


            # =============================================
            # CONTRACT
            # =============================================

            contract = (
                self.financing_contract_repository
                .find_by_id(
                    installment.financing_contract_id
                )
            )

            if not contract:
                raise FinancingContractNotFound()


            # =============================================
            # APPLICATION
            # =============================================

            application = (
                self.application_repository
                .get_by_id(
                    contract.application_id
                )
            )

            if not application:
                raise ApplicationNotFound()


            # =============================================
            # PAYMENT SUCCESS
            # =============================================

            if event_type == "invoice.paid":

                # =========================
                # IDEMPOTENCE
                # =========================

                if (
                    installment.status
                    == InstallmentStatus.PAID
                ):

                    logger.info(
                        "Mensualité déjà payée",
                        extra={
                            "contract_id": contract.id,
                            "installment_id": installment.id,
                            "invoice_id": invoice.id,
                        }
                    )

                    return installment


                # =========================
                # MARK PAID
                # =========================

                installment.status = (
                    InstallmentStatus.PAID
                )

                installment.paid_at = (
                    datetime.now(timezone.utc)
                )

                self.installment_repository.update(
                    installment
                )


                # =========================
                # UPDATE BALANCE
                # =========================

                contract.remaining_balance = max(
                    0,
                    contract.remaining_balance
                    - installment.amount
                )

                self.financing_contract_repository.update(
                    contract
                )


                # =========================
                # EVENT
                # =========================

                self.event_service.log(
                    application_id=application.id,
                    user_id=application.user_id,
                    type=EventType.INSTALLMENT_PAID,
                    message=(
                        f"Mensualité "
                        f"n°{installment.installment_number} "
                        f"payée."
                    ),
                    event_metadata={
                        "contract_id": contract.id,
                        "installment_id": installment.id,
                        "invoice_id": invoice.id,
                    },
                )


                # =========================================
                # FINISHED
                # =========================================

                if contract.remaining_balance == 0:

                    contract.subscription_status = (
                        SubscriptionStatus.COMPLETED
                    )

                    application.status = (
                        ApplicationStatus.COMPLETED
                    )

                    self.financing_contract_repository.update(
                        contract
                    )

                    self.application_repository.update(
                        application
                    )

                    self.event_service.log(
                        application_id=application.id,
                        user_id=application.user_id,
                        type=(
                            EventType
                            .FINANCING_COMPLETED
                        ),
                        message=(
                            "Financement intégralement "
                            "remboursé."
                        ),
                        event_metadata={
                            "contract_id": contract.id,
                        },
                    )


            # =============================================
            # PAYMENT FAILED
            # =============================================

            elif event_type == "invoice.payment_failed":

                installment.status = (
                    InstallmentStatus.FAILED
                )

                self.installment_repository.update(
                    installment
                )

                self.event_service.log(
                    application_id=application.id,
                    user_id=application.user_id,
                    type=EventType.INSTALLMENT_FAILED,
                    message=(
                        f"Le paiement de la "
                        f"mensualité "
                        f"n°{installment.installment_number} "
                        f"a échoué."
                    ),
                    event_metadata={
                        "contract_id": contract.id,
                        "installment_id": installment.id,
                        "invoice_id": invoice.id,
                    },
                )


            # =============================================
            # COMMIT
            # =============================================

            self.uow.commit()


            # =============================================
            # LOG SUCCESS
            # =============================================

            logger.info(
                "Paiement abonnement traité",
                extra={
                    "event_type": event_type,
                    "contract_id": contract.id,
                    "installment_id": installment.id,
                    "invoice_id": invoice.id,
                },
            )


            return installment


        except Exception:

            self.uow.rollback()

            logger.exception(
                "Erreur traitement paiement abonnement",
                extra={
                    "event_type": event_type,
                    "contract_id": (
                        contract.id
                        if contract
                        else None
                    ),
                    "installment_id": (
                        installment.id
                        if installment
                        else None
                    ),
                    "invoice_id": (
                        invoice.id
                        if invoice
                        else None
                    ),
                },
            )

            raise