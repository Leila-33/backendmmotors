from modules.sav.domain.entities.support_ticket import SupportTicket
from modules.sav.infrastructure.db.support_ticket_model import SupportTicketModel
from modules.sav.infrastructure.mappers.ticket_message_mapper import TicketMessageMapper
from modules.sav.api.schemas import (
    SupportTicketResponse,
    TicketMessageResponse,
    SupportTicketListItemResponse,
)
from modules.auth.domain.enums import UserRole
from core.pagination.paginated_result import PaginatedResult
from core.pagination.paginated_response import PaginatedResponse

class SupportTicketMapper:

    @staticmethod
    def to_domain(model: SupportTicketModel) -> SupportTicket:

        return SupportTicket(
            id=model.id,
            user_id=model.user_id,
            application_id=model.application_id,
            subject=model.subject,
            description=model.description,
            category=model.category,
            status=model.status,
            priority=model.priority,
            assigned_to=model.assigned_to,
            created_at=model.created_at,
            updated_at=model.updated_at,
            archived_at=model.archived_at,
            messages=[
                TicketMessageMapper.to_domain(message)
                for message in model.messages
            ],
        )

    @staticmethod
    def to_model(entity: SupportTicket) -> SupportTicketModel:

        return SupportTicketModel(
            id=entity.id,
            user_id=entity.user_id,
            application_id=entity.application_id,
            subject=entity.subject,
            description=entity.description,
            category=entity.category,
            status=entity.status,
            priority=entity.priority,
            assigned_to=entity.assigned_to,
            archived_at=entity.archived_at,
        )

    @staticmethod
    def to_response(ticket: SupportTicket) -> SupportTicketResponse:

        return SupportTicketResponse(
            id=ticket.id,
            user_id=ticket.user_id,
            application_id=ticket.application_id,
            subject=ticket.subject,
            description=ticket.description,
            category=ticket.category,
            status=ticket.status,
            priority=ticket.priority,
            assigned_to=ticket.assigned_to,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,

            archived_at=ticket.archived_at,
            messages=[
                TicketMessageResponse(
                    id=message.id,
                    sender_id=message.sender_id,
                    sender_role=(
                        UserRole(message.sender_role)
                        if isinstance(message.sender_role, str)
                        else message.sender_role
                    ),
                    message=message.message,
                    created_at=message.created_at,
                )
                for message in ticket.messages
            ],
        )

    @staticmethod
    def update_model(
        model: SupportTicketModel,
        ticket: SupportTicket,
    ):

        model.user_id = ticket.user_id
        model.application_id = ticket.application_id
        model.subject = ticket.subject
        model.description = ticket.description
        model.category = ticket.category
        model.status = ticket.status
        model.priority = ticket.priority
        model.assigned_to = ticket.assigned_to
        model.archived_at = ticket.archived_at

        return model

    @staticmethod
    def to_paginated_response(
        result: PaginatedResult,
    ) -> PaginatedResponse[SupportTicketListItemResponse]:

        return PaginatedResponse(
            items=[
                SupportTicketListItemResponse(
                    id=item.id,
                    subject=item.subject,
                    category=item.category,
                    status=item.status,
                    priority=item.priority,
                    user_id=item.user_id,
                    user_name=item.user_name,
                    last_message_preview=item.last_message_preview,
                    last_actor=item.last_actor,
                    last_activity_at=item.last_activity_at,
                    unread=item.unread,
                    created_at=item.created_at,
                    updated_at=item.updated_at,
                    archived_at=item.archived_at,
                )
                for item in result.items
            ],
            page=result.page,
            limit=result.limit,
            total=result.total,
            total_pages=result.total_pages,
        )
