from modules.leads.domain.exceptions import LeadNotFound
from modules.quotes.domain.exceptions import (
    QuoteNotFound,
    QuoteCannotBeDeleted
)

class DeleteQuoteUseCase:


    def __init__(
        self,
        quote_repository,
        quote_trade_in_repository,
        lead_repository,
        authorization,
        unit_of_work,
    ):

        self.quote_repository = quote_repository

        self.quote_trade_in_repository = (
            quote_trade_in_repository
        )

        self.lead_repository = lead_repository

        self.authorization = authorization

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



            self.unit_of_work.commit()



        except Exception:

            self.unit_of_work.rollback()

            raise