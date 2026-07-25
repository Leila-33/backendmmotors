from modules.leads.domain.enums import LeadStatus
import uuid
from modules.quotes.domain.entities.quote import Quote
from modules.financing.api.schemas import FinancingRequest
from datetime import datetime, timezone

from modules.quotes.domain.entities.quote_trade_in import QuoteTradeIn
from modules.quotes.domain.enums import QuoteStatus
from modules.financing.api.schemas import FinancingRequest
from modules.financing.domain.entities.trade_in import TradeInInput

from modules.quotes.domain.exceptions import ActiveQuoteAlreadyExists
from modules.leads.domain.exceptions import (
    LeadNotFound,
    LeadHasActiveQuote
)
from modules.vehicles.domain.exceptions import VehicleNotFound


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
        unit_of_work
    ):

        self.quote_repository = quote_repository
        self.quote_trade_in_repository = quote_trade_in_repository

        self.lead_repository = lead_repository
        self.vehicle_repository = vehicle_repository

        self.financing_service = financing_service
        self.trade_in_service = trade_in_service

        self.authorization = authorization
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

            if self.quote_repository.has_active_quote(
    lead.id
):
                raise LeadHasActiveQuote()


            existing_quote = (
                self.quote_repository.find_active_by_lead(
                    lead.id
                )
            )

            if existing_quote:
                raise ActiveQuoteAlreadyExists()



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


        except Exception:

            self.unit_of_work.rollback()

            raise


        return quote