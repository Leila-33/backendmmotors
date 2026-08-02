from abc import ABC, abstractmethod
from modules.applications.domain.entities.application_trade_in import ApplicationTradeIn

class ApplicationTradeInRepository(ABC):

    @abstractmethod
    def save(
            self,
            trade_in: ApplicationTradeIn
        ):        
        pass

    @abstractmethod
    def delete_by_application(self, application_id: str):
        pass