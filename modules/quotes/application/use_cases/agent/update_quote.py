from modules.financing.api.schemas import FinancingRequest
from modules.quotes.domain.entities.quote_trade_in import QuoteTradeIn
from modules.financing.api.schemas import FinancingRequest
from modules.financing.domain.entities.trade_in_input import TradeInInput
from modules.leads.domain.exceptions import LeadNotFound
from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.quotes.domain.exceptions import QuoteNotFound
from modules.applications.domain.enums import (
    EventType
)
import logging

logger = logging.getLogger(__name__)

class UpdateQuoteUseCase:


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
        unit_of_work,
    ):

        self.quote_repository = quote_repository

        self.quote_trade_in_repository = (
            quote_trade_in_repository
        )

        self.lead_repository = lead_repository

        self.vehicle_repository = vehicle_repository

        self.financing_service = financing_service

        self.trade_in_service = trade_in_service

        self.authorization = authorization
        self.event_service = event_service

        self.unit_of_work = unit_of_work



    def execute(
        self,
        quote_id,
        request,
        agent_id,
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
            # VEHICLE
            # =========================

            vehicle = lead.vehicle



            # =========================
            # TRADE IN
            # =========================

            trade_in_value = 0


            if request.trade_in:


                trade_in_value = (
                    self.trade_in_service
                    .estimate(

                        TradeInInput(

                            brand=
                            request.trade_in.brand,


                            model=
                            request.trade_in.model,


                            year=
                            request.trade_in.year,


                            mileage=
                            request.trade_in.mileage,


                            condition=
                            request.trade_in.condition,

                        )

                    )
                )



            # =========================
            # FINANCING
            # =========================

            financing = (
                self.financing_service
                .calculate(

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



            # =========================
            # DOMAIN UPDATE
            # =========================

            quote.update_financing(

                base_price=
                vehicle.price,


                discount=
                request.discount,


                down_payment=
                request.down_payment,


                trade_in_value=
                trade_in_value,


                duration_months=
                request.duration_months,


                financed_amount=
                financing.financed_amount,


                monthly_payment=
                financing.monthly_payment,

            )



            self.quote_repository.update(
                quote
            )



            # =========================
            # TRADE IN DETAILS
            # =========================

            existing_trade_in = (
                self.quote_trade_in_repository
                .find_by_quote_id(
                    quote.id
                )
            )



            if request.trade_in:


                if existing_trade_in:


                    existing_trade_in.update(

                        brand=
                        request.trade_in.brand,


                        model=
                        request.trade_in.model,


                        year=
                        request.trade_in.year,


                        mileage=
                        request.trade_in.mileage,


                        condition=
                        request.trade_in.condition,


                        estimated_value=
                        trade_in_value,

                    )


                    self.quote_trade_in_repository.update(
                        existing_trade_in
                    )


                else:


                    self.quote_trade_in_repository.save(

                        QuoteTradeIn(

                            quote_id=
                            quote.id,


                            brand=
                            request.trade_in.brand,


                            model=
                            request.trade_in.model,


                            year=
                            request.trade_in.year,


                            mileage=
                            request.trade_in.mileage,


                            condition=
                            request.trade_in.condition,


                            estimated_value=
                            trade_in_value,

                        )

                    )

            else:

                if existing_trade_in:

                    self.quote_trade_in_repository.delete(
                        existing_trade_in.quote_id
                    )

            self.event_service.log(
    type=EventType.QUOTE_UPDATED,
    message="Devis mis à jour",
    quote_id=quote.id,
    user_id=agent_id,
    event_metadata={
        "financed_amount": financing.financed_amount,
        "trade_in_value": trade_in_value,
    }
)

            # =========================
            # COMMIT
            # =========================

            self.unit_of_work.commit()



            logger.info(
                "Devis mis à jour avec succès",
                extra={
                    "quote_id": quote.id,
                    "agent_id": agent_id,
                }
            )


        except Exception:

            self.unit_of_work.rollback()

            logger.exception(
                "Erreur lors de la mise à jour du devis",
                extra={
                    "quote_id": quote_id,
                    "agent_id": agent_id,
                }
            )

            raise