from unittest.mock import Mock

import pytest

from modules.notifications.application.dtos.get_unread_count_dto import (
    GetUnreadCountDTO,
)
from modules.notifications.application.use_cases.get_unread_count import (
    GetUnreadCountUseCase,
)


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def use_case(repository):
    return GetUnreadCountUseCase(
        repository=repository,
    )


@pytest.fixture
def dto():
    return GetUnreadCountDTO(
        user_id="user-123",
    )


def test_get_unread_count_returns_count(
    use_case,
    repository,
    dto,
):
    repository.count_unread.return_value = 5

    result = use_case.execute(dto)

    repository.count_unread.assert_called_once_with(
        "user-123"
    )

    assert result.count == 5


def test_get_unread_count_returns_zero_when_no_unread_notifications(
    use_case,
    repository,
    dto,
):
    repository.count_unread.return_value = 0

    result = use_case.execute(dto)

    repository.count_unread.assert_called_once_with(
        "user-123"
    )

    assert result.count == 0


def test_get_unread_count_propagates_repository_error(
    use_case,
    repository,
    dto,
):
    repository.count_unread.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    repository.count_unread.assert_called_once_with(
        "user-123"
    )
