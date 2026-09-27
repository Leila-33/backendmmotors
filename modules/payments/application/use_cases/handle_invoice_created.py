import logging

from modules.financing.domain.exceptions import (
    FinancingContractNotFound,
)
from modules.payments.application.dtos.handle_invoice_created_dto import (
    HandleInvoiceCreatedDTO,
)
from modules.payments.application.results.handle_invoice_created_result import (
    HandleInvoiceCreatedResult,
)


logger = logging.getLogger(__name__)


class HandleInvoiceCreatedUseCase:
    """
    Traite la création d'une facture Stripe en l'associant
    à la prochaine échéance impayée du contrat de financement.

    Le traitement tient compte de l'ordre variable de réception
    des événements Stripe afin d'éviter les associations en double.
    """
    def __init__(
        self,
        financing_contract_repository,
        installment_repository,
        unit_of_work,
    ):
        self.financing_contract_repository = (
            financing_contract_repository
        )

        self.installment_repository = (
            installment_repository
        )

        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: HandleInvoiceCreatedDTO,
    ):

        try:

            # =========================
            # SUBSCRIPTION
            # =========================

            if not dto.subscription_id:
                return None

            # =========================
            # CHECK EXISTING INVOICE
            # =========================
            # invoice.paid peut avoir été traité
            # avant invoice.created.
            #
            # Dans ce cas, HandleSubscriptionPaymentUseCase
            # a déjà associé cette facture à une mensualité.
            #
            # Il ne faut surtout pas appeler
            # find_next_unpaid(), sinon on pourrait associer
            # la même facture à la mensualité suivante.

            existing_installment = (
                self.installment_repository
                .find_by_stripe_invoice_id(
                    dto.invoice_id
                )
            )

            if existing_installment is not None:

                logger.info(
                    "Facture Stripe déjà associée "
                    "à une échéance",
                    extra={
                        "invoice_id": dto.invoice_id,
                        "subscription_id": (
                            dto.subscription_id
                        ),
                        "installment_id": (
                            existing_installment.id
                        ),
                    },
                )

                return HandleInvoiceCreatedResult(
                    installment_id=(
                        existing_installment.id
                    ),
                    invoice_id=dto.invoice_id,
                    message=(
                        "Facture déjà associée "
                        "à une échéance"
                    ),
                )

            # =========================
            # GET CONTRACT
            # =========================

            contract = (
                self.financing_contract_repository
                .get_by_subscription_id(
                    dto.subscription_id
                )
            )

            if contract is None:
                raise FinancingContractNotFound()

            # =========================
            # FIND INSTALLMENT
            # =========================

            installment = (
                self.installment_repository
                .find_next_unpaid(
                    contract.id
                )
            )

            if installment is None:

                logger.warning(
                    "Aucune mensualité impayée "
                    "disponible pour la facture Stripe",
                    extra={
                        "invoice_id": dto.invoice_id,
                        "subscription_id": (
                            dto.subscription_id
                        ),
                        "contract_id": contract.id,
                    },
                )

                return None

            # =========================
            # LINK INVOICE
            # =========================

            installment.stripe_invoice_id = (
                dto.invoice_id
            )

            self.installment_repository.update(
                installment
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()

            # =========================
            # SUCCESS LOG
            # =========================

            logger.info(
                "Facture Stripe associée à une échéance",
                extra={
                    "invoice_id": dto.invoice_id,
                    "subscription_id": (
                        dto.subscription_id
                    ),
                    "contract_id": contract.id,
                    "installment_id": installment.id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return HandleInvoiceCreatedResult(
                installment_id=installment.id,
                invoice_id=dto.invoice_id,
                message=(
                    "Facture Stripe associée "
                    "à l'échéance"
                ),
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur traitement facture Stripe",
                extra={
                    "invoice_id": (
                        dto.invoice_id
                        if dto
                        else None
                    ),
                    "subscription_id": (
                        dto.subscription_id
                        if dto
                        else None
                    ),
                },
            )

            raise