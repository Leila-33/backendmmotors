from modules.quotes.domain.exceptions import QuoteNotFound
from modules.notifications.domain.enums import (
    NotificationType,
    NotificationEntityType,
)
from modules.leads.domain.exceptions import LeadNotFound
from modules.leads.domain.enums import LeadStatus
from modules.applications.domain.enums import EventType

from modules.quotes.application.dtos.refuse_quote_dto import (
    RefuseQuoteDTO,
)
from modules.quotes.application.results.quote_action_result import (
    QuoteActionResult,
)

import logging

logger = logging.getLogger(__name__)


class RefuseQuoteUseCase:
    """
    Refuse un devis à la demande du client après vérification
    de son accès au devis.

    Le devis est marqué comme refusé, le lead passe à l'état perdu,
    puis l'action est enregistrée dans l'historique des événements
    et l'agent concerné est notifié.
    """
    def __init__(
        self,
        quote_repository,
        lead_repository,
        notification_service,
        event_service,
        unit_of_work,
    ):
        self.quote_repository = quote_repository
        self.lead_repository = lead_repository
        self.notification_service = notification_service
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    async def execute(
        self,
        dto: RefuseQuoteDTO,
    ) -> QuoteActionResult:

        quote = None

        try:

            # =========================
            # QUOTE
            # =========================

            quote = (
                self.quote_repository
                .find_by_id(dto.quote_id)
            )

            if quote is None:
                raise QuoteNotFound()

            # =========================
            # LEAD
            # =========================

            lead = (
                self.lead_repository
                .find_by_id(
                    quote.lead_id
                )
            )

            if lead is None:
                raise LeadNotFound()

            # =========================
            # AUTHORIZATION
            # =========================

            if lead.user_id != dto.customer_id:
                raise QuoteNotFound()

            # =========================
            # REFUSE QUOTE
            # =========================

            quote.refuse(
                reason=dto.reason,
                comment=dto.comment,
            )

            self.quote_repository.update(
                quote
            )

            # =========================
            # LEAD LOST
            # =========================

            lead.change_status(
                LeadStatus.LOST
            )

            self.lead_repository.update(
                lead
            )

            # =========================
            # EVENT
            # =========================

            self.event_service.log(
                type=EventType.QUOTE_REFUSED,
                message="Devis refusé par le client",
                quote_id=quote.id,
                lead_id=lead.id,
                user_id=dto.customer_id,
                vehicle_id=lead.vehicle_id,
                event_metadata={
                    "reason": quote.refusal_reason,
                    "comment": quote.refusal_comment,
                },
            )

            # =========================
            # NOTIFICATION
            # =========================

            await self.notification_service.send(

                user_id=lead.assigned_to,

                title="Offre refusée",

                message=(
                    "Le client a refusé votre offre."
                ),

                notif_type=(
                    NotificationType.QUOTE_REFUSED
                ),

                entity_type=(
                    NotificationEntityType.QUOTE
                ),

                entity_id=quote.id,
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()


            # =========================
            # COUNT ACTIONS REQUIRED
            # =========================

            count = (
                self.quote_repository
                .count_action_required_by_customer(
                    dto.customer_id
                )
            )

            await self.notification_service.send_update(
                user_id=dto.customer_id,
                payload={
                    "type": "QUOTE_UPDATED",
                    "count": count,
                },
            )
            # =========================
            # LOG
            # =========================

            logger.info(
                "Devis refusé",
                extra={
                    "quote_id": quote.id,
                    "customer_id": dto.customer_id,
                },
            )

            # =========================
            # RESULT
            # =========================

            return QuoteActionResult(
                quote_id=quote.id,
                message="Offre refusée avec succès.",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur refus devis",
                extra={
                    "quote_id": dto.quote_id,
                    "customer_id": dto.customer_id,
                },
            )

            raise
