from modules.financing.api.schemas import (FinancingRequest, FinancingResponse)
class FinancingService:

    def calculate(self, data: FinancingRequest) -> FinancingResponse:

        # =========================
        # SANITIZATION
        # =========================
        total_price = max(0, data.total_price)
        down_payment = max(0, data.down_payment)
        trade_in_value = max(0, data.trade_in_value)
        duration = max(1, data.duration_months)

        # =========================
        # FINANCED AMOUNT
        # =========================
        financed_amount = max(
            total_price
            - down_payment
            - trade_in_value,
            0
        )

        # =========================
        # MONTHLY PAYMENT
        # =========================
        monthly_payment = financed_amount / duration

        return FinancingResponse(
            financed_amount=round(financed_amount, 2),
            monthly_payment=round(monthly_payment, 2)
        )