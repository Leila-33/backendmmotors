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

from modules.applications.domain.enums import (
    EventType
)
import logging

logger = logging.getLogger(__name__)


class CreateFinancingContractUseCase:

    def __init__(
        self,
        application_repository,
        financing_contract_repository,
        event_service,
    ):
        self.application_repository = application_repository
        self.financing_contract_repository = financing_contract_repository
        self.event_service = event_service


    def execute(
        self,
        application_id: str
    ) -> FinancingContract:

        application = (
            self.application_repository
            .get_by_id(application_id)
        )

        if not application:
            raise ApplicationNotFound()


        if not application.financing:
            raise FinancingDataNotFound()


        financing = application.financing


        if financing.financed_amount <= 0:
            raise FinancingDataNotFound()


        existing = (
            self.financing_contract_repository
            .find_by_application_id(application_id)
        )


        if existing:
            return existing


        try:

            contract = FinancingContract(
                id=str(uuid4()),
                application_id=application.id,
                financed_amount=financing.financed_amount,
                monthly_payment=financing.monthly_payment,
                duration_months=financing.duration_months,
                remaining_balance=financing.financed_amount,
                created_at=datetime.now(timezone.utc),
            )


            contract = (
                self.financing_contract_repository
                .save(contract)
            )


            self.event_service.log(
                application_id=application.id,
                user_id=application.user_id,
                type=EventType.FINANCING_CONTRACT_CREATED,
                message="Contrat de financement créé.",
                event_metadata={
                    "contract_id": contract.id,
                    "financed_amount": contract.financed_amount,
                },
            )


            logger.info(
                "Contrat financement créé",
                extra={
                    "application_id": application.id,
                    "contract_id": contract.id,
                },
            )


            return contract


        except Exception:

            logger.exception(
                "Erreur création contrat financement",
                extra={
                    "application_id": application_id,
                },
            )

            raise