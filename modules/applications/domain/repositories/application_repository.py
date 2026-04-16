from abc import ABC, abstractmethod
from typing import Optional
from modules.applications.domain.entities.application import Application


class ApplicationRepository(ABC):

    @abstractmethod
    def save(self, application: Application):
        pass

    @abstractmethod
    def get_by_id(self, application_id: str) -> Optional[Application]:
        pass

    @abstractmethod
    def update(self, application: Application):
        pass