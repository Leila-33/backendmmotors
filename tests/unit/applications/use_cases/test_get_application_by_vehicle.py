from unittest.mock import Mock

import pytest

from modules.applications.application.dtos.vehicle_id_dto import VehicleIdDTO
from modules.applications.application.use_cases.get_application_by_vehicle import (
    GetApplicationByVehicleUseCase,
)
from modules.applications.domain.entities.application import Application


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def use_case(application_repository):
    return GetApplicationByVehicleUseCase(
        application_repository=application_repository,
    )


@pytest.fixture
def dto():
    return VehicleIdDTO(
        vehicle_id="vehicle-1",
    )


# ============================================================
# APPLICATION FOUND
# ============================================================

def test_returns_application_when_found(
    use_case,
    application_repository,
    dto,
):
    application = Mock(spec=Application)

    application_repository.find_active_by_user_and_vehicle.return_value = (
        application
    )

    result = use_case.execute(
        dto=dto,
        current_user_id="user-1",
    )

    assert result is application

    application_repository.find_active_by_user_and_vehicle.assert_called_once_with(
        user_id="user-1",
        vehicle_id="vehicle-1",
    )


# ============================================================
# APPLICATION NOT FOUND
# ============================================================

def test_returns_none_when_application_not_found(
    use_case,
    application_repository,
    dto,
):
    application_repository.find_active_by_user_and_vehicle.return_value = None

    result = use_case.execute(
        dto=dto,
        current_user_id="user-1",
    )

    assert result is None

    application_repository.find_active_by_user_and_vehicle.assert_called_once_with(
        user_id="user-1",
        vehicle_id="vehicle-1",
    )


# ============================================================
# USER ID
# ============================================================

def test_passes_current_user_id_to_repository(
    use_case,
    application_repository,
    dto,
):
    application_repository.find_active_by_user_and_vehicle.return_value = None

    use_case.execute(
        dto=dto,
        current_user_id="user-42",
    )

    application_repository.find_active_by_user_and_vehicle.assert_called_once_with(
        user_id="user-42",
        vehicle_id="vehicle-1",
    )


# ============================================================
# VEHICLE ID
# ============================================================

def test_passes_vehicle_id_from_dto_to_repository(
    use_case,
    application_repository,
):
    dto = VehicleIdDTO(
        vehicle_id="vehicle-99",
    )

    application_repository.find_active_by_user_and_vehicle.return_value = None

    use_case.execute(
        dto=dto,
        current_user_id="user-1",
    )

    application_repository.find_active_by_user_and_vehicle.assert_called_once_with(
        user_id="user-1",
        vehicle_id="vehicle-99",
    )


# ============================================================
# RESULT IS RETURNED AS-IS
# ============================================================

def test_returns_exact_repository_result(
    use_case,
    application_repository,
    dto,
):
    application = Mock(spec=Application)

    application_repository.find_active_by_user_and_vehicle.return_value = (
        application
    )

    result = use_case.execute(
        dto=dto,
        current_user_id="user-1",
    )

    assert result is application