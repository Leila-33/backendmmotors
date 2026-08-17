import logging

from modules.quotes.domain.exceptions import QuoteNotFound
from modules.leads.domain.exceptions import LeadNotFound
from modules.applications.domain.enums import EventType

from modules.applications.domain.entities.application import (
    Application,
)
from modules.applications.domain.entities.application_financing import (
    ApplicationFinancing,
)
from modules.applications.domain.entities.application_trade_in import (
    ApplicationTradeIn,
)

from modules.notifications.domain.enums import (
    NotificationType,
)
from modules.quotes.application.results.accept_quote_result import (
    AcceptQuoteResult,
)
from modules.quotes.application.results.accept_quote_result import (
    AcceptQuoteResult,
)


logger = logging.getLogger(__name__)


class AcceptQuoteUseCase:

    def __init__(
        self,
        quote_repository,
        application_repository,
        trade_in_repository,
        financing_repository,
        lead_repository,
        notification_service,
        event_service,
        unit_of_work,
    ):
        self.quote_repository = quote_repository

        self.application_repository = (
            application_repository
        )

        self.trade_in_repository = (
            trade_in_repository
        )

        self.financing_repository = (
            financing_repository
        )

        self.lead_repository = (
            lead_repository
        )

        self.notification_service = (
            notification_service
        )

        self.event_service = event_service

        self.unit_of_work = unit_of_work

    async def execute(
        self,
        dto: AcceptQuoteDTO
    ) -> AcceptQuoteResult:

        try:

            # =========================
            # FIND QUOTE
            # =========================

            quote = (
                self.quote_repository
                .find_by_id(dto.quote_id)
            )

            if quote is None:
                raise QuoteNotFound()


            # =========================
            # FIND LEAD
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
            # ACCEPT QUOTE
            # =========================

            quote.accept()

            self.quote_repository.update(
                quote
            )


            # =========================
            # CREATE APPLICATION
            # =========================

            application = (
                Application.create_draft_from_quote(
                    quote,
                    lead,
                )
            )

            self.application_repository.save(
                application
            )


            # =========================
            # FINANCING
            # =========================

            self.financing_repository.save(
                ApplicationFinancing(
                    application_id=application.id,
                    down_payment=(
                        quote.financing.down_payment
                    ),
                    duration_months=(
                        quote.financing.duration_months
                    ),
                    financed_amount=(
                        quote.financed_amount
                    ),
                    monthly_payment=(
                        quote.monthly_payment
                    ),
                )
            )


            # =========================
            # TRADE-IN
            # =========================

            if quote.trade_in:

                self.trade_in_repository.save(
                    ApplicationTradeIn(
                        application_id=application.id,
                        brand=quote.trade_in.brand,
                        model=quote.trade_in.model,
                        year=quote.trade_in.year,
                        mileage=quote.trade_in.mileage,
                        condition=quote.trade_in.condition,
                        estimated_value=(
                            quote.trade_in_value
                        ),
                    )
                )


            # =========================
            # QUOTE ACCEPTED EVENT
            # =========================

            self.event_service.log(
                type=EventType.QUOTE_ACCEPTED,
                message="Devis accepté",
                quote_id=quote.id,
                lead_id=lead.id,
                vehicle_id=lead.vehicle_id,
                application_id=application.id,
                user_id=dto.customer_id,
            )


            # =========================
            # APPLICATION CREATED EVENT
            # =========================

            self.event_service.log(
                application_id=application.id,
                type=EventType.APPLICATION_CREATED,
                quote_id=quote.id,
                lead_id=lead.id,
                vehicle_id=lead.vehicle_id,
                message=(
                    "Brouillon du dossier créé "
                    "suite à l'acceptation de l'offre."
                ),
                user_id=dto.customer_id,
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

                notif_type=(
                    NotificationType.QUOTE_ACCEPTED
                ),

                entity_type="quote",

                entity_id=quote.id,
            )


            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()


            logger.info(
                "Devis accepté",
                extra={
                    "quote_id": quote.id,
                    "application_id": application.id,
                    "customer_id": dto.customer_id,
                },
            )


            # =========================
            # RESULT
            # =========================

            return AcceptQuoteResult(
                quote_id=quote.id,
                application_id=application.id,
                message=(
                    "Votre offre a été acceptée. "
                    "Votre dossier est maintenant créé."
                ),
            )


        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur acceptation devis",
                extra={
                    "quote_id": dto.quote_id,
                    "customer_id": dto.customer_id,
                },
            )

            raise

