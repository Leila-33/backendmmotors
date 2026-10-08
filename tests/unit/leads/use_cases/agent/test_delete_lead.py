import pytest
from unittest.mock import AsyncMock, MagicMock

from modules.leads.application.dtos.agent.agent_lead_dto import (
    AgentLeadDTO,
)
from modules.leads.application.use_cases.agent.delete_lead import (
    DeleteLeadUseCase,
)
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import (
    LeadNotFound,
    LeadCannotBeDeleted,
)
from modules.applications.domain.enums import EventType


class TestDeleteLeadUseCase:

    @pytest.fixture
    def lead_repository(self):
        return MagicMock()

    @pytest.fixture
    def quote_repository(self):
        return MagicMock()

    @pytest.fixture
    def lead_authorization(self):
        return MagicMock()

    @pytest.fixture
    def sales_dashboard_repository(self):
        return MagicMock()

    @pytest.fixture
    def notification_service(self):
        service = MagicMock()
        service.send_update = AsyncMock()
        return service

    @pytest.fixture
    def event_service(self):
        return MagicMock()

    @pytest.fixture
    def unit_of_work(self):
        return MagicMock()

    @pytest.fixture
    def use_case(
        self,
        lead_repository,
        quote_repository,
        lead_authorization,
        sales_dashboard_repository,
        notification_service,
        event_service,
        unit_of_work,
    ):
        return DeleteLeadUseCase(
            lead_repository=lead_repository,
            quote_repository=quote_repository,
            lead_authorization=lead_authorization,
            sales_dashboard_repository=sales_dashboard_repository,
            notification_service=notification_service,
            event_service=event_service,
            unit_of_work=unit_of_work,
        )

    @staticmethod
    def create_lead(
        lead_id=1,
        agent_id=10,
        vehicle_id=100,
        email="client@test.com",
        status=LeadStatus.NEW,
    ):
        lead = MagicMock()

        lead.id = lead_id
        lead.assigned_to = agent_id
        lead.vehicle_id = vehicle_id
        lead.email = email
        lead.status = status

        return lead

    @staticmethod
    def create_dto(
        lead_id=1,
        agent_id=10,
    ):
        return AgentLeadDTO(
            lead_id=lead_id,
            agent_id=agent_id,
        )

    # ==========================================================
    # SUCCESS
    # ==========================================================

    @pytest.mark.asyncio
    async def test_deletes_lead_successfully(
        self,
        use_case,
        lead_repository,
        quote_repository,
        lead_authorization,
        sales_dashboard_repository,
        notification_service,
        event_service,
        unit_of_work,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False
        sales_dashboard_repository.count_my_leads.return_value = 4

        result = await use_case.execute(dto)

        assert result.lead_id == lead.id
        assert result.message == "Lead supprimé avec succès."

        lead_repository.find_by_id.assert_called_once_with(
            dto.lead_id
        )

        lead_authorization.check_owner.assert_called_once_with(
            lead,
            dto.agent_id,
        )

        quote_repository.has_any_quote.assert_called_once_with(
            lead.id
        )

        lead_repository.delete.assert_called_once_with(
            lead.id
        )

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_not_called()

    # ==========================================================
    # LEAD NOT FOUND
    # ==========================================================

    @pytest.mark.asyncio
    async def test_raises_lead_not_found(
        self,
        use_case,
        lead_repository,
        lead_authorization,
        quote_repository,
        unit_of_work,
    ):
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = None

        with pytest.raises(LeadNotFound):
            await use_case.execute(dto)

        lead_repository.find_by_id.assert_called_once_with(
            dto.lead_id
        )

        lead_authorization.check_owner.assert_not_called()
        quote_repository.has_any_quote.assert_not_called()
        lead_repository.delete.assert_not_called()

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # AUTHORIZATION
    # ==========================================================

    @pytest.mark.asyncio
    async def test_checks_agent_ownership(
        self,
        use_case,
        lead_repository,
        lead_authorization,
        quote_repository,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False

        await use_case.execute(dto)

        lead_authorization.check_owner.assert_called_once_with(
            lead,
            dto.agent_id,
        )

    @pytest.mark.asyncio
    async def test_propagates_authorization_error(
        self,
        use_case,
        lead_repository,
        lead_authorization,
        quote_repository,
        unit_of_work,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead

        authorization_error = Exception("Unauthorized")

        lead_authorization.check_owner.side_effect = (
            authorization_error
        )

        with pytest.raises(Exception, match="Unauthorized"):
            await use_case.execute(dto)

        quote_repository.has_any_quote.assert_not_called()
        lead_repository.delete.assert_not_called()

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # STATUS
    # ==========================================================

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status",
        [
            LeadStatus.NEW,
            LeadStatus.ASSIGNED,
            LeadStatus.CONTACTED,
        ],
    )
    async def test_allows_deletion_for_valid_statuses(
        self,
        status,
        use_case,
        lead_repository,
        quote_repository,
        unit_of_work,
    ):
        lead = self.create_lead(status=status)
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False

        await use_case.execute(dto)

        lead_repository.delete.assert_called_once_with(
            lead.id
        )

        unit_of_work.commit.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "status",
        [
            LeadStatus.LOST,
            LeadStatus.WON,
        ],
    )
    async def test_rejects_deletion_for_invalid_statuses(
        self,
        status,
        use_case,
        lead_repository,
        quote_repository,
        unit_of_work,
    ):
        lead = self.create_lead(status=status)
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead

        with pytest.raises(LeadCannotBeDeleted):
            await use_case.execute(dto)

        quote_repository.has_any_quote.assert_not_called()
        lead_repository.delete.assert_not_called()

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # QUOTE CHECK
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rejects_deletion_when_lead_has_quote(
        self,
        use_case,
        lead_repository,
        quote_repository,
        unit_of_work,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = True

        with pytest.raises(LeadCannotBeDeleted):
            await use_case.execute(dto)

        quote_repository.has_any_quote.assert_called_once_with(
            lead.id
        )

        lead_repository.delete.assert_not_called()

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_allows_deletion_when_lead_has_no_quote(
        self,
        use_case,
        lead_repository,
        quote_repository,
        unit_of_work,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False

        await use_case.execute(dto)

        quote_repository.has_any_quote.assert_called_once_with(
            lead.id
        )

        lead_repository.delete.assert_called_once_with(
            lead.id
        )

        unit_of_work.commit.assert_called_once()

    # ==========================================================
    # DELETE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_deletes_correct_lead(
        self,
        use_case,
        lead_repository,
        quote_repository,
    ):
        lead = self.create_lead(lead_id=42)
        dto = self.create_dto(lead_id=42)

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False

        await use_case.execute(dto)

        lead_repository.delete.assert_called_once_with(42)

    # ==========================================================
    # EVENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_logs_lead_deleted_event(
        self,
        use_case,
        lead_repository,
        quote_repository,
        event_service,
        unit_of_work,
    ):
        lead = self.create_lead(
            lead_id=42,
            agent_id=10,
            vehicle_id=100,
            email="client@test.com",
            status=LeadStatus.NEW,
        )
        dto = self.create_dto(
            lead_id=42,
            agent_id=10,
        )

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False

        await use_case.execute(dto)

        event_service.log.assert_called_once_with(
            type=EventType.LEAD_DELETED,
            message="Lead supprimé",
            user_id=dto.agent_id,
            lead_id=lead.id,
            vehicle_id=lead.vehicle_id,
            event_metadata={
                "email": lead.email,
                "status": lead.status.value,
            },
        )

        unit_of_work.commit.assert_called_once()

    # ==========================================================
    # COMMIT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_commits_after_delete_and_event(
        self,
        use_case,
        lead_repository,
        quote_repository,
        event_service,
        unit_of_work,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False

        await use_case.execute(dto)

        assert lead_repository.delete.call_count == 1
        assert event_service.log.call_count == 1
        assert unit_of_work.commit.call_count == 1

    # ==========================================================
    # DASHBOARD COUNT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_gets_updated_my_leads_count(
        self,
        use_case,
        lead_repository,
        quote_repository,
        sales_dashboard_repository,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False
        sales_dashboard_repository.count_my_leads.return_value = 7

        await use_case.execute(dto)

        sales_dashboard_repository.count_my_leads.assert_called_once_with(
            agent_id=dto.agent_id,
        )

    # ==========================================================
    # NOTIFICATION
    # ==========================================================

    @pytest.mark.asyncio
    async def test_sends_my_leads_updated_notification(
        self,
        use_case,
        lead_repository,
        quote_repository,
        sales_dashboard_repository,
        notification_service,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False
        sales_dashboard_repository.count_my_leads.return_value = 7

        await use_case.execute(dto)

        notification_service.send_update.assert_awaited_once_with(
            user_id=dto.agent_id,
            payload={
                "type": "MY_LEADS_UPDATED",
                "count": 7,
            },
        )

    @pytest.mark.asyncio
    async def test_notification_uses_agent_id(
        self,
        use_case,
        lead_repository,
        quote_repository,
        sales_dashboard_repository,
        notification_service,
    ):
        lead = self.create_lead()
        dto = self.create_dto(agent_id=123)

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False
        sales_dashboard_repository.count_my_leads.return_value = 3

        await use_case.execute(dto)

        notification_service.send_update.assert_awaited_once_with(
            user_id=123,
            payload={
                "type": "MY_LEADS_UPDATED",
                "count": 3,
            },
        )

    # ==========================================================
    # ROLLBACK
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_delete_fails(
        self,
        use_case,
        lead_repository,
        quote_repository,
        unit_of_work,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False

        lead_repository.delete.side_effect = Exception(
            "Delete failed"
        )

        with pytest.raises(Exception, match="Delete failed"):
            await use_case.execute(dto)

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_rolls_back_when_event_fails(
        self,
        use_case,
        lead_repository,
        quote_repository,
        event_service,
        unit_of_work,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False

        event_service.log.side_effect = Exception(
            "Event failed"
        )

        with pytest.raises(Exception, match="Event failed"):
            await use_case.execute(dto)

        lead_repository.delete.assert_called_once_with(
            lead.id
        )

        unit_of_work.commit.assert_not_called()
        unit_of_work.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_rolls_back_when_commit_fails(
        self,
        use_case,
        lead_repository,
        quote_repository,
        unit_of_work,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False

        unit_of_work.commit.side_effect = Exception(
            "Commit failed"
        )

        with pytest.raises(Exception, match="Commit failed"):
            await use_case.execute(dto)

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # NOTIFICATION ERROR
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_notification_fails(
        self,
        use_case,
        lead_repository,
        quote_repository,
        sales_dashboard_repository,
        notification_service,
        unit_of_work,
    ):
        lead = self.create_lead()
        dto = self.create_dto()

        lead_repository.find_by_id.return_value = lead
        quote_repository.has_any_quote.return_value = False
        sales_dashboard_repository.count_my_leads.return_value = 5

        notification_service.send_update.side_effect = Exception(
            "Notification failed"
        )

        with pytest.raises(
            Exception,
            match="Notification failed",
        ):
            await use_case.execute(dto)

        unit_of_work.commit.assert_called_once()
        unit_of_work.rollback.assert_called_once()