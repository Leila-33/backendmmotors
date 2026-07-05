from fastapi import APIRouter, WebSocket, Depends

from modules.sav.api.dependencies import get_ticket_chat_usecase
from modules.sav.application.use_cases.ticket_chat_use_case import TicketChatUseCase
router = APIRouter(tags=["ws Support Tickets"])


@router.websocket("/{ticket_id}")
async def ticket_chat(
    websocket: WebSocket,
    ticket_id: str,
    use_case: TicketChatUseCase = Depends(get_ticket_chat_usecase)
):
    await use_case.handle_connection(websocket, ticket_id)