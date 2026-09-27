import logging

from modules.quotes.domain.entities.quote_trade_in import (
    QuoteTradeIn,
)

from modules.financing.domain.inputs.trade_in_input import (
    TradeInInput,
)
from modules.financing.domain.inputs.financing_input import (
    FinancingInput,
)
from modules.leads.domain.exceptions import (
    LeadNotFound,
)

from modules.quotes.domain.exceptions import (
    QuoteNotFound,
)

from modules.applications.domain.enums import (
    EventType,
)

from modules.quotes.application.dtos.agent.update_quote_dto import (
    UpdateQuoteDTO,
)

from modules.quotes.application.results.quote_action_result import (
    QuoteActionResult,
)


logger = logging.getLogger(__name__)


class UpdateQuoteUseCase:
    """
    Met à jour un devis après vérification des droits de l'agent.

    Les nouvelles informations de financement et de reprise sont recalculées,
    puis les données de reprise associées au devis sont créées, modifiées
    ou supprimées selon les informations fournies.
    """
    def __init__(
        self,
        quote_repository,
        quote_trade_in_repository,
        lead_repository,
        financing_service,
        trade_in_service,
        authorization,
        event_service,
        unit_of_work,
    ):

        self.quote_repository = quote_repository
        self.quote_trade_in_repository = (
            quote_trade_in_repository
        )
        self.lead_repository = lead_repository
        self.financing_service = financing_service
        self.trade_in_service = trade_in_service
        self.authorization = authorization
        self.event_service = event_service
        self.unit_of_work = unit_of_work

    def execute(
        self,
        dto: UpdateQuoteDTO,
    ) -> QuoteActionResult:

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
            # VEHICLE
            # =================================================

            vehicle = lead.vehicle

            # =================================================
            # TRADE-IN
            # =================================================

            trade_in_value = 0

            if dto.trade_in:

                trade_in_value = (
                    self.trade_in_service
                    .estimate(
                        TradeInInput(
                            brand=dto.trade_in.brand,
                            model=dto.trade_in.model,
                            year=dto.trade_in.year,
                            mileage=dto.trade_in.mileage,
                            condition=dto.trade_in.condition,
                        )
                    )
                ).estimated_value

            # =================================================
            # FINANCING
            # =================================================

            financing = (
                self.financing_service
                .calculate(
                    FinancingInput(
                        total_price=(
                            vehicle.price
                            - dto.discount
                        ),
                        down_payment=(
                            dto.down_payment
                        ),
                        trade_in_value=(
                            trade_in_value
                        ),
                        duration_months=(
                            dto.duration_months
                        ),
                    )
                )
            )

            # =================================================
            # DOMAIN UPDATE
            # =================================================

            quote.update_financing(

                base_price=vehicle.price,

                discount=dto.discount,

                down_payment=dto.down_payment,

                trade_in_value=trade_in_value,

                duration_months=dto.duration_months,

                financed_amount=(
                    financing.financed_amount
                ),

                monthly_payment=(
                    financing.monthly_payment
                ),
            )

            self.quote_repository.update(
                quote
            )

            # =================================================
            # TRADE-IN DETAILS
            # =================================================

            existing_trade_in = (
                self.quote_trade_in_repository
                .find_by_quote_id(
                    quote.id
                )
            )

            if dto.trade_in:

                if existing_trade_in:

                    existing_trade_in.update(

                        brand=dto.trade_in.brand,

                        model=dto.trade_in.model,

                        year=dto.trade_in.year,

                        mileage=dto.trade_in.mileage,

                        condition=dto.trade_in.condition,

                        estimated_value=trade_in_value,
                    )

                    self.quote_trade_in_repository.update(
                        existing_trade_in
                    )

                else:

                    trade_in = QuoteTradeIn(

                        quote_id=quote.id,

                        brand=dto.trade_in.brand,

                        model=dto.trade_in.model,

                        year=dto.trade_in.year,

                        mileage=dto.trade_in.mileage,

                        condition=dto.trade_in.condition,

                        estimated_value=trade_in_value,
                    )

                    self.quote_trade_in_repository.save(
                        trade_in
                    )

            else:

                if existing_trade_in:

                    self.quote_trade_in_repository.delete(
                        existing_trade_in.quote_id
                    )

            # =================================================
            # EVENT
            # =================================================

            self.event_service.log(

                type=EventType.QUOTE_UPDATED,

                message="Devis mis à jour",

                quote_id=quote.id,

                lead_id=lead.id,

                user_id=dto.agent_id,

                vehicle_id=vehicle.id,

                event_metadata={
                    "financed_amount": (
                        financing.financed_amount
                    ),
                    "trade_in_value": (
                        trade_in_value
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
                "Devis mis à jour avec succès",
                extra={
                    "quote_id": quote.id,
                    "agent_id": dto.agent_id,
                },
            )

            # =================================================
            # RESULT
            # =================================================

            return QuoteActionResult(

                quote_id=quote.id,

                message="Devis mis à jour avec succès",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur lors de la mise à jour du devis",
                extra={
                    "quote_id": dto.quote_id,
                    "agent_id": dto.agent_id,
                },
            )

            raise