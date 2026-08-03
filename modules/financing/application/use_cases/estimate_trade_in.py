from modules.financing.api.schemas import (
    TradeInEstimateRequest,
    TradeInEstimateResponse
)

from modules.financing.domain.entities.trade_in_input import (
    TradeInInput
)


class EstimateTradeInUseCase:

    def __init__(
        self,
        trade_in_estimation_service
    ):
        self.trade_in_estimation_service = (
            trade_in_estimation_service
        )

    def execute(
        self,
        dto: TradeInEstimateRequest
    ) -> TradeInEstimateResponse:

        trade_input = TradeInInput(
            brand=dto.brand,
            model=dto.model,
            year=dto.year,
            mileage=dto.mileage,
            condition=dto.condition,
        )

        estimated_value = (
            self.trade_in_estimation_service
            .estimate(trade_input)
        )

        return TradeInEstimateResponse(
            estimated_value=estimated_value
        )