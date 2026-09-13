from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.leads.domain.exceptions import LeadNotFound
from modules.quotes.domain.exceptions import (
    QuoteCannotBeDeleted,
    QuoteNotFound,
)
from modules.quotes.application.use_cases.agent.delete_quote import (
    DeleteQuoteUseCase,
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
    can_be_deleted=True,
):
    quote = Mock()

    quote.id = quote_id
    quote.lead_id = lead_id

    quote.can_be_deleted.return_value = can_be_deleted

    return quote


def make_lead(
    lead_id="lead-123",
    vehicle_id="vehicle-123",
    email="client@test.com",
):
    lead = Mock()

    lead.id = lead_id
    lead.vehicle_id = vehicle_id
    lead.email = email

    return lead


@pytest.fixture
def quote_repository():
    return Mock()


@pytest.fixture
def quote_trade_in_repository():
    return Mock()


@pytest.fixture
def lead_repository():
    return Mock()


@pytest.fixture
def authorization():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    authorization,
    event_service,
    unit_of_work,
):
    return DeleteQuoteUseCase(
        quote_repository=quote_repository,
        quote_trade_in_repository=quote_trade_in_repository,
        lead_repository=lead_repository,
        authorization=authorization,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# ============================================================
# SUCCESS - SANS TRADE-IN
# ============================================================


def test_execute_success_without_trade_in(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    authorization,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    quote_trade_in_repository.find_by_quote_id.return_value = None

    dto = make_dto()

    result = use_case.execute(dto)

    assert result.quote_id == "quote-123"
    assert result.message == "Devis supprimé avec succès"

    quote_repository.find_by_id.assert_called_once_with(
        "quote-123"
    )

    lead_repository.find_by_id.assert_called_once_with(
        "lead-123"
    )

    authorization.check_owner.assert_called_once_with(
        lead,
        "agent-123",
    )

    quote.can_be_deleted.assert_called_once_with()

    quote_trade_in_repository.find_by_quote_id.assert_called_once_with(
        "quote-123"
    )

    quote_trade_in_repository.delete.assert_not_called()

    quote_repository.delete.assert_called_once_with(
        "quote-123"
    )

    event_service.log.assert_called_once_with(
        type=EventType.QUOTE_DELETED,
        message="Devis supprimé",
        quote_id="quote-123",
        lead_id="lead-123",
        vehicle_id="vehicle-123",
        user_id="agent-123",
        event_metadata={
            "quote_id": "quote-123",
            "customer_email": "client@test.com",
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# SUCCESS - AVEC TRADE-IN
# ============================================================


def test_execute_success_with_trade_in(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    authorization,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    trade_in = Mock()
    trade_in.quote_id = "quote-123"

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    quote_trade_in_repository.find_by_quote_id.return_value = (
        trade_in
    )

    dto = make_dto()

    result = use_case.execute(dto)

    assert result.quote_id == "quote-123"

    quote_trade_in_repository.delete.assert_called_once_with(
        "quote-123"
    )

    quote_repository.delete.assert_called_once_with(
        "quote-123"
    )

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# QUOTE NOT FOUND
# ============================================================


def test_execute_quote_not_found(
    use_case,
    quote_repository,
    lead_repository,
    authorization,
    unit_of_work,
):
    quote_repository.find_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(QuoteNotFound):
        use_case.execute(dto)

    lead_repository.find_by_id.assert_not_called()
    authorization.check_owner.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# LEAD NOT FOUND
# ============================================================


def test_execute_lead_not_found(
    use_case,
    quote_repository,
    lead_repository,
    authorization,
    unit_of_work,
):
    quote = make_quote()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(LeadNotFound):
        use_case.execute(dto)

    authorization.check_owner.assert_not_called()

    quote_repository.delete.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# AUTHORIZATION ERROR
# ============================================================


def test_execute_authorization_error(
    use_case,
    quote_repository,
    lead_repository,
    authorization,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    authorization.check_owner.side_effect = PermissionError(
        "Unauthorized"
    )

    dto = make_dto()

    with pytest.raises(
        PermissionError,
        match="Unauthorized",
    ):
        use_case.execute(dto)

    quote.can_be_deleted.assert_not_called()

    quote_repository.delete.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# QUOTE CANNOT BE DELETED
# ============================================================


def test_execute_quote_cannot_be_deleted(
    use_case,
    quote_repository,
    lead_repository,
    authorization,
    quote_trade_in_repository,
    unit_of_work,
):
    quote = make_quote(
        can_be_deleted=False,
    )
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    dto = make_dto()

    with pytest.raises(QuoteCannotBeDeleted):
        use_case.execute(dto)

    authorization.check_owner.assert_called_once_with(
        lead,
        "agent-123",
    )

    quote.can_be_deleted.assert_called_once_with()

    quote_trade_in_repository.find_by_quote_id.assert_not_called()
    quote_repository.delete.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# TRADE-IN DELETE ERROR
# ============================================================


def test_execute_trade_in_delete_error_rolls_back(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()
    trade_in = Mock()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    quote_trade_in_repository.find_by_quote_id.return_value = (
        trade_in
    )

    quote_trade_in_repository.delete.side_effect = (
        RuntimeError("Trade-in delete error")
    )

    with pytest.raises(
        RuntimeError,
        match="Trade-in delete error",
    ):
        use_case.execute(make_dto())

    quote_repository.delete.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# QUOTE DELETE ERROR
# ============================================================


def test_execute_quote_delete_error_rolls_back(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    quote_trade_in_repository.find_by_quote_id.return_value = None

    quote_repository.delete.side_effect = RuntimeError(
        "Quote delete error"
    )

    with pytest.raises(
        RuntimeError,
        match="Quote delete error",
    ):
        use_case.execute(make_dto())

    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# EVENT ERROR
# ============================================================


def test_execute_event_error_rolls_back(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    quote_trade_in_repository.find_by_quote_id.return_value = None

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(
        RuntimeError,
        match="Event error",
    ):
        use_case.execute(make_dto())

    quote_repository.delete.assert_called_once_with(
        "quote-123"
    )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# COMMIT ERROR
# ============================================================


def test_execute_commit_error_rolls_back(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead
    quote_trade_in_repository.find_by_quote_id.return_value = None

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(make_dto())

    quote_repository.delete.assert_called_once_with(
        "quote-123"
    )

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()