from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.applications.domain.enums import EventType
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import LeadNotFound
from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType,
)
from modules.quotes.application.dtos.refuse_quote_dto import RefuseQuoteDTO
from modules.quotes.application.use_cases.refuse_quote import (
    RefuseQuoteUseCase,
)
from modules.quotes.domain.exceptions import QuoteNotFound


class TestRefuseQuoteUseCase:

    def setup_method(self):
        self.quote_repository = MagicMock()
        self.lead_repository = MagicMock()
        self.sales_dashboard_repository = MagicMock()

        self.notification_service = MagicMock()
        self.notification_service.send = AsyncMock()
        self.notification_service.send_update = AsyncMock()

        self.event_service = MagicMock()
        self.unit_of_work = MagicMock()

        self.use_case = RefuseQuoteUseCase(
            quote_repository=self.quote_repository,
            lead_repository=self.lead_repository,
            sales_dashboard_repository=self.sales_dashboard_repository,
            notification_service=self.notification_service,
            event_service=self.event_service,
            unit_of_work=self.unit_of_work,
        )

        self.dto = RefuseQuoteDTO(
            quote_id="quote-123",
            customer_id="customer-456",
            reason="PRICE_TOO_HIGH",
            comment="Le montant proposé est trop élevé.",
        )

    # ==========================================================
    # SUCCÈS
    # ==========================================================

    @pytest.mark.asyncio
    async def test_refuse_quote_successfully(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"
        quote.refusal_reason = self.dto.reason
        quote.refusal_comment = self.dto.comment

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = "customer-456"
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = "agent-111"

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.sales_dashboard_repository.count_my_leads.return_value = 4
        self.quote_repository.count_action_required_by_customer.return_value = 2

        # Act
        result = await self.use_case.execute(self.dto)

        # Assert
        assert result.quote_id == "quote-123"
        assert result.message == "Offre refusée avec succès."

        quote.refuse.assert_called_once_with(
            reason=self.dto.reason,
            comment=self.dto.comment,
        )

        self.quote_repository.update.assert_called_once_with(quote)

        lead.change_status.assert_called_once_with(
            LeadStatus.LOST
        )

        self.lead_repository.update.assert_called_once_with(lead)

        self.event_service.log.assert_called_once_with(
            type=EventType.QUOTE_REFUSED,
            message="Devis refusé par le client",
            quote_id=quote.id,
            lead_id=lead.id,
            user_id=self.dto.customer_id,
            vehicle_id=lead.vehicle_id,
            event_metadata={
                "reason": quote.refusal_reason,
                "comment": quote.refusal_comment,
            },
        )

        self.notification_service.send.assert_awaited_once_with(
            user_id=lead.assigned_to,
            title="Offre refusée",
            message="Le client a refusé votre offre.",
            notif_type=NotificationType.QUOTE_REFUSED,
            entity_type=NotificationEntityType.QUOTE,
            entity_id=quote.id,
        )

        self.unit_of_work.commit.assert_called_once()
        self.unit_of_work.rollback.assert_not_called()

        self.sales_dashboard_repository.count_my_leads.assert_called_once_with(
            agent_id=lead.assigned_to,
        )

        self.notification_service.send_update.assert_any_await(
            user_id=lead.assigned_to,
            payload={
                "type": "MY_LEADS_UPDATED",
                "count": 4,
            },
        )

        self.quote_repository.count_action_required_by_customer.assert_called_once_with(
            self.dto.customer_id
        )

        self.notification_service.send_update.assert_any_await(
            user_id=self.dto.customer_id,
            payload={
                "type": "QUOTE_UPDATED",
                "count": 2,
            },
        )

    # ==========================================================
    # QUOTE INTROUVABLE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_raises_quote_not_found_when_quote_does_not_exist(self):
        # Arrange
        self.quote_repository.find_by_id.return_value = None

        # Act / Assert
        with pytest.raises(QuoteNotFound):
            await self.use_case.execute(self.dto)

        self.quote_repository.find_by_id.assert_called_once_with(
            self.dto.quote_id
        )

        self.lead_repository.find_by_id.assert_not_called()
        self.quote_repository.update.assert_not_called()
        self.lead_repository.update.assert_not_called()
        self.event_service.log.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

        self.notification_service.send.assert_not_awaited()
        self.notification_service.send_update.assert_not_awaited()

    # ==========================================================
    # LEAD INTROUVABLE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_raises_lead_not_found_when_lead_does_not_exist(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = None

        # Act / Assert
        with pytest.raises(LeadNotFound):
            await self.use_case.execute(self.dto)

        self.quote_repository.find_by_id.assert_called_once_with(
            self.dto.quote_id
        )

        self.lead_repository.find_by_id.assert_called_once_with(
            quote.lead_id
        )

        self.quote_repository.update.assert_not_called()
        self.lead_repository.update.assert_not_called()
        self.event_service.log.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

        self.notification_service.send.assert_not_awaited()
        self.notification_service.send_update.assert_not_awaited()

    # ==========================================================
    # CLIENT NON AUTORISÉ
    # ==========================================================

    @pytest.mark.asyncio
    async def test_raises_quote_not_found_when_customer_does_not_own_lead(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = "another-customer"

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        # Act / Assert
        with pytest.raises(QuoteNotFound):
            await self.use_case.execute(self.dto)

        quote.refuse.assert_not_called()

        self.quote_repository.update.assert_not_called()
        self.lead_repository.update.assert_not_called()
        self.event_service.log.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

        self.notification_service.send.assert_not_awaited()
        self.notification_service.send_update.assert_not_awaited()

    # ==========================================================
    # REFUS DU DEVIS
    # ==========================================================

    @pytest.mark.asyncio
    async def test_calls_quote_refuse_with_reason_and_comment(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = None

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.quote_repository.count_action_required_by_customer.return_value = 0

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        quote.refuse.assert_called_once_with(
            reason=self.dto.reason,
            comment=self.dto.comment,
        )

    # ==========================================================
    # LEAD PASSE À LOST
    # ==========================================================

    @pytest.mark.asyncio
    async def test_changes_lead_status_to_lost(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = None

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.quote_repository.count_action_required_by_customer.return_value = 0

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        lead.change_status.assert_called_once_with(
            LeadStatus.LOST
        )

        self.lead_repository.update.assert_called_once_with(lead)

    # ==========================================================
    # EVENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_logs_quote_refused_event(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"
        quote.refusal_reason = "PRICE_TOO_HIGH"
        quote.refusal_comment = "Trop cher."

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = None

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.quote_repository.count_action_required_by_customer.return_value = 0

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.event_service.log.assert_called_once_with(
            type=EventType.QUOTE_REFUSED,
            message="Devis refusé par le client",
            quote_id=quote.id,
            lead_id=lead.id,
            user_id=self.dto.customer_id,
            vehicle_id=lead.vehicle_id,
            event_metadata={
                "reason": quote.refusal_reason,
                "comment": quote.refusal_comment,
            },
        )

    # ==========================================================
    # NOTIFICATION AGENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_notifies_assigned_agent(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = "agent-111"

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.sales_dashboard_repository.count_my_leads.return_value = 3
        self.quote_repository.count_action_required_by_customer.return_value = 1

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.notification_service.send.assert_awaited_once_with(
            user_id="agent-111",
            title="Offre refusée",
            message="Le client a refusé votre offre.",
            notif_type=NotificationType.QUOTE_REFUSED,
            entity_type=NotificationEntityType.QUOTE,
            entity_id=quote.id,
        )

    # ==========================================================
    # PAS DE NOTIFICATION AGENT SI NON ASSIGNÉ
    # ==========================================================

    @pytest.mark.asyncio
    async def test_does_not_notify_agent_when_lead_is_not_assigned(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = None

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.quote_repository.count_action_required_by_customer.return_value = 2

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.notification_service.send.assert_not_awaited()

        self.sales_dashboard_repository.count_my_leads.assert_not_called()

        self.notification_service.send_update.assert_awaited_once_with(
            user_id=self.dto.customer_id,
            payload={
                "type": "QUOTE_UPDATED",
                "count": 2,
            },
        )

    # ==========================================================
    # COMPTEUR AGENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_updates_assigned_agent_leads_count(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = "agent-111"

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.sales_dashboard_repository.count_my_leads.return_value = 7
        self.quote_repository.count_action_required_by_customer.return_value = 1

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.sales_dashboard_repository.count_my_leads.assert_called_once_with(
            agent_id="agent-111"
        )

        self.notification_service.send_update.assert_any_await(
            user_id="agent-111",
            payload={
                "type": "MY_LEADS_UPDATED",
                "count": 7,
            },
        )

    # ==========================================================
    # COMPTEUR CLIENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_updates_customer_quote_count(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = None

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.quote_repository.count_action_required_by_customer.return_value = 5

        # Act
        await self.use_case.execute(self.dto)

        # Assert
        self.quote_repository.count_action_required_by_customer.assert_called_once_with(
            self.dto.customer_id
        )

        self.notification_service.send_update.assert_awaited_once_with(
            user_id=self.dto.customer_id,
            payload={
                "type": "QUOTE_UPDATED",
                "count": 5,
            },
        )

    # ==========================================================
    # ERREUR REFUS DU QUOTE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_quote_refuse_fails(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = None

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        quote.refuse.side_effect = RuntimeError("refusal error")

        # Act / Assert
        with pytest.raises(RuntimeError, match="refusal error"):
            await self.use_case.execute(self.dto)

        self.quote_repository.update.assert_not_called()
        self.lead_repository.update.assert_not_called()
        self.event_service.log.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

        self.notification_service.send.assert_not_awaited()
        self.notification_service.send_update.assert_not_awaited()

    # ==========================================================
    # ERREUR UPDATE QUOTE
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_quote_update_fails(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.quote_repository.update.side_effect = RuntimeError(
            "database error"
        )

        # Act / Assert
        with pytest.raises(RuntimeError, match="database error"):
            await self.use_case.execute(self.dto)

        self.lead_repository.update.assert_not_called()
        self.event_service.log.assert_not_called()

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # ERREUR EVENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_event_logging_fails(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = None

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.event_service.log.side_effect = RuntimeError(
            "event error"
        )

        # Act / Assert
        with pytest.raises(RuntimeError, match="event error"):
            await self.use_case.execute(self.dto)

        self.quote_repository.update.assert_called_once_with(quote)
        self.lead_repository.update.assert_called_once_with(lead)

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

    # ==========================================================
    # ERREUR NOTIFICATION AGENT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_agent_notification_fails(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = "agent-111"

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.notification_service.send.side_effect = RuntimeError(
            "notification error"
        )

        # Act / Assert
        with pytest.raises(RuntimeError, match="notification error"):
            await self.use_case.execute(self.dto)

        self.unit_of_work.commit.assert_not_called()
        self.unit_of_work.rollback.assert_called_once()

        self.sales_dashboard_repository.count_my_leads.assert_not_called()

    # ==========================================================
    # ERREUR COMMIT
    # ==========================================================

    @pytest.mark.asyncio
    async def test_rolls_back_when_commit_fails(self):
        # Arrange
        quote = MagicMock()
        quote.id = "quote-123"
        quote.lead_id = "lead-789"

        lead = MagicMock()
        lead.id = "lead-789"
        lead.user_id = self.dto.customer_id
        lead.vehicle_id = "vehicle-999"
        lead.assigned_to = None

        self.quote_repository.find_by_id.return_value = quote
        self.lead_repository.find_by_id.return_value = lead

        self.quote_repository.count_action_required_by_customer.return_value = 0

        self.unit_of_work.commit.side_effect = RuntimeError(
            "commit error"
        )

        # Act / Assert
        with pytest.raises(RuntimeError, match="commit error"):
            await self.use_case.execute(self.dto)

        self.unit_of_work.commit.assert_called_once()
        self.unit_of_work.rollback.assert_called_once()

        self.notification_service.send_update.assert_not_awaited()