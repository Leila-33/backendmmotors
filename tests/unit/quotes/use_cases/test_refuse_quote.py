from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import LeadNotFound
from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType,
)
from modules.quotes.application.dtos.refuse_quote_dto import (
    RefuseQuoteDTO,
)
from modules.quotes.application.results.quote_action_result import (
    QuoteActionResult,
)
from modules.quotes.application.use_cases.refuse_quote import (
    RefuseQuoteUseCase,
)
from modules.quotes.domain.exceptions import QuoteNotFound


# ============================================================
# HELPERS
# ============================================================


def make_quote(
    *,
    quote_id: str = "quote-1",
    lead_id: str = "lead-1",
):
    quote = Mock(
        id=quote_id,
        lead_id=lead_id,
        refusal_reason=None,
        refusal_comment=None,
    )

    quote.refuse.side_effect = lambda reason, comment: (
        setattr(quote, "refusal_reason", reason),
        setattr(quote, "refusal_comment", comment),
    )

    return quote


def make_lead(
    *,
    lead_id: str = "lead-1",
    user_id: str = "user-1",
    vehicle_id: str = "vehicle-1",
    assigned_to: str = "agent-1",
):
    return Mock(
        id=lead_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        assigned_to=assigned_to,
    )


def make_dto(
    *,
    quote_id: str = "quote-1",
    customer_id: str = "user-1",
    reason: str = "Prix trop élevé",
    comment: str = "Le montant dépasse mon budget.",
):
    return RefuseQuoteDTO(
        quote_id=quote_id,
        customer_id=customer_id,
        reason=reason,
        comment=comment,
    )


# ============================================================
# FIXTURES
# ============================================================


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
    service.send_update = AsyncMock()
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


# ============================================================
# QUOTE NOT FOUND
# ============================================================


@pytest.mark.asyncio
async def test_quote_not_found(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
    event_service,
    unit_of_work,
):
    dto = make_dto()

    quote_repository.find_by_id.return_value = None

    with pytest.raises(QuoteNotFound):
        await use_case.execute(dto)

    quote_repository.find_by_id.assert_called_once_with(
        "quote-1"
    )

    lead_repository.find_by_id.assert_not_called()

    quote_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    notification_service.send.assert_not_awaited()
    notification_service.send_update.assert_not_awaited()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# LEAD NOT FOUND
# ============================================================


@pytest.mark.asyncio
async def test_lead_not_found(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
    event_service,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = None

    with pytest.raises(LeadNotFound):
        await use_case.execute(dto)

    quote_repository.find_by_id.assert_called_once_with(
        "quote-1"
    )

    lead_repository.find_by_id.assert_called_once_with(
        "lead-1"
    )

    quote.refuse.assert_not_called()
    quote_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    notification_service.send.assert_not_awaited()
    notification_service.send_update.assert_not_awaited()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# AUTHORIZATION
# ============================================================


@pytest.mark.asyncio
async def test_customer_cannot_refuse_another_customer_quote(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
    event_service,
    unit_of_work,
):
    dto = make_dto(
        customer_id="another-user"
    )

    quote = make_quote()

    lead = make_lead(
        user_id="owner-user"
    )

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    with pytest.raises(QuoteNotFound):
        await use_case.execute(dto)

    quote.refuse.assert_not_called()

    quote_repository.update.assert_not_called()
    lead.change_status.assert_not_called()
    lead_repository.update.assert_not_called()

    event_service.log.assert_not_called()

    notification_service.send.assert_not_awaited()
    notification_service.send_update.assert_not_awaited()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# QUOTE REFUSAL
# ============================================================


@pytest.mark.asyncio
async def test_quote_is_refused_with_reason_and_comment(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    dto = make_dto(
        reason="Prix trop élevé",
        comment="Je ne souhaite pas donner suite.",
    )

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(dto)

    quote.refuse.assert_called_once_with(
        reason="Prix trop élevé",
        comment="Je ne souhaite pas donner suite.",
    )

    quote_repository.update.assert_called_once_with(
        quote
    )

    unit_of_work.commit.assert_called_once()


@pytest.mark.asyncio
async def test_quote_is_updated_after_refusal(
    use_case,
    quote_repository,
    lead_repository,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(dto)

    quote_repository.update.assert_called_once_with(
        quote
    )


# ============================================================
# LEAD STATUS
# ============================================================


@pytest.mark.asyncio
async def test_lead_is_marked_as_lost(
    use_case,
    quote_repository,
    lead_repository,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(dto)

    lead.change_status.assert_called_once_with(
        LeadStatus.LOST
    )

    lead_repository.update.assert_called_once_with(
        lead
    )


# ============================================================
# EVENT
# ============================================================


@pytest.mark.asyncio
async def test_quote_refused_event_is_logged(
    use_case,
    quote_repository,
    lead_repository,
    event_service,
):
    dto = make_dto(
        customer_id="user-1",
        reason="Prix trop élevé",
        comment="Budget insuffisant.",
    )

    quote = make_quote()

    lead = make_lead(
        lead_id="lead-1",
        user_id="user-1",
        vehicle_id="vehicle-1",
    )

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(dto)

    event_service.log.assert_called_once_with(
        type=EventType.QUOTE_REFUSED,
        message="Devis refusé par le client",
        quote_id="quote-1",
        lead_id="lead-1",
        user_id="user-1",
        vehicle_id="vehicle-1",
        event_metadata={
            "reason": "Prix trop élevé",
            "comment": "Budget insuffisant.",
        },
    )


@pytest.mark.asyncio
async def test_quote_refused_event_contains_refusal_metadata(
    use_case,
    quote_repository,
    lead_repository,
    event_service,
):
    dto = make_dto(
        reason="Délai trop long",
        comment="Je souhaite une livraison plus rapide.",
    )

    quote = make_quote()

    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(dto)

    event_args = event_service.log.call_args.kwargs

    assert event_args["type"] == EventType.QUOTE_REFUSED
    assert event_args["quote_id"] == "quote-1"
    assert event_args["lead_id"] == "lead-1"
    assert event_args["user_id"] == "user-1"
    assert event_args["vehicle_id"] == "vehicle-1"

    assert event_args["event_metadata"] == {
        "reason": "Délai trop long",
        "comment": "Je souhaite une livraison plus rapide.",
    }
# ============================================================
# NOTIFICATION
# ============================================================


@pytest.mark.asyncio
async def test_agent_is_notified_when_quote_is_refused(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead(
        assigned_to="agent-42"
    )

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(dto)

    notification_service.send.assert_awaited_once_with(
        user_id="agent-42",
        title="Offre refusée",
        message="Le client a refusé votre offre.",
        notif_type=NotificationType.QUOTE_REFUSED,
        entity_type=NotificationEntityType.QUOTE,
        entity_id="quote-1",
    )


# ============================================================
# COMMIT
# ============================================================


@pytest.mark.asyncio
async def test_transaction_is_committed(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# ACTION REQUIRED COUNT
# ============================================================


@pytest.mark.asyncio
async def test_action_required_count_is_loaded_after_commit(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    quote_repository.count_action_required_by_customer.return_value = 3

    await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()

    quote_repository.count_action_required_by_customer.assert_called_once_with(
        "user-1"
    )


# ============================================================
# SEND UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_customer_receives_quote_updated_notification(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    quote_repository.count_action_required_by_customer.return_value = 4

    await use_case.execute(dto)

    notification_service.send_update.assert_awaited_once_with(
        user_id="user-1",
        payload={
            "type": "QUOTE_UPDATED",
            "count": 4,
        },
    )


@pytest.mark.asyncio
async def test_send_update_uses_current_action_required_count(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    quote_repository.count_action_required_by_customer.return_value = 0

    await use_case.execute(dto)

    notification_service.send_update.assert_awaited_once_with(
        user_id="user-1",
        payload={
            "type": "QUOTE_UPDATED",
            "count": 0,
        },
    )


# ============================================================
# RESULT
# ============================================================


@pytest.mark.asyncio
async def test_quote_action_result_is_returned(
    use_case,
    quote_repository,
    lead_repository,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    result = await use_case.execute(dto)

    assert isinstance(
        result,
        QuoteActionResult,
    )

    assert result.quote_id == "quote-1"

    assert result.message == (
        "Offre refusée avec succès."
    )


# ============================================================
# ROLLBACK — QUOTE REFUSAL
# ============================================================


@pytest.mark.asyncio
async def test_quote_refusal_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    quote.refuse.side_effect = RuntimeError(
        "refusal error"
    )

    with pytest.raises(
        RuntimeError,
        match="refusal error",
    ):
        await use_case.execute(dto)

    quote_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — QUOTE UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_quote_update_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    quote_repository.update.side_effect = RuntimeError(
        "quote update error"
    )

    with pytest.raises(
        RuntimeError,
        match="quote update error",
    ):
        await use_case.execute(dto)

    lead.change_status.assert_not_called()
    lead_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — LEAD STATUS
# ============================================================


@pytest.mark.asyncio
async def test_lead_status_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    lead.change_status.side_effect = RuntimeError(
        "lead status error"
    )

    with pytest.raises(
        RuntimeError,
        match="lead status error",
    ):
        await use_case.execute(dto)

    lead_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — LEAD UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_lead_update_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    lead_repository.update.side_effect = RuntimeError(
        "lead update error"
    )

    with pytest.raises(
        RuntimeError,
        match="lead update error",
    ):
        await use_case.execute(dto)

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — EVENT
# ============================================================


@pytest.mark.asyncio
async def test_event_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    event_service,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        await use_case.execute(dto)

    notification_service = use_case.notification_service

    notification_service.send.assert_not_awaited()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — NOTIFICATION
# ============================================================


@pytest.mark.asyncio
async def test_notification_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    notification_service.send.side_effect = RuntimeError(
        "notification error"
    )

    with pytest.raises(
        RuntimeError,
        match="notification error",
    ):
        await use_case.execute(dto)

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — COMMIT
# ============================================================


@pytest.mark.asyncio
async def test_commit_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — COUNT
# ============================================================


@pytest.mark.asyncio
async def test_count_action_required_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    quote_repository.count_action_required_by_customer.side_effect = (
        RuntimeError("count error")
    )

    with pytest.raises(
        RuntimeError,
        match="count error",
    ):
        await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ROLLBACK — SEND UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_send_update_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    quote_repository.count_action_required_by_customer.return_value = 2

    notification_service.send_update.side_effect = RuntimeError(
        "send update error"
    )

    with pytest.raises(
        RuntimeError,
        match="send update error",
    ):
        await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ORDER OF OPERATIONS
# ============================================================


@pytest.mark.asyncio
async def test_count_is_loaded_after_commit(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    dto = make_dto()

    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    quote_repository.count_action_required_by_customer.return_value = 5

    call_order = []

    def commit():
        call_order.append("commit")

    def count(customer_id):
        call_order.append("count")
        return 5

    unit_of_work.commit.side_effect = commit
    quote_repository.count_action_required_by_customer.side_effect = count

    await use_case.execute(dto)

    assert call_order == [
        "commit",
        "count",
    ]