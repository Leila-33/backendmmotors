import logging
from datetime import datetime, timezone
from uuid import uuid4

from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import Forbidden

from modules.sav.application.dtos.create_ticket_message_dto import (
    CreateTicketMessageDTO,
)

from modules.sav.application.results.create_ticket_message_result import (
    CreateTicketMessageResult,
)

from modules.sav.domain.entities.ticket_message import (
    TicketMessage,
)

from modules.sav.domain.enums import TicketStatus

from modules.sav.domain.exceptions import (
    SupportTicketNotFound,
    TicketClosedException,
    EmptyMessageException,
    MessageTooLongException,
)


logger = logging.getLogger(__name__)


class CreateTicketMessageUseCase:

    def __init__(
        self,
        ticket_repository,
        message_repository,
        read_state_repository,
        unit_of_work,
    ):
        self.ticket_repository = ticket_repository
        self.message_repository = message_repository
        self.read_state_repository = read_state_repository
        self.unit_of_work = unit_of_work

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        dto: CreateTicketMessageDTO,
        user_id: str,
        user_role: UserRole,
    ) -> CreateTicketMessageResult:

        message = None

        try:

            # =================================================
            # LOAD TICKET
            # =================================================

            ticket = (
                self.ticket_repository
                .get_by_id(dto.ticket_id)
            )

            if ticket is None:
                raise SupportTicketNotFound()

            # =================================================
            # AUTHORIZATION
            # =================================================

            if (
                ticket.user_id != user_id
                and user_role not in (
                    UserRole.ADMIN,
                    UserRole.SAV_AGENT,
                )
            ):
                raise Forbidden()

            # =================================================
            # TICKET STATUS
            # =================================================

            if ticket.status == TicketStatus.CLOSED:
                raise TicketClosedException()

            # =================================================
            # MESSAGE VALIDATION
            # =================================================

            content = dto.message.strip()

            if not content:
                raise EmptyMessageException()

            if len(content) > 2000:
                raise MessageTooLongException()

            # =================================================
            # CREATE MESSAGE
            # =================================================

            message = TicketMessage(
                id=str(uuid4()),

                ticket_id=dto.ticket_id,

                sender_id=user_id,

                sender_role=user_role,

                message=content,

                created_at=datetime.now(
                    timezone.utc
                ),
            )

            message = (
                self.message_repository
                .create(message)
            )

            # =================================================
            # READ STATE
            # =================================================

            self.read_state_repository.mark_last_read(
                ticket_id=dto.ticket_id,
                user_id=user_id,
                last_read_at=message.created_at,
            )

            # =================================================
            # UPDATE TICKET
            # =================================================

            ticket.updated_at = datetime.now(
                timezone.utc
            )

            self.ticket_repository.update(
                ticket
            )

            # =================================================
            # COMMIT
            # =================================================

            self.unit_of_work.commit()

            # =================================================
            # LOG
            # =================================================

            logger.info(
                "Message ticket SAV créé",
                extra={
                    "ticket_id": dto.ticket_id,
                    "message_id": message.id,
                    "user_id": user_id,
                },
            )

            # =================================================
            # RESULT
            # =================================================

            return CreateTicketMessageResult(
                message=message,
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création message ticket SAV",
                extra={
                    "ticket_id": dto.ticket_id,
                    "user_id": user_id,
                    "message_id": (
                        message.id
                        if message
                        else None
                    ),
                },
            )

            raise