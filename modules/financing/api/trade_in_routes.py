from fastapi import APIRouter, Depends

from modules.financing.api.schemas import (
    TradeInEstimateRequest,
    TradeInEstimateResponse,
)

from modules.financing.api.dependencies import (
    get_estimate_trade_in_usecase,
)

from modules.financing.application.dtos.trade_in_estimate_dto import (
    TradeInEstimateDTO,
)

from modules.financing.application.use_cases.estimate_trade_in import (
    EstimateTradeInUseCase,
)


router = APIRouter(
    tags=["Trade In"],
)


# ============================================================
# ESTIMATE TRADE IN
# ============================================================

@router.post(
    "/estimate",
    response_model=TradeInEstimateResponse,
)
def estimate_trade_in(
    request: TradeInEstimateRequest,
    usecase: EstimateTradeInUseCase = Depends(
        get_estimate_trade_in_usecase
    ),
):
    # ========================================================
    # REQUEST → DTO
    # ========================================================

    dto = TradeInEstimateDTO(
        brand=request.brand,
        model=request.model,
        year=request.year,
        mileage=request.mileage,
        condition=request.condition,
    )

    # ========================================================
    # USE CASE
    # ========================================================

    result = usecase.execute(dto)

    # ========================================================
    # RESULT → RESPONSE
    # ========================================================

    return TradeInEstimateResponse(
        estimated_value=result.estimated_value,
    )