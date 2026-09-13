from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.leads.domain.exceptions import LeadNotFound
from modules.quotes.domain.exceptions import QuoteNotFound
from modules.quotes.application.use_cases.agent.update_quote import (
    UpdateQuoteUseCase,
)


def make_dto(
    quote_id="quote-123",
    agent_id="agent-123",
    discount=1000,
    down_payment=5000,
    duration_months=48,
    trade_in=None,
):
    dto = Mock()

    dto.quote_id = quote_id
    dto.agent_id = agent_id
    dto.discount = discount
    dto.down_payment = down_payment
    dto.duration_months = duration_months
    dto.trade_in = trade_in

    return dto


def make_trade_in(
    brand="Renault",
    model="Clio",
    year=2020,
    mileage=60000,
    condition="GOOD",
):
    trade_in = Mock()

    trade_in.brand = brand
    trade_in.model = model
    trade_in.year = year
    trade_in.mileage = mileage
    trade_in.condition = condition

    return trade_in


def make_quote(
    quote_id="quote-123",
    lead_id="lead-123",
):
    quote = Mock()

    quote.id = quote_id
    quote.lead_id = lead_id

    return quote


def make_vehicle(
    vehicle_id="vehicle-123",
    price=30000,
):
    vehicle = Mock()

    vehicle.id = vehicle_id
    vehicle.price = price

    return vehicle


def make_lead(
    lead_id="lead-123",
    vehicle=None,
):
    lead = Mock()

    lead.id = lead_id
    lead.vehicle_id = "vehicle-123"
    lead.email = "client@test.com"
    lead.vehicle = vehicle or make_vehicle()

    return lead


def make_financing_result(
    financed_amount=19000,
    monthly_payment=395.83,
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
    return UpdateQuoteUseCase(
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
# SUCCESS - SANS TRADE-IN
# ============================================================


def test_execute_success_without_trade_in(
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
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    financing_result = make_financing_result()

    financing_service.calculate.return_value = financing_result
    quote_trade_in_repository.find_by_quote_id.return_value = None

    dto = make_dto(
        discount=1000,
        down_payment=5000,
        duration_months=48,
        trade_in=None,
    )

    result = use_case.execute(dto)

    assert result.quote_id == "quote-123"
    assert result.message == "Devis mis à jour avec succès"

    authorization.check_owner.assert_called_once_with(
        lead,
        "agent-123",
    )

    trade_in_service.estimate.assert_not_called()

    financing_service.calculate.assert_called_once()

    quote.update_financing.assert_called_once_with(
        base_price=30000,
        discount=1000,
        down_payment=5000,
        trade_in_value=0,
        duration_months=48,
        financed_amount=19000,
        monthly_payment=395.83,
    )

    quote_repository.update.assert_called_once_with(
        quote
    )

    quote_trade_in_repository.find_by_quote_id.assert_called_once_with(
        "quote-123"
    )

    quote_trade_in_repository.save.assert_not_called()
    quote_trade_in_repository.update.assert_not_called()
    quote_trade_in_repository.delete.assert_not_called()

    lead_repository.update.assert_not_called()

    event_service.log.assert_called_once_with(
        type=EventType.QUOTE_UPDATED,
        message="Devis mis à jour",
        quote_id="quote-123",
        lead_id="lead-123",
        user_id="agent-123",
        vehicle_id="vehicle-123",
        event_metadata={
            "financed_amount": 19000,
            "trade_in_value": 0,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# SUCCESS - NOUVEAU TRADE-IN
# ============================================================


def test_execute_success_with_new_trade_in(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    financing_service,
    trade_in_service,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()
    trade_in = make_trade_in()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    trade_in_service.estimate.return_value = (
        make_trade_in_result(8000)
    )

    financing_service.calculate.return_value = (
        make_financing_result(
            financed_amount=11000,
            monthly_payment=229.17,
        )
    )

    quote_trade_in_repository.find_by_quote_id.return_value = None

    dto = make_dto(
        discount=1000,
        down_payment=10000,
        duration_months=48,
        trade_in=trade_in,
    )

    result = use_case.execute(dto)

    assert result.quote_id == "quote-123"

    trade_in_service.estimate.assert_called_once()

    financing_service.calculate.assert_called_once()

    quote.update_financing.assert_called_once_with(
        base_price=30000,
        discount=1000,
        down_payment=10000,
        trade_in_value=8000,
        duration_months=48,
        financed_amount=11000,
        monthly_payment=229.17,
    )

    quote_trade_in_repository.save.assert_called_once()

    saved_trade_in = (
        quote_trade_in_repository.save.call_args.args[0]
    )

    assert saved_trade_in.quote_id == "quote-123"
    assert saved_trade_in.brand == "Renault"
    assert saved_trade_in.model == "Clio"
    assert saved_trade_in.year == 2020
    assert saved_trade_in.mileage == 60000
    assert saved_trade_in.condition == "GOOD"
    assert saved_trade_in.estimated_value == 8000

    quote_trade_in_repository.update.assert_not_called()
    quote_trade_in_repository.delete.assert_not_called()

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# SUCCESS - MISE À JOUR TRADE-IN EXISTANT
# ============================================================


def test_execute_success_update_existing_trade_in(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    financing_service,
    trade_in_service,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()
    existing_trade_in = Mock()

    existing_trade_in.quote_id = "quote-123"

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    trade_in_service.estimate.return_value = (
        make_trade_in_result(9000)
    )

    financing_service.calculate.return_value = (
        make_financing_result()
    )

    quote_trade_in_repository.find_by_quote_id.return_value = (
        existing_trade_in
    )

    dto_trade_in = make_trade_in(
        brand="Peugeot",
        model="208",
        year=2021,
        mileage=45000,
        condition="EXCELLENT",
    )

    dto = make_dto(
        trade_in=dto_trade_in
    )

    result = use_case.execute(dto)

    assert result.quote_id == "quote-123"

    existing_trade_in.update.assert_called_once_with(
        brand="Peugeot",
        model="208",
        year=2021,
        mileage=45000,
        condition="EXCELLENT",
        estimated_value=9000,
    )

    quote_trade_in_repository.update.assert_called_once_with(
        existing_trade_in
    )

    quote_trade_in_repository.save.assert_not_called()
    quote_trade_in_repository.delete.assert_not_called()

    event_service.log.assert_called_once()
    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


# ============================================================
# SUCCESS - SUPPRESSION TRADE-IN
# ============================================================


def test_execute_success_delete_existing_trade_in(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    financing_service,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()
    existing_trade_in = Mock()

    existing_trade_in.quote_id = "quote-123"

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    financing_service.calculate.return_value = (
        make_financing_result()
    )

    quote_trade_in_repository.find_by_quote_id.return_value = (
        existing_trade_in
    )

    dto = make_dto(
        trade_in=None
    )

    result = use_case.execute(dto)

    assert result.quote_id == "quote-123"

    quote_trade_in_repository.delete.assert_called_once_with(
        "quote-123"
    )

    quote_trade_in_repository.save.assert_not_called()
    quote_trade_in_repository.update.assert_not_called()

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
    unit_of_work,
):
    quote_repository.find_by_id.return_value = None

    dto = make_dto()

    with pytest.raises(QuoteNotFound):
        use_case.execute(dto)

    lead_repository.find_by_id.assert_not_called()

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
    trade_in_service,
    financing_service,
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

    trade_in_service.estimate.assert_not_called()
    financing_service.calculate.assert_not_called()

    quote.update_financing.assert_not_called()
    quote_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# TRADE-IN SERVICE ERROR
# ============================================================


def test_execute_trade_in_service_error(
    use_case,
    quote_repository,
    lead_repository,
    trade_in_service,
    financing_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    trade_in_service.estimate.side_effect = RuntimeError(
        "Trade-in error"
    )

    dto = make_dto(
        trade_in=make_trade_in()
    )

    with pytest.raises(
        RuntimeError,
        match="Trade-in error",
    ):
        use_case.execute(dto)

    financing_service.calculate.assert_not_called()

    quote_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# FINANCING SERVICE ERROR
# ============================================================


def test_execute_financing_service_error(
    use_case,
    quote_repository,
    lead_repository,
    financing_service,
    trade_in_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    financing_service.calculate.side_effect = RuntimeError(
        "Financing error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Financing error",
    ):
        use_case.execute(dto)

    trade_in_service.estimate.assert_not_called()

    quote.update_financing.assert_not_called()
    quote_repository.update.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# QUOTE UPDATE ERROR
# ============================================================


def test_execute_quote_update_error(
    use_case,
    quote_repository,
    lead_repository,
    financing_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    financing_service.calculate.return_value = (
        make_financing_result()
    )

    quote_repository.update.side_effect = RuntimeError(
        "Quote update error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Quote update error",
    ):
        use_case.execute(dto)

    quote.update_financing.assert_called_once()

    quote_trade_in_repository = (
        use_case.quote_trade_in_repository
    )

    quote_trade_in_repository.find_by_quote_id.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# TRADE-IN UPDATE ERROR
# ============================================================


def test_execute_trade_in_update_error(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    financing_service,
    trade_in_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()
    existing_trade_in = Mock()

    existing_trade_in.quote_id = "quote-123"

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    trade_in_service.estimate.return_value = (
        make_trade_in_result(8000)
    )

    financing_service.calculate.return_value = (
        make_financing_result()
    )

    quote_trade_in_repository.find_by_quote_id.return_value = (
        existing_trade_in
    )

    quote_trade_in_repository.update.side_effect = (
        RuntimeError("Trade-in update error")
    )

    dto = make_dto(
        trade_in=make_trade_in()
    )

    with pytest.raises(
        RuntimeError,
        match="Trade-in update error",
    ):
        use_case.execute(dto)

    existing_trade_in.update.assert_called_once()

    quote_trade_in_repository.update.assert_called_once_with(
        existing_trade_in
    )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# EVENT ERROR
# ============================================================


def test_execute_event_error(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    financing_service,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    financing_service.calculate.return_value = (
        make_financing_result()
    )

    quote_trade_in_repository.find_by_quote_id.return_value = None

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Event error",
    ):
        use_case.execute(dto)

    quote_repository.update.assert_called_once_with(
        quote
    )

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once()


# ============================================================
# COMMIT ERROR
# ============================================================


def test_execute_commit_error(
    use_case,
    quote_repository,
    quote_trade_in_repository,
    lead_repository,
    financing_service,
    event_service,
    unit_of_work,
):
    quote = make_quote()
    lead = make_lead()

    quote_repository.find_by_id.return_value = quote
    lead_repository.find_by_id.return_value = lead

    financing_service.calculate.return_value = (
        make_financing_result()
    )

    quote_trade_in_repository.find_by_quote_id.return_value = None

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="Commit error",
    ):
        use_case.execute(dto)

    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()