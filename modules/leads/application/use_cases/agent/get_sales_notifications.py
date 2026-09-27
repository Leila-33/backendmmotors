from modules.leads.application.dtos.agent.agent_dto import (
    AgentDTO
)
from modules.leads.application.results.agent.sales_notification_counts_result import (
    SalesNotificationCountsResult,
)
from modules.leads.domain.repositories.sales_dashboard_repository import (
    SalesDashboardRepository,
)


class GetSalesNotificationsUseCase:
    """
    Récupère les compteurs de notifications nécessaires
    au tableau de bord commercial de l'agent.
    """
    def __init__(
        self,
        sales_dashboard_repository: SalesDashboardRepository,
    ):
        self.sales_dashboard_repository = sales_dashboard_repository

    def execute(
        self,
        dto: AgentDTO,
    ) -> SalesNotificationCountsResult:

        return self.sales_dashboard_repository.get_notification_counts(
            agent_id=dto.agent_id,
        )