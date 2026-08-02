from abc import ABC, abstractmethod
from modules.applications.domain.entities.application_financing import ApplicationFinancing

class ApplicationFinancingRepository(ABC):
    
    @abstractmethod
    def save(
            self,
            financing: ApplicationFinancing
        ):   
        pass

    @abstractmethod
    def delete_by_application(self, application_id: str):
        pass