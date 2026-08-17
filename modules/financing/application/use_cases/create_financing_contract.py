from datetime import datetime, timezone
from uuid import uuid4
import logging

from modules.financing.domain.entities.financing_contract import (
    FinancingContract
)

from modules.financing.application.dtos.create_financing_contract_dto import (
    CreateFinancingContractDTO
)

from modules.financing.application.results.create_financing_contract_result import (
    CreateFinancingContractResult
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


logger = logging.getLogger(__name__)


class CreateFinancingContractUseCase:

    def __init__(
        self,
        application_repository,
        financing_contract_repository,
        event_service,
    ):
        self.application_repository = (
            application_repository
        )

        self.financing_contract_repository = (
            financing_contract_repository
        )

        self.event_service = event_service

    def execute(
        self,
        dto: CreateFinancingContractDTO,
    ) -> CreateFinancingContractResult:

        try:

            # =========================
            # APPLICATION
            # =========================

            application = (
                self.application_repository
                .get_by_id(
                    dto.application_id
                )
            )

            if application is None:
                raise ApplicationNotFound()

            # =========================
            # FINANCING DATA
            # =========================

            if application.financing is None:
                raise FinancingDataNotFound()

            financing = application.financing

            if financing.financed_amount <= 0:
                raise FinancingDataNotFound()

            # =========================
            # IDEMPOTENCE
            # =========================

            existing = (
                self.financing_contract_repository
                .find_by_application_id(
                    dto.application_id
                )
            )

            if existing:

                logger.info(
                    "Contrat de financement déjà existant",
                    extra={
                        "application_id": (
                            application.id
                        ),
                        "contract_id": (
                            existing.id
                        ),
                    },
                )

                return CreateFinancingContractResult(
                    contract_id=existing.id,
                    application_id=existing.application_id,
                    financed_amount=existing.financed_amount,
                    monthly_payment=existing.monthly_payment,
                    duration_months=existing.duration_months,
                    remaining_balance=existing.remaining_balance,
                )

            # =========================
            # CREATE CONTRACT
            # =========================

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

            # =========================
            # PERSIST
            # =========================

            contract = (
                self.financing_contract_repository
                .save(contract)
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                application_id=application.id,
                vehicle_id=application.vehicle_id,
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
                },
            )

            # =========================
            # SUCCESS LOG
            # =========================

            logger.info(
                "Contrat financement créé",
                extra={
                    "application_id": (
                        application.id
                    ),
                    "contract_id": (
                        contract.id
                    ),
                },
            )

            # =========================
            # RESULT
            # =========================

            return CreateFinancingContractResult(
                contract_id=contract.id,
                application_id=contract.application_id,
                financed_amount=contract.financed_amount,
                monthly_payment=contract.monthly_payment,
                duration_months=contract.duration_months,
                remaining_balance=contract.remaining_balance,
            )

        except Exception:

            logger.exception(
                "Erreur création contrat financement",
                extra={
                    "application_id": (
                        dto.application_id
                    ),
                },
            )

            raise