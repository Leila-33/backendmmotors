from modules.sav.application.results.agent.get_sav_dashboard_result import (
    GetSavDashboardResult,
    SavDashboardTicketResult,
)


class GetSavDashboardUseCase:
    """
    Récupère les données nécessaires au tableau de bord SAV,
    notamment les statistiques des tickets et les tickets récents.
    """
    def __init__(self, repo):
        self.repo = repo


    def execute(
        self,
        user_id: str,
    ) -> GetSavDashboardResult:

        data = self.repo.get_dashboard_stats(
            user_id=user_id
        )

        recent_tickets = [
            SavDashboardTicketResult(
                id=t.id,
                subject=t.subject,
                priority=t.priority,
                status=t.status,
                created_at=t.created_at,
            )
            for t in data["recent_tickets"]
        ]

        return GetSavDashboardResult(
            total=data["total"],
            open=data["open"],
            urgent=data["urgent"],
            recent_tickets=recent_tickets,
        )