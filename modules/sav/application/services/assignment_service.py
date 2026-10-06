from modules.auth.domain.repositories.user_repository import UserRepository
from modules.sav.domain.repositories.support_ticket_repository import SupportTicketRepository
from modules.auth.domain.enums import UserRole

class AssignmentService:

    def __init__(
        self,
        user_repository: UserRepository,
        ticket_repository: SupportTicketRepository
    ):
        self.user_repo = user_repository
        self.ticket_repo = ticket_repository

    def get_next_agent(self):

        agents = self.user_repo.get_by_role(UserRole.SAV_AGENT)

        if not agents:
            return None
        
        best_agent = None
        best_score = float("inf")

        for agent in agents:

            score = self.ticket_repo.count_open_tickets_by_agent(
                agent.id
            )

            if score < best_score:
                best_score = score
                best_agent = agent
        return best_agent