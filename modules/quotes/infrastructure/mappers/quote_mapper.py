from modules.quotes.domain.entities.quote import Quote

from modules.quotes.infrastructure.db.quote_model import QuoteModel
from modules.leads.infrastructure.mappers.lead_mapper import LeadMapper
from modules.quotes.infrastructure.mappers.quote_trade_in_mapper import QuoteTradeInMapper
from modules.quotes.domain.enums import QuoteStatus

class QuoteMapper:

    # =====================================
    # DOMAIN -> MODEL
    # =====================================

    @staticmethod
    def to_model(
        quote: Quote
    ) -> QuoteModel:

        return QuoteModel(

            id=quote.id,

            lead_id=quote.lead_id,

            status=quote.status,

            base_price=quote.base_price,

            discount=quote.discount,

            down_payment=quote.down_payment,

            trade_in_value=quote.trade_in_value,

            duration_months=quote.duration_months,

            financed_amount=quote.financed_amount,

            monthly_payment=quote.monthly_payment,

            created_at=quote.created_at,

            sent_at=quote.sent_at,

            accepted_at=quote.accepted_at,

            refusal_reason=quote.refusal_reason,

            refusal_comment=quote.refusal_comment,

            refused_at=quote.refused_at,
            expires_at = quote.expires_at

        )


    # =====================================
    # MODEL -> DOMAIN
    # =====================================

    @staticmethod
    def to_domain(
        model: QuoteModel
    ) -> Quote:

        return Quote(

            id=model.id,

            lead_id=model.lead_id,

            status=model.status,

            base_price=model.base_price,

            discount=model.discount,

            down_payment=model.down_payment,

            trade_in_value=model.trade_in_value,

            duration_months=model.duration_months,

            financed_amount=model.financed_amount,

            monthly_payment=model.monthly_payment,

            created_at=model.created_at,

            sent_at=model.sent_at,

            accepted_at=model.accepted_at,

            refusal_reason=model.refusal_reason,

            refusal_comment=model.refusal_comment,

            refused_at=model.refused_at,
            expires_at = model.expires_at,

            lead=(
                LeadMapper.to_domain(
                    model.lead
                )
                if model.lead
                else None
            ),

            trade_in=(
                QuoteTradeInMapper.to_domain(
                    model.trade_in
                )
                if model.trade_in
                else None
            )
        )


    # =====================================
    # UPDATE MODEL
    # =====================================

    @staticmethod
    def update_model(
        model: QuoteModel,
        quote: Quote,
    ) -> None:
        
        model.base_price = quote.base_price

        model.status = quote.status

        model.discount = quote.discount

        model.down_payment = quote.down_payment

        model.trade_in_value = quote.trade_in_value

        model.duration_months = quote.duration_months

        model.financed_amount = quote.financed_amount

        model.monthly_payment = quote.monthly_payment

        model.sent_at = quote.sent_at

        model.accepted_at = quote.accepted_at

        model.refusal_reason = quote.refusal_reason

        model.refusal_comment = quote.refusal_comment

        model.refused_at = quote.refused_at
        model.expires_at = quote.expires_at


    @staticmethod
    def to_detail_response(model):

        return {

            "id": model.id,

            "status": (
                model.status.value
                if hasattr(model.status, "value")
                else model.status
            ),

            "base_price": model.base_price,

            "discount": model.discount,

            "down_payment": model.down_payment,

            "trade_in_value": model.trade_in_value,

            "financed_amount": model.financed_amount,

            "duration_months": model.duration_months,

            "monthly_payment": model.monthly_payment,

            "lead": {

                "id": model.lead.id,

                "first_name": model.lead.first_name,

                "last_name": model.lead.last_name,

                "email": model.lead.email,

                "phone": model.lead.phone,

            },

            "vehicle": {

        "id": model.lead.vehicle.id,

        "brand": model.lead.vehicle.brand,

        "model": model.lead.vehicle.model,

        "price": model.lead.vehicle.price,

    },

            "trade_in": (

                {

                    "brand": model.trade_in.brand,

                    "model": model.trade_in.model,

                    "year": model.trade_in.year,

                    "mileage": model.trade_in.mileage,

                    "condition": model.trade_in.condition,

                    "estimated_value": model.trade_in.estimated_value,

                }

                if model.trade_in

                else None

            ),

            "created_at": model.created_at,

        }

    @staticmethod
    def to_list_response(
        quote,
    ):

        return {

            "id": quote.id,

            "status": (
                quote.status.value
                if hasattr(
                    quote.status,
                    "value",
                )
                else quote.status
            ),

            "base_price": quote.base_price,

            "monthly_payment": quote.monthly_payment,

            "created_at": quote.created_at,

            "vehicle": {

    "id": quote.lead.vehicle.id,

    "brand": quote.lead.vehicle.brand,

    "model": quote.lead.vehicle.model,

    "price": quote.lead.vehicle.price,

},
            "requires_action": (
                    quote.status == QuoteStatus.SENT
                ),

        }
    

    @staticmethod
    def to_customer_detail_response(
            quote,
    application_id=None,
    ):

        return {

            "id": quote.id,


            "status": (
                quote.status.value
                if hasattr(
                    quote.status,
                    "value"
                )
                else quote.status
            ),


            "base_price": quote.base_price,

            "discount": quote.discount,

            "down_payment": quote.down_payment,

            "trade_in_value": quote.trade_in_value,

            "financed_amount": quote.financed_amount,

            "duration_months": quote.duration_months,

            "monthly_payment": quote.monthly_payment,


            "vehicle": {

                "id": quote.lead.vehicle.id,

                "brand": quote.lead.vehicle.brand,

                "model": quote.lead.vehicle.model,

                "price": quote.lead.vehicle.price,

            },



            "trade_in": (

                {
                    "brand": quote.trade_in.brand,

                    "model": quote.trade_in.model,

                    "year": quote.trade_in.year,

                    "mileage": quote.trade_in.mileage,

                    "condition": quote.trade_in.condition,

                    "estimated_value": quote.trade_in.estimated_value,
                }

                if quote.trade_in

                else None

            ),



            "sales_agent": (

    {
        "id": quote.lead.assigned_agent.id,

        "first_name": quote.lead.assigned_agent.first_name,

        "last_name": quote.lead.assigned_agent.last_name,
    }

    if quote.lead.assigned_agent

    else None
),



            "created_at": quote.created_at,
            "application_id": application_id


        }