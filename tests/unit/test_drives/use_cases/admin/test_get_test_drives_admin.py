from unittest.mock import Mock

import pytest

from modules.test_drives.application.dtos.admin.get_test_drives_admin_dto import (
    GetTestDrivesAdminDTO,
)
from core.pagination.paginated_result import (
    PaginatedResult,
)
from modules.test_drives.application.use_cases.admin.get_test_drives_admin import (
    GetTestDrivesAdminUseCase,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def use_case(repository):
    return GetTestDrivesAdminUseCase(
        repository=repository,
    )


# ============================================================
# HELPERS
# ============================================================


def make_dto(
    *,
    status=None,
    search="",
    page=1,
    limit=10,
):
    return GetTestDrivesAdminDTO(
        status=status,
        search=search,
        page=page,
        limit=limit,
    )


def make_result(
    *,
    items=None,
    total=0,
    page=1,
    limit=10,
):
    return PaginatedResult(
        items=items or [],
        total=total,
        page=page,
        limit=limit,
    )


# ============================================================
# SUCCESS
# ============================================================


def test_execute_returns_repository_result(
    use_case,
    repository,
):
    expected_result = make_result(
        items=["test-drive-1", "test-drive-2"],
        total=2,
        page=1,
        limit=10,
    )

    repository.get_all_admin.return_value = expected_result

    dto = make_dto(
        status=None,
        search="",
        page=1,
        limit=10,
    )

    result = use_case.execute(dto)

    assert result is expected_result


def test_execute_returns_paginated_result(
    use_case,
    repository,
):
    expected_result = make_result(
        items=["test-drive-1"],
        total=1,
        page=2,
        limit=5,
    )

    repository.get_all_admin.return_value = expected_result

    dto = make_dto(
        status=None,
        search="",
        page=2,
        limit=5,
    )

    result = use_case.execute(dto)

    assert isinstance(
        result,
        PaginatedResult,
    )

    assert result.items == ["test-drive-1"]
    assert result.total == 1
    assert result.page == 2
    assert result.limit == 5


# ============================================================
# REPOSITORY CALL
# ============================================================


def test_execute_calls_repository_with_exact_dto_values(
    use_case,
    repository,
):
    repository.get_all_admin.return_value = make_result()

    dto = make_dto(
        status="PENDING",
        search="BMW",
        page=3,
        limit=20,
    )

    use_case.execute(dto)

    repository.get_all_admin.assert_called_once_with(
        status="PENDING",
        search="BMW",
        page=3,
        limit=20,
    )


def test_execute_passes_empty_search(
    use_case,
    repository,
):
    repository.get_all_admin.return_value = make_result()

    dto = make_dto(
        status="PENDING",
        search="",
        page=1,
        limit=10,
    )

    use_case.execute(dto)

    repository.get_all_admin.assert_called_once_with(
        status="PENDING",
        search="",
        page=1,
        limit=10,
    )


def test_execute_passes_pagination_values(
    use_case,
    repository,
):
    repository.get_all_admin.return_value = make_result()

    dto = make_dto(
        status="CONFIRMED",
        search="Audi",
        page=4,
        limit=25,
    )

    use_case.execute(dto)

    repository.get_all_admin.assert_called_once_with(
        status="CONFIRMED",
        search="Audi",
        page=4,
        limit=25,
    )


# ============================================================
# EMPTY RESULT
# ============================================================


def test_execute_returns_empty_paginated_result(
    use_case,
    repository,
):
    expected_result = make_result(
        items=[],
        total=0,
        page=1,
        limit=10,
    )

    repository.get_all_admin.return_value = expected_result

    dto = make_dto()

    result = use_case.execute(dto)

    assert result is expected_result
    assert result.items == []
    assert result.total == 0


# ============================================================
# DIFFERENT FILTERS
# ============================================================


@pytest.mark.parametrize(
    "status,search,page,limit",
    [
        (None, "", 1, 10),
        ("PENDING", "", 1, 10),
        ("CONFIRMED", "BMW", 2, 10),
        ("CANCELLED", "Audi", 3, 20),
    ],
)
def test_execute_passes_all_filters(
    status,
    search,
    page,
    limit,
    use_case,
    repository,
):
    repository.get_all_admin.return_value = make_result()

    dto = make_dto(
        status=status,
        search=search,
        page=page,
        limit=limit,
    )

    use_case.execute(dto)

    repository.get_all_admin.assert_called_once_with(
        status=status,
        search=search,
        page=page,
        limit=limit,
    )


# ============================================================
# REPOSITORY ERROR
# ============================================================


def test_repository_error_is_propagated(
    use_case,
    repository,
):
    repository.get_all_admin.side_effect = RuntimeError(
        "repository error"
    )

    dto = make_dto()

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        use_case.execute(dto)


# ============================================================
# NO UNEXPECTED OPERATIONS
# ============================================================


def test_execute_does_not_modify_repository(
    use_case,
    repository,
):
    repository.get_all_admin.return_value = make_result()

    dto = make_dto()

    use_case.execute(dto)

    repository.create.assert_not_called()
    repository.update.assert_not_called()
    repository.delete.assert_not_called()