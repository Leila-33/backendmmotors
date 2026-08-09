from modules.quotes.domain.exceptions import QuoteNotFound
from modules.notifications.domain.enums import NotificationType, NotificationEntityType
from modules.quotes.api.schemas import QuoteActionResponse
from modules.leads.domain.exceptions import LeadNotFound
from modules.leads.domain.enums import LeadStatus
from modules.applications.domain.enums import EventType
import logging

logger = logging.getLogger(__name__)

class RefuseQuoteUseCase:


    def __init__(

        self,
        quote_repository,
        lead_repository,
        notification_service,
        event_service,
        unit_of_work
    ):

        self.quote_repository = quote_repository
        self.lead_repository = lead_repository
        self.notification_service = notification_service
        self.event_service = event_service
        self.unit_of_work = unit_of_work




    async def execute(

        self,

        quote_id: str,

        customer_id: str,

        request

    ):

        try:
            quote = self.quote_repository.find_by_id(
                quote_id
            )

            if quote is None:
                raise QuoteNotFound()
            
            lead = (
                    self.lead_repository
                    .find_by_id(
                        quote.lead_id
                    )
                )

            if lead is None:
                    raise LeadNotFound()
                
            if lead.user_id != customer_id:
                    raise QuoteNotFound()




            quote.refuse(

                reason=request.reason,

                comment=request.comment,

            )


            self.quote_repository.update(
                quote
            )
            
            self.event_service.log(
    type=EventType.QUOTE_REFUSED,
    message="Devis refusé par le client",
    quote_id=quote.id,
    user_id=customer_id,
    event_metadata={
        "quote_id": quote.id,
        "reason": quote.refusal_reason
    }
)
            lead.change_status(LeadStatus.LOST)

            self.lead_repository.update(
    lead
)


            await self.notification_service.send(

                user_id=lead.assigned_to,

                title="Offre refusée",

                message=(
                    "Le client a refusé votre offre."
                ),

                notif_type=NotificationType.QUOTE_REFUSED,

                entity_type=NotificationEntityType.QUOTE,

                entity_id=quote.id,

            )
            self.unit_of_work.commit()

            logger.info(
    "Devis refusé",
    extra={
        "quote_id": quote.id
    }
)
            return QuoteActionResponse(
        message="Offre refusée avec succès."
    )
        except Exception:

            self.unit_of_work.rollback()
       
            logger.exception(
                "Erreur refus devis",
                extra={
                    "quote_id": quote_id
                }
            )

            raise


