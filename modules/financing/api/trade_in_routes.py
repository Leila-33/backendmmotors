from fastapi import APIRouter

from modules.financing.api.schemas import (
    TradeInEstimateRequest
)

from modules.financing.domain.entities.trade_in import (
    TradeInInput
)

from modules.financing.domain.services.trade_in_service import (
    TradeInService
)

router = APIRouter()


@router.post("/estimate")
def estimate_trade_in(
    request: TradeInEstimateRequest
):

    trade_input = TradeInInput(
        brand=request.brand,
        model=request.model,
        year=request.year,
        mileage=request.mileage,
        condition=request.condition
    )

    estimated_value = TradeInService.estimate(
        trade_input
    )

    return {
        "estimated_value": estimated_value
    }