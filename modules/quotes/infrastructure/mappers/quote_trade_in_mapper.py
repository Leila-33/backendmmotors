from modules.quotes.domain.entities.quote_trade_in import QuoteTradeIn

from modules.quotes.infrastructure.db.quote_trade_in_model import (
    QuoteTradeInModel,
)


class QuoteTradeInMapper:


    @staticmethod
    def to_domain(
        model: QuoteTradeInModel
    ):

        return QuoteTradeIn(

            quote_id=model.quote_id,

            brand=model.brand,

            model=model.model,

            year=model.year,

            mileage=model.mileage,

            condition=model.condition,

            estimated_value=model.estimated_value,
        )


    @staticmethod
    def to_model(
        domain: QuoteTradeIn
    ):

        return QuoteTradeInModel(

            quote_id=domain.quote_id,

            brand=domain.brand,

            model=domain.model,

            year=domain.year,

            mileage=domain.mileage,

            condition=domain.condition,

            estimated_value=domain.estimated_value,
        )



    @staticmethod
    def update_model(
        model: QuoteTradeInModel,
        domain: QuoteTradeIn
    ):

        model.brand = domain.brand

        model.model = domain.model

        model.year = domain.year

        model.mileage = domain.mileage

        model.condition = domain.condition

        model.estimated_value = (
            domain.estimated_value
        )