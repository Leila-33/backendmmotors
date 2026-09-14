from unittest.mock import Mock

import pytest

from modules.vehicles.application.results.get_vehicle_interest_status_result import (
    GetVehicleInterestStatusResult,
)
from modules.vehicles.application.use_cases.get_vehicle_interest_status import (
    GetVehicleInterestStatusUseCase,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def lead_repository():
    return Mock()


@pytest.fixture
def quote_repository():
    return Mock()


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def use_case(
    lead_repository,
    quote_repository,
    application_repository,
):
    return GetVehicleInterestStatusUseCase(
        lead_repository=lead_repository,
        quote_repository=quote_repository,
        application_repository=application_repository,
    )


# ============================================================
# HELPERS
# ============================================================


def make_lead(
    *,
    lead_id="lead-1",
):
    return Mock(
        id=lead_id,
    )


def make_quote(
    *,
    quote_id="quote-1",
    status="PENDING",
):
    quote = Mock(
        id=quote_id,
    )

    # Le use case utilise quote.status.value.
    quote.status.value = status

    return quote


def make_application(
    *,
    application_id="application-1",
):
    return Mock(
        id=application_id,
    )


# ============================================================
# NO ACTIVE LEAD
# ============================================================


def test_no_active_lead_means_not_interested(
    use_case,
    lead_repository,
    quote_repository,
    application_repository,
):
    lead_repository.find_active_by_user_and_vehicle.return_value = None

    result = use_case.execute(
        vehicle_id="vehicle-1",
        user_id="user-1",
    )

    assert isinstance(
        result,
        GetVehicleInterestStatusResult,
    )

    assert result.already_interested is False


def test_no_active_lead_does_not_search_quote(
    use_case,
    lead_repository,
    quote_repository,
    application_repository,
):
    lead_repository.find_active_by_user_and_vehicle.return_value = None

    use_case.execute(
        vehicle_id="vehicle-1",
        user_id="user-1",
    )

    quote_repository.find_active_by_lead.assert_not_called()
    application_repository.find_by_quote_id.assert_not_called()


def test_no_active_lead_calls_repository_with_exact_values(
    use_case,
    lead_repository,
):
    lead_repository.find_active_by_user_and_vehicle.return_value = None

    use_case.execute(
        vehicle_id="vehicle-42",
        user_id="user-15",
    )

    lead_repository.find_active_by_user_and_vehicle.assert_called_once_with(
        user_id="user-15",
        vehicle_id="vehicle-42",
    )


# ============================================================
# ACTIVE LEAD — NO QUOTE
# ============================================================


def test_active_lead_without_quote_means_already_interested(
    use_case,
    lead_repository,
    quote_repository,
    application_repository,
):
    lead = make_lead()

    lead_repository.find_active_by_user_and_vehicle.return_value = lead
    quote_repository.find_active_by_lead.return_value = None

    result = use_case.execute(
        vehicle_id="vehicle-1",
        user_id="user-1",
    )

    assert isinstance(
        result,
        GetVehicleInterestStatusResult,
    )

    assert result.already_interested is True


def test_active_lead_without_quote_does_not_search_application(
    use_case,
    lead_repository,
    quote_repository,
    application_repository,
):
    lead = make_lead()

    lead_repository.find_active_by_user_and_vehicle.return_value = lead
    quote_repository.find_active_by_lead.return_value = None

    use_case.execute(
        vehicle_id="vehicle-1",
        user_id="user-1",
    )

    application_repository.find_by_quote_id.assert_not_called()


def test_quote_is_searched_using_lead_id(
    use_case,
    lead_repository,
    quote_repository,
):
    lead = make_lead(
        lead_id="lead-42",
    )

    lead_repository.find_active_by_user_and_vehicle.return_value = lead
    quote_repository.find_active_by_lead.return_value = None

    use_case.execute(
        vehicle_id="vehicle-1",
        user_id="user-1",
    )

    quote_repository.find_active_by_lead.assert_called_once_with(
        "lead-42"
    )


# ============================================================
# ACTIVE LEAD + QUOTE + APPLICATION
# ============================================================


def test_active_lead_with_quote_and_application(
    use_case,
    lead_repository,
    quote_repository,
    application_repository,
):
    lead = make_lead(
        lead_id="lead-1",
    )

    quote = make_quote(
        quote_id="quote-1",
        status="SENT",
    )

    application = make_application(
        application_id="application-1",
    )

    lead_repository.find_active_by_user_and_vehicle.return_value = lead
    quote_repository.find_active_by_lead.return_value = quote
    application_repository.find_by_quote_id.return_value = application

    result = use_case.execute(
        vehicle_id="vehicle-1",
        user_id="user-1",
    )

    assert isinstance(
        result,
        GetVehicleInterestStatusResult,
    )

    assert result.already_interested is True
    assert result.quote_id == "quote-1"
    assert result.quote_status == "SENT"
    assert result.application_id == "application-1"


def test_application_is_searched_using_quote_id(
    use_case,
    lead_repository,
    quote_repository,
    application_repository,
):
    lead = make_lead(
        lead_id="lead-1",
    )

    quote = make_quote(
        quote_id="quote-99",
        status="PENDING",
    )

    lead_repository.find_active_by_user_and_vehicle.return_value = lead
    quote_repository.find_active_by_lead.return_value = quote
    application_repository.find_by_quote_id.return_value = None

    use_case.execute(
        vehicle_id="vehicle-1",
        user_id="user-1",
    )

    application_repository.find_by_quote_id.assert_called_once_with(
        "quote-99"
    )


# ============================================================
# ACTIVE LEAD + QUOTE WITHOUT APPLICATION
# ============================================================


def test_active_lead_with_quote_without_application(
    use_case,
    lead_repository,
    quote_repository,
    application_repository,
):
    lead = make_lead()
    quote = make_quote(
        quote_id="quote-1",
        status="ACCEPTED",
    )

    lead_repository.find_active_by_user_and_vehicle.return_value = lead
    quote_repository.find_active_by_lead.return_value = quote
    application_repository.find_by_quote_id.return_value = None

    result = use_case.execute(
        vehicle_id="vehicle-1",
        user_id="user-1",
    )

    assert result.already_interested is True
    assert result.quote_id == "quote-1"
    assert result.quote_status == "ACCEPTED"
    assert result.application_id is None


# ============================================================
# DIFFERENT QUOTE STATUSES
# ============================================================


@pytest.mark.parametrize(
    "status",
    [
        "PENDING",
        "SENT",
        "ACCEPTED",
        "REJECTED",
    ],
)
def test_quote_status_is_returned_from_enum_value(
    status,
    use_case,
    lead_repository,
    quote_repository,
    application_repository,
):
    lead = make_lead()
    quote = make_quote(
        quote_id="quote-1",
        status=status,
    )

    lead_repository.find_active_by_user_and_vehicle.return_value = lead
    quote_repository.find_active_by_lead.return_value = quote
    application_repository.find_by_quote_id.return_value = None

    result = use_case.execute(
        vehicle_id="vehicle-1",
        user_id="user-1",
    )

    assert result.quote_status == status


# ============================================================
# REPOSITORY ERRORS
# ============================================================


def test_lead_repository_error_is_propagated(
    use_case,
    lead_repository,
):
    lead_repository.find_active_by_user_and_vehicle.side_effect = (
        RuntimeError("lead repository error")
    )

    with pytest.raises(
        RuntimeError,
        match="lead repository error",
    ):
        use_case.execute(
            vehicle_id="vehicle-1",
            user_id="user-1",
        )


def test_quote_repository_error_is_propagated(
    use_case,
    lead_repository,
    quote_repository,
):
    lead_repository.find_active_by_user_and_vehicle.return_value = (
        make_lead()
    )

    quote_repository.find_active_by_lead.side_effect = (
        RuntimeError("quote repository error")
    )

    with pytest.raises(
        RuntimeError,
        match="quote repository error",
    ):
        use_case.execute(
            vehicle_id="vehicle-1",
            user_id="user-1",
        )


def test_application_repository_error_is_propagated(
    use_case,
    lead_repository,
    quote_repository,
    application_repository,
):
    lead_repository.find_active_by_user_and_vehicle.return_value = (
        make_lead()
    )

    quote_repository.find_active_by_lead.return_value = (
        make_quote()
    )

    application_repository.find_by_quote_id.side_effect = (
        RuntimeError("application repository error")
    )

    with pytest.raises(
        RuntimeError,
        match="application repository error",
    ):
        use_case.execute(
            vehicle_id="vehicle-1",
            user_id="user-1",
        )


# ============================================================
# NO UNEXPECTED WRITES
# ============================================================


def test_use_case_does_not_modify_repositories(
    use_case,
    lead_repository,
    quote_repository,
    application_repository,
):
    lead_repository.find_active_by_user_and_vehicle.return_value = None

    use_case.execute(
        vehicle_id="vehicle-1",
        user_id="user-1",
    )

    lead_repository.create.assert_not_called()
    lead_repository.update.assert_not_called()
    lead_repository.delete.assert_not_called()

    quote_repository.create.assert_not_called()
    quote_repository.update.assert_not_called()
    quote_repository.delete.assert_not_called()

    application_repository.create.assert_not_called()
    application_repository.update.assert_not_called()
    application_repository.delete.assert_not_called()