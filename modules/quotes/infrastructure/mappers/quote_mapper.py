from modules.quotes.domain.entities.quote import Quote
from modules.quotes.infrastructure.db.quote_model import QuoteModel
from modules.leads.infrastructure.mappers.lead_mapper import LeadMapper
from modules.quotes.infrastructure.mappers.quote_trade_in_mapper import QuoteTradeInMapper


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



