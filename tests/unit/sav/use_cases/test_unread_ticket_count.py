from unittest.mock import Mock

import pytest

from modules.sav.application.results.unread_ticket_count_result import (
    UnreadTicketCountResult,
)
from modules.sav.application.use_cases.get_unread_ticket_count import (
    GetUnreadTicketCountUseCase,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def support_ticket_repository():
    return Mock()


@pytest.fixture
def use_case(
    support_ticket_repository,
):
    return GetUnreadTicketCountUseCase(
        support_ticket_repository=support_ticket_repository,
    )


@pytest.fixture
def user_id():
    return "user-123"


@pytest.fixture
def user_role():
    return "CLIENT"


# ============================================================
# BASIC
# ============================================================


def test_execute_returns_zero_when_no_unread_ticket(
    use_case,
    support_ticket_repository,
    user_id,
    user_role,
):
    support_ticket_repository.count_unread.return_value = 0

    result = use_case.execute(
        user_id=user_id,
        user_role=user_role,
    )

    assert isinstance(
        result,
        UnreadTicketCountResult,
    )

    assert result.count == 0


def test_execute_returns_unread_ticket_count(
    use_case,
    support_ticket_repository,
    user_id,
    user_role,
):
    support_ticket_repository.count_unread.return_value = 5

    result = use_case.execute(
        user_id=user_id,
        user_role=user_role,
    )

    assert isinstance(
        result,
        UnreadTicketCountResult,
    )

    assert result.count == 5


# ============================================================
# REPOSITORY CALL
# ============================================================


def test_execute_calls_repository_with_user_id_and_role(
    use_case,
    support_ticket_repository,
    user_id,
    user_role,
):
    support_ticket_repository.count_unread.return_value = 3

    use_case.execute(
        user_id=user_id,
        user_role=user_role,
    )

    support_ticket_repository.count_unread.assert_called_once_with(
        user_id=user_id,
        user_role=user_role,
    )


# ============================================================
# DIFFERENT COUNTS
# ============================================================


@pytest.mark.parametrize(
    "count",
    [
        0,
        1,
        2,
        10,
        42,
        100,
    ],
)
def test_execute_preserves_repository_count(
    count,
    use_case,
    support_ticket_repository,
    user_id,
    user_role,
):
    support_ticket_repository.count_unread.return_value = count

    result = use_case.execute(
        user_id=user_id,
        user_role=user_role,
    )

    assert result.count == count


# ============================================================
# RESULT
# ============================================================


def test_execute_returns_correct_result(
    use_case,
    support_ticket_repository,
    user_id,
    user_role,
):
    support_ticket_repository.count_unread.return_value = 7

    result = use_case.execute(
        user_id=user_id,
        user_role=user_role,
    )

    expected = UnreadTicketCountResult(
        count=7,
    )

    assert result == expected


# ============================================================
# ERROR
# ============================================================


def test_repository_error_is_propagated(
    use_case,
    support_ticket_repository,
    user_id,
    user_role,
):
    support_ticket_repository.count_unread.side_effect = RuntimeError(
        "repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        use_case.execute(
            user_id=user_id,
            user_role=user_role,
        )

    support_ticket_repository.count_unread.assert_called_once_with(
        user_id=user_id,
        user_role=user_role,
    )


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_execute_only_calls_count_unread(
    use_case,
    support_ticket_repository,
    user_id,
    user_role,
):
    support_ticket_repository.count_unread.return_value = 2

    use_case.execute(
        user_id=user_id,
        user_role=user_role,
    )

    support_ticket_repository.count_unread.assert_called_once()

    support_ticket_repository.create.assert_not_called()
    support_ticket_repository.update.assert_not_called()
    support_ticket_repository.delete.assert_not_called()