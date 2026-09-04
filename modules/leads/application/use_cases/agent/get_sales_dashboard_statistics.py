from modules.leads.application.dtos.agent.agent_dto import (
    AgentDTO,
)
from modules.leads.application.results.agent.get_sales_dashboard_statistics_result import (
    SalesDashboardStatisticsResult,
)
from modules.leads.domain.repositories.sales_dashboard_repository import (
    SalesDashboardRepository,
)


class GetSalesDashboardStatisticsUseCase:

    def __init__(
        self,
        sales_dashboard_repository: SalesDashboardRepository,
    ):
        self.sales_dashboard_repository = sales_dashboard_repository

    def execute(
        self,
        dto: AgentDTO,
    ) -> SalesDashboardStatisticsResult:

        return self.sales_dashboard_repository.get_statistics(
            agent_id=dto.agent_id,
        )