from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from modules.auth.domain.enums import UserRole
from modules.auth.domain.exceptions import Unauthorized
from modules.test_drives.application.results.get_test_drive_detail_result import (
    GetTestDriveDetailsResult,
)
from modules.test_drives.application.use_cases.get_test_drive_detail import (
    GetTestDriveDetailUseCase,
)
from modules.test_drives.domain.exceptions import TestDriveNotFound


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


def make_event(
    *,
    event_id: str = "event-1",
    test_drive_id: str = "test-drive-1",
):
    return Mock(
        id=event_id,
        test_drive_id=test_drive_id,
        type=Mock(value="TEST_DRIVE_CREATED"),
        message="Demande d'essai véhicule créée",
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def event_repository():
    return Mock()


@pytest.fixture
def use_case(
    repository,
    event_repository,
):
    return GetTestDriveDetailUseCase(
        repository=repository,
        event_repository=event_repository,
    )


# ============================================================
# NOT FOUND
# ============================================================


def test_test_drive_not_found(
    use_case,
    repository,
    event_repository,
):
    repository.get_full_by_id.return_value = None

    with pytest.raises(TestDriveNotFound):
        use_case.execute(
            test_drive_id="test-drive-1",
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )

    repository.get_full_by_id.assert_called_once_with(
        "test-drive-1",
    )

    event_repository.get_by_test_drive_id.assert_not_called()


# ============================================================
# CLIENT SECURITY
# ============================================================


def test_client_can_access_own_test_drive(
    use_case,
    repository,
    event_repository,
):
    test_drive = make_test_drive(
        user_id="user-1",
    )

    events = [
        make_event(),
    ]

    repository.get_full_by_id.return_value = test_drive
    event_repository.get_by_test_drive_id.return_value = events

    result = use_case.execute(
        test_drive_id="test-drive-1",
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    assert isinstance(
        result,
        GetTestDriveDetailsResult,
    )

    assert result.test_drive is test_drive
    assert result.events is events


def test_client_cannot_access_another_users_test_drive(
    use_case,
    repository,
    event_repository,
):
    test_drive = make_test_drive(
        user_id="owner-1",
    )

    repository.get_full_by_id.return_value = test_drive

    with pytest.raises(Unauthorized):
        use_case.execute(
            test_drive_id="test-drive-1",
            user_id="another-user",
            user_role=UserRole.CLIENT,
        )

    repository.get_full_by_id.assert_called_once_with(
        "test-drive-1",
    )

    event_repository.get_by_test_drive_id.assert_not_called()


# ============================================================
# PRIVILEGED ROLES
# ============================================================


@pytest.mark.parametrize(
    "user_role",
    [
        UserRole.ADMIN,
        UserRole.SAV_AGENT,
    ],
)
def test_privileged_user_can_access_any_test_drive(
    user_role,
    use_case,
    repository,
    event_repository,
):
    test_drive = make_test_drive(
        user_id="owner-1",
    )

    events = [
        make_event(),
    ]

    repository.get_full_by_id.return_value = test_drive
    event_repository.get_by_test_drive_id.return_value = events

    result = use_case.execute(
        test_drive_id="test-drive-1",
        user_id="another-user",
        user_role=user_role,
    )

    assert isinstance(
        result,
        GetTestDriveDetailsResult,
    )

    assert result.test_drive is test_drive
    assert result.events is events

    event_repository.get_by_test_drive_id.assert_called_once_with(
        "test-drive-1",
    )


# ============================================================
# EVENTS
# ============================================================


def test_events_are_loaded_for_test_drive(
    use_case,
    repository,
    event_repository,
):
    test_drive = make_test_drive()

    events = [
        make_event(
            event_id="event-1",
        ),
        make_event(
            event_id="event-2",
        ),
    ]

    repository.get_full_by_id.return_value = test_drive
    event_repository.get_by_test_drive_id.return_value = events

    result = use_case.execute(
        test_drive_id="test-drive-1",
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    event_repository.get_by_test_drive_id.assert_called_once_with(
        "test-drive-1",
    )

    assert result.events == events


def test_empty_events_are_preserved(
    use_case,
    repository,
    event_repository,
):
    test_drive = make_test_drive()

    repository.get_full_by_id.return_value = test_drive
    event_repository.get_by_test_drive_id.return_value = []

    result = use_case.execute(
        test_drive_id="test-drive-1",
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    assert isinstance(
        result,
        GetTestDriveDetailsResult,
    )

    assert result.events == []


def test_event_order_is_preserved(
    use_case,
    repository,
    event_repository,
):
    test_drive = make_test_drive()

    event_1 = make_event(
        event_id="event-1",
    )
    event_2 = make_event(
        event_id="event-2",
    )
    event_3 = make_event(
        event_id="event-3",
    )

    events = [
        event_1,
        event_2,
        event_3,
    ]

    repository.get_full_by_id.return_value = test_drive
    event_repository.get_by_test_drive_id.return_value = events

    result = use_case.execute(
        test_drive_id="test-drive-1",
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    assert result.events[0] is event_1
    assert result.events[1] is event_2
    assert result.events[2] is event_3


# ============================================================
# RESULT
# ============================================================


def test_result_contains_test_drive_and_events(
    use_case,
    repository,
    event_repository,
):
    test_drive = make_test_drive()

    events = [
        make_event(),
    ]

    repository.get_full_by_id.return_value = test_drive
    event_repository.get_by_test_drive_id.return_value = events

    result = use_case.execute(
        test_drive_id="test-drive-1",
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    assert isinstance(
        result,
        GetTestDriveDetailsResult,
    )

    assert result.test_drive is test_drive
    assert result.events is events


# ============================================================
# REPOSITORY ERRORS
# ============================================================


def test_test_drive_repository_error_is_propagated(
    use_case,
    repository,
    event_repository,
):
    repository.get_full_by_id.side_effect = RuntimeError(
        "test drive repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="test drive repository error",
    ):
        use_case.execute(
            test_drive_id="test-drive-1",
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )

    event_repository.get_by_test_drive_id.assert_not_called()


def test_event_repository_error_is_propagated(
    use_case,
    repository,
    event_repository,
):
    test_drive = make_test_drive()

    repository.get_full_by_id.return_value = test_drive

    event_repository.get_by_test_drive_id.side_effect = RuntimeError(
        "event repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="event repository error",
    ):
        use_case.execute(
            test_drive_id="test-drive-1",
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )


# ============================================================
# VALIDATION ORDER / NO UNEXPECTED CALLS
# ============================================================


def test_events_are_not_loaded_when_test_drive_does_not_exist(
    use_case,
    repository,
    event_repository,
):
    repository.get_full_by_id.return_value = None

    with pytest.raises(TestDriveNotFound):
        use_case.execute(
            test_drive_id="missing-test-drive",
            user_id="user-1",
            user_role=UserRole.CLIENT,
        )

    event_repository.get_by_test_drive_id.assert_not_called()


def test_events_are_not_loaded_when_client_is_not_owner(
    use_case,
    repository,
    event_repository,
):
    repository.get_full_by_id.return_value = make_test_drive(
        user_id="owner-1",
    )

    with pytest.raises(Unauthorized):
        use_case.execute(
            test_drive_id="test-drive-1",
            user_id="another-user",
            user_role=UserRole.CLIENT,
        )

    event_repository.get_by_test_drive_id.assert_not_called()


def test_execute_does_not_modify_test_drive(
    use_case,
    repository,
    event_repository,
):
    test_drive = make_test_drive()

    repository.get_full_by_id.return_value = test_drive
    event_repository.get_by_test_drive_id.return_value = []

    result = use_case.execute(
        test_drive_id="test-drive-1",
        user_id="user-1",
        user_role=UserRole.CLIENT,
    )

    assert result.test_drive is test_drive

    repository.create.assert_not_called()
    repository.update.assert_not_called()
    repository.delete.assert_not_called()

    event_repository.create.assert_not_called()
    event_repository.update.assert_not_called()
    event_repository.delete.assert_not_called()