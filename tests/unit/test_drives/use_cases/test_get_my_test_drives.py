from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from modules.test_drives.application.results.get_my_test_drives_result import (
    GetMyTestDrivesResult,
)
from modules.test_drives.application.use_cases.get_my_test_drives import (
    GetMyTestDrivesUseCase,
)


# ============================================================
# HELPERS
# ============================================================


def make_test_drive(
    *,
    test_drive_id: str = "test-drive-1",
    user_id: str = "user-1",
):
    return Mock(
        id=test_drive_id,
        user_id=user_id,
        vehicle_id="vehicle-1",
        appointment_date=datetime(
            2026,
            9,
            20,
            10,
            0,
            tzinfo=timezone.utc,
        ),
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def use_case(repository):
    return GetMyTestDrivesUseCase(
        repository=repository,
    )


# ============================================================
# SUCCESS
# ============================================================


def test_execute_returns_user_test_drives(
    use_case,
    repository,
):
    test_drives = [
        make_test_drive(
            test_drive_id="test-drive-1",
            user_id="user-1",
        ),
        make_test_drive(
            test_drive_id="test-drive-2",
            user_id="user-1",
        ),
    ]

    repository.get_by_user_id.return_value = test_drives

    result = use_case.execute(
        user_id="user-1",
    )

    assert isinstance(
        result,
        GetMyTestDrivesResult,
    )

    assert result.items == test_drives


def test_repository_is_called_with_user_id(
    use_case,
    repository,
):
    repository.get_by_user_id.return_value = []

    use_case.execute(
        user_id="user-42",
    )

    repository.get_by_user_id.assert_called_once_with(
        "user-42",
    )


# ============================================================
# EMPTY RESULT
# ============================================================


def test_execute_returns_empty_items_when_user_has_no_test_drives(
    use_case,
    repository,
):
    repository.get_by_user_id.return_value = []

    result = use_case.execute(
        user_id="user-1",
    )

    assert isinstance(
        result,
        GetMyTestDrivesResult,
    )

    assert result.items == []


# ============================================================
# RESULT PRESERVATION
# ============================================================


def test_execute_preserves_repository_order(
    use_case,
    repository,
):
    test_drive_1 = make_test_drive(
        test_drive_id="test-drive-1",
    )
    test_drive_2 = make_test_drive(
        test_drive_id="test-drive-2",
    )
    test_drive_3 = make_test_drive(
        test_drive_id="test-drive-3",
    )

    test_drives = [
        test_drive_1,
        test_drive_2,
        test_drive_3,
    ]

    repository.get_by_user_id.return_value = test_drives

    result = use_case.execute(
        user_id="user-1",
    )

    assert result.items[0] is test_drive_1
    assert result.items[1] is test_drive_2
    assert result.items[2] is test_drive_3


def test_execute_preserves_same_list_instance(
    use_case,
    repository,
):
    test_drives = [
        make_test_drive(),
    ]

    repository.get_by_user_id.return_value = test_drives

    result = use_case.execute(
        user_id="user-1",
    )

    assert result.items is test_drives


# ============================================================
# REPOSITORY ERRORS
# ============================================================


def test_repository_error_is_propagated(
    use_case,
    repository,
):
    repository.get_by_user_id.side_effect = RuntimeError(
        "repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        use_case.execute(
            user_id="user-1",
        )


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_execute_does_not_modify_test_drives(
    use_case,
    repository,
):
    test_drives = [
        make_test_drive(),
    ]

    repository.get_by_user_id.return_value = test_drives

    result = use_case.execute(
        user_id="user-1",
    )

    assert result.items == test_drives

    repository.create.assert_not_called()
    repository.update.assert_not_called()
    repository.delete.assert_not_called()
