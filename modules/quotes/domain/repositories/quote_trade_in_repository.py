from abc import ABC, abstractmethod
from modules.quotes.domain.entities.quote_trade_in import QuoteTradeIn

class QuoteTradeInRepository(ABC):

    @abstractmethod
    def save(
        self,
        trade_in: QuoteTradeIn,
    ) -> QuoteTradeIn:
        pass

    @abstractmethod
    def find_by_quote_id(
        self,
        quote_id: str,
    ) -> QuoteTradeIn | None:
        pass

    @abstractmethod
    def update(
        self,
        trade_in: QuoteTradeIn,
    ) -> QuoteTradeIn:
        pass

    @abstractmethod
    def delete(
        self,
        quote_id: str,
    ) -> None:
        pass
   