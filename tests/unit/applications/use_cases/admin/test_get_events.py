import math
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from modules.applications.api.schemas import (
    EventDetailResponse,
    EventPaginationResponse,
)
from modules.applications.application.use_cases.admin.get_events import (
    GetEventsUseCase,
)


# ============================================================
# HELPERS
# ============================================================


def make_event(
    *,
    event_id="event-1",
    event_type="APPLICATION_CREATED",
    message="Application créée.",
    event_metadata=None,
    application_id="application-1",
    test_drive_id=None,
    user_id="user-1",
    created_at=None,
):
    event = Mock()

    event.id = event_id
    event.type = Mock(value=event_type)
    event.message = message
    event.event_metadata = event_metadata or {}
    event.created_at = created_at or datetime(
        2026,
        1,
        15,
        10,
        30,
        tzinfo=timezone.utc,
    )
    event.application_id = application_id
    event.test_drive_id = test_drive_id
    event.user_id = user_id

    return event


# ============================================================
# FIXTURES
# ============================================================


@pytest.fixture
def event_repository():
    return Mock()


@pytest.fixture
def use_case(event_repository):
    return GetEventsUseCase(
        event_repository=event_repository,
    )


# ============================================================
# REPOSITORY CALL
# ============================================================


def test_repository_is_called_with_all_filters(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = ([], 0)

    use_case.execute(
        page=2,
        limit=10,
        search="application",
        event_type="APPLICATION_CREATED",
        date="2026-01-15",
    )

    event_repository.find_all.assert_called_once_with(
        page=2,
        limit=10,
        search="application",
        event_type="APPLICATION_CREATED",
        date="2026-01-15",
    )


def test_repository_is_called_with_default_filters(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = ([], 0)

    use_case.execute(
        page=1,
        limit=10,
    )

    event_repository.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search=None,
        event_type=None,
        date=None,
    )


# ============================================================
# EVENTS MAPPING
# ============================================================


def test_events_are_transformed_into_event_detail_responses(
    use_case,
    event_repository,
):
    created_at = datetime(
        2026,
        2,
        10,
        14,
        20,
        tzinfo=timezone.utc,
    )

    event = make_event(
        event_id="event-123",
        event_type="APPLICATION_CREATED",
        message="Nouvelle application",
        event_metadata={
            "source": "client",
            "status": "DRAFT",
        },
        application_id="application-123",
        test_drive_id="test-drive-123",
        user_id="user-123",
        created_at=created_at,
    )

    event_repository.find_all.return_value = (
        [event],
        1,
    )

    result = use_case.execute(
        page=1,
        limit=10,
    )

    assert isinstance(
        result,
        EventPaginationResponse,
    )

    assert len(result.items) == 1

    item = result.items[0]

    assert isinstance(
        item,
        EventDetailResponse,
    )

    assert item.id == "event-123"
    assert item.type == "APPLICATION_CREATED"
    assert item.message == "Nouvelle application"
    assert item.event_metadata == {
        "source": "client",
        "status": "DRAFT",
    }
    assert item.created_at == created_at
    assert item.application_id == "application-123"
    assert item.test_drive_id == "test-drive-123"
    assert item.user_id == "user-123"


def test_event_type_value_is_used(
    use_case,
    event_repository,
):
    event = make_event(
        event_type="LEAD_CREATED",
    )

    event_repository.find_all.return_value = (
        [event],
        1,
    )

    result = use_case.execute(
        page=1,
        limit=10,
    )

    assert result.items[0].type == "LEAD_CREATED"


def test_multiple_events_are_mapped_in_same_order(
    use_case,
    event_repository,
):
    events = [
        make_event(
            event_id="event-1",
            event_type="LEAD_CREATED",
            message="Lead créé",
        ),
        make_event(
            event_id="event-2",
            event_type="QUOTE_CREATED",
            message="Devis créé",
        ),
        make_event(
            event_id="event-3",
            event_type="APPLICATION_CREATED",
            message="Dossier créé",
        ),
    ]

    event_repository.find_all.return_value = (
        events,
        3,
    )

    result = use_case.execute(
        page=1,
        limit=10,
    )

    assert len(result.items) == 3

    assert result.items[0].id == "event-1"
    assert result.items[0].type == "LEAD_CREATED"

    assert result.items[1].id == "event-2"
    assert result.items[1].type == "QUOTE_CREATED"

    assert result.items[2].id == "event-3"
    assert result.items[2].type == "APPLICATION_CREATED"


def test_empty_event_list_returns_empty_items(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        0,
    )

    result = use_case.execute(
        page=1,
        limit=10,
    )

    assert result.items == []
    assert result.total == 0


# ============================================================
# PAGINATION
# ============================================================


@pytest.mark.parametrize(
    "total,limit,expected_total_pages",
    [
        (0, 10, 0),
        (1, 10, 1),
        (10, 10, 1),
        (11, 10, 2),
        (20, 10, 2),
        (21, 10, 3),
        (25, 10, 3),
        (99, 20, 5),
    ],
)
def test_total_pages_are_calculated_correctly(
    total,
    limit,
    expected_total_pages,
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        total,
    )

    result = use_case.execute(
        page=1,
        limit=limit,
    )

    assert result.total_pages == expected_total_pages


def test_pagination_information_is_returned(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        25,
    )

    result = use_case.execute(
        page=2,
        limit=10,
    )

    assert result.total == 25
    assert result.page == 2
    assert result.limit == 10
    assert result.total_pages == 3


# ============================================================
# HAS NEXT
# ============================================================


@pytest.mark.parametrize(
    "page,total,limit,expected",
    [
        (1, 25, 10, True),
        (2, 25, 10, True),
        (3, 25, 10, False),
        (1, 10, 10, False),
        (1, 0, 10, False),
    ],
)
def test_has_next_is_calculated_correctly(
    page,
    total,
    limit,
    expected,
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        total,
    )

    result = use_case.execute(
        page=page,
        limit=limit,
    )

    assert result.has_next is expected


# ============================================================
# HAS PREVIOUS
# ============================================================


@pytest.mark.parametrize(
    "page,expected",
    [
        (1, False),
        (2, True),
        (3, True),
        (10, True),
    ],
)
def test_has_previous_is_calculated_correctly(
    page,
    expected,
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        100,
    )

    result = use_case.execute(
        page=page,
        limit=10,
    )

    assert result.has_previous is expected


# ============================================================
# COMPLETE PAGINATION EXAMPLES
# ============================================================


def test_first_page_has_next_but_no_previous(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        25,
    )

    result = use_case.execute(
        page=1,
        limit=10,
    )

    assert result.total_pages == 3
    assert result.has_next is True
    assert result.has_previous is False


def test_middle_page_has_next_and_previous(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        25,
    )

    result = use_case.execute(
        page=2,
        limit=10,
    )

    assert result.total_pages == 3
    assert result.has_next is True
    assert result.has_previous is True


def test_last_page_has_no_next_but_has_previous(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        25,
    )

    result = use_case.execute(
        page=3,
        limit=10,
    )

    assert result.total_pages == 3
    assert result.has_next is False
    assert result.has_previous is True


# ============================================================
# FILTERS
# ============================================================


def test_search_filter_is_forwarded(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        0,
    )

    use_case.execute(
        page=1,
        limit=10,
        search="paiement",
    )

    event_repository.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search="paiement",
        event_type=None,
        date=None,
    )


def test_event_type_filter_is_forwarded(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        0,
    )

    use_case.execute(
        page=1,
        limit=10,
        event_type="PAYMENT_COMPLETED",
    )

    event_repository.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search=None,
        event_type="PAYMENT_COMPLETED",
        date=None,
    )


def test_date_filter_is_forwarded(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        0,
    )

    use_case.execute(
        page=1,
        limit=10,
        date="2026-03-15",
    )

    event_repository.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search=None,
        event_type=None,
        date="2026-03-15",
    )


def test_all_filters_can_be_combined(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        0,
    )

    use_case.execute(
        page=3,
        limit=20,
        search="client",
        event_type="LEAD_CREATED",
        date="2026-03-15",
    )

    event_repository.find_all.assert_called_once_with(
        page=3,
        limit=20,
        search="client",
        event_type="LEAD_CREATED",
        date="2026-03-15",
    )


# ============================================================
# REPOSITORY RESULT IS PRESERVED
# ============================================================


def test_total_from_repository_is_preserved(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        42,
    )

    result = use_case.execute(
        page=2,
        limit=10,
    )

    assert result.total == 42


def test_page_and_limit_are_preserved(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        50,
    )

    result = use_case.execute(
        page=4,
        limit=15,
    )

    assert result.page == 4
    assert result.limit == 15
