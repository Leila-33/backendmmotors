from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from modules.quotes.application.use_cases.accept_quote import (
    AcceptQuoteUseCase,
)
from modules.quotes.domain.exceptions import QuoteNotFound
from modules.leads.domain.exceptions import LeadNotFound
from modules.applications.domain.enums import EventType
from modules.notifications.domain.enums import NotificationType


@pytest.fixture
def dependencies():
    return {
        "quote_repository": Mock(),
        "application_repository": Mock(),
        "trade_in_repository": Mock(),
        "financing_repository": Mock(),
        "lead_repository": Mock(),
        "notification_service": Mock(),
        "event_service": Mock(),
        "unit_of_work": Mock(),
    }


@pytest.fixture
def use_case(dependencies):
    dependencies["notification_service"].send = AsyncMock()

    return AcceptQuoteUseCase(
        quote_repository=dependencies["quote_repository"],
        application_repository=dependencies["application_repository"],
        trade_in_repository=dependencies["trade_in_repository"],
        financing_repository=dependencies["financing_repository"],
        lead_repository=dependencies["lead_repository"],
        notification_service=dependencies["notification_service"],
        event_service=dependencies["event_service"],
        unit_of_work=dependencies["unit_of_work"],
    )


@pytest.fixture
def dto():
    return SimpleNamespace(
        quote_id="quote-123",
        customer_id="customer-123",
    )


@pytest.fixture
def quote():
    quote = Mock()

    quote.id = "quote-123"
    quote.lead_id = "lead-123"

    quote.down_payment = 5000
    quote.duration_months = 48
    quote.financed_amount = 25000
    quote.monthly_payment = 520.83

    quote.trade_in = None
    quote.trade_in_value = 0

    return quote


@pytest.fixture
def lead():
    lead = Mock()

    lead.id = "lead-123"
    lead.user_id = "customer-123"
    lead.vehicle_id = "vehicle-123"
    lead.assigned_to = "agent-123"

    return lead


# ============================================================
# SUCCESS
# ============================================================

@pytest.mark.asyncio
async def test_execute_success_without_trade_in(
    use_case,
    dependencies,
    dto,
    quote,
    lead,
):
    dependencies["quote_repository"].find_by_id.return_value = quote
    dependencies["lead_repository"].find_by_id.return_value = lead

    application = SimpleNamespace(
        id="application-123",
    )

    use_case.quote_repository.update.return_value = None

    # Mock de la méthode de création du domaine
    with pytest.MonkeyPatch.context() as mp:
        application_factory = Mock(
            return_value=application
        )

        mp.setattr(
            "modules.quotes.application.use_cases.accept_quote.Application.create_draft_from_quote",
            application_factory,
        )

        result = await use_case.execute(dto)

    # Quote
    quote.accept.assert_called_once()
    dependencies["quote_repository"].update.assert_called_once_with(
        quote
    )

    # Application
    application_factory.assert_called_once_with(
        quote,
        lead,
    )

    dependencies[
        "application_repository"
    ].create_base.assert_called_once_with(
        application
    )

    # Financing
    financing = (
        dependencies[
            "financing_repository"
        ].save.call_args.args[0]
    )

    assert financing.application_id == "application-123"
    assert financing.down_payment == 5000
    assert financing.duration_months == 48
    assert financing.financed_amount == 25000
    assert financing.monthly_payment == 520.83

    # Pas de reprise
    dependencies[
        "trade_in_repository"
    ].save.assert_not_called()

    # Events
    assert (
        dependencies["event_service"].log.call_count
        == 2
    )

    first_event = (
        dependencies["event_service"]
        .log.call_args_list[0]
    )

    assert first_event.kwargs["type"] == (
        EventType.QUOTE_ACCEPTED
    )
    assert first_event.kwargs["quote_id"] == "quote-123"
    assert first_event.kwargs["lead_id"] == "lead-123"
    assert first_event.kwargs["vehicle_id"] == "vehicle-123"
    assert first_event.kwargs["application_id"] == (
        "application-123"
    )
    assert first_event.kwargs["user_id"] == (
        "customer-123"
    )

    second_event = (
        dependencies["event_service"]
        .log.call_args_list[1]
    )

    assert second_event.kwargs["type"] == (
        EventType.APPLICATION_CREATED
    )

    # Notification
    dependencies[
        "notification_service"
    ].send.assert_awaited_once_with(
        user_id="agent-123",
        title="Offre acceptée",
        message="Le client a accepté votre offre.",
        notif_type=NotificationType.QUOTE_ACCEPTED,
        entity_type="quote",
        entity_id="quote-123",
    )

    # Commit
    dependencies[
        "unit_of_work"
    ].commit.assert_called_once()

    dependencies[
        "unit_of_work"
    ].rollback.assert_not_called()

    # Result
    assert result.quote_id == "quote-123"
    assert result.application_id == "application-123"
    assert result.message == (
        "Votre offre a été acceptée. "
        "Votre dossier est maintenant créé."
    )


@pytest.mark.asyncio
async def test_execute_success_with_trade_in(
    use_case,
    dependencies,
    dto,
    quote,
    lead,
):
    trade_in = SimpleNamespace(
        brand="Renault",
        model="Clio",
        year=2020,
        mileage=80000,
        condition="GOOD",
    )

    quote.trade_in = trade_in
    quote.trade_in_value = 7500

    dependencies["quote_repository"].find_by_id.return_value = quote
    dependencies["lead_repository"].find_by_id.return_value = lead

    application = SimpleNamespace(
        id="application-123",
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "modules.quotes.application.use_cases.accept_quote.Application.create_draft_from_quote",
            Mock(return_value=application),
        )

        result = await use_case.execute(dto)

    dependencies[
        "trade_in_repository"
    ].save.assert_called_once()

    application_trade_in = (
        dependencies[
            "trade_in_repository"
        ].save.call_args.args[0]
    )

    assert application_trade_in.application_id == (
        "application-123"
    )
    assert application_trade_in.brand == "Renault"
    assert application_trade_in.model == "Clio"
    assert application_trade_in.year == 2020
    assert application_trade_in.mileage == 80000
    assert application_trade_in.condition == "GOOD"
    assert application_trade_in.estimated_value == 7500

    assert result.quote_id == "quote-123"
    assert result.application_id == "application-123"


# ============================================================
# QUOTE NOT FOUND
# ============================================================

@pytest.mark.asyncio
async def test_execute_quote_not_found(
    use_case,
    dependencies,
    dto,
):
    dependencies[
        "quote_repository"
    ].find_by_id.return_value = None

    with pytest.raises(QuoteNotFound):
        await use_case.execute(dto)

    dependencies[
        "lead_repository"
    ].find_by_id.assert_not_called()

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()

    dependencies[
        "unit_of_work"
    ].commit.assert_not_called()


# ============================================================
# LEAD NOT FOUND
# ============================================================

@pytest.mark.asyncio
async def test_execute_lead_not_found(
    use_case,
    dependencies,
    dto,
    quote,
):
    dependencies[
        "quote_repository"
    ].find_by_id.return_value = quote

    dependencies[
        "lead_repository"
    ].find_by_id.return_value = None

    with pytest.raises(LeadNotFound):
        await use_case.execute(dto)

    quote.accept.assert_not_called()

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()

    dependencies[
        "unit_of_work"
    ].commit.assert_not_called()


# ============================================================
# AUTHORIZATION
# ============================================================

@pytest.mark.asyncio
async def test_execute_rejects_customer_not_owner(
    use_case,
    dependencies,
    dto,
    quote,
    lead,
):
    dependencies[
        "quote_repository"
    ].find_by_id.return_value = quote

    lead.user_id = "another-customer"

    dependencies[
        "lead_repository"
    ].find_by_id.return_value = lead

    with pytest.raises(QuoteNotFound):
        await use_case.execute(dto)

    quote.accept.assert_not_called()

    dependencies[
        "application_repository"
    ].create_base.assert_not_called()

    dependencies[
        "financing_repository"
    ].save.assert_not_called()

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()


# ============================================================
# QUOTE ACCEPT
# ============================================================

@pytest.mark.asyncio
async def test_execute_quote_accept_error(
    use_case,
    dependencies,
    dto,
    quote,
    lead,
):
    dependencies[
        "quote_repository"
    ].find_by_id.return_value = quote

    dependencies[
        "lead_repository"
    ].find_by_id.return_value = lead

    quote.accept.side_effect = ValueError(
        "Quote cannot be accepted"
    )

    with pytest.raises(ValueError):
        await use_case.execute(dto)

    dependencies[
        "quote_repository"
    ].update.assert_not_called()

    dependencies[
        "application_repository"
    ].create_base.assert_not_called()

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()


# ============================================================
# APPLICATION CREATION
# ============================================================

@pytest.mark.asyncio
async def test_execute_application_creation_error(
    use_case,
    dependencies,
    dto,
    quote,
    lead,
):
    dependencies[
        "quote_repository"
    ].find_by_id.return_value = quote

    dependencies[
        "lead_repository"
    ].find_by_id.return_value = lead

    application = SimpleNamespace(
        id="application-123",
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "modules.quotes.application.use_cases.accept_quote.Application.create_draft_from_quote",
            Mock(return_value=application),
        )

        dependencies[
            "application_repository"
        ].create_base.side_effect = ValueError(
            "Application creation failed"
        )

        with pytest.raises(ValueError):
            await use_case.execute(dto)

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()

    dependencies[
        "financing_repository"
    ].save.assert_not_called()


# ============================================================
# FINANCING
# ============================================================

@pytest.mark.asyncio
async def test_execute_financing_save_error(
    use_case,
    dependencies,
    dto,
    quote,
    lead,
):
    dependencies[
        "quote_repository"
    ].find_by_id.return_value = quote

    dependencies[
        "lead_repository"
    ].find_by_id.return_value = lead

    application = SimpleNamespace(
        id="application-123",
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "modules.quotes.application.use_cases.accept_quote.Application.create_draft_from_quote",
            Mock(return_value=application),
        )

        dependencies[
            "financing_repository"
        ].save.side_effect = ValueError(
            "Financing save failed"
        )

        with pytest.raises(ValueError):
            await use_case.execute(dto)

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()

    dependencies[
        "trade_in_repository"
    ].save.assert_not_called()


# ============================================================
# TRADE-IN
# ============================================================

@pytest.mark.asyncio
async def test_execute_trade_in_save_error(
    use_case,
    dependencies,
    dto,
    quote,
    lead,
):
    quote.trade_in = SimpleNamespace(
        brand="Renault",
        model="Clio",
        year=2020,
        mileage=80000,
        condition="GOOD",
    )

    quote.trade_in_value = 7500

    dependencies[
        "quote_repository"
    ].find_by_id.return_value = quote

    dependencies[
        "lead_repository"
    ].find_by_id.return_value = lead

    application = SimpleNamespace(
        id="application-123",
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "modules.quotes.application.use_cases.accept_quote.Application.create_draft_from_quote",
            Mock(return_value=application),
        )

        dependencies[
            "trade_in_repository"
        ].save.side_effect = ValueError(
            "Trade-in save failed"
        )

        with pytest.raises(ValueError):
            await use_case.execute(dto)

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()

    dependencies[
        "event_service"
    ].log.assert_not_called()


# ============================================================
# EVENT
# ============================================================

@pytest.mark.asyncio
async def test_execute_quote_accepted_event_error(
    use_case,
    dependencies,
    dto,
    quote,
    lead,
):
    dependencies[
        "quote_repository"
    ].find_by_id.return_value = quote

    dependencies[
        "lead_repository"
    ].find_by_id.return_value = lead

    application = SimpleNamespace(
        id="application-123",
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "modules.quotes.application.use_cases.accept_quote.Application.create_draft_from_quote",
            Mock(return_value=application),
        )

        dependencies[
            "event_service"
        ].log.side_effect = ValueError(
            "Event error"
        )

        with pytest.raises(ValueError):
            await use_case.execute(dto)

    dependencies[
        "event_service"
    ].log.assert_called_once()

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()

    dependencies[
        "notification_service"
    ].send.assert_not_awaited()


# ============================================================
# NOTIFICATION
# ============================================================

@pytest.mark.asyncio
async def test_execute_notification_error(
    use_case,
    dependencies,
    dto,
    quote,
    lead,
):
    dependencies[
        "quote_repository"
    ].find_by_id.return_value = quote

    dependencies[
        "lead_repository"
    ].find_by_id.return_value = lead

    application = SimpleNamespace(
        id="application-123",
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "modules.quotes.application.use_cases.accept_quote.Application.create_draft_from_quote",
            Mock(return_value=application),
        )

        dependencies[
            "notification_service"
        ].send.side_effect = ValueError(
            "Notification error"
        )

        with pytest.raises(ValueError):
            await use_case.execute(dto)

    dependencies[
        "notification_service"
    ].send.assert_awaited_once()

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()

    dependencies[
        "unit_of_work"
    ].commit.assert_not_called()


# ============================================================
# COMMIT
# ============================================================

@pytest.mark.asyncio
async def test_execute_commit_error(
    use_case,
    dependencies,
    dto,
    quote,
    lead,
):
    dependencies[
        "quote_repository"
    ].find_by_id.return_value = quote

    dependencies[
        "lead_repository"
    ].find_by_id.return_value = lead

    application = SimpleNamespace(
        id="application-123",
    )

    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(
            "modules.quotes.application.use_cases.accept_quote.Application.create_draft_from_quote",
            Mock(return_value=application),
        )

        dependencies[
            "unit_of_work"
        ].commit.side_effect = ValueError(
            "Commit failed"
        )

        with pytest.raises(ValueError):
            await use_case.execute(dto)

    dependencies[
        "unit_of_work"
    ].commit.assert_called_once()

    dependencies[
        "unit_of_work"
    ].rollback.assert_called_once()