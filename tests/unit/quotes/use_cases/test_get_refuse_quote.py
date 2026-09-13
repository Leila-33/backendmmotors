from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from modules.quotes.application.use_cases.refuse_quote import (
    RefuseQuoteUseCase,
)
from modules.quotes.application.dtos.refuse_quote_dto import (
    RefuseQuoteDTO,
)
from modules.quotes.domain.exceptions import QuoteNotFound
from modules.leads.domain.exceptions import LeadNotFound
from modules.leads.domain.enums import LeadStatus
from modules.notifications.domain.enums import (
    NotificationType,
    NotificationEntityType,
)
from modules.applications.domain.enums import EventType


@pytest.fixture
def quote_repository():
    return Mock()


@pytest.fixture
def lead_repository():
    return Mock()


@pytest.fixture
def notification_service():
    service = Mock()
    service.send = AsyncMock()
    return service


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    quote_repository,
    lead_repository,
    notification_service,
    event_service,
    unit_of_work,
):
    return RefuseQuoteUseCase(
        quote_repository=quote_repository,
        lead_repository=lead_repository,
        notification_service=notification_service,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return RefuseQuoteDTO(
        quote_id="quote-123",
        customer_id="customer-123",
        reason="PRICE_TOO_HIGH",
        comment="Le montant proposé est trop élevé.",
    )


def make_quote():
    quote = Mock()

    quote.id = "quote-123"
    quote.lead_id = "lead-123"

    quote.refusal_reason = "PRICE_TOO_HIGH"
    quote.refusal_comment = "Le montant proposé est trop élevé."

    return quote


def make_lead():
    lead = Mock()

    lead.id = "lead-123"
    lead.user_id = "customer-123"
    lead.vehicle_id = "vehicle-123"
    lead.assigned_to = "agent-123"

    return lead


def configure_success(
    quote_repository,
    lead_repository,
    dto,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    quote.refuse.side_effect = lambda reason, comment: (
        setattr(quote, "refusal_reason", reason),
        setattr(quote, "refusal_comment", comment),
    )

    lead.change_status.side_effect = (
        lambda status: setattr(lead, "status", status)
    )

    return quote, lead


@pytest.mark.asyncio
async def test_execute_refuses_quote_and_marks_lead_as_lost(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
    event_service,
    unit_of_work,
    dto,
):
    quote, lead = configure_success(
        quote_repository,
        lead_repository,
        dto,
    )

    result = await use_case.execute(dto)

    quote_repository.find_by_id.assert_called_once_with(
        "quote-123",
    )

    lead_repository.find_by_id.assert_called_once_with(
        "lead-123",
    )

    quote.refuse.assert_called_once_with(
        reason="PRICE_TOO_HIGH",
        comment="Le montant proposé est trop élevé.",
    )

    quote_repository.update.assert_called_once_with(quote)

    lead.change_status.assert_called_once_with(
        LeadStatus.LOST,
    )

    lead_repository.update.assert_called_once_with(lead)

    event_service.log.assert_called_once_with(
        type=EventType.QUOTE_REFUSED,
        message="Devis refusé par le client",
        quote_id="quote-123",
        lead_id="lead-123",
        user_id="customer-123",
        vehicle_id="vehicle-123",
        event_metadata={
            "reason": "PRICE_TOO_HIGH",
            "comment": "Le montant proposé est trop élevé.",
        },
    )

    notification_service.send.assert_awaited_once_with(
        user_id="agent-123",
        title="Offre refusée",
        message="Le client a refusé votre offre.",
        notif_type=NotificationType.QUOTE_REFUSED,
        entity_type=NotificationEntityType.QUOTE,
        entity_id="quote-123",
    )

    unit_of_work.commit.assert_called_once_with()
    unit_of_work.rollback.assert_not_called()

    assert result.quote_id == "quote-123"
    assert result.message == "Offre refusée avec succès."


@pytest.mark.asyncio
async def test_execute_raises_quote_not_found_when_quote_does_not_exist(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
    dto,
):
    quote_repository.find_by_id.return_value = None

    with pytest.raises(QuoteNotFound):
        await use_case.execute(dto)

    quote_repository.find_by_id.assert_called_once_with(
        "quote-123",
    )

    lead_repository.find_by_id.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


@pytest.mark.asyncio
async def test_execute_raises_lead_not_found_when_lead_does_not_exist(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
    dto,
):
    quote = make_quote()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = None

    with pytest.raises(LeadNotFound):
        await use_case.execute(dto)

    quote_repository.find_by_id.assert_called_once_with(
        "quote-123",
    )

    lead_repository.find_by_id.assert_called_once_with(
        "lead-123",
    )

    quote.refuse.assert_not_called()
    quote_repository.update.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


@pytest.mark.asyncio
async def test_execute_raises_quote_not_found_for_wrong_customer(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
    dto,
):
    quote = make_quote()
    lead = make_lead()
    lead.user_id = "another-customer"

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    with pytest.raises(QuoteNotFound):
        await use_case.execute(dto)

    quote.refuse.assert_not_called()
    quote_repository.update.assert_not_called()
    lead_repository.update.assert_not_called()

    unit_of_work.rollback.assert_called_once_with()


@pytest.mark.asyncio
async def test_execute_propagates_quote_refuse_error(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
    dto,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    quote.refuse.side_effect = RuntimeError("Refuse error")

    with pytest.raises(RuntimeError, match="Refuse error"):
        await use_case.execute(dto)

    quote.refuse.assert_called_once_with(
        reason="PRICE_TOO_HIGH",
        comment="Le montant proposé est trop élevé.",
    )

    quote_repository.update.assert_not_called()
    lead.change_status.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


@pytest.mark.asyncio
async def test_execute_propagates_quote_update_error(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
    dto,
):
    quote, lead = configure_success(
        quote_repository,
        lead_repository,
        dto,
    )

    quote_repository.update.side_effect = RuntimeError(
        "Quote update error"
    )

    with pytest.raises(RuntimeError, match="Quote update error"):
        await use_case.execute(dto)

    quote.refuse.assert_called_once()
    quote_repository.update.assert_called_once_with(quote)

    lead.change_status.assert_not_called()
    lead_repository.update.assert_not_called()

    unit_of_work.rollback.assert_called_once_with()


@pytest.mark.asyncio
async def test_execute_propagates_lead_status_change_error(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
    dto,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    lead.change_status.side_effect = RuntimeError(
        "Status change error"
    )

    with pytest.raises(RuntimeError, match="Status change error"):
        await use_case.execute(dto)

    quote_repository.update.assert_called_once_with(quote)

    lead.change_status.assert_called_once_with(
        LeadStatus.LOST,
    )

    lead_repository.update.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


@pytest.mark.asyncio
async def test_execute_propagates_lead_update_error(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
    dto,
):
    quote, lead = configure_success(
        quote_repository,
        lead_repository,
        dto,
    )

    lead_repository.update.side_effect = RuntimeError(
        "Lead update error"
    )

    with pytest.raises(RuntimeError, match="Lead update error"):
        await use_case.execute(dto)

    quote_repository.update.assert_called_once_with(quote)

    lead.change_status.assert_called_once_with(
        LeadStatus.LOST,
    )

    lead_repository.update.assert_called_once_with(lead)

    event_service = use_case.event_service
    event_service.log.assert_not_called()

    unit_of_work.rollback.assert_called_once_with()


@pytest.mark.asyncio
async def test_execute_propagates_event_error(
    use_case,
    quote_repository,
    lead_repository,
    event_service,
    notification_service,
    unit_of_work,
    dto,
):
    quote, lead = configure_success(
        quote_repository,
        lead_repository,
        dto,
    )

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(RuntimeError, match="Event error"):
        await use_case.execute(dto)

    quote_repository.update.assert_called_once_with(quote)
    lead_repository.update.assert_called_once_with(lead)

    notification_service.send.assert_not_awaited()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


@pytest.mark.asyncio
async def test_execute_propagates_notification_error(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
    event_service,
    unit_of_work,
    dto,
):
    quote, lead = configure_success(
        quote_repository,
        lead_repository,
        dto,
    )

    notification_service.send.side_effect = RuntimeError(
        "Notification error"
    )

    with pytest.raises(RuntimeError, match="Notification error"):
        await use_case.execute(dto)

    event_service.log.assert_called_once()

    notification_service.send.assert_awaited_once()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


@pytest.mark.asyncio
async def test_execute_propagates_commit_error(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
    unit_of_work,
    dto,
):
    quote, lead = configure_success(
        quote_repository,
        lead_repository,
        dto,
    )

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(RuntimeError, match="Commit error"):
        await use_case.execute(dto)

    quote_repository.update.assert_called_once_with(quote)
    lead_repository.update.assert_called_once_with(lead)

    notification_service.send.assert_awaited_once()

    unit_of_work.commit.assert_called_once_with()
    unit_of_work.rollback.assert_called_once_with()