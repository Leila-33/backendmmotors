from abc import ABC, abstractmethod
from typing import List
from modules.applications.domain.entities.application_event import ApplicationEvent


class ApplicationEventRepository(ABC):

    @abstractmethod
    def save(self, event: ApplicationEvent):
        pass

    @abstractmethod
    def get_by_application_id(self, application_id: str) -> List[ApplicationEvent]:
        pass