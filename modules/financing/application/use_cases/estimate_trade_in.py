from modules.financing.application.dtos.trade_in_estimate_dto import (
    TradeInEstimateDTO,
)
from modules.financing.application.results.trade_in_estimate_result import (
    TradeInEstimateResult,
)

from modules.financing.domain.inputs.trade_in_input import (
    TradeInInput,
)


class EstimateTradeInUseCase:

    def __init__(
        self,
        trade_in_estimation_service,
    ):
        self.trade_in_estimation_service = (
            trade_in_estimation_service
        )

    def execute(
        self,
        dto: TradeInEstimateDTO,
    ) -> TradeInEstimateResult:

        trade_input = TradeInInput(
            brand=dto.brand,
            model=dto.model,
            year=dto.year,
            mileage=dto.mileage,
            condition=dto.condition,
        )

        return self.trade_in_estimation_service.estimate(trade_input)
