from fastapi import APIRouter
from fastapi import (
    APIRouter,
    Depends
)

from modules.financing.api.schemas import (
    TradeInEstimateRequest,
    TradeInEstimateResponse
)

from modules.financing.application.use_cases.estimate_trade_in import (
    EstimateTradeInUseCase
)

from modules.financing.api.dependencies import (
    get_estimate_trade_in_use_case
)


router = APIRouter(
    tags=["Trade In"]
)


# =====================================================
# ESTIMATE
# =====================================================

@router.post(
    "/estimate",
    response_model=TradeInEstimateResponse
)
def estimate_trade_in(
    request: TradeInEstimateRequest,
    use_case: EstimateTradeInUseCase = Depends(
        get_estimate_trade_in_use_case
    )
):

    return use_case.execute(
        request
    )