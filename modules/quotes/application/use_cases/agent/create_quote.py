from modules.leads.domain.enums import LeadStatus
import uuid
from modules.quotes.domain.entities.quote import Quote
from modules.financing.api.schemas import FinancingRequest
from datetime import datetime, timezone

from modules.quotes.domain.entities.quote_trade_in import QuoteTradeIn
from modules.quotes.domain.enums import QuoteStatus
from modules.financing.api.schemas import FinancingRequest
from modules.financing.domain.entities.trade_in_input import TradeInInput
from modules.leads.domain.exceptions import (
    LeadNotFound,
    LeadHasActiveQuote
)
from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.applications.domain.enums import (
    EventType
)
import logging

logger = logging.getLogger(__name__)

class CreateQuoteUseCase:

    def __init__(
        self,
        quote_repository,
        quote_trade_in_repository,
        lead_repository,
        vehicle_repository,
        financing_service,
        trade_in_service,
        authorization,
        event_service,
        unit_of_work
    ):

        self.quote_repository = quote_repository
        self.quote_trade_in_repository = quote_trade_in_repository

        self.lead_repository = lead_repository
        self.vehicle_repository = vehicle_repository

        self.financing_service = financing_service
        self.trade_in_service = trade_in_service

        self.authorization = authorization
        self.event_service = event_service
        self.unit_of_work = unit_of_work



    def execute(
        self,
        request,
        agent_id,
    ):
        try:


            # =====================================
            # LOAD LEAD
            # =====================================

            lead = self.lead_repository.find_by_id(
                request.lead_id
            )

            if not lead:
                raise LeadNotFound()


            # =====================================
            # AUTHORIZATION
            # =====================================

            self.authorization.check_owner(
                lead,
                agent_id
            )


            # =====================================
            # BUSINESS RULE
            # =====================================

            existing_quote = (
                self.quote_repository.find_active_by_lead(
                    lead.id
                )
            )

            if existing_quote:
                raise LeadHasActiveQuote()



            # =====================================
            # VEHICLE
            # =====================================

            vehicle = self.vehicle_repository.get_by_id(
                lead.vehicle_id
            )

            if not vehicle:
                raise VehicleNotFound()



            # =====================================
            # TRADE IN ESTIMATION
            # =====================================

            trade_in_value = 0

            if request.trade_in:

                trade_in_value = (
                    self.trade_in_service.estimate(
                        TradeInInput(

                            brand=request.trade_in.brand,

                            model=request.trade_in.model,

                            year=request.trade_in.year,

                            mileage=request.trade_in.mileage,

                            condition=request.trade_in.condition,
                        )
                    )
                )



            # =====================================
            # FINANCING
            # =====================================

            financing = (
                self.financing_service.calculate(

                    FinancingRequest(

                        total_price=
                            vehicle.price
                            - request.discount,

                        down_payment=
                            request.down_payment,

                        trade_in_value=
                            trade_in_value,

                        duration_months=
                            request.duration_months,
                    )
                )
            )



            # =====================================
            # CREATE QUOTE
            # =====================================

            quote = Quote(

                id=str(uuid.uuid4()),

                lead_id=lead.id,

                base_price=vehicle.price,

                discount=request.discount,

                down_payment=request.down_payment,

                trade_in_value=trade_in_value,

                duration_months=request.duration_months,

                financed_amount=
                    financing.financed_amount,

                monthly_payment=
                    financing.monthly_payment,

                status=QuoteStatus.DRAFT,

                created_at=datetime.now(timezone.utc),
            )


            self.quote_repository.save(
                quote
            )

            self.event_service.log(
    type=EventType.QUOTE_CREATED,
    message="Devis créé",
    vehicle_id=vehicle.id,
    quote_id=quote.id,
    user_id=agent_id,
    event_metadata={
        "amount": quote.total_amount
    }
)

            # =====================================
            # SAVE TRADE IN DETAILS
            # =====================================

            if request.trade_in:


                quote_trade_in = QuoteTradeIn(

                    quote_id=quote.id,

                    brand=request.trade_in.brand,

                    model=request.trade_in.model,

                    year=request.trade_in.year,

                    mileage=request.trade_in.mileage,

                    condition=request.trade_in.condition,

                    estimated_value=trade_in_value,

                )


                self.quote_trade_in_repository.save(
                    quote_trade_in
                )

            self.unit_of_work.commit()

            logger.info(
                "Devis créé",
                extra={
                    "quote_id": quote.id
                }
            )


            return quote


        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur création devis",
                extra={
                    "lead_id": lead.id
                }
            )

            raise