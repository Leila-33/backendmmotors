from uuid import uuid4
from datetime import datetime
from dateutil.relativedelta import relativedelta
from modules.financing.domain.entities.installment import InstallmentPayment
from modules.core.exceptions import FinancingContractNotFound
from modules.core.enums import InstallmentStatus

class CreateInstallmentsUseCase:

    def __init__(
        self,
        financing_contract_repository,
        installment_repository
    ):

        self.financing_contract_repository = (
            financing_contract_repository
        )

        self.installment_repository = (
            installment_repository
        )

    # =========================
    # EXECUTE
    # =========================
    def execute(
        self,
        contract_id: str
    ):

        contract = (
            self.financing_contract_repository
            .find_by_id(contract_id)
        )

        if not contract:
            raise FinancingContractNotFound()

        existing = (
            self.installment_repository
            .count_by_contract_id(
                contract.id
            )
        )

        # idempotence webhook
        if existing > 0:
            return

        start_date = contract.created_at

        installments = []

        for month in range(
            contract.duration_months
        ):
            installment = InstallmentPayment(


                id=str(uuid4()),

                financing_contract_id=
                contract.id,
                installment_number=month + 1,
                amount=contract.monthly_payment,

                due_date=
                start_date +
                relativedelta(
                    months=month
                ),

                status=InstallmentStatus.PENDING
            )
            installments.append(
                installment
            )

        self.installment_repository.save_all(
            installments
        )
        return installments