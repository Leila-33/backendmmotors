from unittest.mock import Mock

import pytest

from modules.test_drives.application.results.admin.get_pending_test_drive_count_result import (
    GetPendingTestDriveCountResult,
)
from modules.test_drives.application.use_cases.admin.get_pending_test_drive_count import (
    GetPendingTestDriveCountUseCase,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def use_case(repository):
    return GetPendingTestDriveCountUseCase(
        repository=repository,
    )


# ============================================================
# SUCCESS
# ============================================================


def test_execute_returns_pending_test_drive_count(
    use_case,
    repository,
):
    repository.count_pending.return_value = 5

    result = use_case.execute()

    assert isinstance(
        result,
        GetPendingTestDriveCountResult,
    )

    assert result.count == 5


def test_repository_count_pending_is_called_once(
    use_case,
    repository,
):
    repository.count_pending.return_value = 3

    use_case.execute()

    repository.count_pending.assert_called_once_with()


# ============================================================
# ZERO
# ============================================================


def test_execute_returns_zero_when_no_pending_test_drive_exists(
    use_case,
    repository,
):
    repository.count_pending.return_value = 0

    result = use_case.execute()

    assert isinstance(
        result,
        GetPendingTestDriveCountResult,
    )

    assert result.count == 0


# ============================================================
# DIFFERENT COUNTS
# ============================================================


@pytest.mark.parametrize(
    "count",
    [
        0,
        1,
        5,
        10,
        100,
    ],
)
def test_execute_preserves_repository_count(
    count,
    use_case,
    repository,
):
    repository.count_pending.return_value = count

    result = use_case.execute()

    assert result.count == count


# ============================================================
# REPOSITORY ERROR
# ============================================================


def test_repository_error_is_propagated(
    use_case,
    repository,
):
    repository.count_pending.side_effect = RuntimeError(
        "repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        use_case.execute()


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_execute_does_not_modify_repository(
    use_case,
    repository,
):
    repository.count_pending.return_value = 2

    result = use_case.execute()

    assert result.count == 2

    repository.create.assert_not_called()
    repository.update.assert_not_called()
    repository.delete.assert_not_called()