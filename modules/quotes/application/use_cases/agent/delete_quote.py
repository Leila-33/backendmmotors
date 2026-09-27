import logging

from modules.leads.domain.exceptions import (
    LeadNotFound,
)

from modules.quotes.domain.exceptions import (
    QuoteNotFound,
    QuoteCannotBeDeleted,
)

from modules.applications.domain.enums import (
    EventType,
)

from modules.quotes.application.dtos.agent.quote_agent_dto import (
    QuoteAgentDTO,
)

from modules.quotes.application.results.quote_action_result import (
    QuoteActionResult,
)


logger = logging.getLogger(__name__)


class DeleteQuoteUseCase:
    """
    Supprime un devis après vérification des droits de l'agent
    et des règles métier autorisant sa suppression.

    Les informations de reprise associées sont également supprimées,
    puis la suppression est enregistrée dans l'historique des événements.
    """
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

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        dto: QuoteAgentDTO,
    ) -> QuoteActionResult:

        quote_id = dto.quote_id

        try:

            # =================================================
            # LOAD QUOTE
            # =================================================

            quote = (
                self.quote_repository
                .find_by_id(
                    dto.quote_id
                )
            )

            if quote is None:
                raise QuoteNotFound()

            # =================================================
            # LOAD LEAD
            # =================================================

            lead = (
                self.lead_repository
                .find_by_id(
                    quote.lead_id
                )
            )

            if lead is None:
                raise LeadNotFound()

            # =================================================
            # AUTHORIZATION
            # =================================================

            self.authorization.check_owner(
                lead,
                dto.agent_id,
            )

            # =================================================
            # BUSINESS RULE
            # =================================================

            if not quote.can_be_deleted():

                raise QuoteCannotBeDeleted()

            # =================================================
            # DELETE TRADE-IN
            # =================================================

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

            # =================================================
            # DELETE QUOTE
            # =================================================

            self.quote_repository.delete(
                quote.id
            )

            # =================================================
            # EVENT
            # =================================================

            self.event_service.log(

                type=EventType.QUOTE_DELETED,

                message="Devis supprimé",

                quote_id=quote.id,

                lead_id=lead.id,

                vehicle_id=lead.vehicle_id,

                user_id=dto.agent_id,

                event_metadata={
                    "quote_id": quote.id,
                    "customer_email": (
                        lead.email
                    ),
                },
            )

            # =================================================
            # COMMIT
            # =================================================

            self.unit_of_work.commit()

            # =================================================
            # SUCCESS LOG
            # =================================================

            logger.info(
                "Devis supprimé avec succès",
                extra={
                    "quote_id": quote.id,
                    "lead_id": lead.id,
                    "agent_id": dto.agent_id,
                },
            )

            # =================================================
            # RESULT
            # =================================================

            return QuoteActionResult(
                quote_id=quote.id,
                message="Devis supprimé avec succès",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur suppression devis",
                extra={
                    "quote_id": quote_id,
                },
            )

            raise