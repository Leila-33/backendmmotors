from fastapi import APIRouter, Depends, status

from core.security.dependencies import (
    get_current_user,
)

from modules.quotes.api.schemas import (
    CustomerQuoteListResponse,
    QuoteCustomerDetailResponse,
    QuoteActionRequiredCountResponse,
    RefuseQuoteRequest,
    QuoteActionResponse,
    AcceptQuoteResponse,
)

from modules.quotes.api.dependencies import (
    get_get_customer_quotes_usecase,
    get_get_customer_quote_detail_usecase,
    get_client_quote_action_required_count_usecase,
    get_refuse_quote_usecase,
    get_accept_quote_usecase,
)

from modules.quotes.application.use_cases.get_customer_quotes import (
    GetCustomerQuotesUseCase,
)

from modules.quotes.application.use_cases.get_customer_quote_detail import (
    GetCustomerQuoteDetailUseCase,
)

from modules.quotes.application.use_cases.get_client_quote_action_required_count import (
    GetClientQuoteActionRequiredCountUseCase,
)

from modules.quotes.application.use_cases.refuse_quote import (
    RefuseQuoteUseCase,
)

from modules.quotes.application.use_cases.accept_quote import (
    AcceptQuoteUseCase,
)

from modules.quotes.application.dtos.get_customer_quotes_dto import (
    GetCustomerQuotesDTO,
)

from modules.quotes.application.dtos.get_customer_quote_detail_dto import (
    GetCustomerQuoteDetailDTO,
)

from modules.quotes.application.dtos.get_client_quote_action_required_count_dto import (
    GetClientQuoteActionRequiredCountDTO,
)

from modules.quotes.application.dtos.refuse_quote_dto import (
    RefuseQuoteDTO,
)

from modules.quotes.application.dtos.accept_quote_dto import (
    AcceptQuoteDTO,
)

from modules.quotes.infrastructure.mappers.quote_mapper import (
    QuoteMapper,
)


router = APIRouter(
    tags=["Customer Quotes"]
)


# =========================================================
# GET CUSTOMER QUOTES
# =========================================================

@router.get(
    "",
    response_model=list[CustomerQuoteListResponse],
)
def get_customer_quotes(
    current_user=Depends(
        get_current_user
    ),

    usecase: GetCustomerQuotesUseCase = Depends(
        get_get_customer_quotes_usecase
    ),
):

    dto = GetCustomerQuotesDTO(
        customer_id=current_user.id,
    )

    result = usecase.execute(
        dto
    )

    return QuoteMapper.to_customer_list_response(
        result
    )


# =========================================================
# GET ACTION REQUIRED COUNT
# =========================================================

@router.get(
    "/action-required/count",
    response_model=QuoteActionRequiredCountResponse,
)
def get_action_required_count(
    current_user=Depends(
        get_current_user
    ),

    usecase: GetClientQuoteActionRequiredCountUseCase = Depends(
        get_client_quote_action_required_count_usecase
    ),
):

    dto = GetClientQuoteActionRequiredCountDTO(
        customer_id=current_user.id,
    )

    result = usecase.execute(
        dto
    )

    return QuoteMapper.to_action_required_count_response(
        result
    )


# =========================================================
# GET CUSTOMER QUOTE DETAIL
# =========================================================

@router.get(
    "/{quote_id}",
    response_model=QuoteCustomerDetailResponse,
)
def get_customer_quote_detail(
    quote_id: str,

    current_user=Depends(
        get_current_user
    ),

    usecase: GetCustomerQuoteDetailUseCase = Depends(
        get_get_customer_quote_detail_usecase
    ),
):

    dto = GetCustomerQuoteDetailDTO(
        quote_id=quote_id,
        customer_id=current_user.id,
    )

    result = usecase.execute(
        dto
    )

    return QuoteMapper.to_customer_detail_response(
        result
    )


# =========================================================
# ACCEPT QUOTE
# =========================================================

@router.post(
    "/{quote_id}/accept",
    response_model=AcceptQuoteResponse,
    status_code=status.HTTP_200_OK,
)
async def accept_quote(
    quote_id: str,

    current_user=Depends(
        get_current_user
    ),

    usecase: AcceptQuoteUseCase = Depends(
        get_accept_quote_usecase
    ),
):

    dto = AcceptQuoteDTO(
        quote_id=quote_id,
        customer_id=current_user.id,
    )

    result = await usecase.execute(
        dto
    )

    return QuoteMapper.to_accept_response(
        result
    )


# =========================================================
# REFUSE QUOTE
# =========================================================

@router.post(
    "/{quote_id}/refuse",
    response_model=QuoteActionResponse,
)
async def refuse_quote(
    quote_id: str,

    request: RefuseQuoteRequest,

    current_user=Depends(
        get_current_user
    ),

    usecase: RefuseQuoteUseCase = Depends(
        get_refuse_quote_usecase
    ),
):

    dto = RefuseQuoteDTO(
        quote_id=quote_id,
        customer_id=current_user.id,
        reason=request.reason,
        comment=request.comment,
    )

    result = await usecase.execute(
        dto
    )

    return QuoteMapper.to_action_response(
        result
    )