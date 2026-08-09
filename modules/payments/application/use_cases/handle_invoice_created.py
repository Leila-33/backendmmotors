from modules.financing.domain.exceptions import FinancingContractNotFound
import logging

logger = logging.getLogger(__name__)

class HandleInvoiceCreatedUseCase:


    def __init__(
        self,
        financing_contract_repository,
        installment_repository,
        uow
    ):

        self.financing_contract_repository = (
            financing_contract_repository
        )

        self.installment_repository = (
            installment_repository
        )

        self.uow = uow



    def execute(
        self,
        event: dict
    ):
        invoice_id = None

        try:

            invoice = event["data"]["object"]
            invoice_id = invoice.id


            subscription_id = invoice.subscription


            if not subscription_id:
                return None


            # =============================================
            # CONTRACT
            # =============================================

            contract = (
                self.financing_contract_repository
                .get_by_subscription_id(
                    subscription_id
                )
            )


            if not contract:
                raise FinancingContractNotFound()



            # =============================================
            # FIND INSTALLMENT
            # =============================================

            installment = (
                self.installment_repository
                .find_next_unpaid(
                    contract.id
                )
            )


            if not installment:
                return None



            # =============================================
            # LINK STRIPE INVOICE
            # =============================================

            installment.stripe_invoice_id = (
                invoice.id
            )


            self.installment_repository.update(
                installment
            )


            self.uow.commit()

            logger.info(
                "Facture Stripe associée à une échéance",
                extra={
                    "invoice_id": invoice_id,
                    "subscription_id": subscription_id,
                    "contract_id": contract.id,
                    "installment_id": installment.id,
                }
            )
            return installment

        except Exception:

            logger.exception(
                "Erreur traitement facture Stripe",
                extra={
                    "invoice_id": invoice_id,
                }
            )

            raise