from modules.auth.domain.repositories.user_repository import UserRepository
from modules.sav.domain.repositories.support_ticket_repository import SupportTicketRepository

class AssignmentService:

    def __init__(
        self,
        user_repo: UserRepository,
        ticket_repo: SupportTicketRepository
    ):
        self.user_repo = user_repo
        self.ticket_repo = ticket_repo

    def get_next_agent(self):

        agents = self.user_repo.get_active_agents()

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
        print('1', best_agent)
        return best_agent