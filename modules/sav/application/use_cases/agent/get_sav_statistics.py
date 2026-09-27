from modules.sav.application.results.agent.get_sav_statistics_result import (
    GetSavStatisticsResult,
    CategoryStatResult,
)


class GetSavStatisticsUseCase:
    """
    Récupère les statistiques du service après-vente, notamment
    le volume de tickets, les tickets clôturés, leur répartition
    par catégorie et le taux de résolution.
    """
    def __init__(self, repo):
        self.repo = repo

    def execute(self, user_id: str) -> GetSavStatisticsResult:

        data = self.repo.get_sav_statistics(user_id)

        return GetSavStatisticsResult(
            total=data["total"],
            closed=data["closed"],
            last_7_days=data["last_7_days"],
            last_30_days=data["last_30_days"],
            category_distribution=[
                CategoryStatResult(
                    category=category,
                    count=count,
                )
                for category, count
                in data["category_distribution"]
            ],
            resolution_rate=data["resolution_rate"],
        )