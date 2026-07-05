from abc import ABC, abstractmethod
from typing import List, Optional

from modules.applications.domain.entities.application_financing import ApplicationFinancing
from modules.applications.domain.entities.application_trade_in import ApplicationTradeIn


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

    # =========================
    # OPTIONS
    # =========================
    @abstractmethod
    def replace_options(self, application_id: str, option_ids: List[str]) -> None:
        pass

    # =========================
    # FINANCING SNAPSHOT
    # =========================
    @abstractmethod
    def save_financing(self, application_id: str, data: ApplicationFinancing) -> None:
        pass

    # =========================
    # TRADE-IN SNAPSHOT
    # =========================
    @abstractmethod
    def save_trade_in(self, application_id: str, trade_in_value: float, data: ApplicationTradeIn) -> None:
        pass

    @abstractmethod
    def find_draft_by_user_and_vehicle(
        self,
        user_id: str,
        vehicle_id: str
    ):
        pass

    # =========================
    # DOCUMENTS
    # =========================
    @abstractmethod
    def sync_documents(
        self,
        application_id: str,
        documents: list
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
    def archive(self, application_id: str):
        pass

    @abstractmethod
    def unarchive(self, application_id: str):
        pass

    @abstractmethod
    def soft_delete(self, application_id: str):
        pass