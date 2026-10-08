from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.applications.domain.enums import EventType
from modules.auth.domain.enums import UserRole
from modules.leads.application.dtos.agent.agent_lead_dto import (
    AgentLeadDTO,
)
from modules.leads.application.use_cases.agent.assign_lead import (
    AssignLeadUseCase,
)
from modules.leads.domain.exceptions import LeadNotFound


class TestAssignLeadUseCase:
    """Tests du Use Case d'attribution d'un lead."""

    def setup_method(self):
        self.user_repository = MagicMock()
        self.lead_repository = MagicMock()
        self.sales_dashboard_repository = MagicMock()
        self.notification_service = MagicMock()
        self.notification_service.send_update = AsyncMock()
        self.event_service = MagicMock()
        self.unit_of_work = MagicMock()

        self.use_case = AssignLeadUseCase(
            user_repository=self.user_repository,
            lead_repository=self.lead_repository,
            sales_dashboard_repository=self.sales_dashboard_repository,
            notification_service=self.notification_service,
            event_service=self.event_service,
            unit_of_work=self.unit_of_work,
        )

        self.dto = AgentLeadDTO(
            lead_id="lead-123",
            agent_id="agent-456",
        )

    # =========================
    # SUCCESS
    # =========================

    @pytest.mark.asyncio
    async def test_execute_assigns_lead_successfully(self):
        # Arrange
        lead = MagicMock()
        lead.id = "lead-123"
        lead.vehicle_id = "vehicle-789"
        lead.status.value = "ASSIGNED"
        lead.assigned_to = "agent-456"

        self.lead_repository.find_by_id.return_value = lead

        counts = SimpleNamespace(
            my_leads_count=5,
            new_leads_count=12,
        )

        self.sales_dashboard_repository.get_notification_counts.return_value = (
            counts
        )

        sales_agents = [
            SimpleNamespace(id="agent-456"),
            SimpleNamespace(id="agent-789"),
        ]

        self.user_repository.get_by_role.return_value = sales_agents

        # Act
        result = await self.use_case.execute(self.dto)

        # Assert
        self.lead_repository.find_by_id.assert_called_once_with(
            "lead-123"
        )

        lead.ensure_assignable.assert_called_once_with()
        lead.assign_to.assert_called_once_with("agent-456")

        self.lead_repository.update.assert_called_once_with(
            lead
        )

        self.event_service.log.assert_called_once_with(
            type=EventType.LEAD_ASSIGNED,
            message="Lead assigné à un agent",
            user_id="agent-456",
            lead_id="lead-123",
            vehicle_id="vehicle-789",
            event_metadata={
                "assigned_to": "agent-456",
                "status": "ASSIGNED",
            },
        )

        self.unit_of_work.commit.assert_called_once()
        self.unit_of_work.rollback.assert_not_called()

        assert result.id == "lead-123"
        assert result.status == "ASSIGNED"
        assert result.assigned_to == "agent-456"
        assert result.message == "Lead assigné"

    # =========================
    # LEAD NOT FOUND
    # =========================

    @pytest.mark.asyncio
    async def test_execute_raises_lead_not_found(self):
        # Arrange
        self.lead_repository.find_by_id.return_value = None

        # Act / Assert
        with pytest.raises(LeadNotFound):
            await self.use_case.execute(self.dto)

        self.lead_repository.find_by_id.assert_called_once_with(
            "lead-123"
        )

        self.lead_repository.update.assert_not_called()
        self.event_service.log.assert_not_called()
        self.unit_of_work.commit.assert_not_called()

        self.unit_of_work.rollback.assert_called_once()

        self.notification_service.send_update.assert_not_awaited()

    # =========================
    # LEAD NOT ASSIGNABLE
    # =========================

    @pytest.mark.asyncio
    async def test_execute_rolls_back_when_lead_is_not_assignable(self):
        # Arrange
        lead = MagicMock()
        lead.id = "lead-123"

        lead.ensure_assignable.side_effect = ValueError(
            "Lead non attribuable"
        )

        self.lead_repository.find_by_id.return_value = lead

        # Act / Assert
        with pytest.raises(ValueError, match="Lead non attribuable"):
            await self.use_case.execute(self.dto)

        lead.ensure_assignable.assert_called_once_with()

        lead.assign_to.assert_not_called()
        self.lead_repository.update.assert_not_called()
        self.event_service.log.assert_not_called()
        self.unit_of_work.commit.assert_not_called()

        self.unit_of_work.rollback.assert_called_once()

    # =========================
    # UPDATE FAILURE
    # =========================

    @pytest.mark.asyncio
    async def test_execute_rolls_back_when_update_fails(self):
        # Arrange
        lead = MagicMock()
        lead.id = "lead-123"
        lead.vehicle_id = "vehicle-789"

        self.lead_repository.find_by_id.return_value = lead

        self.lead_repository.update.side_effect = RuntimeError(
            "Erreur de persistance"
        )

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match="Erreur de persistance",
        ):
            await self.use_case.execute(self.dto)

        lead.ensure_assignable.assert_called_once_with()
        lead.assign_to.assert_called_once_with("agent-456")

        self.lead_repository.update.assert_called_once_with(
            lead
        )

        self.event_service.log.assert_not_called()
        self.unit_of_work.commit.assert_not_called()

        self.unit_of_work.rollback.assert_called_once()

    # =========================
    # EVENT FAILURE
    # =========================

    @pytest.mark.asyncio
    async def test_execute_rolls_back_when_event_logging_fails(self):
        # Arrange
        lead = MagicMock()
        lead.id = "lead-123"
        lead.vehicle_id = "vehicle-789"
        lead.status.value = "ASSIGNED"

        self.lead_repository.find_by_id.return_value = lead

        self.event_service.log.side_effect = RuntimeError(
            "Erreur événement"
        )

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match="Erreur événement",
        ):
            await self.use_case.execute(self.dto)

        self.lead_repository.update.assert_called_once_with(
            lead
        )

        self.event_service.log.assert_called_once()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

    # =========================
    # DASHBOARD COUNTS
    # =========================

    @pytest.mark.asyncio
    async def test_execute_gets_notification_counts_for_assigned_agent(
        self,
    ):
        # Arrange
        lead = MagicMock()
        lead.id = "lead-123"
        lead.vehicle_id = "vehicle-789"
        lead.status.value = "ASSIGNED"
        lead.assigned_to = "agent-456"

        self.lead_repository.find_by_id.return_value = lead

        counts = SimpleNamespace(
            my_leads_count=7,
            new_leads_count=15,
        )

        self.sales_dashboard_repository.get_notification_counts.return_value = (
            counts
        )

        self.user_repository.get_by_role.return_value = []

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.sales_dashboard_repository.get_notification_counts.assert_called_once_with(
            agent_id="agent-456",
        )

    # =========================
    # PERSONAL NOTIFICATION
    # =========================

    @pytest.mark.asyncio
    async def test_execute_sends_personal_notification(self):
        # Arrange
        lead = MagicMock()
        lead.id = "lead-123"
        lead.vehicle_id = "vehicle-789"
        lead.status.value = "ASSIGNED"
        lead.assigned_to = "agent-456"

        self.lead_repository.find_by_id.return_value = lead

        counts = SimpleNamespace(
            my_leads_count=7,
            new_leads_count=15,
        )

        self.sales_dashboard_repository.get_notification_counts.return_value = (
            counts
        )

        self.user_repository.get_by_role.return_value = []

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.notification_service.send_update.assert_any_await(
            user_id="agent-456",
            payload={
                "type": "MY_LEADS_UPDATED",
                "count": 7,
            },
        )

    # =========================
    # GLOBAL NOTIFICATIONS
    # =========================

    @pytest.mark.asyncio
    async def test_execute_notifies_all_sales_agents(self):
        # Arrange
        lead = MagicMock()
        lead.id = "lead-123"
        lead.vehicle_id = "vehicle-789"
        lead.status.value = "ASSIGNED"
        lead.assigned_to = "agent-456"

        self.lead_repository.find_by_id.return_value = lead

        counts = SimpleNamespace(
            my_leads_count=7,
            new_leads_count=15,
        )

        self.sales_dashboard_repository.get_notification_counts.return_value = (
            counts
        )

        sales_agents = [
            SimpleNamespace(id="agent-456"),
            SimpleNamespace(id="agent-789"),
            SimpleNamespace(id="agent-999"),
        ]

        self.user_repository.get_by_role.return_value = sales_agents

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.user_repository.get_by_role.assert_called_once_with(
            UserRole.SALES_AGENT,
        )

        assert self.notification_service.send_update.await_count == 4

        self.notification_service.send_update.assert_any_await(
            user_id="agent-456",
            payload={
                "type": "NEW_LEADS_UPDATED",
                "count": 15,
            },
        )

        self.notification_service.send_update.assert_any_await(
            user_id="agent-789",
            payload={
                "type": "NEW_LEADS_UPDATED",
                "count": 15,
            },
        )

        self.notification_service.send_update.assert_any_await(
            user_id="agent-999",
            payload={
                "type": "NEW_LEADS_UPDATED",
                "count": 15,
            },
        )

    # =========================
    # USER REPOSITORY FAILURE
    # =========================

    @pytest.mark.asyncio
    async def test_execute_rolls_back_when_getting_sales_agents_fails(
        self,
    ):
        # Arrange
        lead = MagicMock()
        lead.id = "lead-123"
        lead.vehicle_id = "vehicle-789"
        lead.status.value = "ASSIGNED"

        self.lead_repository.find_by_id.return_value = lead

        counts = SimpleNamespace(
            my_leads_count=7,
            new_leads_count=15,
        )

        self.sales_dashboard_repository.get_notification_counts.return_value = (
            counts
        )

        self.user_repository.get_by_role.side_effect = RuntimeError(
            "Erreur récupération agents"
        )

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match="Erreur récupération agents",
        ):
            await self.use_case.execute(self.dto)

        self.unit_of_work.commit.assert_called_once()
        self.unit_of_work.rollback.assert_called_once()

    # =========================
    # NOTIFICATION FAILURE
    # =========================

    @pytest.mark.asyncio
    async def test_execute_rolls_back_when_notification_fails(self):
        # Arrange
        lead = MagicMock()
        lead.id = "lead-123"
        lead.vehicle_id = "vehicle-789"
        lead.status.value = "ASSIGNED"

        self.lead_repository.find_by_id.return_value = lead

        counts = SimpleNamespace(
            my_leads_count=7,
            new_leads_count=15,
        )

        self.sales_dashboard_repository.get_notification_counts.return_value = (
            counts
        )

        self.user_repository.get_by_role.return_value = []

        self.notification_service.send_update.side_effect = (
            RuntimeError("Erreur notification")
        )

        # Act / Assert
        with pytest.raises(
            RuntimeError,
            match="Erreur notification",
        ):
            await self.use_case.execute(self.dto)

        self.unit_of_work.commit.assert_called_once()
        self.unit_of_work.rollback.assert_called_once()