from modules.analytics.application.results.dashboard_result import (
    DashboardResult,
)


class GetDashboardUseCase:
    """
    Récupère les données du tableau de bord de l'utilisateur
    connecté : dossiers, prochain essai routier, notifications
    et statistiques associées.
    """
    def __init__(
        self,
        dashboard_repository,
    ):
        self.dashboard_repository = dashboard_repository

    def execute(
        self,
        user_id: str,
    ) -> DashboardResult:

        return self.dashboard_repository.get_user_dashboard(
            user_id=user_id
        )
