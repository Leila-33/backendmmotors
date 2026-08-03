from datetime import (
    datetime,
    timezone
)
from modules.financing.domain.exceptions import FinancingContractNotFound
from modules.payments.domain.enums import InstallmentStatus, SubscriptionStatus
from modules.applications.domain.enums import ApplicationStatus, EventType
from modules.applications.domain.entities.event import Event
from uuid import uuid4
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.financing.domain.exceptions import InstallmentNotFound

class HandleSubscriptionPaymentUseCase:


    def __init__(
        self,
        installment_repository,
        financing_contract_repository,
        application_repository,
        event_repository,
        uow
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

        self.event_repository = (
            event_repository
        )

        self.uow = uow



    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        event: dict
    ):

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
                    installment
                    .financing_contract_id
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



            # =============================================
            # PAYMENT SUCCESS
            # =============================================

            if event_type == "invoice.paid":


                if (
                    installment.status
                    == InstallmentStatus.PAID
                ):
                    return installment



                installment.status = (
                    InstallmentStatus.PAID
                )

                installment.paid_at = (
                    datetime.now(timezone.utc)
                )


                self.installment_repository.update(
                    installment
                )



                contract.remaining_balance = max(
                    0,
                    contract.remaining_balance
                    - installment.amount
                )


                self.financing_contract_repository.update(
                    contract
                )



                self.event_repository.save(
                    Event(

                        id=str(uuid4()),

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
                            "invoice_id": invoice.id
                        },

                        created_at=datetime.now(
                            timezone.utc
                        )
                    )
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


                    self.event_repository.save(
                        Event(

                            id=str(uuid4()),

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
                                "contract_id": contract.id
                            },

                            created_at=datetime.now(
                                timezone.utc
                            )
                        )
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


                self.event_repository.save(
                    Event(

                        id=str(uuid4()),

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
                            "invoice_id": invoice.id
                        },

                        created_at=datetime.now(
                            timezone.utc
                        )
                    )
                )


            self.uow.commit()


            return installment

        except Exception:
            self.uow.rollback()
            raise