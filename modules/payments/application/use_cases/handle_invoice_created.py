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
                    "invoice_id": dto.invoice_id,
                    "subscription_id": (
                        dto.subscription_id
                    ),
                },
            )

            raise