from modules.financing.domain.exceptions import FinancingContractNotFound

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
        try:

            invoice = event["data"]["object"]


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


            return installment

        except Exception:
            self.uow.rollback()
            raise
        