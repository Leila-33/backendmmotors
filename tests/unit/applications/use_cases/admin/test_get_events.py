from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from core.pagination.paginated_result import PaginatedResult
from modules.applications.domain.entities.event import Event
from modules.applications.domain.enums import EventCategory, EventType
from modules.applications.application.use_cases.admin.get_events import (
    GetEventsUseCase,
)


# ============================================================
# HELPERS
# ============================================================


def make_event(
    *,
    event_id: str = "event-1",
    event_type: EventType = EventType.APPLICATION_CREATED,
    message: str = "Événement de test",
    event_metadata: dict | None = None,
    application_id: str | None = "application-1",
    test_drive_id: str | None = None,
    user_id: str | None = "user-1",
    vehicle_id: str | None = "vehicle-1",
    quote_id: str | None = None,
    lead_id: str | None = None,
):
    return Event(
        id=event_id,
        type=event_type,
        message=message,
        event_metadata=event_metadata,
        created_at=datetime.now(timezone.utc),
        application_id=application_id,
        test_drive_id=test_drive_id,
        user_id=user_id,
        vehicle_id=vehicle_id,
        quote_id=quote_id,
        lead_id=lead_id,
    )


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
# BASIC RETRIEVAL
# ============================================================


def test_get_events_returns_paginated_result(
    use_case,
    event_repository,
):
    events = [
        make_event(event_id="event-1"),
        make_event(event_id="event-2"),
    ]

    event_repository.find_all.return_value = (
        events,
        2,
    )

    result = use_case.execute(
        page=1,
        limit=10,
    )

    assert isinstance(
        result,
        PaginatedResult,
    )

    assert result.items == events
    assert result.total == 2
    assert result.page == 1
    assert result.limit == 10


def test_get_events_calls_repository_with_pagination(
    use_case,
    event_repository,
):
    event_repository.find_all.return_value = (
        [],
        0,
    )

    use_case.execute(
        page=2,
        limit=20,
    )

    event_repository.find_all.assert_called_once_with(
        page=2,
        limit=20,
        search=None,
        event_category=None,
        date=None,
    )


# ============================================================
# SEARCH
# ============================================================


def test_get_events_with_search(
    use_case,
    event_repository,
):
    events = [
        make_event(
            event_id="event-1",
            message="Dossier créé",
        )
    ]

    event_repository.find_all.return_value = (
        events,
        1,
    )

    result = use_case.execute(
        page=1,
        limit=10,
        search="Dossier",
    )

    event_repository.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search="Dossier",
        event_category=None,
        date=None,
    )

    assert result.items == events
    assert result.total == 1


# ============================================================
# EVENT CATEGORY
# ============================================================


def test_get_events_with_event_category(
    use_case,
    event_repository,
):
    event_category = EventCategory.APPLICATION

    events = [
        make_event(
            event_id="event-1",
        )
    ]

    event_repository.find_all.return_value = (
        events,
        1,
    )

    result = use_case.execute(
        page=1,
        limit=10,
        event_category=event_category,
    )

    event_repository.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search=None,
        event_category=event_category,
        date=None,
    )

    assert result.items == events
    assert result.total == 1


# ============================================================
# DATE
# ============================================================


def test_get_events_with_date(
    use_case,
    event_repository,
):
    events = [
        make_event(
            event_id="event-1",
        )
    ]

    event_repository.find_all.return_value = (
        events,
        1,
    )

    result = use_case.execute(
        page=1,
        limit=10,
        date="2026-09-27",
    )

    event_repository.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search=None,
        event_category=None,
        date="2026-09-27",
    )

    assert result.items == events
    assert result.total == 1


# ============================================================
# ALL FILTERS
# ============================================================


def test_get_events_with_all_filters(
    use_case,
    event_repository,
):
    event_category = EventCategory.APPLICATION

    events = [
        make_event(
            event_id="event-1",
            message="Application créée",
        )
    ]

    event_repository.find_all.return_value = (
        events,
        1,
    )

    result = use_case.execute(
        page=2,
        limit=5,
        search="Application",
        event_category=event_category,
        date="2026-09-27",
    )

    event_repository.find_all.assert_called_once_with(
        page=2,
        limit=5,
        search="Application",
        event_category=event_category,
        date="2026-09-27",
    )

    assert result.items == events
    assert result.total == 1
    assert result.page == 2
    assert result.limit == 5


# ============================================================
# EMPTY RESULT
# ============================================================


def test_get_events_returns_empty_result(
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

    assert isinstance(
        result,
        PaginatedResult,
    )

    assert result.items == []
    assert result.total == 0
    assert result.page == 1
    assert result.limit == 10


# ============================================================
# MULTIPLE EVENTS
# ============================================================


def test_get_events_preserves_event_order(
    use_case,
    event_repository,
):
    event_1 = make_event(
        event_id="event-1",
        message="Premier événement",
    )

    event_2 = make_event(
        event_id="event-2",
        message="Deuxième événement",
    )

    event_3 = make_event(
        event_id="event-3",
        message="Troisième événement",
    )

    event_repository.find_all.return_value = (
        [event_1, event_2, event_3],
        3,
    )

    result = use_case.execute(
        page=1,
        limit=10,
    )

    assert result.items == [
        event_1,
        event_2,
        event_3,
    ]


# ============================================================
# REPOSITORY ERROR
# ============================================================


def test_get_events_propagates_repository_error(
    use_case,
    event_repository,
):
    event_repository.find_all.side_effect = RuntimeError(
        "repository error"
    )

    with pytest.raises(
        RuntimeError,
        match="repository error",
    ):
        use_case.execute(
            page=1,
            limit=10,
        )

    event_repository.find_all.assert_called_once_with(
        page=1,
        limit=10,
        search=None,
        event_category=None,
        date=None,
    )