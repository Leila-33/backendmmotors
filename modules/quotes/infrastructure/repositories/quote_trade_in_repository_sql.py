from sqlalchemy.orm import Session, joinedload

from modules.quotes.domain.entities.quote_trade_in import QuoteTradeIn

from modules.quotes.infrastructure.db.quote_trade_in_model import (
    QuoteTradeInModel,
)

from modules.quotes.infrastructure.mappers.quote_trade_in_mapper import (
    QuoteTradeInMapper,
)

from modules.quotes.domain.repositories.quote_trade_in_repository import (
    QuoteTradeInRepository,
)

class QuoteTradeInRepositorySQL(
    QuoteTradeInRepository
):

    def __init__(
        self,
        db: Session
    ):
        self.db = db



    def save(
        self,
        trade_in: QuoteTradeIn
    ) -> None:

        model = (
            QuoteTradeInMapper
            .to_model(trade_in)
        )

        self.db.add(model)

        self.db.commit()

        self.db.refresh(model)



    def find_by_quote_id(
        self,
        quote_id: str
    ) -> QuoteTradeIn | None:


        model = (
            self.db
            .query(QuoteTradeInModel)
            .filter(
                QuoteTradeInModel.quote_id == quote_id
            )
            .first()
        )


        if not model:
            return None


        return (
            QuoteTradeInMapper
            .to_domain(model)
        )



    def delete(
        self,
        quote_id: str
    ) -> None:


        model = (
            self.db
            .query(QuoteTradeInModel)
            .filter(
                QuoteTradeInModel.quote_id == quote_id
            )
            .first()
        )


        if model:

            self.db.delete(model)

            self.db.commit()
        
    def delete(
    self,
    quote_id: str,
):

        model = (
            self.db.query(QuoteTradeInModel)
            .filter(
                QuoteTradeInModel.quote_id == quote_id
            )
            .first()
        )


        if model is None:
            return


        self.db.delete(model)