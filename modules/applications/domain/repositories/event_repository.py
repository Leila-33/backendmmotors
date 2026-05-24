from abc import ABC, abstractmethod
from typing import List
from modules.applications.domain.entities.event import Event


class EventRepository(ABC):

    @abstractmethod
    def save(self, event: Event):
        pass

    @abstractmethod
    def get_by_application_id(self, application_id: str) -> List[Event]:
        pass
    
    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def delete_by_application(self, application_id: str):
        pass