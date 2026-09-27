import pytest
from unittest.mock import Mock

from core.pagination.paginated_result import PaginatedResult

from modules.test_drives.application.dtos.admin.get_test_drives_admin_dto import (
    GetTestDrivesAdminDTO,
)
from modules.test_drives.application.results.admin.get_test_drives_admin_result import (
    GetTestDrivesAdminResult,
    TestDriveAdminStats,
)
from modules.test_drives.application.use_cases.admin.get_test_drives_admin import (
    GetTestDrivesAdminUseCase,
)


# ============================================================
# HELPERS
# ============================================================


def make_dto(
    *,
    status=None,
    search=None,
    date=None,
    sort_by="created_at",
    sort_order="desc",
    page=1,
    limit=10,
):
    return GetTestDrivesAdminDTO(
        status=status,
        search=search,
        date=date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
    )


def make_result():
    pagination = Mock(
        spec=PaginatedResult
    )

    stats = TestDriveAdminStats(
        pending=5,
        confirmed=3,
        completed=10,
        cancelled=2,
    )

    return GetTestDrivesAdminResult(
        pagination=pagination,
        stats=stats,
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
        repository=repository
    )


# ============================================================
# BASIC EXECUTION
# ============================================================


def test_execute_calls_repository(
    use_case,
    repository,
):
    dto = make_dto()

    expected_result = make_result()

    repository.get_all_admin.return_value = (
        expected_result
    )

    result = use_case.execute(dto)

    repository.get_all_admin.assert_called_once()

    assert result is expected_result


# ============================================================
# REPOSITORY PARAMETERS
# ============================================================


def test_all_dto_parameters_are_forwarded(
    use_case,
    repository,
):
    dto = make_dto(
        status="CONFIRMED",
        search="Dupont",
        date="2026-09-15",
        sort_by="date",
        sort_order="asc",
        page=3,
        limit=20,
    )

    expected_result = make_result()

    repository.get_all_admin.return_value = (
        expected_result
    )

    result = use_case.execute(dto)

    repository.get_all_admin.assert_called_once_with(
        status="CONFIRMED",
        search="Dupont",
        date="2026-09-15",
        sort_by="date",
        sort_order="asc",
        page=3,
        limit=20,
    )

    assert result is expected_result


# ============================================================
# STATUS
# ============================================================


def test_status_is_forwarded(
    use_case,
    repository,
):
    dto = make_dto(
        status="PENDING"
    )

    repository.get_all_admin.return_value = (
        make_result()
    )

    use_case.execute(dto)

    call_kwargs = (
        repository
        .get_all_admin
        .call_args
        .kwargs
    )

    assert call_kwargs["status"] == "PENDING"


# ============================================================
# SEARCH
# ============================================================


def test_search_is_forwarded(
    use_case,
    repository,
):
    dto = make_dto(
        search="Martin"
    )

    repository.get_all_admin.return_value = (
        make_result()
    )

    use_case.execute(dto)

    call_kwargs = (
        repository
        .get_all_admin
        .call_args
        .kwargs
    )

    assert call_kwargs["search"] == "Martin"


# ============================================================
# DATE
# ============================================================


def test_date_is_forwarded(
    use_case,
    repository,
):
    dto = make_dto(
        date="2026-09-20"
    )

    repository.get_all_admin.return_value = (
        make_result()
    )

    use_case.execute(dto)

    call_kwargs = (
        repository
        .get_all_admin
        .call_args
        .kwargs
    )

    assert call_kwargs["date"] == "2026-09-20"


# ============================================================
# SORT
# ============================================================


def test_sort_parameters_are_forwarded(
    use_case,
    repository,
):
    dto = make_dto(
        sort_by="status",
        sort_order="asc",
    )

    repository.get_all_admin.return_value = (
        make_result()
    )

    use_case.execute(dto)

    repository.get_all_admin.assert_called_once_with(
        status=None,
        search=None,
        date=None,
        sort_by="status",
        sort_order="asc",
        page=1,
        limit=10,
    )


# ============================================================
# PAGINATION
# ============================================================


def test_pagination_parameters_are_forwarded(
    use_case,
    repository,
):
    dto = make_dto(
        page=5,
        limit=25,
    )

    repository.get_all_admin.return_value = (
        make_result()
    )

    use_case.execute(dto)

    call_kwargs = (
        repository
        .get_all_admin
        .call_args
        .kwargs
    )

    assert call_kwargs["page"] == 5
    assert call_kwargs["limit"] == 25


# ============================================================
# NONE / DEFAULT FILTERS
# ============================================================


def test_optional_filters_can_be_none(
    use_case,
    repository,
):
    dto = make_dto(
        status=None,
        search=None,
        date=None,
    )

    repository.get_all_admin.return_value = (
        make_result()
    )

    result = use_case.execute(dto)

    repository.get_all_admin.assert_called_once_with(
        status=None,
        search=None,
        date=None,
        sort_by="created_at",
        sort_order="desc",
        page=1,
        limit=10,
    )

    assert result is repository.get_all_admin.return_value


# ============================================================
# RESULT IDENTITY
# ============================================================


def test_repository_result_is_returned_without_modification(
    use_case,
    repository,
):
    expected_result = make_result()

    repository.get_all_admin.return_value = (
        expected_result
    )

    dto = make_dto()

    result = use_case.execute(dto)

    assert result is expected_result


# ============================================================
# RESULT CONTENT
# ============================================================


def test_result_contains_expected_stats(
    use_case,
    repository,
):
    expected_result = make_result()

    repository.get_all_admin.return_value = (
        expected_result
    )

    dto = make_dto()

    result = use_case.execute(dto)

    assert result.stats.pending == 5
    assert result.stats.confirmed == 3
    assert result.stats.completed == 10
    assert result.stats.cancelled == 2


# ============================================================
# REPOSITORY ERROR
# ============================================================


def test_repository_error_is_propagated(
    use_case,
    repository,
):
    dto = make_dto()

    repository.get_all_admin.side_effect = RuntimeError(
        "database error"
    )

    with pytest.raises(
        RuntimeError,
        match="database error",
    ):
        use_case.execute(dto)


# ============================================================
# REPOSITORY CALLED ONLY ONCE
# ============================================================


def test_repository_is_called_only_once(
    use_case,
    repository,
):
    dto = make_dto()

    repository.get_all_admin.return_value = (
        make_result()
    )

    use_case.execute(dto)

    repository.get_all_admin.assert_called_once()