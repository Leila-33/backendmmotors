from fastapi import APIRouter, Depends

from modules.quotes.api.schemas import (
    QuoteListResponse,
    QuoteDetailCustomerResponse,
    QuoteActionRequiredCountResponse,
    RefuseQuoteRequest,
    QuoteActionResponse,
    AcceptQuoteResponse
    )
from modules.quotes.api.dependencies import (
    get_customer_quotes_usecase,
    get_customer_quote_detail_usecase,
    get_client_quote_action_required_count_usecase,
    get_refuse_quote_usecase,
    get_accept_quote_usecase
)
from core.security.dependencies import get_current_user
from modules.quotes.application.use_cases.get_customer_quotes import GetCustomerQuotesUseCase
from modules.quotes.application.use_cases.get_customer_quote_detail import GetCustomerQuoteDetailUseCase
from modules.quotes.application.use_cases.get_client_quote_action_required_count import GetClientQuoteActionRequiredCountUseCase
from modules.quotes.application.use_cases.refuse_quote import RefuseQuoteUseCase
from modules.quotes.application.use_cases.accept_quote import AcceptQuoteUseCase

router = APIRouter(tags=["Quotes"])

@router.get(
    "",
    response_model=list[QuoteListResponse],
)
def get_my_quotes(
    current_user=Depends(get_current_user),
    use_case: GetCustomerQuotesUseCase = Depends(
        get_customer_quotes_usecase,
    ),
):
    return use_case.execute(
        current_user.id
    )

@router.get(
    "/action-required-count",
    response_model=QuoteActionRequiredCountResponse,
)
def get_action_required_quotes_count(
    current_user = Depends(get_current_user),

    usecase: GetClientQuoteActionRequiredCountUseCase = Depends(
        get_client_quote_action_required_count_usecase
    ),
):

    return usecase.execute(
        current_user.id
    )

@router.get(
    "/{id}",
    response_model=QuoteDetailCustomerResponse,
)
def get_customer_quote_detail(

    id: str,

    current_user=Depends(
        get_current_user
    ),

    use_case: GetCustomerQuoteDetailUseCase = Depends(
        get_customer_quote_detail_usecase
    ),

):

    return use_case.execute(
        quote_id=id,
        customer_id=current_user.id,
    )

@router.post(
    "/{quote_id}/accept",
    response_model=AcceptQuoteResponse,
)
async def accept_quote(

    quote_id: str,

    current_user=Depends(get_current_user),

    usecase: AcceptQuoteUseCase = Depends(
        get_accept_quote_usecase
    ),

):

    return await usecase.execute(
        quote_id=quote_id,
        customer_id=current_user.id,
    )


@router.post(
    "/{quote_id}/refuse",
    response_model=QuoteActionResponse,
)
async def refuse_quote(

    quote_id: str,

    request: RefuseQuoteRequest,

    current_user=Depends(get_current_user),

    usecase: RefuseQuoteUseCase = Depends(
        get_refuse_quote_usecase
    ),

):

    return await usecase.execute(

        quote_id=quote_id,

        customer_id=current_user.id,

        request=request,

    )