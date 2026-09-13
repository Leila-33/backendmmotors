from datetime import datetime, timezone
from unittest.mock import Mock, patch

import pytest

from modules.applications.domain.enums import EventType
from modules.leads.domain.exceptions import (
    LeadHasActiveQuote,
    LeadNotFound,
)
from modules.quotes.domain.enums import QuoteStatus
from modules.quotes.application.use_cases.agent.create_quote import (
    CreateQuoteUseCase,
)


def make_dto(
    lead_id="lead-123",
    agent_id="agent-123",
    discount=1000,
    down_payment=5000,
    duration_months=48,
    trade_in=None,
):
    dto = Mock()

    dto.lead_id = lead_id
    dto.agent_id = agent_id
    dto.discount = discount
    dto.down_payment = down_payment
    dto.duration_months = duration_months
    dto.trade_in = trade_in

    return dto


def make_lead(
    lead_id="lead-123",
    vehicle=None,
):
    lead = Mock()

    lead.id = lead_id
    lead.vehicle = vehicle

    return lead


def make_vehicle(
    vehicle_id="vehicle-123",
    price=30000,
):
    vehicle = Mock()

    vehicle.id = vehicle_id
    vehicle.price = price

    return vehicle


def make_financing_result(
    financed_amount=24000,
    monthly_payment=500,
):
    result = Mock()

    result.financed_amount = financed_amount
    result.monthly_payment = monthly_payment

    return result


def make_trade_in_result(
    estimated_value=8000,
):
    result = Mock()

    result.estimated_value = estimated_value

    return result


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
def financing_service():
    return Mock()


@pytest.fixture
def trade_in_service():
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
    financing_service,
    trade_in_service,
    authorization,
    event_service,
    unit_of_work,
):
    return CreateQuoteUseCase(
        quote_repository=quote_repository,
        quote_trade_in_repository=quote_trade_in_repository,
        lead_repository=lead_repository,
        financing_service=financing_service,
        trade_in_service=trade_in_service,
        authorization=authorization,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


# ============================================================
# SUCCESS
# ============================================================


@patch(
    "modules.quotes.application.use_cases.agent.create_quote.uuid4",
)
def test_execute_success_without_trade_in(
    mock_uuid4,
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    financing_service,
    trade_in_service,
    authorization,
    event_service,
    unit_of_work,
):
    mock_uuid4.return_value = "quote-123"

    vehicle = make_vehicle(
        vehicle_id="vehicle-123",
        price=30000,
    )

    lead = make_lead(
        lead_id="lead-123",
        vehicle=vehicle,
    )

    financing_result = make_financing_result(
        financed_amount=24000,
        monthly_payment=500,
    )

    lead_repository.find_by_id.return_value = lead
    quote_repository.find_active_by_lead.return_value = None
    financing_service.calculate.return_value = financing_result

    dto = make_dto(
        discount=1000,
        down_payment=5000,
        duration_months=48,
        trade_in=None,
    )

    result = use_case.execute(dto)

    assert result.quote_id == "quote-123"
    assert result.lead_id == "lead-123"
    assert result.vehicle_id == "vehicle-123"
    assert result.message == "Devis créé avec succès"

    lead_repository.find_by_id.assert_called_once_with(
        "lead-123"
    )

    authorization.check_owner.assert_called_once_with(
        lead,
        "agent-123",
    )

    quote_repository.find_active_by_lead.assert_called_once_with(
        "lead-123"
    )

    financing_service.calculate.assert_called_once()

    financing_input = (
        financing_service.calculate.call_args.args[0]
    )

    assert financing_input.total_price == 29000
    assert financing_input.down_payment == 5000
    assert financing_input.trade_in_value == 0
    assert financing_input.duration_months == 48

    trade_in_service.estimate.assert_not_called()

    quote = quote_repository.save.call_args.args[0]

    assert quote.id == "quote-123"
    assert quote.lead_id == "lead-123"
    assert quote.base_price == 30000
    assert quote.discount == 1000
    assert quote.down_payment == 5000
    assert quote.trade_in_value == 0
    assert quote.duration_months == 48
    assert quote.financed_amount == 24000
    assert quote.monthly_payment == 500
    assert quote.status == QuoteStatus.DRAFT

    assert isinstance(quote.created_at, datetime)
    assert quote.created_at.tzinfo == timezone.utc

    quote_trade_in_repository.save.assert_not_called()

    event_service.log.assert_called_once_with(
        type=EventType.QUOTE_CREATED,
        message="Devis créé",
        vehicle_id="vehicle-123",
        quote_id="quote-123",
        lead_id="lead-123",
        user_id="agent-123",
        event_metadata={
            "base_price": 30000,
            "discount": 1000,
            "down_payment": 5000,
            "trade_in_value": 0,
            "financed_amount": 24000,
            "monthly_payment": 500,
            "duration_months": 48,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# SUCCESS AVEC TRADE-IN
# ============================================================


@patch(
    "modules.quotes.application.use_cases.agent.create_quote.uuid4",
)
def test_execute_success_with_trade_in(
    mock_uuid4,
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    financing_service,
    trade_in_service,
    authorization,
    event_service,
    unit_of_work,
):
    mock_uuid4.return_value = "quote-123"

    vehicle = make_vehicle(
        vehicle_id="vehicle-123",
        price=30000,
    )

    lead = make_lead(
        vehicle=vehicle,
    )

    trade_in = Mock()
    trade_in.brand = "Renault"
    trade_in.model = "Clio"
    trade_in.year = 2020
    trade_in.mileage = 50000
    trade_in.condition = "GOOD"

    trade_in_service.estimate.return_value = (
        make_trade_in_result(estimated_value=8000)
    )

    financing_service.calculate.return_value = (
        make_financing_result(
            financed_amount=17000,
            monthly_payment=354.17,
        )
    )

    lead_repository.find_by_id.return_value = lead
    quote_repository.find_active_by_lead.return_value = None

    dto = make_dto(
        discount=1000,
        down_payment=4000,
        duration_months=48,
        trade_in=trade_in,
    )

    result = use_case.execute(dto)

    assert result.quote_id == "quote-123"

    trade_in_service.estimate.assert_called_once()

    trade_input = (
        trade_in_service.estimate.call_args.args[0]
    )

    assert trade_input.brand == "Renault"
    assert trade_input.model == "Clio"
    assert trade_input.year == 2020
    assert trade_input.mileage == 50000
    assert trade_input.condition == "GOOD"

    financing_input = (
        financing_service.calculate.call_args.args[0]
    )

    assert financing_input.total_price == 29000
    assert financing_input.down_payment == 4000
    assert financing_input.trade_in_value == 8000
    assert financing_input.duration_months == 48

    quote = quote_repository.save.call_args.args[0]

    assert quote.trade_in_value == 8000

    quote_trade_in = (
        quote_trade_in_repository.save.call_args.args[0]
    )

    assert quote_trade_in.quote_id == "quote-123"
    assert quote_trade_in.brand == "Renault"
    assert quote_trade_in.model == "Clio"
    assert quote_trade_in.year == 2020
    assert quote_trade_in.mileage == 50000
    assert quote_trade_in.condition == "GOOD"
    assert quote_trade_in.estimated_value == 8000

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# LEAD NOT FOUND
# ============================================================


def test_execute_lead_not_found(
    use_case,
    lead_repository,
    authorization,
    quote_repository,
    financing_service,
    event_service,
    unit_of_work,
):
    lead_repository.find_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(LeadNotFound):
        use_case.execute(dto)

    authorization.check_owner.assert_not_called()
    quote_repository.find_active_by_lead.assert_not_called()
    financing_service.calculate.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# AUTHORIZATION
# ============================================================


def test_execute_authorization_error(
    use_case,
    lead_repository,
    authorization,
    quote_repository,
    financing_service,
    unit_of_work,
):
    lead = make_lead(
        vehicle=make_vehicle(),
    )

    lead_repository.find_by_id.return_value = lead

    authorization.check_owner.side_effect = PermissionError(
        "Unauthorized"
    )

    with pytest.raises(PermissionError, match="Unauthorized"):
        use_case.execute(make_dto())

    quote_repository.find_active_by_lead.assert_not_called()
    financing_service.calculate.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# ACTIVE QUOTE
# ============================================================


def test_execute_active_quote_rejected(
    use_case,
    lead_repository,
    quote_repository,
    authorization,
    financing_service,
    event_service,
    unit_of_work,
):
    lead = make_lead(
        vehicle=make_vehicle(),
    )

    existing_quote = Mock()

    lead_repository.find_by_id.return_value = lead
    quote_repository.find_active_by_lead.return_value = (
        existing_quote
    )

    dto = make_dto()

    with pytest.raises(LeadHasActiveQuote):
        use_case.execute(dto)

    authorization.check_owner.assert_called_once_with(
        lead,
        dto.agent_id,
    )

    financing_service.calculate.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# TRADE-IN SERVICE ERROR
# ============================================================


def test_execute_trade_in_error_rolls_back(
    use_case,
    lead_repository,
    quote_repository,
    trade_in_service,
    financing_service,
    unit_of_work,
):
    vehicle = make_vehicle()
    lead = make_lead(vehicle=vehicle)

    trade_in = Mock()
    trade_in.brand = "Renault"
    trade_in.model = "Clio"
    trade_in.year = 2020
    trade_in.mileage = 50000
    trade_in.condition = "GOOD"

    lead_repository.find_by_id.return_value = lead
    quote_repository.find_active_by_lead.return_value = None

    trade_in_service.estimate.side_effect = RuntimeError(
        "Trade-in error"
    )

    dto = make_dto(
        trade_in=trade_in,
    )

    with pytest.raises(
        RuntimeError,
        match="Trade-in error",
    ):
        use_case.execute(dto)

    financing_service.calculate.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# FINANCING SERVICE ERROR
# ============================================================


def test_execute_financing_error_rolls_back(
    use_case,
    lead_repository,
    quote_repository,
    financing_service,
    unit_of_work,
):
    vehicle = make_vehicle()
    lead = make_lead(vehicle=vehicle)

    lead_repository.find_by_id.return_value = lead
    quote_repository.find_active_by_lead.return_value = None

    financing_service.calculate.side_effect = RuntimeError(
        "Financing error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Financing error",
    ):
        use_case.execute(dto)

    quote_repository.save.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# QUOTE SAVE ERROR
# ============================================================


@patch(
    "modules.quotes.application.use_cases.agent.create_quote.uuid4",
)
def test_execute_quote_save_error_rolls_back(
    mock_uuid4,
    use_case,
    lead_repository,
    quote_repository,
    financing_service,
    event_service,
    unit_of_work,
):
    mock_uuid4.return_value = "quote-123"

    lead = make_lead(
        vehicle=make_vehicle(),
    )

    lead_repository.find_by_id.return_value = lead
    quote_repository.find_active_by_lead.return_value = None
    financing_service.calculate.return_value = (
        make_financing_result()
    )

    quote_repository.save.side_effect = RuntimeError(
        "Save error"
    )

    with pytest.raises(
        RuntimeError,
        match="Save error",
    ):
        use_case.execute(make_dto())

    event_service.log.assert_not_called()
    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# EVENT ERROR
# ============================================================


@patch(
    "modules.quotes.application.use_cases.agent.create_quote.uuid4",
)
def test_execute_event_error_rolls_back(
    mock_uuid4,
    use_case,
    lead_repository,
    quote_repository,
    financing_service,
    event_service,
    unit_of_work,
):
    mock_uuid4.return_value = "quote-123"

    lead = make_lead(
        vehicle=make_vehicle(),
    )

    lead_repository.find_by_id.return_value = lead
    quote_repository.find_active_by_lead.return_value = None
    financing_service.calculate.return_value = (
        make_financing_result()
    )

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(
        RuntimeError,
        match="Event error",
    ):
        use_case.execute(make_dto())

    quote_trade_in_repository = (
        use_case.quote_trade_in_repository
    )

    quote_repository.save.assert_called_once()
    quote_trade_in_repository.save.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# TRADE-IN DETAILS SAVE ERROR
# ============================================================


@patch(
    "modules.quotes.application.use_cases.agent.create_quote.uuid4",
)
def test_execute_trade_in_details_save_error_rolls_back(
    mock_uuid4,
    use_case,
    lead_repository,
    quote_repository,
    quote_trade_in_repository,
    financing_service,
    trade_in_service,
    event_service,
    unit_of_work,
):
    mock_uuid4.return_value = "quote-123"

    lead = make_lead(
        vehicle=make_vehicle(),
    )

    trade_in = Mock()
    trade_in.brand = "Peugeot"
    trade_in.model = "208"
    trade_in.year = 2021
    trade_in.mileage = 30000
    trade_in.condition = "GOOD"

    lead_repository.find_by_id.return_value = lead
    quote_repository.find_active_by_lead.return_value = None

    trade_in_service.estimate.return_value = (
        make_trade_in_result(estimated_value=7000)
    )

    financing_service.calculate.return_value = (
        make_financing_result()
    )

    quote_trade_in_repository.save.side_effect = (
        RuntimeError("Trade-in save error")
    )

    dto = make_dto(
        trade_in=trade_in,
    )

    with pytest.raises(
        RuntimeError,
        match="Trade-in save error",
    ):
        use_case.execute(dto)

    quote_repository.save.assert_called_once()
    event_service.log.assert_called_once()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# COMMIT ERROR
# ============================================================


@patch(
    "modules.quotes.application.use_cases.agent.create_quote.uuid4",
)
def test_execute_commit_error_rolls_back(
    mock_uuid4,
    use_case,
    lead_repository,
    quote_repository,
    financing_service,
    event_service,
    unit_of_work,
):
    mock_uuid4.return_value = "quote-123"

    lead = make_lead(
        vehicle=make_vehicle(),
    )

    lead_repository.find_by_id.return_value = lead
    quote_repository.find_active_by_lead.return_value = None
    financing_service.calculate.return_value = (
        make_financing_result()
    )

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(make_dto())

    quote_repository.save.assert_called_once()
    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()