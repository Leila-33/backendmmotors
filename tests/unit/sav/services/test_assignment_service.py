from types import SimpleNamespace
from unittest.mock import MagicMock

from modules.auth.domain.enums import UserRole
from modules.sav.application.services.assignment_service import AssignmentService


class TestAssignmentService:

    def setup_method(self):
        self.user_repository = MagicMock()
        self.ticket_repository = MagicMock()

        self.service = AssignmentService(
            user_repository=self.user_repository,
            ticket_repository=self.ticket_repository,
        )

    def test_get_next_agent_returns_none_when_no_sav_agent_exists(self):
        # Arrange
        self.user_repository.get_by_role.return_value = []

        # Act
        result = self.service.get_next_agent()

        # Assert
        assert result is None

        self.user_repository.get_by_role.assert_called_once_with(
            UserRole.SAV_AGENT
        )

        self.ticket_repository.count_open_tickets_by_agent.assert_not_called()

    def test_get_next_agent_returns_agent_with_fewest_open_tickets(self):
        # Arrange
        agent_1 = SimpleNamespace(id="agent-1")
        agent_2 = SimpleNamespace(id="agent-2")
        agent_3 = SimpleNamespace(id="agent-3")

        self.user_repository.get_by_role.return_value = [
            agent_1,
            agent_2,
            agent_3,
        ]

        self.ticket_repository.count_open_tickets_by_agent.side_effect = [
            5,
            2,
            4,
        ]

        # Act
        result = self.service.get_next_agent()

        # Assert
        assert result is agent_2

        self.user_repository.get_by_role.assert_called_once_with(
            UserRole.SAV_AGENT
        )

        assert self.ticket_repository.count_open_tickets_by_agent.call_count == 3

        self.ticket_repository.count_open_tickets_by_agent.assert_any_call(
            "agent-1"
        )
        self.ticket_repository.count_open_tickets_by_agent.assert_any_call(
            "agent-2"
        )
        self.ticket_repository.count_open_tickets_by_agent.assert_any_call(
            "agent-3"
        )

    def test_get_next_agent_returns_only_agent_when_one_exists(self):
        # Arrange
        agent = SimpleNamespace(id="agent-1")

        self.user_repository.get_by_role.return_value = [agent]

        self.ticket_repository.count_open_tickets_by_agent.return_value = 3

        # Act
        result = self.service.get_next_agent()

        # Assert
        assert result is agent

        self.user_repository.get_by_role.assert_called_once_with(
            UserRole.SAV_AGENT
        )

        self.ticket_repository.count_open_tickets_by_agent.assert_called_once_with(
            "agent-1"
        )

    def test_get_next_agent_selects_agent_with_zero_open_tickets(self):
        # Arrange
        agent_1 = SimpleNamespace(id="agent-1")
        agent_2 = SimpleNamespace(id="agent-2")
        agent_3 = SimpleNamespace(id="agent-3")

        self.user_repository.get_by_role.return_value = [
            agent_1,
            agent_2,
            agent_3,
        ]

        self.ticket_repository.count_open_tickets_by_agent.side_effect = [
            7,
            0,
            3,
        ]

        # Act
        result = self.service.get_next_agent()

        # Assert
        assert result is agent_2

    def test_get_next_agent_keeps_first_agent_when_scores_are_equal(self):
        # Arrange
        agent_1 = SimpleNamespace(id="agent-1")
        agent_2 = SimpleNamespace(id="agent-2")

        self.user_repository.get_by_role.return_value = [
            agent_1,
            agent_2,
        ]

        self.ticket_repository.count_open_tickets_by_agent.side_effect = [
            2,
            2,
        ]

        # Act
        result = self.service.get_next_agent()

        # Assert
        assert result is agent_1

        assert self.ticket_repository.count_open_tickets_by_agent.call_count == 2