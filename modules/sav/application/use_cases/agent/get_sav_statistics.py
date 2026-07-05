from modules.sav.api.schemas import SavStatisticsResponse, CategoryStat

class GetSavStatisticsUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, user):

        data = self.repo.get_sav_statistics(user)

        return SavStatisticsResponse(
            total=data["total"],
            closed=data["closed"],
            last_7_days=data["last_7_days"],
            last_30_days=data["last_30_days"],
            category_distribution=[
                CategoryStat(
                    category=cat,
                    count=count
                )
                for cat, count in data["category_distribution"]
            ],
            resolution_rate=data["resolution_rate"],
        )