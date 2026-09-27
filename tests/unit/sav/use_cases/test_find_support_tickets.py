from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from core.pagination.paginated_result import PaginatedResult
from modules.auth.domain.enums import UserRole
from modules.sav.application.dtos.find_support_tickets_dto import (
    FindSupportTicketsDTO,
)
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
# HELPERS
# ============================================================


def make_dto(
    *,
    page=1,
    limit=10,
    search=None,
    status=None,
    category=None,
    priority=None,
    filter=None,
    sort=None,
    archive=False,
):
    return FindSupportTicketsDTO(
        page=page,
        limit=limit,
        search=search,
        status=status,
        category=category,
        priority=priority,
        filter=filter,
        sort=sort,
        archive=archive,
    )


def make_ticket(
    *,
    ticket_id="ticket-1",
    user_id="user-1",
    application_id=None,
    subject="Problème véhicule",
    description="Description du problème",
    category=None,
    status=TicketStatus.OPEN,
    priority=TicketPriority.MEDIUM,
    assigned_to=None,
):
    """
    SupportTicket réel avec les valeurs nécessaires aux tests.

    La catégorie est récupérée dynamiquement si nécessaire afin
    de ne pas dépendre d'une valeur inventée.
    """
    if category is None:
        category = next(iter(TicketCategory))

    return SimpleNamespace(
        id=ticket_id,
        user_id=user_id,
        application_id=application_id,
        subject=subject,
        description=description,
        category=category,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        created_at=None,
        updated_at=None,
        messages=[],
        archived_at=None,
    )


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def repo():
    repository = Mock()

    repository.find_all.return_value = (
        [],
        0,
    )

    return repository


@pytest.fixture
def use_case(repo):
    return FindSupportTicketsUseCase(
        repo=repo,
    )


@pytest.fixture
def user_id():
    return "user-42"


@pytest.fixture
def user_role():
    return UserRole.CLIENT


# ============================================================
# BASIC SEARCH
# ============================================================


def test_find_support_tickets_calls_repository(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto()

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    repo.find_all.assert_called_once()


def test_repository_receives_pagination_parameters(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        page=3,
        limit=20,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["page"] == 3
    assert kwargs["limit"] == 20


def test_repository_receives_search(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        search="frein",
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["search"] == "frein"


def test_repository_receives_status(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        status=[TicketStatus.OPEN],
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["status"] == [TicketStatus.OPEN]


def test_repository_receives_category(
    use_case,
    repo,
    user_id,
    user_role,
):
    category = next(iter(TicketCategory))

    dto = make_dto(
        category=category,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["category"] == category


def test_repository_receives_priority(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        priority=TicketPriority.URGENT,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["priority"] == TicketPriority.URGENT


def test_repository_receives_sort(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        sort="created_at_desc",
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["sort"] == "created_at_desc"


def test_repository_receives_archive(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        archive=True,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["archive"] is True


# ============================================================
# USER / ROLE
# ============================================================


def test_repository_receives_user_id(
    use_case,
    repo,
    user_role,
):
    dto = make_dto()

    use_case.execute(
        dto=dto,
        user_id="user-99",
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["user_id"] == "user-99"


def test_repository_receives_user_role(
    use_case,
    repo,
    user_id,
):
    dto = make_dto()

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=UserRole.CLIENT,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["user_role"] == UserRole.CLIENT


# ============================================================
# FILTER — OPEN
# ============================================================


def test_open_filter_replaces_status_with_open_statuses(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
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


def test_open_filter_overrides_explicit_status(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        filter=TicketFilter.OPEN,
        status=[TicketStatus.CLOSED],
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


# ============================================================
# FILTER — URGENT
# ============================================================


def test_urgent_filter_sets_urgent_priority(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        filter=TicketFilter.URGENT,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["priority"] == TicketPriority.URGENT


def test_urgent_filter_overrides_explicit_priority(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        filter=TicketFilter.URGENT,
        priority=TicketPriority.MEDIUM,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["priority"] == TicketPriority.URGENT


# ============================================================
# NO SPECIAL FILTER
# ============================================================


def test_without_filter_preserves_status_and_priority(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        status=[TicketStatus.OPEN],
        priority=TicketPriority.MEDIUM,
        filter=None,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["status"] == [TicketStatus.OPEN]
    assert kwargs["priority"] == TicketPriority.MEDIUM


def test_without_filter_keeps_none_status_and_priority(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        status=None,
        priority=None,
        filter=None,
    )

    use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["status"] is None
    assert kwargs["priority"] is None


# ============================================================
# PAGINATION
# ============================================================


def test_returns_paginated_result(
    use_case,
    repo,
    user_id,
    user_role,
):
    tickets = [
        make_ticket(
            ticket_id="ticket-1",
        ),
        make_ticket(
            ticket_id="ticket-2",
        ),
    ]

    repo.find_all.return_value = (
        tickets,
        2,
    )

    dto = make_dto(
        page=1,
        limit=10,
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


def test_paginated_result_contains_items(
    use_case,
    repo,
    user_id,
    user_role,
):
    tickets = [
        make_ticket(
            ticket_id="ticket-1",
        ),
        make_ticket(
            ticket_id="ticket-2",
        ),
    ]

    repo.find_all.return_value = (
        tickets,
        2,
    )

    dto = make_dto(
        page=1,
        limit=10,
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert result.items == tickets


def test_paginated_result_contains_total(
    use_case,
    repo,
    user_id,
    user_role,
):
    tickets = [
        make_ticket(
            ticket_id="ticket-1",
        ),
    ]

    repo.find_all.return_value = (
        tickets,
        25,
    )

    dto = make_dto(
        page=2,
        limit=10,
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert result.total == 25


def test_paginated_result_contains_page(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        page=4,
        limit=10,
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert result.page == 4


def test_paginated_result_contains_limit(
    use_case,
    repo,
    user_id,
    user_role,
):
    dto = make_dto(
        page=1,
        limit=25,
    )

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert result.limit == 25


# ============================================================
# EMPTY RESULT
# ============================================================


def test_empty_result_is_supported(
    use_case,
    repo,
    user_id,
    user_role,
):
    repo.find_all.return_value = (
        [],
        0,
    )

    dto = make_dto()

    result = use_case.execute(
        dto=dto,
        user_id=user_id,
        user_role=user_role,
    )

    assert result.items == []
    assert result.total == 0


# ============================================================
# COMPLETE FLOW
# ============================================================


def test_find_support_tickets_complete_flow(
    use_case,
    repo,
):
    tickets = [
        make_ticket(
            ticket_id="ticket-1",
            user_id="user-42",
            status=TicketStatus.OPEN,
            priority=TicketPriority.URGENT,
        ),
        make_ticket(
            ticket_id="ticket-2",
            user_id="user-42",
            status=TicketStatus.IN_PROGRESS,
            priority=TicketPriority.URGENT,
        ),
    ]

    repo.find_all.return_value = (
        tickets,
        2,
    )

    dto = make_dto(
        page=1,
        limit=10,
        search="véhicule",
        filter=TicketFilter.OPEN,
        sort="created_at_desc",
        archive=False,
    )

    result = use_case.execute(
        dto=dto,
        user_id="user-42",
        user_role=UserRole.CLIENT,
    )

    # Repository
    repo.find_all.assert_called_once()

    kwargs = repo.find_all.call_args.kwargs

    assert kwargs["page"] == 1
    assert kwargs["limit"] == 10
    assert kwargs["search"] == "véhicule"

    assert kwargs["status"] == [
        TicketStatus.OPEN,
        TicketStatus.IN_PROGRESS,
        TicketStatus.WAITING_CUSTOMER,
    ]

    assert kwargs["category"] is None
    assert kwargs["priority"] is None
    assert kwargs["sort"] == "created_at_desc"
    assert kwargs["archive"] is False
    assert kwargs["user_id"] == "user-42"
    assert kwargs["user_role"] == UserRole.CLIENT

    # Résultat
    assert isinstance(
        result,
        PaginatedResult,
    )

    assert result.items == tickets
    assert result.total == 2
    assert result.page == 1
    assert result.limit == 10