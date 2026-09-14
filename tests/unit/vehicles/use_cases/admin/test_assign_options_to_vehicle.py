from unittest.mock import Mock

import pytest

from modules.vehicles.application.use_cases.admin.create_vehicle import (
    AssignOptionsToVehicleUseCase,
)
from modules.vehicles.domain.enums import VehicleOptionType
from modules.vehicles.domain.exceptions import VehicleNotFound
from modules.options.domain.exceptions import OptionNotFound


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def option_repository():
    return Mock()


@pytest.fixture
def vehicle_option_repository():
    return Mock()


@pytest.fixture
def use_case(
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    return AssignOptionsToVehicleUseCase(
        vehicle_repository=vehicle_repository,
        option_repository=option_repository,
        vehicle_option_repository=vehicle_option_repository,
    )


# ============================================================
# HELPERS
# ============================================================


def make_vehicle(
    vehicle_id="vehicle-1",
):
    return Mock(
        id=vehicle_id,
    )


def make_option(
    option_id,
):
    return Mock(
        id=option_id,
    )


# ============================================================
# VEHICLE NOT FOUND
# ============================================================


def test_vehicle_not_found(
    use_case,
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    vehicle_repository.get_by_id.return_value = None

    with pytest.raises(VehicleNotFound):
        use_case.execute(
            vehicle_id="vehicle-1",
            included_option_ids=[],
            optional_option_ids=[],
        )

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-1"
    )

    option_repository.get_by_id.assert_not_called()
    vehicle_option_repository.delete_by_vehicle.assert_not_called()
    vehicle_option_repository.create.assert_not_called()


# ============================================================
# EMPTY OPTIONS
# ============================================================


def test_execute_with_no_options(
    use_case,
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    use_case.execute(
        vehicle_id="vehicle-1",
        included_option_ids=[],
        optional_option_ids=[],
    )

    option_repository.get_by_id.assert_not_called()

    vehicle_option_repository.delete_by_vehicle.assert_called_once_with(
        "vehicle-1"
    )

    vehicle_option_repository.create.assert_not_called()


def test_none_option_lists_are_treated_as_empty(
    use_case,
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    use_case.execute(
        vehicle_id="vehicle-1",
        included_option_ids=None,
        optional_option_ids=None,
    )

    option_repository.get_by_id.assert_not_called()

    vehicle_option_repository.delete_by_vehicle.assert_called_once_with(
        "vehicle-1"
    )

    vehicle_option_repository.create.assert_not_called()


# ============================================================
# INCLUDED OPTIONS
# ============================================================


def test_included_options_are_created(
    use_case,
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    option1 = make_option("option-1")
    option2 = make_option("option-2")

    option_repository.get_by_id.side_effect = [
        option1,
        option2,
    ]

    use_case.execute(
        vehicle_id="vehicle-1",
        included_option_ids=[
            "option-1",
            "option-2",
        ],
        optional_option_ids=[],
    )

    assert option_repository.get_by_id.call_count == 2

    option_repository.get_by_id.assert_any_call(
        "option-1"
    )
    option_repository.get_by_id.assert_any_call(
        "option-2"
    )

    assert vehicle_option_repository.create.call_count == 2

    created_options = [
        call.args[0]
        for call in vehicle_option_repository.create.call_args_list
    ]

    assert created_options[0].vehicle_id == "vehicle-1"
    assert created_options[0].option_id == "option-1"
    assert created_options[0].type == VehicleOptionType.INCLUDED

    assert created_options[1].vehicle_id == "vehicle-1"
    assert created_options[1].option_id == "option-2"
    assert created_options[1].type == VehicleOptionType.INCLUDED


# ============================================================
# OPTIONAL OPTIONS
# ============================================================


def test_optional_options_are_created(
    use_case,
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    option1 = make_option("option-1")
    option2 = make_option("option-2")

    option_repository.get_by_id.side_effect = [
        option1,
        option2,
    ]

    use_case.execute(
        vehicle_id="vehicle-1",
        included_option_ids=[],
        optional_option_ids=[
            "option-1",
            "option-2",
        ],
    )

    assert vehicle_option_repository.create.call_count == 2

    created_options = [
        call.args[0]
        for call in vehicle_option_repository.create.call_args_list
    ]

    assert created_options[0].vehicle_id == "vehicle-1"
    assert created_options[0].option_id == "option-1"
    assert created_options[0].type == VehicleOptionType.OPTIONAL

    assert created_options[1].vehicle_id == "vehicle-1"
    assert created_options[1].option_id == "option-2"
    assert created_options[1].type == VehicleOptionType.OPTIONAL


# ============================================================
# INCLUDED + OPTIONAL
# ============================================================


def test_included_and_optional_options_are_created(
    use_case,
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    option_repository.get_by_id.side_effect = [
        make_option("included-1"),
        make_option("optional-1"),
    ]

    use_case.execute(
        vehicle_id="vehicle-1",
        included_option_ids=["included-1"],
        optional_option_ids=["optional-1"],
    )

    assert vehicle_option_repository.create.call_count == 2

    created_options = [
        call.args[0]
        for call in vehicle_option_repository.create.call_args_list
    ]

    assert created_options[0].option_id == "included-1"
    assert created_options[0].type == VehicleOptionType.INCLUDED

    assert created_options[1].option_id == "optional-1"
    assert created_options[1].type == VehicleOptionType.OPTIONAL


# ============================================================
# EXISTING OPTIONS ARE REMOVED FIRST
# ============================================================


def test_existing_vehicle_options_are_deleted_before_creation(
    use_case,
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    option_repository.get_by_id.return_value = make_option(
        "option-1"
    )

    use_case.execute(
        vehicle_id="vehicle-1",
        included_option_ids=["option-1"],
        optional_option_ids=[],
    )

    vehicle_option_repository.delete_by_vehicle.assert_called_once_with(
        "vehicle-1"
    )

    vehicle_option_repository.create.assert_called_once()


# ============================================================
# OPTION NOT FOUND — INCLUDED
# ============================================================


def test_included_option_not_found(
    use_case,
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    option_repository.get_by_id.return_value = None

    with pytest.raises(OptionNotFound):
        use_case.execute(
            vehicle_id="vehicle-1",
            included_option_ids=["unknown-option"],
            optional_option_ids=[],
        )

    option_repository.get_by_id.assert_called_once_with(
        "unknown-option"
    )

    # Validation happens before deletion.
    vehicle_option_repository.delete_by_vehicle.assert_not_called()
    vehicle_option_repository.create.assert_not_called()


# ============================================================
# OPTION NOT FOUND — OPTIONAL
# ============================================================


def test_optional_option_not_found(
    use_case,
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    option_repository.get_by_id.side_effect = [
        make_option("included-1"),
        None,
    ]

    with pytest.raises(OptionNotFound):
        use_case.execute(
            vehicle_id="vehicle-1",
            included_option_ids=["included-1"],
            optional_option_ids=["unknown-option"],
        )

    option_repository.get_by_id.assert_any_call(
        "included-1"
    )

    option_repository.get_by_id.assert_any_call(
        "unknown-option"
    )

    # Existing relations are not removed if validation fails.
    vehicle_option_repository.delete_by_vehicle.assert_not_called()
    vehicle_option_repository.create.assert_not_called()


# ============================================================
# EXACT REPOSITORY CALLS
# ============================================================


def test_vehicle_is_loaded_with_exact_id(
    use_case,
    vehicle_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    use_case.execute(
        vehicle_id="vehicle-42",
        included_option_ids=[],
        optional_option_ids=[],
    )

    vehicle_repository.get_by_id.assert_called_once_with(
        "vehicle-42"
    )


def test_each_option_is_loaded_with_exact_id(
    use_case,
    vehicle_repository,
    option_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    option_repository.get_by_id.side_effect = [
        make_option("option-1"),
        make_option("option-2"),
        make_option("option-3"),
    ]

    use_case.execute(
        vehicle_id="vehicle-1",
        included_option_ids=[
            "option-1",
            "option-2",
        ],
        optional_option_ids=[
            "option-3",
        ],
    )

    assert option_repository.get_by_id.call_count == 3

    option_repository.get_by_id.assert_any_call(
        "option-1"
    )
    option_repository.get_by_id.assert_any_call(
        "option-2"
    )
    option_repository.get_by_id.assert_any_call(
        "option-3"
    )


# ============================================================
# GENERATED IDS
# ============================================================


def test_created_vehicle_options_have_unique_ids(
    use_case,
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    option_repository.get_by_id.side_effect = [
        make_option("option-1"),
        make_option("option-2"),
    ]

    use_case.execute(
        vehicle_id="vehicle-1",
        included_option_ids=["option-1"],
        optional_option_ids=["option-2"],
    )

    created_options = [
        call.args[0]
        for call in vehicle_option_repository.create.call_args_list
    ]

    assert len(created_options) == 2
    assert created_options[0].id != created_options[1].id

    assert all(
        option.id
        for option in created_options
    )


# ============================================================
# REPOSITORY ERRORS
# ============================================================


def test_vehicle_repository_error_is_propagated(
    use_case,
    vehicle_repository,
):
    vehicle_repository.get_by_id.side_effect = RuntimeError(
        "vehicle repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="vehicle repository error",
    ):
        use_case.execute(
            vehicle_id="vehicle-1",
            included_option_ids=[],
            optional_option_ids=[],
        )


def test_option_repository_error_is_propagated(
    use_case,
    vehicle_repository,
    option_repository,
    vehicle_option_repository,
):
    vehicle_repository.get_by_id.return_value = make_vehicle()

    option_repository.get_by_id.side_effect = RuntimeError(
        "option repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="option repository error",
    ):
        use_case.execute(
            vehicle_id="vehicle-1",
            included_option_ids=["option-1"],
            optional_option_ids=[],
        )

    vehicle_option_repository.delete_by_vehicle.assert_not_called()
    vehicle_option_repository.create.assert_not_called()