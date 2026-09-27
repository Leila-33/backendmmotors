from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.leads.domain.exceptions import LeadNotFound
from modules.notifications.domain.enums import NotificationType
from modules.quotes.application.dtos.customer_quote_dto import (
    CustomerQuoteDTO,
)
from modules.quotes.application.results.accept_quote_result import (
    AcceptQuoteResult,
)
from modules.quotes.application.use_cases.accept_quote import (
    AcceptQuoteUseCase,
)
from modules.quotes.domain.exceptions import QuoteNotFound


# ============================================================
# HELPERS
# ============================================================


def make_quote(
    *,
    quote_id="quote-1",
    lead_id="lead-1",
    down_payment=5000,
    duration_months=48,
    financed_amount=20000,
    monthly_payment=450,
    trade_in=None,
):
    quote = Mock()

    quote.id = quote_id
    quote.lead_id = lead_id
    quote.down_payment = down_payment
    quote.duration_months = duration_months
    quote.financed_amount = financed_amount
    quote.monthly_payment = monthly_payment
    quote.trade_in = trade_in
    quote.trade_in_value = (
        trade_in.value
        if trade_in is not None
        and hasattr(trade_in, "value")
        else 3000
    )

    return quote


def make_lead(
    *,
    lead_id="lead-1",
    customer_id="customer-1",
    vehicle_id="vehicle-1",
    assigned_to="agent-1",
    first_name="Leila",
    last_name="El",
    email="leila@example.com",
    phone="0600000000",
):
    return SimpleNamespace(
        id=lead_id,
        user_id=customer_id,
        vehicle_id=vehicle_id,
        assigned_to=assigned_to,
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
    )


def make_trade_in(
    *,
    brand="Renault",
    model="Clio",
    year=2020,
    mileage=50000,
    condition="GOOD",
    value=3000,
):
    return SimpleNamespace(
        brand=brand,
        model=model,
        year=year,
        mileage=mileage,
        condition=condition,
        value=value,
    )


def make_dto(
    *,
    quote_id="quote-1",
    customer_id="customer-1",
):
    return CustomerQuoteDTO(
        quote_id=quote_id,
        customer_id=customer_id,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def quote_repository():
    repository = Mock()

    repository.find_by_id.return_value = None
    repository.count_action_required_by_customer.return_value = 0

    return repository


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def trade_in_repository():
    return Mock()


@pytest.fixture
def financing_repository():
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
    application_repository,
    trade_in_repository,
    financing_repository,
    lead_repository,
    notification_service,
    event_service,
    unit_of_work,
):
    return AcceptQuoteUseCase(
        quote_repository=quote_repository,
        application_repository=application_repository,
        trade_in_repository=trade_in_repository,
        financing_repository=financing_repository,
        lead_repository=lead_repository,
        notification_service=notification_service,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# ============================================================
# QUOTE
# ============================================================


@pytest.mark.asyncio
async def test_quote_not_found(
    use_case,
    quote_repository,
    unit_of_work,
):
    quote_repository.find_by_id.return_value = None

    with pytest.raises(QuoteNotFound):
        await use_case.execute(
            make_dto()
        )

    quote_repository.find_by_id.assert_called_once_with(
        "quote-1"
    )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# LEAD
# ============================================================


@pytest.mark.asyncio
async def test_lead_not_found(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    quote = make_quote()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = None

    with pytest.raises(LeadNotFound):
        await use_case.execute(
            make_dto()
        )

    lead_repository.find_by_id.assert_called_once_with(
        "lead-1"
    )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# AUTHORIZATION
# ============================================================


@pytest.mark.asyncio
async def test_customer_cannot_accept_another_customer_quote(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    quote = make_quote()

    lead = make_lead(
        customer_id="owner-1"
    )

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    with pytest.raises(QuoteNotFound):
        await use_case.execute(
            make_dto(
                customer_id="another-customer"
            )
        )

    quote.accept.assert_not_called()

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


# ============================================================
# QUOTE ACCEPTANCE
# ============================================================


@pytest.mark.asyncio
async def test_quote_is_accepted(
    use_case,
    quote_repository,
    lead_repository,
    application_repository,
    financing_repository,
    notification_service,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(
        make_dto()
    )

    quote.accept.assert_called_once()

    quote_repository.update.assert_called_once_with(
        quote
    )


# ============================================================
# APPLICATION CREATION
# ============================================================


@pytest.mark.asyncio
async def test_application_is_created_from_quote(
    use_case,
    quote_repository,
    lead_repository,
    application_repository,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(
        make_dto()
    )

    application_repository.create_base.assert_called_once()

    application = (
        application_repository
        .create_base
        .call_args.args[0]
    )

    assert application.user_id == "customer-1"
    assert application.vehicle_id == "vehicle-1"


# ============================================================
# FINANCING
# ============================================================


@pytest.mark.asyncio
async def test_financing_is_created_from_quote(
    use_case,
    quote_repository,
    lead_repository,
    financing_repository,
):
    quote = make_quote(
        down_payment=5000,
        duration_months=48,
        financed_amount=20000,
        monthly_payment=450,
    )

    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(
        make_dto()
    )

    financing_repository.save.assert_called_once()

    financing = (
        financing_repository
        .save
        .call_args.args[0]
    )

    assert financing.application_id is not None
    assert financing.down_payment == 5000
    assert financing.duration_months == 48
    assert financing.financed_amount == 20000
    assert financing.monthly_payment == 450


# ============================================================
# TRADE-IN
# ============================================================


@pytest.mark.asyncio
async def test_trade_in_is_created_when_quote_has_trade_in(
    use_case,
    quote_repository,
    lead_repository,
    trade_in_repository,
):
    trade_in = make_trade_in()

    quote = make_quote(
        trade_in=trade_in
    )

    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(
        make_dto()
    )

    trade_in_repository.save.assert_called_once()

    saved_trade_in = (
        trade_in_repository
        .save
        .call_args.args[0]
    )

    assert saved_trade_in.application_id is not None
    assert saved_trade_in.brand == "Renault"
    assert saved_trade_in.model == "Clio"
    assert saved_trade_in.year == 2020
    assert saved_trade_in.mileage == 50000
    assert saved_trade_in.condition == "GOOD"
    assert saved_trade_in.estimated_value == 3000


@pytest.mark.asyncio
async def test_trade_in_is_not_created_without_trade_in(
    use_case,
    quote_repository,
    lead_repository,
    trade_in_repository,
):
    quote = make_quote(
        trade_in=None
    )

    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(
        make_dto()
    )

    trade_in_repository.save.assert_not_called()


# ============================================================
# EVENTS
# ============================================================


@pytest.mark.asyncio
async def test_quote_accepted_event_is_logged(
    use_case,
    quote_repository,
    lead_repository,
    event_service,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(
        make_dto()
    )

    calls = event_service.log.call_args_list

    assert len(calls) == 2

    quote_event = calls[0].kwargs

    assert quote_event["type"] == EventType.QUOTE_ACCEPTED
    assert quote_event["message"] == "Devis accepté"
    assert quote_event["quote_id"] == "quote-1"
    assert quote_event["lead_id"] == "lead-1"
    assert quote_event["vehicle_id"] == "vehicle-1"
    assert quote_event["user_id"] == "customer-1"
    assert quote_event["application_id"] is not None


@pytest.mark.asyncio
async def test_application_created_event_is_logged(
    use_case,
    quote_repository,
    lead_repository,
    event_service,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(
        make_dto()
    )

    calls = event_service.log.call_args_list

    application_event = calls[1].kwargs

    assert (
        application_event["type"]
        == EventType.APPLICATION_CREATED
    )

    assert (
        application_event["message"]
        == "Brouillon du dossier créé suite à l'acceptation de l'offre."
    )

    assert application_event["quote_id"] == "quote-1"
    assert application_event["lead_id"] == "lead-1"
    assert application_event["vehicle_id"] == "vehicle-1"
    assert application_event["user_id"] == "customer-1"
    assert application_event["application_id"] is not None


# ============================================================
# NOTIFICATION
# ============================================================


@pytest.mark.asyncio
async def test_agent_is_notified_when_quote_is_accepted(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
):
    quote = make_quote()
    lead = make_lead(
        assigned_to="agent-42"
    )

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    await use_case.execute(
        make_dto()
    )

    notification_service.send.assert_awaited_once()

    call_args = (
        notification_service
        .send
        .call_args
        .kwargs
    )

    assert call_args["user_id"] == "agent-42"
    assert call_args["title"] == "Offre acceptée"
    assert (
        call_args["message"]
        == "Le client a accepté votre offre."
    )
    assert (
        call_args["notif_type"]
        == NotificationType.QUOTE_ACCEPTED
    )
    assert call_args["entity_type"] == "quote"
    assert call_args["entity_id"] == "quote-1"


# ============================================================
# COMMIT
# ============================================================


@pytest.mark.asyncio
async def test_successful_execution_commits(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    quote_repository.find_by_id.return_value = make_quote()
    lead_repository.find_by_id.return_value = make_lead()

    await use_case.execute(
        make_dto()
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# ACTION REQUIRED COUNT
# ============================================================


@pytest.mark.asyncio
async def test_action_required_count_is_retrieved_after_commit(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    quote_repository.find_by_id.return_value = make_quote()
    lead_repository.find_by_id.return_value = make_lead()

    quote_repository.count_action_required_by_customer.return_value = (
        4
    )

    await use_case.execute(
        make_dto(
            customer_id="customer-1"
        )
    )

    quote_repository.count_action_required_by_customer.assert_called_once_with(
        "customer-1"
    )

    unit_of_work.commit.assert_called_once()


@pytest.mark.asyncio
async def test_customer_receives_updated_action_required_count(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
):
    quote_repository.find_by_id.return_value = make_quote()
    lead_repository.find_by_id.return_value = make_lead()

    quote_repository.count_action_required_by_customer.return_value = (
        7
    )

    await use_case.execute(
        make_dto(
            customer_id="customer-1"
        )
    )

    notification_service.send_update.assert_awaited_once_with(
        user_id="customer-1",
        payload={
            "type": "QUOTE_UPDATED",
            "count": 7,
        },
    )


# ============================================================
# RESULT
# ============================================================


@pytest.mark.asyncio
async def test_execute_returns_accept_quote_result(
    use_case,
    quote_repository,
    lead_repository,
):
    quote_repository.find_by_id.return_value = make_quote()
    lead_repository.find_by_id.return_value = make_lead()

    result = await use_case.execute(
        make_dto()
    )

    assert isinstance(
        result,
        AcceptQuoteResult,
    )

    assert result.quote_id == "quote-1"
    assert result.application_id is not None

    assert (
        result.message
        == (
            "Votre offre a été acceptée. "
            "Votre dossier est maintenant créé."
        )
    )


# ============================================================
# ROLLBACK / ERRORS
# ============================================================


@pytest.mark.asyncio
async def test_quote_accept_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    quote = make_quote()

    quote.accept.side_effect = RuntimeError(
        "accept error"
    )

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = make_lead()

    with pytest.raises(
        RuntimeError,
        match="accept error",
    ):
        await use_case.execute(
            make_dto()
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_application_creation_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    application_repository,
    unit_of_work,
):
    quote_repository.find_by_id.return_value = make_quote()
    lead_repository.find_by_id.return_value = make_lead()

    application_repository.create_base.side_effect = (
        RuntimeError("application error")
    )

    with pytest.raises(
        RuntimeError,
        match="application error",
    ):
        await use_case.execute(
            make_dto()
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_financing_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    financing_repository,
    unit_of_work,
):
    quote_repository.find_by_id.return_value = make_quote()
    lead_repository.find_by_id.return_value = make_lead()

    financing_repository.save.side_effect = RuntimeError(
        "financing error"
    )

    with pytest.raises(
        RuntimeError,
        match="financing error",
    ):
        await use_case.execute(
            make_dto()
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_trade_in_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    trade_in_repository,
    unit_of_work,
):
    trade_in = make_trade_in()

    quote_repository.find_by_id.return_value = make_quote(
        trade_in=trade_in
    )

    lead_repository.find_by_id.return_value = make_lead()

    trade_in_repository.save.side_effect = RuntimeError(
        "trade in error"
    )

    with pytest.raises(
        RuntimeError,
        match="trade in error",
    ):
        await use_case.execute(
            make_dto()
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_event_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    event_service,
    unit_of_work,
):
    quote_repository.find_by_id.return_value = make_quote()
    lead_repository.find_by_id.return_value = make_lead()

    event_service.log.side_effect = RuntimeError(
        "event error"
    )

    with pytest.raises(
        RuntimeError,
        match="event error",
    ):
        await use_case.execute(
            make_dto()
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_notification_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
    unit_of_work,
):
    quote_repository.find_by_id.return_value = make_quote()
    lead_repository.find_by_id.return_value = make_lead()

    notification_service.send.side_effect = RuntimeError(
        "notification error"
    )

    with pytest.raises(
        RuntimeError,
        match="notification error",
    ):
        await use_case.execute(
            make_dto()
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


@pytest.mark.asyncio
async def test_commit_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    unit_of_work,
):
    quote_repository.find_by_id.return_value = make_quote()
    lead_repository.find_by_id.return_value = make_lead()

    unit_of_work.commit.side_effect = RuntimeError(
        "commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="commit error",
    ):
        await use_case.execute(
            make_dto()
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()


@pytest.mark.asyncio
async def test_send_update_error_rolls_back(
    use_case,
    quote_repository,
    lead_repository,
    notification_service,
    unit_of_work,
):
    quote_repository.find_by_id.return_value = make_quote()
    lead_repository.find_by_id.return_value = make_lead()

    notification_service.send_update.side_effect = (
        RuntimeError("update error")
    )

    with pytest.raises(
        RuntimeError,
        match="update error",
    ):
        await use_case.execute(
            make_dto()
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()