from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from core.pagination.paginated_result import PaginatedResult
from modules.auth.application.dtos.admin.find_users_dto import FindUsersDTO
from modules.auth.application.results.admin.user_list_item_result import (
    UserListItemResult,
)
from modules.auth.application.use_cases.admin.find_users import (
    FindUsersUseCase,
)


# ============================================================
# HELPERS
# ============================================================


def make_user(
    *,
    user_id="user-1",
    first_name="leila",
    last_name="leila",
    email="leila@example.com",
    role="CLIENT",
    is_active=True,
    is_deleted=False,
    is_verified=True,
    created_at=None,
):
    return SimpleNamespace(
        id=user_id,
        first_name=first_name,
        last_name=last_name,
        email=email,
        role=role,
        is_active=is_active,
        is_deleted=is_deleted,
        is_verified=is_verified,
        created_at=created_at
        or datetime(
            2026,
            1,
            15,
            10,
            30,
            tzinfo=timezone.utc,
        ),
    )


def make_dto(
    *,
    page=1,
    limit=10,
    search=None,
    role=None,
    status=None,
    sort=None,
):
    return FindUsersDTO(
        page=page,
        limit=limit,
        search=search,
        role=role,
        status=status,
        sort=sort,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def user_repo():
    return Mock()


@pytest.fixture
def use_case(user_repo):
    return FindUsersUseCase(
        user_repo=user_repo,
    )


# ============================================================
# BASIC EXECUTION
# ============================================================


def test_execute_returns_paginated_result(
    use_case,
    user_repo,
):
    users = [
        make_user(),
        make_user(
            user_id="user-2",
            first_name="Jane",
            last_name="Smith",
            email="jane@example.com",
        ),
    ]

    user_repo.find_all.return_value = (
        users,
        2,
    )

    dto = make_dto()

    result = use_case.execute(dto)

    assert isinstance(
        result,
        PaginatedResult,
    )

    assert result.total == 2
    assert result.page == 1
    assert result.limit == 10
    assert result.total_pages == 1


# ============================================================
# REPOSITORY CALL
# ============================================================


def test_find_all_is_called_with_dto_parameters(
    use_case,
    user_repo,
):
    user_repo.find_all.return_value = (
        [],
        0,
    )

    dto = make_dto(
        page=2,
        limit=20,
        search="leila",
        role="ADMIN",
        status="ACTIVE",
        sort="created_at_desc",
    )

    use_case.execute(dto)

    user_repo.find_all.assert_called_once_with(
        page=2,
        limit=20,
        search="leila",
        role="ADMIN",
        status="ACTIVE",
        sort="created_at_desc",
    )


# ============================================================
# USER MAPPING
# ============================================================


def test_users_are_mapped_to_user_list_item_results(
    use_case,
    user_repo,
):
    created_at = datetime(
        2026,
        2,
        10,
        14,
        30,
        tzinfo=timezone.utc,
    )

    user = make_user(
        user_id="user-123",
        first_name="Alice",
        last_name="Martin",
        email="alice@example.com",
        role="ADMIN",
        is_active=False,
        is_deleted=True,
        is_verified=False,
        created_at=created_at,
    )

    user_repo.find_all.return_value = (
        [user],
        1,
    )

    result = use_case.execute(
        make_dto()
    )

    assert len(result.items) == 1

    item = result.items[0]

    assert isinstance(
        item,
        UserListItemResult,
    )

    assert item.id == "user-123"
    assert item.first_name == "Alice"
    assert item.last_name == "Martin"
    assert item.email == "alice@example.com"
    assert item.role == "ADMIN"
    assert item.is_active is False
    assert item.is_deleted is True
    assert item.is_verified is False
    assert item.created_at == created_at


def test_multiple_users_are_mapped_in_same_order(
    use_case,
    user_repo,
):
    users = [
        make_user(
            user_id="user-1",
            first_name="Alice",
        ),
        make_user(
            user_id="user-2",
            first_name="Bob",
        ),
        make_user(
            user_id="user-3",
            first_name="Charlie",
        ),
    ]

    user_repo.find_all.return_value = (
        users,
        3,
    )

    result = use_case.execute(
        make_dto()
    )

    assert [
        item.id
        for item in result.items
    ] == [
        "user-1",
        "user-2",
        "user-3",
    ]

    assert [
        item.first_name
        for item in result.items
    ] == [
        "Alice",
        "Bob",
        "Charlie",
    ]


# ============================================================
# EMPTY RESULT
# ============================================================


def test_execute_with_no_users_returns_empty_items(
    use_case,
    user_repo,
):
    user_repo.find_all.return_value = (
        [],
        0,
    )

    result = use_case.execute(
        make_dto()
    )

    assert result.items == []
    assert result.total == 0
    assert result.page == 1
    assert result.limit == 10
    assert result.total_pages == 0


# ============================================================
# PAGINATION
# ============================================================


@pytest.mark.parametrize(
    ("total", "limit", "expected_total_pages"),
    [
        (0, 10, 0),
        (1, 10, 1),
        (10, 10, 1),
        (11, 10, 2),
        (20, 10, 2),
        (21, 10, 3),
        (25, 10, 3),
        (100, 20, 5),
    ],
)
def test_total_pages_are_calculated_correctly(
    total,
    limit,
    expected_total_pages,
    use_case,
    user_repo,
):
    user_repo.find_all.return_value = (
        [],
        total,
    )

    dto = make_dto(
        page=1,
        limit=limit,
    )

    result = use_case.execute(dto)

    assert result.total == total
    assert result.limit == limit
    assert result.total_pages == expected_total_pages


def test_pagination_page_is_preserved(
    use_case,
    user_repo,
):
    user_repo.find_all.return_value = (
        [],
        45,
    )

    dto = make_dto(
        page=4,
        limit=10,
    )

    result = use_case.execute(dto)

    assert result.page == 4
    assert result.limit == 10
    assert result.total == 45
    assert result.total_pages == 5


# ============================================================
# FILTERS
# ============================================================


def test_search_filter_is_forwarded(
    use_case,
    user_repo,
):
    user_repo.find_all.return_value = (
        [],
        0,
    )

    dto = make_dto(
        search="martin",
    )

    use_case.execute(dto)

    user_repo.find_all.assert_called_once_with(
        page=dto.page,
        limit=dto.limit,
        search="martin",
        role=dto.role,
        status=dto.status,
        sort=dto.sort,
    )


def test_role_filter_is_forwarded(
    use_case,
    user_repo,
):
    user_repo.find_all.return_value = (
        [],
        0,
    )

    dto = make_dto(
        role="ADMIN",
    )

    use_case.execute(dto)

    user_repo.find_all.assert_called_once_with(
        page=dto.page,
        limit=dto.limit,
        search=dto.search,
        role="ADMIN",
        status=dto.status,
        sort=dto.sort,
    )


def test_status_filter_is_forwarded(
    use_case,
    user_repo,
):
    user_repo.find_all.return_value = (
        [],
        0,
    )

    dto = make_dto(
        status="ACTIVE",
    )

    use_case.execute(dto)

    user_repo.find_all.assert_called_once_with(
        page=dto.page,
        limit=dto.limit,
        search=dto.search,
        role=dto.role,
        status="ACTIVE",
        sort=dto.sort,
    )


def test_sort_is_forwarded(
    use_case,
    user_repo,
):
    user_repo.find_all.return_value = (
        [],
        0,
    )

    dto = make_dto(
        sort="created_at_desc",
    )

    use_case.execute(dto)

    user_repo.find_all.assert_called_once_with(
        page=dto.page,
        limit=dto.limit,
        search=dto.search,
        role=dto.role,
        status=dto.status,
        sort="created_at_desc",
    )


def test_all_filters_are_forwarded_together(
    use_case,
    user_repo,
):
    user_repo.find_all.return_value = (
        [],
        0,
    )

    dto = make_dto(
        page=3,
        limit=25,
        search="leila",
        role="EMPLOYEE",
        status="INACTIVE",
        sort="last_name_asc",
    )

    use_case.execute(dto)

    user_repo.find_all.assert_called_once_with(
        page=3,
        limit=25,
        search="leila",
        role="EMPLOYEE",
        status="INACTIVE",
        sort="last_name_asc",
    )


# ============================================================
# OPTIONAL / BOOLEAN FIELDS
# ============================================================


def test_user_boolean_fields_are_preserved(
    use_case,
    user_repo,
):
    user = make_user(
        is_active=False,
        is_deleted=True,
        is_verified=False,
    )

    user_repo.find_all.return_value = (
        [user],
        1,
    )

    result = use_case.execute(
        make_dto()
    )

    item = result.items[0]

    assert item.is_active is False
    assert item.is_deleted is True
    assert item.is_verified is False


# ============================================================
# REPOSITORY ERROR
# ============================================================


def test_repository_error_is_propagated(
    use_case,
    user_repo,
):
    user_repo.find_all.side_effect = RuntimeError(
        "database error"
    )

    with pytest.raises(
        RuntimeError,
        match="database error",
    ):
        use_case.execute(
            make_dto()
        )


# ============================================================
# REPOSITORY CALLED ONCE
# ============================================================


def test_repository_is_called_once(
    use_case,
    user_repo,
):
    user_repo.find_all.return_value = (
        [],
        0,
    )

    use_case.execute(
        make_dto()
    )

    user_repo.find_all.assert_called_once()