from modules.notifications.domain.enums import NotificationType, NotificationEntityType
from modules.quotes.domain.enums import QuoteStatus
from modules.quotes.domain.exceptions import QuoteNotFound, QuoteAlreadySent
from modules.leads.domain.exceptions import LeadNotFound
from modules.leads.domain.enums import LeadStatus
from modules.applications.domain.enums import (
    EventType
)
class SendQuoteUseCase:


    def __init__(
        self,
        quote_repository,
        lead_repository,
        lead_authorization,
        customer_account_service,
        email_service,
        notification_service,
        event_service,
        unit_of_work,
    ):
        self.quote_repository = quote_repository
        self.lead_repository = lead_repository
        self.lead_authorization = lead_authorization
        self.customer_account_service = customer_account_service
        self.email_service = email_service
        self.notification_service = notification_service
        self.event_service = event_service
        self.unit_of_work = unit_of_work



    async def execute(
    self,
    quote_id: str,
    agent_id: str,
):

        try:

            # =========================
            # FIND QUOTE
            # =========================

            quote = (
                self.quote_repository.find_by_id(
                    quote_id
                )
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


            vehicle = lead.vehicle


            # =========================
            # AUTHORIZATION
            # =========================

            self.lead_authorization.check_owner(
                lead,
                agent_id,
            )


            # =========================
            # STATUS
            # =========================

            if quote.status != QuoteStatus.DRAFT:
                raise QuoteAlreadySent()


            # =========================
            # CUSTOMER ACCOUNT
            # =========================

            account = (
                self.customer_account_service
                .ensure_account(
                    lead,
                    quote.id,
                )
            )

            customer = account["user"]
            activation_token = account["token"]


            # =========================
            # UPDATE QUOTE
            # =========================

            quote.send()

            self.quote_repository.update(
                quote
            )

            self.event_service.log(
    type=EventType.QUOTE_SENT,
    message="Devis envoyé au client",
    quote_id=quote.id,
    user_id=customer.id
)

            lead.change_status(LeadStatus.QUOTE_SENT)

            self.lead_repository.update(
    lead
)


            # =========================
            # NOTIFICATION CLIENT
            # =========================

            await self.notification_service.send(

                user_id=customer.id,

                email=customer.email,

                title=(
                    "Nouvelle offre commerciale"
                ),

                message=(
                    "Votre conseiller vous a envoyé "
                    "une nouvelle offre."
                ),

                notif_type=(
                    NotificationType.QUOTE_SENT
                ),

                entity_type=(
                    NotificationEntityType.QUOTE
                ),

                entity_id=(
                    quote.id
                ),
            )
            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()


        except Exception:

            self.unit_of_work.rollback()

            raise


        # =========================
        # EMAIL
        # =========================

        self.email_service.send_quote_email(
    quote=quote,
    customer=customer,
    vehicle=vehicle,
    activation_token=activation_token,
)
        return quote