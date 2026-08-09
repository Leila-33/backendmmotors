from uuid import uuid4
from dateutil.relativedelta import relativedelta
from modules.financing.domain.entities.installment import InstallmentPayment
from modules.financing.domain.exceptions import FinancingContractNotFound
from modules.payments.domain.enums import InstallmentStatus
import logging

logger = logging.getLogger(__name__)


class CreateInstallmentsUseCase:

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
        contract_id: str,
    ) -> list[InstallmentPayment]:

        try:

            # =========================
            # CONTRACT
            # =========================

            contract = (
                self.financing_contract_repository
                .find_by_id(contract_id)
            )

            if not contract:
                raise FinancingContractNotFound()


            # =========================
            # IDEMPOTENCY
            # =========================

            existing = (
                self.installment_repository
                .count_by_contract_id(
                    contract.id
                )
            )

            if existing > 0:

                return (
                    self.installment_repository
                    .find_all_by_contract_id(
                        contract.id
                    )
                )


            # =========================
            # CREATE INSTALLMENTS
            # =========================

            installments = []

            for month in range(
                contract.duration_months
            ):

                installments.append(
                    InstallmentPayment(

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
                )


            installments = (
                self.installment_repository
                .save_all(installments)
            )

            logger.info(
                "Échéances de financement créées",
                extra={
                    "contract_id": contract.id,
                    "count": len(installments),
                }
            )


            return installments


        except Exception:

            logger.exception(
                "Erreur lors de la création des échéances",
                extra={
                    "contract_id": contract_id,
                }
            )

            raise