from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from modules.quotes.application.dtos.agent.quote_agent_dto import (
    QuoteAgentDTO,
)
from modules.quotes.application.results.quote_action_result import (
    QuoteActionResult,
)
from modules.quotes.application.use_cases.agent.send_quote import (
    SendQuoteUseCase,
)
from modules.quotes.domain.entities.quote import Quote
from modules.quotes.domain.enums import QuoteStatus
from modules.quotes.domain.exceptions import (
    QuoteAlreadySent,
    QuoteNotFound,
)
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import LeadNotFound
from modules.applications.domain.enums import EventType


# ============================================================
# HELPERS
# ============================================================


def make_dto(
    *,
    quote_id="quote-1",
    agent_id="agent-1",
):
    return SimpleNamespace(
        quote_id=quote_id,
        agent_id=agent_id,
    )


def make_vehicle(
    *,
    vehicle_id="vehicle-1",
):
    return SimpleNamespace(
        id=vehicle_id,
    )


def make_customer(
    *,
    customer_id="customer-1",
    email="customer@example.com",
):
    return SimpleNamespace(
        id=customer_id,
        email=email,
    )


def make_lead(
    *,
    lead_id="lead-1",
    user_id="customer-1",
    vehicle=None,
    status=None,
):
    if vehicle is None:
        vehicle = make_vehicle()

    lead = SimpleNamespace(
        id=lead_id,
        user_id=user_id,
        vehicle=vehicle,
        status=status,
    )

    # Le use case appelle cette méthode lors de l'envoi du devis.
    lead.change_status = Mock()

    return lead


def make_quote(
    *,
    quote_id="quote-1",
    lead_id="lead-1",
    status=QuoteStatus.DRAFT,
):
    return Quote(
        id=quote_id,
        lead_id=lead_id,
        base_price=20000,
        status=status,
    )


def make_account(
    *,
    customer=None,
    token="activation-token",
):
    if customer is None:
        customer = make_customer()

    return {
        "user": customer,
        "token": token,
    }


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
def lead_authorization():
    return Mock()


@pytest.fixture
def customer_account_service():
    return Mock()


@pytest.fixture
def email_service():
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
    lead_authorization,
    customer_account_service,
    email_service,
    notification_service,
    event_service,
    unit_of_work,
):
    return SendQuoteUseCase(
        quote_repository=quote_repository,
        lead_repository=lead_repository,
        lead_authorization=lead_authorization,
        customer_account_service=customer_account_service,
        email_service=email_service,
        notification_service=notification_service,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return make_dto(
        quote_id="quote-42",
        agent_id="agent-1",
    )


@pytest.fixture
def quote():
    return make_quote(
        quote_id="quote-42",
    )


@pytest.fixture
def lead():
    return make_lead()


@pytest.fixture
def customer():
    return make_customer()


@pytest.fixture
def account(customer):
    return make_account(
        customer=customer,
        token="activation-token",
    )


# ============================================================
# QUOTE NOT FOUND
# ============================================================


@pytest.mark.asyncio
async def test_quote_not_found(
    use_case,
    quote_repository,
    unit_of_work,
    dto,
):
    quote_repository.find_by_id.return_value = None

    with pytest.raises(QuoteNotFound):
        await use_case.execute(dto)

    quote_repository.find_by_id.assert_called_once_with(
        "quote-42"
    )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# LEAD NOT FOUND
# ============================================================


@pytest.mark.asyncio
async def test_lead_not_found(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
        lead_id="lead-42",
    )

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = None

    with pytest.raises(LeadNotFound):
        await use_case.execute(dto)

    quote_repository.find_by_id.assert_called_once_with(
        "quote-42"
    )

    lead_repository.find_by_id.assert_called_once_with(
        "lead-42"
    )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# AUTHORIZATION
# ============================================================


@pytest.mark.asyncio
async def test_agent_authorization_is_checked(
    use_case,
    quote_repository,
    lead_repository,
    lead_authorization,
    customer_account_service,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
    )

    lead = make_lead()

    customer = make_customer()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    customer_account_service.ensure_account.return_value = {
        "user": customer,
        "token": "activation-token",
    }

    await use_case.execute(dto)

    lead_authorization.check_owner.assert_called_once_with(
        lead,
        "agent-1",
    )


@pytest.mark.asyncio
async def test_authorization_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    lead_authorization,
    unit_of_work,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
    )
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    lead_authorization.check_owner.side_effect = PermissionError(
        "forbidden"
    )

    with pytest.raises(
        PermissionError,
        match="forbidden",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# QUOTE STATUS
# ============================================================


@pytest.mark.asyncio
async def test_already_sent_quote_cannot_be_sent(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
        status=QuoteStatus.SENT,
    )

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = make_lead()

    with pytest.raises(QuoteAlreadySent):
        await use_case.execute(dto)

    quote_repository.update.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# CUSTOMER ACCOUNT
# ============================================================


@pytest.mark.asyncio
async def test_customer_account_is_ensured(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    account,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
    )
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    customer_account_service.ensure_account.return_value = account

    await use_case.execute(dto)

    customer_account_service.ensure_account.assert_called_once_with(
        lead,
        "quote-42",
    )


# ============================================================
# QUOTE UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_quote_is_sent(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    account,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
    )
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    customer_account_service.ensure_account.return_value = account

    await use_case.execute(dto)

    assert quote.status == QuoteStatus.SENT
    assert quote.sent_at is not None
    assert quote.expires_at is not None

    quote_repository.update.assert_called_once_with(
        quote
    )


@pytest.mark.asyncio
async def test_lead_status_is_changed_to_quote_sent(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    account,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
    )
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    customer_account_service.ensure_account.return_value = account

    await use_case.execute(dto)

    lead.change_status.assert_called_once_with(
        LeadStatus.QUOTE_SENT
    )

    lead_repository.update.assert_called_once_with(
        lead
    )


# ============================================================
# EVENT
# ============================================================


@pytest.mark.asyncio
async def test_quote_sent_event_is_logged(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    event_service,
    account,
    customer,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
    )
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    customer_account_service.ensure_account.return_value = account

    await use_case.execute(dto)

    event_service.log.assert_called_once_with(
        type=EventType.QUOTE_SENT,
        message="Devis envoyé au client",
        quote_id="quote-42",
        lead_id=lead.id,
        user_id="agent-1",
        vehicle_id=lead.vehicle.id,
        event_metadata={
            "customer_id": customer.id,
            "customer_email": customer.email,
        },
    )


# ============================================================
# NOTIFICATION
# ============================================================


@pytest.mark.asyncio
async def test_customer_notification_is_sent(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    notification_service,
    account,
    customer,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
    )
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    customer_account_service.ensure_account.return_value = account

    await use_case.execute(dto)

    notification_service.send.assert_awaited_once()

    kwargs = notification_service.send.await_args.kwargs

    assert kwargs["user_id"] == customer.id
    assert kwargs["email"] == customer.email
    assert kwargs["entity_id"] == "quote-42"


# ============================================================
# COMMIT
# ============================================================


@pytest.mark.asyncio
async def test_commit_is_called(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    unit_of_work,
    account,
    dto,
):
    quote_repository.find_by_id.return_value = make_quote(
        quote_id="quote-42",
    )
    lead_repository.find_by_id.return_value = make_lead()
    customer_account_service.ensure_account.return_value = account

    await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# ACTION REQUIRED COUNT
# ============================================================


@pytest.mark.asyncio
async def test_action_required_count_is_loaded(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    account,
    customer,
    dto,
):
    quote_repository.find_by_id.return_value = make_quote(
        quote_id="quote-42",
    )
    lead_repository.find_by_id.return_value = make_lead()
    customer_account_service.ensure_account.return_value = account

    quote_repository.count_action_required_by_customer.return_value = 3

    await use_case.execute(dto)

    quote_repository.count_action_required_by_customer.assert_called_once_with(
        customer.id
    )


# ============================================================
# REALTIME NOTIFICATION UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_notification_update_is_sent(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    notification_service,
    account,
    customer,
    dto,
):
    quote_repository.find_by_id.return_value = make_quote(
        quote_id="quote-42",
    )
    lead_repository.find_by_id.return_value = make_lead()
    customer_account_service.ensure_account.return_value = account

    quote_repository.count_action_required_by_customer.return_value = 2

    await use_case.execute(dto)

    notification_service.send_update.assert_awaited_once_with(
        user_id=customer.id,
        payload={
            "type": "QUOTE_UPDATED",
            "count": 2,
        },
    )


# ============================================================
# EMAIL
# ============================================================


@pytest.mark.asyncio
async def test_quote_email_is_sent(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    email_service,
    account,
    customer,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
    )
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    customer_account_service.ensure_account.return_value = account

    await use_case.execute(dto)

    email_service.send_quote_email.assert_called_once_with(
        quote=quote,
        customer=customer,
        vehicle=lead.vehicle,
        activation_token="activation-token",
    )


# ============================================================
# RESULT
# ============================================================


@pytest.mark.asyncio
async def test_quote_action_result_is_returned(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    account,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
    )
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    customer_account_service.ensure_account.return_value = account

    result = await use_case.execute(dto)

    assert isinstance(
        result,
        QuoteActionResult,
    )

    assert result.quote_id == "quote-42"
    assert result.message == "Devis envoyé avec succès"


# ============================================================
# ROLLBACK — QUOTE UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_quote_update_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    unit_of_work,
    account,
    dto,
):
    quote = make_quote(
        quote_id="quote-42",
    )

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = make_lead()
    customer_account_service.ensure_account.return_value = account

    quote_repository.update.side_effect = RuntimeError(
        "quote update error"
    )

    with pytest.raises(
        RuntimeError,
        match="quote update error",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# ROLLBACK — LEAD UPDATE
# ============================================================


@pytest.mark.asyncio
async def test_lead_update_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    unit_of_work,
    account,
    dto,
):
    quote_repository.find_by_id.return_value = make_quote(
        quote_id="quote-42",
    )
    lead_repository.find_by_id.return_value = make_lead()
    customer_account_service.ensure_account.return_value = account

    lead_repository.update.side_effect = RuntimeError(
        "lead update error"
    )

    with pytest.raises(
        RuntimeError,
        match="lead update error",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# ROLLBACK — EVENT
# ============================================================


@pytest.mark.asyncio
async def test_event_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    event_service,
    unit_of_work,
    account,
    dto,
):
    quote_repository.find_by_id.return_value = make_quote(
        quote_id="quote-42",
    )
    lead_repository.find_by_id.return_value = make_lead()
    customer_account_service.ensure_account.return_value = account

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# ROLLBACK — NOTIFICATION
# ============================================================


@pytest.mark.asyncio
async def test_notification_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    notification_service,
    unit_of_work,
    account,
    dto,
):
    quote_repository.find_by_id.return_value = make_quote(
        quote_id="quote-42",
    )
    lead_repository.find_by_id.return_value = make_lead()
    customer_account_service.ensure_account.return_value = account

    notification_service.send.side_effect = RuntimeError(
        "notification error"
    )

    with pytest.raises(
        RuntimeError,
        match="notification error",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# ROLLBACK — EMAIL
# ============================================================


@pytest.mark.asyncio
async def test_email_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    email_service,
    unit_of_work,
    account,
    dto,
):
    quote_repository.find_by_id.return_value = make_quote(
        quote_id="quote-42",
    )
    lead_repository.find_by_id.return_value = make_lead()
    customer_account_service.ensure_account.return_value = account

    email_service.send_quote_email.side_effect = RuntimeError(
        "email error"
    )

    with pytest.raises(
        RuntimeError,
        match="email error",
    ):
        await use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_called_once()


# ============================================================
# COMPLETE FLOW
# ============================================================


@pytest.mark.asyncio
async def test_send_quote_complete_flow(
    use_case,
    quote_repository,
    lead_repository,
    lead_authorization,
    customer_account_service,
    notification_service,
    event_service,
    email_service,
    unit_of_work,
):
    quote = make_quote(
        quote_id="quote-42",
        lead_id="lead-42",
    )

    vehicle = make_vehicle(
        vehicle_id="vehicle-42",
    )

    lead = make_lead(
        lead_id="lead-42",
        user_id="customer-42",
        vehicle=vehicle,
    )

    customer = make_customer(
        customer_id="customer-42",
        email="customer42@example.com",
    )

    account = make_account(
        customer=customer,
        token="token-42",
    )

    dto = make_dto(
        quote_id="quote-42",
        agent_id="agent-42",
    )

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    customer_account_service.ensure_account.return_value = account

    quote_repository.count_action_required_by_customer.return_value = 4

    result = await use_case.execute(dto)

    # Autorisation
    lead_authorization.check_owner.assert_called_once_with(
        lead,
        "agent-42",
    )

    # Quote
    assert quote.status == QuoteStatus.SENT

    quote_repository.update.assert_called_once_with(
        quote
    )

    # Lead
    lead.change_status.assert_called_once_with(
        LeadStatus.QUOTE_SENT
    )

    lead_repository.update.assert_called_once_with(
        lead
    )

    # Event
    event_service.log.assert_called_once()

    event_kwargs = event_service.log.call_args.kwargs

    assert event_kwargs["type"] == EventType.QUOTE_SENT
    assert event_kwargs["quote_id"] == "quote-42"
    assert event_kwargs["lead_id"] == "lead-42"
    assert event_kwargs["user_id"] == "agent-42"
    assert event_kwargs["vehicle_id"] == "vehicle-42"

    # Notification
    notification_service.send.assert_awaited_once()

    notification_kwargs = (
        notification_service.send.await_args.kwargs
    )

    assert notification_kwargs["user_id"] == "customer-42"
    assert notification_kwargs["email"] == "customer42@example.com"
    assert notification_kwargs["entity_id"] == "quote-42"

    # Count
    quote_repository.count_action_required_by_customer.assert_called_once_with(
        "customer-42"
    )

    # Realtime update
    notification_service.send_update.assert_awaited_once_with(
        user_id="customer-42",
        payload={
            "type": "QUOTE_UPDATED",
            "count": 4,
        },
    )

    # Email
    email_service.send_quote_email.assert_called_once_with(
        quote=quote,
        customer=customer,
        vehicle=vehicle,
        activation_token="token-42",
    )

    # Transaction
    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    # Result
    assert isinstance(
        result,
        QuoteActionResult,
    )

    assert result.quote_id == "quote-42"
    assert result.message == "Devis envoyé avec succès"