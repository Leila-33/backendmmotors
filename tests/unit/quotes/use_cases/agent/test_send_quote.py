from unittest.mock import AsyncMock, Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.leads.domain.enums import LeadStatus
from modules.leads.domain.exceptions import LeadNotFound
from modules.notifications.domain.enums import (
    NotificationEntityType,
    NotificationType,
)
from modules.quotes.domain.enums import QuoteStatus
from modules.quotes.domain.exceptions import (
    QuoteAlreadySent,
    QuoteNotFound,
)
from modules.quotes.application.use_cases.agent.send_quote import (
    SendQuoteUseCase,
)


def make_dto(
    quote_id="quote-123",
    agent_id="agent-123",
):
    dto = Mock()
    dto.quote_id = quote_id
    dto.agent_id = agent_id
    return dto


def make_quote(
    quote_id="quote-123",
    lead_id="lead-123",
    status=QuoteStatus.DRAFT,
):
    quote = Mock()

    quote.id = quote_id
    quote.lead_id = lead_id
    quote.status = status

    return quote


def make_customer(
    customer_id="customer-123",
    email="client@test.com",
):
    customer = Mock()

    customer.id = customer_id
    customer.email = email

    return customer


def make_lead(
    lead_id="lead-123",
    vehicle_id="vehicle-123",
    email="client@test.com",
):
    lead = Mock()

    lead.id = lead_id
    lead.vehicle_id = vehicle_id
    lead.email = email

    vehicle = Mock()
    vehicle.id = vehicle_id

    lead.vehicle = vehicle

    return lead


def make_account(
    customer=None,
    token="activation-token",
):
    if customer is None:
        customer = make_customer()

    return {
        "user": customer,
        "token": token,
    }


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


# ============================================================
# SUCCESS
# ============================================================


@pytest.mark.asyncio
async def test_execute_success(
    use_case,
    quote_repository,
    lead_repository,
    lead_authorization,
    customer_account_service,
    email_service,
    notification_service,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()
    customer = make_customer()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    customer_account_service.ensure_account.return_value = (
        make_account(customer, "activation-token")
    )

    dto = make_dto()

    result = await use_case.execute(dto)

    assert result.quote_id == "quote-123"
    assert result.message == "Devis envoyé avec succès"

    quote.send.assert_called_once()

    quote_repository.update.assert_called_once_with(
        quote
    )

    lead.change_status.assert_called_once_with(
        LeadStatus.QUOTE_SENT
    )

    lead_repository.update.assert_called_once_with(
        lead
    )

    event_service.log.assert_called_once_with(
        type=EventType.QUOTE_SENT,
        message="Devis envoyé au client",
        quote_id="quote-123",
        lead_id="lead-123",
        user_id="agent-123",
        vehicle_id="vehicle-123",
        event_metadata={
            "customer_id": "customer-123",
            "customer_email": "client@test.com",
        },
    )

    notification_service.send.assert_awaited_once_with(
        user_id="customer-123",
        email="client@test.com",
        title="Nouvelle offre commerciale",
        message=(
            "Votre conseiller vous a envoyé "
            "une nouvelle offre."
        ),
        notif_type=NotificationType.QUOTE_SENT,
        entity_type=NotificationEntityType.QUOTE,
        entity_id="quote-123",
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

    email_service.send_quote_email.assert_called_once_with(
        quote=quote,
        customer=customer,
        vehicle=lead.vehicle,
        activation_token="activation-token",
    )


# ============================================================
# QUOTE NOT FOUND
# ============================================================


@pytest.mark.asyncio
async def test_execute_quote_not_found(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    unit_of_work,
):
    quote_repository.find_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(QuoteNotFound):
        await use_case.execute(dto)

    lead_repository.find_by_id.assert_not_called()
    customer_account_service.ensure_account.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# LEAD NOT FOUND
# ============================================================


@pytest.mark.asyncio
async def test_execute_lead_not_found(
    use_case,
    quote_repository,
    lead_repository,
    lead_authorization,
    unit_of_work,
):
    quote = make_quote()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(LeadNotFound):
        await use_case.execute(dto)

    lead_authorization.check_owner.assert_not_called()

    quote.send.assert_not_called()
    quote_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# AUTHORIZATION ERROR
# ============================================================


@pytest.mark.asyncio
async def test_execute_authorization_error(
    use_case,
    quote_repository,
    lead_repository,
    lead_authorization,
    customer_account_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    lead_authorization.check_owner.side_effect = (
        PermissionError("Unauthorized")
    )

    dto = make_dto()

    with pytest.raises(
        PermissionError,
        match="Unauthorized",
    ):
        await use_case.execute(dto)

    customer_account_service.ensure_account.assert_not_called()

    quote.send.assert_not_called()
    quote_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# QUOTE ALREADY SENT
# ============================================================


@pytest.mark.asyncio
async def test_execute_quote_already_sent(
    use_case,
    quote_repository,
    lead_repository,
    lead_authorization,
    customer_account_service,
    unit_of_work,
):
    quote = make_quote(
        status=QuoteStatus.SENT,
    )
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    dto = make_dto()

    with pytest.raises(QuoteAlreadySent):
        await use_case.execute(dto)

    lead_authorization.check_owner.assert_called_once_with(
        lead,
        "agent-123",
    )

    customer_account_service.ensure_account.assert_not_called()

    quote.send.assert_not_called()
    quote_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# CUSTOMER ACCOUNT ERROR
# ============================================================


@pytest.mark.asyncio
async def test_execute_customer_account_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    customer_account_service.ensure_account.side_effect = (
        RuntimeError("Account error")
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Account error",
    ):
        await use_case.execute(dto)

    quote.send.assert_not_called()
    quote_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# QUOTE UPDATE ERROR
# ============================================================


@pytest.mark.asyncio
async def test_execute_quote_update_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    customer_account_service.ensure_account.return_value = (
        make_account()
    )

    quote_repository.update.side_effect = RuntimeError(
        "Quote update error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Quote update error",
    ):
        await use_case.execute(dto)

    quote.send.assert_called_once()

    lead_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# LEAD UPDATE ERROR
# ============================================================


@pytest.mark.asyncio
async def test_execute_lead_update_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    customer_account_service.ensure_account.return_value = (
        make_account()
    )

    lead_repository.update.side_effect = RuntimeError(
        "Lead update error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Lead update error",
    ):
        await use_case.execute(dto)

    quote.send.assert_called_once()
    quote_repository.update.assert_called_once_with(
        quote
    )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# EVENT ERROR
# ============================================================


@pytest.mark.asyncio
async def test_execute_event_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    event_service,
    notification_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    customer_account_service.ensure_account.return_value = (
        make_account()
    )

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Event error",
    ):
        await use_case.execute(dto)

    quote_repository.update.assert_called_once_with(
        quote
    )

    lead_repository.update.assert_called_once_with(
        lead
    )

    notification_service.send.assert_not_awaited()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# NOTIFICATION ERROR
# ============================================================


@pytest.mark.asyncio
async def test_execute_notification_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    notification_service,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    customer_account_service.ensure_account.return_value = (
        make_account()
    )

    notification_service.send.side_effect = RuntimeError(
        "Notification error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Notification error",
    ):
        await use_case.execute(dto)

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# COMMIT ERROR
# ============================================================


@pytest.mark.asyncio
async def test_execute_commit_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    notification_service,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    customer_account_service.ensure_account.return_value = (
        make_account()
    )

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        await use_case.execute(dto)

    notification_service.send.assert_awaited_once()
    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()

    email_service = use_case.email_service
    email_service.send_quote_email.assert_not_called()


# ============================================================
# EMAIL ERROR
# ============================================================


@pytest.mark.asyncio
async def test_execute_email_error_rolls_back_after_commit(
    use_case,
    quote_repository,
    lead_repository,
    customer_account_service,
    email_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    customer_account_service.ensure_account.return_value = (
        make_account()
    )

    email_service.send_quote_email.side_effect = RuntimeError(
        "Email error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Email error",
    ):
        await use_case.execute(dto)

    unit_of_work.commit.assert_called_once()

    email_service.send_quote_email.assert_called_once()

    # Le rollback est appelé même si le commit a déjà eu lieu.
    unit_of_work.rollback.assert_called_once()