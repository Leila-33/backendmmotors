from modules.leads.domain.exceptions import LeadNotFound
from modules.quotes.domain.exceptions import (
    QuoteNotFound,
    QuoteCannotBeDeleted
)
from modules.applications.domain.enums import (
    EventType
)
import logging

logger = logging.getLogger(__name__)

class DeleteQuoteUseCase:


    def __init__(
        self,
        quote_repository,
        quote_trade_in_repository,
        lead_repository,
        authorization,
        event_service,
        unit_of_work,
    ):

        self.quote_repository = quote_repository

        self.quote_trade_in_repository = (
            quote_trade_in_repository
        )

        self.lead_repository = lead_repository

        self.authorization = authorization
        self.event_service = event_service
        self.unit_of_work = unit_of_work



    def execute(
        self,
        quote_id: str,
        agent_id: str,
    ):

        try:

            # =========================
            # LOAD QUOTE
            # =========================

            quote = (
                self.quote_repository
                .find_by_id(
                    quote_id
                )
            )


            if quote is None:
                raise QuoteNotFound()



            # =========================
            # LOAD LEAD
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

            self.authorization.check_owner(
                lead,
                agent_id
            )



            # =========================
            # BUSINESS RULE
            # =========================

            if not quote.can_be_deleted():

                raise QuoteCannotBeDeleted()



            # =========================
            # DELETE TRADE IN
            # =========================

            trade_in = (
                self.quote_trade_in_repository
                .find_by_quote_id(
                    quote.id
                )
            )


            if trade_in:

                self.quote_trade_in_repository.delete(
                    quote.id
                )



            # =========================
            # DELETE QUOTE
            # =========================

            self.quote_repository.delete(
                quote.id
            )

            self.event_service.log(
    type=EventType.QUOTE_DELETED,
    message="Devis supprimé",
    quote_id=quote.id,
    user_id=agent_id,
    event_metadata={
        "quote_id": quote.id,
        "customer_email": quote.lead.customer.email,
    }
)

            self.unit_of_work.commit()



        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur suppression devis",
                extra={
                    "quote_id": quote_id
                }
            )

            raise