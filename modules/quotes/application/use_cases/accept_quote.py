from modules.quotes.domain.exceptions import QuoteNotFound
from modules.applications.domain.enums import EventType
from modules.notifications.domain.enums import NotificationType
from modules.quotes.api.schemas import AcceptQuoteResponse
from modules.applications.domain.entities.application import Application
from modules.applications.infrastructure.mappers.application_mapper import ApplicationMapper
from modules.applications.domain.entities.application_financing import ApplicationFinancing
from modules.applications.api.schemas import TradeInSnapshot
from modules.leads.domain.exceptions import LeadNotFound
from modules.applications.domain.enums import (
    EventType
)

class AcceptQuoteUseCase:


    def __init__(
        self,
        quote_repository,
        application_repository,
        lead_repository,
        event_repository,
        notification_service,
        email_service,
        event_service,
        unit_of_work
    ):

        self.quote_repository = quote_repository
        self.application_repository = application_repository
        self.lead_repository = lead_repository
        self.event_repository = event_repository
        self.notification_service = notification_service
        self.email_service = email_service
        self.event_service = event_service
        self.unit_of_work = unit_of_work



    async def execute(
        self,
        quote_id: str,
        customer_id: str,
    ):

        try:

            # =========================
            # FIND QUOTE
            # =========================

            quote = (
                self.quote_repository
                .find_by_id(quote_id)
            )

            if not quote:
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


            # =========================
            # ACCEPT QUOTE
            # =========================

            quote.accept()

            self.quote_repository.update(
                quote
            )

            self.event_service.log(
    type=EventType.QUOTE_ACCEPTED,
    message="Devis accepté",
    quote_id=quote.id,
    application_id=application.id,
    user_id=customer_id
)
            # =========================
            # CREATE APPLICATION
            # =========================

            application = Application.create_draft_from_quote(
                quote, lead
                )

            
            

            self.application_repository.create_base(
                **ApplicationMapper.to_dict(
                    application
                )
            )


            # =========================
            # FINANCING SNAPSHOT
            # =========================

            financing_snapshot = ApplicationFinancing(

                down_payment=quote.down_payment,

                duration_months=quote.duration_months,

                financed_amount=quote.financed_amount,

                monthly_payment=quote.monthly_payment,
            )

            self.application_repository.save_financing(

                application_id=application.id,

                data=financing_snapshot,
            )


            # =========================
            # TRADE-IN SNAPSHOT
            # =========================

            if quote.trade_in:

                trade_in_snapshot = TradeInSnapshot(

                    brand=quote.trade_in.brand,

                    model=quote.trade_in.model,

                    year=quote.trade_in.year,

                    mileage=quote.trade_in.mileage,

                    condition=quote.trade_in.condition,
                )

                self.application_repository.save_trade_in(

                    application_id=application.id,

                    trade_in_value=quote.trade_in_value,

                    data=trade_in_snapshot,
                )


            # =========================
            # EVENT
            # =========================

            self.event_service.log(

                application_id=application.id,

                type=EventType.APPLICATION_CREATED,

                message=(
                    "Brouillon du dossier créé "
                    "suite à l'acceptation de l'offre."
                ),

                user_id=customer_id
            )

            # =========================
            # NOTIFICATION
            # =========================

            await self.notification_service.send(

                user_id=lead.assigned_to,

                title="Offre acceptée",

                message=(
                    "Le client a accepté votre offre."
                ),

                notif_type=NotificationType.QUOTE_ACCEPTED,

                entity_type="quote",

                entity_id=quote.id,
            )

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()


        except Exception:

            self.unit_of_work.rollback()

            raise


        return AcceptQuoteResponse(

            message=(
                "Votre offre a été acceptée. "
                "Votre dossier est maintenant créé."
            ),

            application_id=application.id,
        )