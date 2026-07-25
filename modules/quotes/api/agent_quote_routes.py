from fastapi import APIRouter, Depends, status

from modules.quotes.api.schemas import (
    QuoteResponse,
    CreateQuoteRequest,
    QuoteDetailResponse,
    UpdateQuoteRequest
    )
from modules.quotes.api.dependencies import (
    get_create_quote_usecase,
    get_get_quote_detail_usecase,
    get_send_quote_usecase,
    get_update_quote_usecase,
    get_delete_quote_usecase
)
from core.security.dependencies import get_current_sales_agent
from modules.quotes.application.use_cases.agent.create_quote import CreateQuoteUseCase
from modules.quotes.application.use_cases.agent.get_quote_detail import GetQuoteDetailUseCase
from modules.quotes.application.use_cases.agent.send_quote import SendQuoteUseCase
from modules.quotes.application.use_cases.agent.update_quote import UpdateQuoteUseCase
from modules.quotes.application.use_cases.agent.delete_quote import DeleteQuoteUseCase

router = APIRouter(tags=["Agent Quotes"])


@router.post(
    "",
    response_model=QuoteResponse
)
def create_quote(

    request: CreateQuoteRequest,

    use_case: CreateQuoteUseCase = Depends(
        get_create_quote_usecase
    ),

    current_user = Depends(
        get_current_sales_agent
    )

):

    return use_case.execute(

        request,

        agent_id=current_user.id

    )

@router.get(
    "/{quote_id}",
    response_model=QuoteDetailResponse,
)
def get_quote(
    quote_id: str,
    current_user=Depends(get_current_sales_agent),
    use_case: GetQuoteDetailUseCase = Depends(
        get_get_quote_detail_usecase
    ),
):
    return use_case.execute(
        quote_id=quote_id,
        agent_id=current_user.id,
    )






@router.put(
    "/{quote_id}",
    response_model=QuoteResponse,
    status_code=status.HTTP_200_OK,
)
def update_quote(
    quote_id: str,

    request: UpdateQuoteRequest,

    agent = Depends(
        get_current_sales_agent
    ),

    usecase: UpdateQuoteUseCase = Depends(
        get_update_quote_usecase
    ),
):


    quote = usecase.execute(

        quote_id=quote_id,

        request=request,

        agent_id=agent.id,

    )


    return quote

@router.post(
    "/{quote_id}/send",
    response_model=QuoteDetailResponse,
)
async def send_quote(
    quote_id: str,
    current_user=Depends(get_current_sales_agent),
    use_case: SendQuoteUseCase = Depends(
        get_send_quote_usecase,
    ),
):

    return await use_case.execute(
        quote_id=quote_id,
        agent_id=current_user.id,
    )

@router.delete(
    "/{quote_id}",
    status_code=204,
)
def delete_quote(

    quote_id: str,

    agent = Depends(
        get_current_sales_agent
    ),

    usecase: DeleteQuoteUseCase = Depends(
        get_delete_quote_usecase
    ),

):

    usecase.execute(

        quote_id=quote_id,

        agent_id=agent.id,

    )
