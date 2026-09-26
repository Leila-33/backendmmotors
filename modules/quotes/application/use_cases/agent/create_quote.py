import logging
from datetime import datetime, timezone
from uuid import uuid4

from modules.applications.domain.enums import EventType

from modules.financing.domain.inputs.trade_in_input import (
    TradeInInput,
)

from modules.financing.domain.inputs.financing_input import (
    FinancingInput,
)

from modules.leads.domain.exceptions import (
    LeadNotFound,
    LeadHasActiveQuote,
)

from modules.quotes.domain.entities.quote import (
    Quote,
)

from modules.quotes.domain.entities.quote_trade_in import (
    QuoteTradeIn,
)

from modules.quotes.domain.enums import (
    QuoteStatus,
)

from modules.quotes.application.dtos.agent.create_quote_dto import (
    CreateQuoteDTO,
)

from modules.quotes.application.results.agent.create_quote_result import (
    CreateQuoteResult,
)


logger = logging.getLogger(__name__)


class CreateQuoteUseCase:

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

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        dto: CreateQuoteDTO,
    ) -> CreateQuoteResult:

        try:

            # =================================================
            # LOAD LEAD
            # =================================================

            lead = (
                self.lead_repository
                .find_by_id(
                    dto.lead_id
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
            # ACTIVE QUOTE
            # =================================================

            existing_quote = (
                self.quote_repository
                .find_active_by_lead(
                    lead.id
                )
            )

            if existing_quote:
                raise LeadHasActiveQuote()

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
            # CREATE QUOTE
            # =================================================

            quote = Quote(

                id=str(uuid4()),

                lead_id=lead.id,

                base_price=vehicle.price,

                discount=dto.discount,

                down_payment=dto.down_payment,

                trade_in_value=trade_in_value,

                duration_months=(
                    dto.duration_months
                ),

                financed_amount=(
                    financing.financed_amount
                ),

                monthly_payment=(
                    financing.monthly_payment
                ),

                status=QuoteStatus.DRAFT,

                created_at=datetime.now(
                    timezone.utc
                ),
            )

            self.quote_repository.save(
                quote
            )

            # =================================================
            # EVENT
            # =================================================

            self.event_service.log(
    type=EventType.QUOTE_CREATED,
    message="Devis créé",
    vehicle_id=vehicle.id,
    quote_id=quote.id,
    lead_id=lead.id,
    user_id=dto.agent_id,
    event_metadata={
        "base_price": quote.base_price,
        "discount": quote.discount,
        "down_payment": quote.down_payment,
        "trade_in_value": quote.trade_in_value,
        "financed_amount": quote.financed_amount,
        "monthly_payment": quote.monthly_payment,
        "duration_months": quote.duration_months,
    },
)

            # =================================================
            # TRADE-IN DETAILS
            # =================================================

            if dto.trade_in:

                quote_trade_in = QuoteTradeIn(

                    quote_id=quote.id,

                    brand=dto.trade_in.brand,

                    model=dto.trade_in.model,

                    year=dto.trade_in.year,

                    mileage=dto.trade_in.mileage,

                    condition=dto.trade_in.condition,

                    estimated_value=trade_in_value,
                )

                self.quote_trade_in_repository.save(
                    quote_trade_in
                )

            # =================================================
            # COMMIT
            # =================================================

            self.unit_of_work.commit()

            # =================================================
            # LOG SUCCESS
            # =================================================

            logger.info(
                "Devis créé avec succès",
                extra={
                    "quote_id": quote.id,
                    "lead_id": lead.id,
                    "vehicle_id": vehicle.id,
                    "agent_id": dto.agent_id,
                },
            )

            # =================================================
            # RESULT
            # =================================================

            return CreateQuoteResult(
                quote_id=quote.id,
                lead_id=lead.id,
                vehicle_id=vehicle.id,
                message="Devis créé avec succès",
            )

        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création devis",
                extra={
                    "lead_id": dto.lead_id,
                },
            )

            raise