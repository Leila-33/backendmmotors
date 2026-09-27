from uuid import uuid4
from dateutil.relativedelta import relativedelta
import logging

from modules.financing.domain.entities.installment import (
    InstallmentPayment,
)

from modules.financing.domain.exceptions import (
    FinancingContractNotFound,
)

from modules.financing.domain.enums import (
    InstallmentStatus,
)

from modules.financing.application.dtos.create_installments_dto import (
    CreateInstallmentsDTO,
)

from modules.financing.application.results.create_installments_result import (
    CreateInstallmentsResult,
)


logger = logging.getLogger(__name__)


class CreateInstallmentsUseCase:
    """
    Crée les échéances de paiement d'un contrat de financement
    à partir de sa durée et de son montant mensuel.

    La création est idempotente afin d'éviter de générer
    plusieurs fois les mêmes échéances.
    """
    def __init__(
        self,
        financing_contract_repository,
        installment_repository,
    ):
        self.financing_contract_repository = (
            financing_contract_repository
        )

        self.installment_repository = (
            installment_repository
        )

    def execute(
        self,
        dto: CreateInstallmentsDTO,
    ) -> CreateInstallmentsResult:

        try:

            # =========================
            # CONTRACT
            # =========================

            contract = (
                self.financing_contract_repository
                .find_by_id(
                    dto.contract_id
                )
            )

            if contract is None:
                raise FinancingContractNotFound()

            # =========================
            # IDEMPOTENCY
            # =========================

            existing_count = (
                self.installment_repository
                .count_by_contract_id(
                    contract.id
                )
            )

            if existing_count > 0:

                existing_installments = (
                    self.installment_repository
                    .find_all_by_contract_id(
                        contract.id
                    )
                )

                logger.info(
                    "Échéances déjà créées",
                    extra={
                        "contract_id": contract.id,
                        "count": len(
                            existing_installments
                        ),
                    },
                )

                return CreateInstallmentsResult(
                    contract_id=contract.id,
                    installment_ids=[
                        installment.id
                        for installment
                        in existing_installments
                    ],
                    count=len(
                        existing_installments
                    ),
                )

            # =========================
            # CREATE INSTALLMENTS
            # =========================

            installments = []

            for month in range(
                contract.duration_months
            ):

                installment = InstallmentPayment(

                    id=str(uuid4()),

                    financing_contract_id=(
                        contract.id
                    ),

                    installment_number=(
                        month + 1
                    ),

                    amount=(
                        contract.monthly_payment
                    ),

                    due_date=(
                        contract.created_at
                        + relativedelta(
                            months=month + 1
                        )
                    ),

                    status=(
                        InstallmentStatus.PENDING
                    ),
                )

                installments.append(
                    installment
                )

            # =========================
            # PERSIST
            # =========================

            installments = (
                self.installment_repository
                .save_all(
                    installments
                )
            )

            # =========================
            # SUCCESS LOG
            # =========================

            logger.info(
                "Échéances de financement créées",
                extra={
                    "contract_id": contract.id,
                    "count": len(
                        installments
                    ),
                },
            )

            # =========================
            # RESULT
            # =========================

            return CreateInstallmentsResult(
                contract_id=contract.id,
                installment_ids=[
                    installment.id
                    for installment
                    in installments
                ],
                count=len(
                    installments
                ),
            )

        except Exception:

            logger.exception(
                "Erreur lors de la création des échéances",
                extra={
                    "contract_id": dto.contract_id,
                },
            )

            raise