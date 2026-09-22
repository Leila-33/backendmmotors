from unittest.mock import Mock

import pytest

from modules.sav.application.dtos.find_support_tickets_dto import (
    FindSupportTicketsDTO,
)
from core.pagination.paginated_result import PaginatedResult
from modules.sav.application.use_cases.find_support_tickets import (
    FindSupportTicketsUseCase,
)
from modules.sav.domain.enums import (
    TicketCategory,
    TicketFilter,
    TicketPriority,
    TicketStatus,
)


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repo():
    return Mock()


@pytest.fixture
def use_case(repo):
    return FindSupportTicketsUseCase(
        repo=repo,
    )


@pytest.fixture
def user_id():
    return "user-123"


@pytest.fixture
def user_role():
    return "CLIENT"


@pytest.fixture
def items():
    return [
        Mock(id="ticket-1"),
        Mock(id="ticket-2"),
    ]


# ============================================================
# BASIC SEARCH
# ============================================================


def test_execute_calls_repository_with_dto_values(
    use_case,
    repo,
    user_id,
    user_role,
    items,
):
    repo.find_all.return_value = (
        items,
        2,
    )

    dto = FindSupportTicketsDTO(
        page=2,
        limit=10,
        search="véhicule",
        status=TicketStatus.OPEN,
        priority=TicketPriority.HIGH,
        category=TicketCategory.VEHICLE_ISSUE,
        sort="created_at_desc",
        filter=TicketFilter.ALL,
        archive=False,
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    repo.find_all.assert_called_once_with(
        page=2,
        limit=10,
        search="véhicule",
        status=TicketStatus.OPEN,
        category=TicketCategory.VEHICLE_ISSUE,
        priority=TicketPriority.HIGH,
        sort="created_at_desc",
        archive=False,
        user_id="user-123",
        user_role="CLIENT",
    )

    assert isinstance(
        result,
        PaginatedResult,
    )

    assert result.items == items
    assert result.page == 2
    assert result.limit == 10
    assert result.total == 2
    assert result.total_pages == 1


# ============================================================
# DEFAULT DTO VALUES
# ============================================================


def test_execute_uses_default_dto_values(
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO()

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    repo.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search="",
        status="ALL",
        category="ALL",
        priority="ALL",
        sort="created_at_desc",
        archive=False,
        user_id="user-123",
        user_role="CLIENT",
    )

    assert result.items == []
    assert result.page == 1
    assert result.limit == 10
    assert result.total == 0
    assert result.total_pages == 1


# ============================================================
# OPEN FILTER
# ============================================================


def test_open_filter_overrides_status(
    use_case,
    repo,
    user_id,
    user_role,
    items,
):
    repo.find_all.return_value = (
        items,
        3,
    )

    dto = FindSupportTicketsDTO(
        page=1,
        limit=10,
        status=TicketStatus.RESOLVED,
        priority=TicketPriority.HIGH,
        filter=TicketFilter.OPEN,
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    repo.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search="",
        status=[
            TicketStatus.OPEN,
            TicketStatus.IN_PROGRESS,
            TicketStatus.WAITING_CUSTOMER,
        ],
        category="ALL",
        priority=TicketPriority.HIGH,
        sort="created_at_desc",
        archive=False,
        user_id="user-123",
        user_role="CLIENT",
    )

    assert result.total == 3


def test_open_filter_keeps_priority(
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO(
        status=TicketStatus.RESOLVED,
        priority=TicketPriority.URGENT,
        filter=TicketFilter.OPEN,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["status"] == [
        TicketStatus.OPEN,
        TicketStatus.IN_PROGRESS,
        TicketStatus.WAITING_CUSTOMER,
    ]

    assert kwargs["priority"] == TicketPriority.URGENT


# ============================================================
# URGENT FILTER
# ============================================================


def test_urgent_filter_overrides_priority(
    use_case,
    repo,
    user_id,
    user_role,
    items,
):
    repo.find_all.return_value = (
        items,
        2,
    )

    dto = FindSupportTicketsDTO(
        status=TicketStatus.OPEN,
        priority=TicketPriority.LOW,
        filter=TicketFilter.URGENT,
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    repo.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search="",
        status=TicketStatus.OPEN,
        category="ALL",
        priority=TicketPriority.URGENT,
        sort="created_at_desc",
        archive=False,
        user_id="user-123",
        user_role="CLIENT",
    )

    assert result.total == 2


def test_urgent_filter_keeps_status(
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO(
        status=TicketStatus.IN_PROGRESS,
        priority=TicketPriority.LOW,
        filter=TicketFilter.URGENT,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["status"] == TicketStatus.IN_PROGRESS
    assert kwargs["priority"] == TicketPriority.URGENT


# ============================================================
# ALL FILTER
# ============================================================


def test_all_filter_does_not_override_status_or_priority(
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO(
        status=TicketStatus.WAITING_CUSTOMER,
        priority=TicketPriority.MEDIUM,
        filter=TicketFilter.ALL,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    repo.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search="",
        status=TicketStatus.WAITING_CUSTOMER,
        category="ALL",
        priority=TicketPriority.MEDIUM,
        sort="created_at_desc",
        archive=False,
        user_id="user-123",
        user_role="CLIENT",
    )


# ============================================================
# CATEGORY
# ============================================================


def test_category_is_forwarded_to_repository(
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO(
        category=TicketCategory.FINANCING,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert (
        repo.find_all.call_args.kwargs["category"]
        == TicketCategory.FINANCING
    )


# ============================================================
# SEARCH
# ============================================================


def test_search_is_forwarded_to_repository(
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO(
        search="frein",
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert (
        repo.find_all.call_args.kwargs["search"]
        == "frein"
    )


# ============================================================
# ARCHIVE
# ============================================================


@pytest.mark.parametrize(
    "archive",
    [True, False],
)
def test_archive_is_forwarded(
    archive,
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO(
        archive=archive,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert (
        repo.find_all.call_args.kwargs["archive"]
        == archive
    )


# ============================================================
# SORT
# ============================================================


def test_sort_is_forwarded(
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO(
        sort="priority_desc",
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert (
        repo.find_all.call_args.kwargs["sort"]
        == "priority_desc"
    )


# ============================================================
# USER CONTEXT
# ============================================================


def test_user_id_is_forwarded(
    use_case,
    repo,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO()

    use_case.execute(
        dto=dto,
        user_id="specific-user",
        user_role="CLIENT",
    )

    assert (
        repo.find_all.call_args.kwargs["user_id"]
        == "specific-user"
    )


def test_user_role_is_forwarded(
    use_case,
    repo,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO()

    use_case.execute(
        dto=dto,
        user_id="user-123",
        user_role="ADMIN",
    )

    assert (
        repo.find_all.call_args.kwargs["user_role"]
        == "ADMIN"
    )


# ============================================================
# PAGINATION
# ============================================================


@pytest.mark.parametrize(
    "total,limit,expected_pages",
    [
        (0, 10, 1),
        (1, 10, 1),
        (9, 10, 1),
        (10, 10, 1),
        (11, 10, 2),
        (19, 10, 2),
        (20, 10, 2),
        (21, 10, 3),
        (25, 10, 3),
        (100, 10, 10),
    ],
)
def test_pages_are_calculated_correctly(
    total,
    limit,
    expected_pages,
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        total,
    )

    dto = FindSupportTicketsDTO(
        page=1,
        limit=limit,
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert result.total_pages == expected_pages


def test_empty_result_always_has_one_page(
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO(
        page=5,
        limit=10,
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert result.total == 0
    assert result.total_pages == 1
    assert result.total_pages == 5


# ============================================================
# RESULT
# ============================================================


def test_result_contains_repository_items(
    use_case,
    repo,
    user_id,
    user_role,
):
    items = [
        Mock(id="ticket-1"),
        Mock(id="ticket-2"),
        Mock(id="ticket-3"),
    ]

    repo.find_all.return_value = (
        items,
        3,
    )

    dto = FindSupportTicketsDTO(
        page=2,
        limit=2,
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert isinstance(
        result,
        PaginatedResult,
    )

    assert result.items == items
    assert result.page == 2
    assert result.limit == 2
    assert result.total == 3
    assert result.total_pages == 2


# ============================================================
# REPOSITORY ERROR
# ============================================================


def test_repository_error_is_propagated(
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.side_effect = RuntimeError(
        "repository error"
    )

    dto = FindSupportTicketsDTO()

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        use_case.execute(
            dto=dto,
            user_id=user_id,
            user_role=user_role,
        )


# ============================================================
# NO UNEXPECTED SIDE EFFECTS
# ============================================================


def test_use_case_does_not_modify_repository_data(
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = FindSupportTicketsDTO()

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    repo.create.assert_not_called()
    repo.update.assert_not_called()
    repo.delete.assert_not_called()