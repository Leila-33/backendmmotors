from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from modules.test_drives.application.dtos.get_existing_test_drive_dto import (
    GetExistingTestDriveDTO,
)
from modules.test_drives.application.use_cases.get_existing_test_drive import (
    GetExistingTestDriveUseCase,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def use_case(repository):
    return GetExistingTestDriveUseCase(
        repository=repository,
    )


@pytest.fixture
def dto():
    return GetExistingTestDriveDTO(
        user_id="user-1",
        vehicle_id="vehicle-1",
    )


# ============================================================
# GET EXISTING TEST DRIVE
# ============================================================


def test_existing_test_drive_is_returned(
    use_case,
    repository,
    dto,
):
    test_drive = SimpleNamespace(
        id="test-drive-1",
        user_id="user-1",
        vehicle_id="vehicle-1",
    )

    repository.get_existing_for_user_vehicle.return_value = test_drive

    result = use_case.execute(
        dto=dto,
    )

    assert result is test_drive

    repository.get_existing_for_user_vehicle.assert_called_once_with(
        user_id="user-1",
        vehicle_id="vehicle-1",
    )


def test_no_existing_test_drive_returns_none(
    use_case,
    repository,
    dto,
):
    repository.get_existing_for_user_vehicle.return_value = None

    result = use_case.execute(
        dto=dto,
    )

    assert result is None

    repository.get_existing_for_user_vehicle.assert_called_once_with(
        user_id="user-1",
        vehicle_id="vehicle-1",
    )


def test_repository_result_is_returned_without_modification(
    use_case,
    repository,
    dto,
):
    repository_result = object()

    repository.get_existing_for_user_vehicle.return_value = (
        repository_result
    )

    result = use_case.execute(
        dto=dto,
    )

    assert result is repository_result