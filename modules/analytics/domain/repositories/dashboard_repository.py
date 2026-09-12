from abc import ABC, abstractmethod
from modules.analytics.application.results.dashboard_result import (
    DashboardResult,
)

class DashboardRepository(ABC):

    @abstractmethod
    def get_admin_dashboard_data(self) -> dict:
        pass


    @abstractmethod
    def get_user_dashboard(
        self,
        user_id: str,
    ) -> DashboardResult:
        pass
