from modules.financing.domain.inputs.financing_input import FinancingInput
from modules.financing.application.results.financing_result import FinancingResult

from modules.financing.domain.exceptions import (
    InvalidFinancingAmount,
    InvalidFinancingDuration,
)


class FinancingService:

    def calculate(
        self,
        data: FinancingInput,
    ) -> FinancingResult:

        if data.total_price < 0:
            raise InvalidFinancingAmount(
                "Le prix total ne peut pas être négatif."
            )

        if data.down_payment < 0:
            raise InvalidFinancingAmount(
                "L'apport ne peut pas être négatif."
            )

        if data.trade_in_value < 0:
            raise InvalidFinancingAmount(
                "La valeur de reprise ne peut pas être négative."
            )

        if (
            data.down_payment
            + data.trade_in_value
            > data.total_price
        ):
            raise InvalidFinancingAmount(
                "L'apport et la reprise dépassent le prix du véhicule."
            )

        if data.duration_months not in (24, 36, 48, 60):
            raise InvalidFinancingDuration(
                "La durée doit être de 24, 36, 48 ou 60 mois."
            )

        financed_amount = (
            data.total_price
            - data.down_payment
            - data.trade_in_value
        )

        monthly_payment = (
            financed_amount
            / data.duration_months
        )

        return FinancingResult(
            financed_amount=round(
                financed_amount,
                2,
            ),
            monthly_payment=round(
                monthly_payment,
                2,
            ),
        )