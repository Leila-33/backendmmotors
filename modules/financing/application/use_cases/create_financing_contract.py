from datetime import datetime, timezone
from uuid import uuid4

from modules.financing.domain.entities.financing_contract import (
    FinancingContract
)

from modules.applications.domain.exceptions import (
    ApplicationNotFound
)

from modules.financing.domain.exceptions import (
    FinancingDataNotFound
)

from modules.applications.domain.entities.event import (
    Event
)

from modules.applications.domain.enums import (
    EventType
)


class CreateFinancingContractUseCase:


    def __init__(
        self,
        application_repository,
        financing_contract_repository,
        event_repository,
        uow
    ):

        self.application_repository = (
            application_repository
        )

        self.financing_contract_repository = (
            financing_contract_repository
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
        application_id: str
    ) -> FinancingContract:

        try:
            # =================================================
            # APPLICATION
            # =================================================

            application = (
                self.application_repository
                .get_by_id(application_id)
            )


            if not application:
                raise ApplicationNotFound()


            # =================================================
            # FINANCING DATA
            # =================================================

            if not application.financing:
                raise FinancingDataNotFound()


            financing = application.financing


            if financing.financed_amount <= 0:
                raise FinancingDataNotFound()



            # =================================================
            # ALREADY EXISTS
            # =================================================

            existing_contract = (
                self.financing_contract_repository
                .find_by_application_id(
                    application_id
                )
            )


            if existing_contract:
                return existing_contract



            # =================================================
            # CREATE
            # =================================================

            contract = FinancingContract(

                id=str(uuid4()),

                application_id=application.id,

                financed_amount=(
                    financing.financed_amount
                ),

                monthly_payment=(
                    financing.monthly_payment
                ),

                duration_months=(
                    financing.duration_months
                ),

                remaining_balance=(
                    financing.financed_amount
                ),

                created_at=datetime.now(
                    timezone.utc
                ),

            )


            contract = (
                self.financing_contract_repository
                .save(contract)
            )


            # =================================================
            # EVENT
            # =================================================

            self.event_repository.save(
                Event(

                    id=str(uuid4()),

                    application_id=application.id,

                    user_id=application.user_id,

                    type=(
                        EventType
                        .FINANCING_CONTRACT_CREATED
                    ),

                    message=(
                        "Contrat de financement créé."
                    ),

                    event_metadata={

                        "contract_id": contract.id,

                        "financed_amount": (
                            contract.financed_amount
                        ),

                        "duration_months": (
                            contract.duration_months
                        ),

                        "monthly_payment": (
                            contract.monthly_payment
                        )

                    },

                    created_at=datetime.now(
                        timezone.utc
                    )
                )
            )


            # =================================================
            # COMMIT
            # =================================================

            self.uow.commit()


            return contract

        except Exception:
            self.uow.rollback()
            raise