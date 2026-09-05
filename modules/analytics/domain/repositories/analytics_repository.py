from abc import ABC, abstractmethod
from datetime import datetime


class AnalyticsRepository(ABC):

    @abstractmethod
    def get_statistics(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> dict:
        pass