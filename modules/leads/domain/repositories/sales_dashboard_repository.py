from abc import ABC, abstractmethod

from modules.leads.application.results.agent.get_sales_dashboard_statistics_result import (
    SalesDashboardStatisticsResult,
)
from modules.leads.application.results.agent.sales_notification_counts_result import (
    SalesNotificationCountsResult,
)


class SalesDashboardRepository(ABC):

    @abstractmethod
    def get_statistics(
        self,
        agent_id: str,
    ) -> SalesDashboardStatisticsResult:
        """
        Retourne les statistiques du dashboard commercial
        pour un agent donné.
        """
        raise NotImplementedError

    @abstractmethod
    def get_notification_counts(
        self,
        agent_id: str,
    ) -> SalesNotificationCountsResult:
        """
        Retourne le nombre de leads non assignés et le nombre de leads
        assignés à un agent donné.
        """
        raise NotImplementedError

    @abstractmethod
    def count_my_leads(
        self,
        agent_id: str,
    ) -> int:
        """
        Retourne le nombre de leads actifs assignés à l'agent.
        """
        raise NotImplementedError

    @abstractmethod
    def count_new_leads(self) -> int:
        """
        Retourne le nombre de nouveaux leads non attribués.
        """
        raise NotImplementedError