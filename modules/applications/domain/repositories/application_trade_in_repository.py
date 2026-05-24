from abc import ABC, abstractmethod

class ApplicationTradeInRepository(ABC):

    @abstractmethod
    def delete_by_application(self, application_id: str):
        pass