from abc import ABC, abstractmethod
from modules.applications.domain.entities.application_option import ApplicationOption


class ApplicationOptionRepository(ABC):

    @abstractmethod
    def delete_by_application(self, application_id: str):
        pass