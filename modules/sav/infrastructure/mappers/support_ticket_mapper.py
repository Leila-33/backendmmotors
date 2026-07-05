from modules.sav.domain.entities.support_ticket import SupportTicket
from modules.sav.infrastructure.db.support_ticket_model import SupportTicketModel
from modules.sav.infrastructure.mappers.ticket_message_mapper import TicketMessageMapper
from modules.sav.api.schemas import SupportTicketResponseDTO, TicketMessageDTO

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
            messages=[
                TicketMessageMapper.to_domain(m)
                for m in model.messages
            ]
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
        )
    
    @staticmethod
    def to_response(ticket: SupportTicket) -> SupportTicketResponseDTO:

        return SupportTicketResponseDTO(
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
            messages=[
                TicketMessageDTO(
                    id=m.id,
                    sender_id=m.sender_id,
                    sender_role=m.sender_role,
                    message=m.message,
                    created_at=m.created_at,
                )
                for m in ticket.messages
            ],
        )
    
    @staticmethod
    def update_model(model: SupportTicketModel, ticket: SupportTicket):

        model.user_id = ticket.user_id
        model.application_id = ticket.application_id
        model.subject = ticket.subject
        model.description = ticket.description
        model.category = ticket.category
        model.status = ticket.status
        model.priority = ticket.priority
        model.assigned_to = ticket.assigned_to

        return model