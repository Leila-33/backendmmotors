import logging
from datetime import datetime, timezone

from modules.financing.domain.exceptions import (
    FinancingContractNotFound,
)
from modules.financing.domain.exceptions import (
    InstallmentNotFound,
)

from modules.payments.domain.enums import (
    SubscriptionStatus,
)
from modules.financing.domain.enums import (
    InstallmentStatus,
)
from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)

from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)
from modules.payments.application.dtos.handle_payment_success_dto import (
    HandlePaymentSuccessDTO,
)
from modules.payments.application.results.handle_subscription_payment_result import (
    HandleSubscriptionPaymentResult,
)


logger = logging.getLogger(__name__)


class HandleSubscriptionPaymentUseCase:

    def __init__(
        self,
        installment_repository,
        financing_contract_repository,
        application_repository,
        event_service,
        unit_of_work,
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
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: HandlePaymentSuccessDTO,
    ):

        installment = None
        contract = None
        application = None

        try:

            # =========================
            # GET INSTALLMENT
            # =========================

            installment = (
                self.installment_repository
                .find_by_stripe_invoice_id(
                    dto.invoice_id
                )
            )

            # =========================
            # FALLBACK
            # =========================
            # invoice.paid peut arriver avant
            # invoice.created.
            #
            # Dans ce cas, la facture n'est pas
            # encore associée à une mensualité.
            # On retrouve alors le contrat grâce
            # au subscription_id puis la prochaine
            # mensualité impayée.

            if installment is None:

                if not dto.subscription_id:
                    raise InstallmentNotFound()

                contract = (
                    self.financing_contract_repository
                    .get_by_subscription_id(
                        dto.subscription_id
                    )
                )

                if contract is None:
                    raise FinancingContractNotFound()

                installment = (
                    self.installment_repository
                    .find_next_unpaid(
                        contract.id
                    )
                )

                if installment is None:
                    raise InstallmentNotFound()

                # =========================
                # LINK INVOICE
                # =========================

                installment.stripe_invoice_id = (
                    dto.invoice_id
                )

                self.installment_repository.update(
                    installment
                )

                logger.info(
                    "Facture Stripe associée "
                    "à une échéance pendant "
                    "le traitement du paiement",
                    extra={
                        "invoice_id": dto.invoice_id,
                        "subscription_id": (
                            dto.subscription_id
                        ),
                        "installment_id": (
                            installment.id
                        ),
                    },
                )

            # =========================
            # GET CONTRACT
            # =========================

            if contract is None:

                contract = (
                    self.financing_contract_repository
                    .find_by_id(
                        installment.financing_contract_id
                    )
                )

            if contract is None:
                raise FinancingContractNotFound()

            # =========================
            # GET APPLICATION
            # =========================

            application = (
                self.application_repository
                .get_by_id(
                    contract.application_id
                )
            )

            if application is None:
                raise ApplicationNotFound()

            # =========================
            # PAYMENT SUCCESS
            # =========================

            if dto.event_type == "invoice.paid":

                # =========================
                # IDEMPOTENCY
                # =========================

                if (
                    installment.status
                    == InstallmentStatus.PAID
                ):

                    logger.info(
                        "Mensualité déjà payée",
                        extra={
                            "contract_id": contract.id,
                            "installment_id": (
                                installment.id
                            ),
                            "invoice_id": (
                                dto.invoice_id
                            ),
                        },
                    )

                    return HandleSubscriptionPaymentResult(
                        installment_id=installment.id,
                        status=(
                            installment.status.value
                        ),
                        invoice_id=dto.invoice_id,
                        message=(
                            "Mensualité déjà payée"
                        ),
                    )

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
                    - installment.amount,
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
                    vehicle_id=application.vehicle_id,
                    type=EventType.INSTALLMENT_PAID,
                    message=(
                        f"Mensualité "
                        f"n°{installment.installment_number} "
                        f"payée."
                    ),
                    event_metadata={
                        "contract_id": contract.id,
                        "installment_id": (
                            installment.id
                        ),
                        "invoice_id": (
                            dto.invoice_id
                        ),
                    },
                )

                # =========================
                # FINANCING COMPLETED
                # =========================

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
                        vehicle_id=application.vehicle_id,
                        type=EventType.FINANCING_COMPLETED,
                        message=(
                            "Financement intégralement "
                            "remboursé."
                        ),
                        event_metadata={
                            "contract_id": contract.id,
                        },
                    )

            # =========================
            # PAYMENT FAILED
            # =========================

            elif (
                dto.event_type
                == "invoice.payment_failed"
            ):

                # =========================
                # IDEMPOTENCY
                # =========================

                if (
                    installment.status
                    == InstallmentStatus.PAID
                ):

                    logger.warning(
                        "Paiement échoué reçu "
                        "pour une mensualité déjà payée",
                        extra={
                            "contract_id": contract.id,
                            "installment_id": (
                                installment.id
                            ),
                            "invoice_id": (
                                dto.invoice_id
                            ),
                        },
                    )

                    return HandleSubscriptionPaymentResult(
                        installment_id=installment.id,
                        status=(
                            installment.status.value
                        ),
                        invoice_id=dto.invoice_id,
                        message=(
                            "Mensualité déjà payée"
                        ),
                    )

                # =========================
                # MARK FAILED
                # =========================

                installment.status = (
                    InstallmentStatus.FAILED
                )

                self.installment_repository.update(
                    installment
                )

                # =========================
                # EVENT
                # =========================

                self.event_service.log(
                    application_id=application.id,
                    user_id=application.user_id,
                    vehicle_id=application.vehicle_id,
                    type=EventType.INSTALLMENT_FAILED,
                    message=(
                        f"Le paiement de la "
                        f"mensualité "
                        f"n°{installment.installment_number} "
                        f"a échoué."
                    ),
                    event_metadata={
                        "contract_id": contract.id,
                        "installment_id": (
                            installment.id
                        ),
                        "invoice_id": (
                            dto.invoice_id
                        ),
                    },
                )

            # =========================
            # UNKNOWN EVENT
            # =========================

            else:

                logger.warning(
                    "Type d'événement Stripe "
                    "non pris en charge",
                    extra={
                        "event_type": dto.event_type,
                        "invoice_id": dto.invoice_id,
                    },
                )

                return None

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            # =========================
            # SUCCESS LOG
            # =========================

            logger.info(
                "Paiement abonnement traité",
                extra={
                    "event_type": dto.event_type,
                    "contract_id": contract.id,
                    "installment_id": (
                        installment.id
                    ),
                    "invoice_id": dto.invoice_id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return HandleSubscriptionPaymentResult(
                installment_id=installment.id,
                status=installment.status.value,
                invoice_id=dto.invoice_id,
                message=(
                    "Mensualité payée"
                    if dto.event_type
                    == "invoice.paid"
                    else (
                        "Paiement de la mensualité "
                        "échoué"
                    )
                ),
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur traitement paiement abonnement",
                extra={
                    "event_type": (
                        dto.event_type
                        if dto
                        else None
                    ),
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
                        dto.invoice_id
                        if dto
                        else None
                    ),
                },
            )

            raise
