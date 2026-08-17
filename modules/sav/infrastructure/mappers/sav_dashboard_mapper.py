from modules.sav.api.schemas import (
    SavDashboardTicketDTO,
    SavDashboardResponse,
)
from modules.sav.application.results.agent.get_sav_dashboard_result import GetSavDashboardResult

class SavDashboardMapper:

    @staticmethod
    def to_response(
        result: GetSavDashboardResult,
    ) -> SavDashboardResponse:

        recent_tickets = [
            SavDashboardTicketDTO(
                id=ticket.id,
                subject=ticket.subject,
                priority=ticket.priority,
                status=ticket.status,
                created_at=ticket.created_at,
            )
            for ticket in result.recent_tickets
        ]

        return SavDashboardResponse(
            total=result.total,
            open=result.open,
            urgent=result.urgent,
            recent_tickets=recent_tickets,
        )