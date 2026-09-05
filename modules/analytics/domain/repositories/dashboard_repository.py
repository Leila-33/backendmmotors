from abc import ABC, abstractmethod


class DashboardRepository(ABC):

    @abstractmethod
    def get_dashboard_data(self) -> dict:
        pass