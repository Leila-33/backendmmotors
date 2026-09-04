from fastapi import APIRouter, Depends, status

from core.security.dependencies import (
    get_current_sales_agent,
)

from modules.quotes.api.schemas import (
    CreateQuoteRequest,
    CreateQuoteResponse,
    QuoteDetailResponse,
    UpdateQuoteRequest,
    QuoteActionResponse,
)

from modules.quotes.api.dependencies import (
    get_create_quote_usecase,
    get_get_quote_detail_usecase,
    get_send_quote_usecase,
    get_update_quote_usecase,
    get_delete_quote_usecase,
)

from modules.quotes.application.use_cases.agent.create_quote import (
    CreateQuoteUseCase,
)

from modules.quotes.application.use_cases.agent.get_quote_detail import (
    GetQuoteDetailUseCase,
)

from modules.quotes.application.use_cases.agent.send_quote import (
    SendQuoteUseCase,
)

from modules.quotes.application.use_cases.agent.update_quote import (
    UpdateQuoteUseCase,
)

from modules.quotes.application.use_cases.agent.delete_quote import (
    DeleteQuoteUseCase,
)

from modules.quotes.application.dtos.agent.create_quote_dto import (
    CreateQuoteDTO,
)

from modules.quotes.application.dtos.agent.quote_agent_dto import (
    QuoteAgentDTO,
)

from modules.quotes.application.dtos.agent.update_quote_dto import (
    UpdateQuoteDTO,
)

from modules.financing.domain.inputs.trade_in_input import (
    TradeInInput,
)

from modules.quotes.infrastructure.mappers.quote_mapper import (
    QuoteMapper,
)


router = APIRouter(
    tags=["Agent Quotes"]
)


# =========================================================
# CREATE QUOTE
# =========================================================

@router.post(
    "",
    response_model=CreateQuoteResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_quote(
    request: CreateQuoteRequest,

    current_agent=Depends(
        get_current_sales_agent
    ),

    usecase: CreateQuoteUseCase = Depends(
        get_create_quote_usecase
    ),
):

    trade_in = None

    if request.trade_in:

        trade_in = TradeInInput(
            brand=request.trade_in.brand,
            model=request.trade_in.model,
            year=request.trade_in.year,
            mileage=request.trade_in.mileage,
            condition=request.trade_in.condition,
        )

    dto = CreateQuoteDTO(
        lead_id=request.lead_id,
        agent_id=current_agent.id,
        discount=request.discount,
        down_payment=request.down_payment,
        duration_months=request.duration_months,
        trade_in=trade_in,
    )

    result = usecase.execute(
        dto
    )

    return QuoteMapper.to_create_response(
        result
    )


# =========================================================
# GET QUOTE DETAIL
# =========================================================

@router.get(
    "/{quote_id}",
    response_model=QuoteDetailResponse,
)
def get_quote_detail(
    quote_id: str,

    current_agent=Depends(
        get_current_sales_agent
    ),

    usecase: GetQuoteDetailUseCase = Depends(
        get_get_quote_detail_usecase
    ),
):

    dto = QuoteAgentDTO(
        quote_id=quote_id,
        agent_id=current_agent.id,
    )

    result = usecase.execute(
        dto
    )

    return QuoteMapper.to_detail_response(
        result
    )


# =========================================================
# UPDATE QUOTE
# =========================================================

@router.put(
    "/{quote_id}",
    response_model=QuoteActionResponse,
)
def update_quote(
    quote_id: str,

    request: UpdateQuoteRequest,

    current_agent=Depends(
        get_current_sales_agent
    ),

    usecase: UpdateQuoteUseCase = Depends(
        get_update_quote_usecase
    ),
):

    trade_in = None

    if request.trade_in:

        trade_in = TradeInInput(
            brand=request.trade_in.brand,
            model=request.trade_in.model,
            year=request.trade_in.year,
            mileage=request.trade_in.mileage,
            condition=request.trade_in.condition,
        )

    dto = UpdateQuoteDTO(
        quote_id=quote_id,
        discount=request.discount,
        down_payment=request.down_payment,
        duration_months=request.duration_months,
        trade_in=trade_in,
        agent_id=current_agent.id,
    )

    result = usecase.execute(
        dto
    )

    return QuoteMapper.to_action_response(
        result
    )


# =========================================================
# SEND QUOTE
# =========================================================

@router.post(
    "/{quote_id}/send",
    response_model=QuoteActionResponse,
)
async def send_quote(
    quote_id: str,

    current_agent=Depends(
        get_current_sales_agent
    ),

    usecase: SendQuoteUseCase = Depends(
        get_send_quote_usecase
    ),
):

    dto = QuoteAgentDTO(
        quote_id=quote_id,
        agent_id=current_agent.id,
    )

    result = await usecase.execute(
        dto
    )

    return QuoteMapper.to_action_response(
        result
    )


# =========================================================
# DELETE QUOTE
# =========================================================

@router.delete(
    "/{quote_id}",
    response_model=QuoteActionResponse,
)
def delete_quote(
    quote_id: str,

    current_agent=Depends(
        get_current_sales_agent
    ),

    usecase: DeleteQuoteUseCase = Depends(
        get_delete_quote_usecase
    ),
):

    dto = QuoteAgentDTO(
        quote_id=quote_id,
        agent_id=current_agent.id,
    )

    result = usecase.execute(
        dto
    )

    return QuoteMapper.to_action_response(
        result
    )