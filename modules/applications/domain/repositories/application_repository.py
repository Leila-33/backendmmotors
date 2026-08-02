from abc import ABC, abstractmethod
from typing import List, Optional

from modules.applications.infrastructure.db.application_model import ApplicationModel

class ApplicationRepository(ABC):

    # =========================
    # BASE APPLICATION
    # =========================
    @abstractmethod
    def create_base(self, **kwargs) -> "ApplicationModel":
        pass

    @abstractmethod
    def get_by_id(self, application_id: str) -> Optional["ApplicationModel"]:
        pass

    @abstractmethod
    def update(self, application: "ApplicationModel") -> "ApplicationModel":
        pass


    @abstractmethod
    def find_draft_by_user_and_vehicle(
        self,
        user_id: str,
        vehicle_id: str
    ):
        pass

    @abstractmethod
    def find_all(
        self,
        page: int,
        limit: int,
        search: str | None,
        status: str | None,
        type: str | None,
        sort: str
    ):
        pass

    @abstractmethod
    def delete(self, application_id: str):
        pass
    
    @abstractmethod
    def find_by_quote_id(
    self,
    quote_id: str
) -> ApplicationModel | None:
        pass