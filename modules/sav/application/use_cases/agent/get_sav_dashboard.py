from modules.sav.api.schemas import SavDashboardTicketDTO, SavDashboardResponse

class GetSavDashboardUseCase:

    def __init__(self, repo):
        self.repo = repo

    def execute(self, user):

        data = self.repo.get_dashboard_stats(user)

        recent = [
    SavDashboardTicketDTO(
        id=t.id,
        subject=t.subject,
        priority=t.priority,
        status=t.status,
        created_at=t.created_at,
    )
    for t in data["recent_tickets"]
]

        return SavDashboardResponse(
            total=data["total"],
            open=data["open"],
            urgent=data["urgent"],
            recent_tickets=recent,
        )