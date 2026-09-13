from unittest.mock import Mock

import pytest

from modules.applications.application.services.event_service import EventService
from modules.applications.domain.enums import EventType


@pytest.fixture
def event_repository():
    return Mock()


@pytest.fixture
def service(event_repository):
    return EventService(
        event_repository=event_repository,
    )


def test_log_creates_and_saves_event(
    service,
    event_repository,
):
    event = Mock()
    event_repository.save.return_value = event

    result = service.log(
        type=EventType.APPLICATION_CREATED,
        message="Dossier créé.",
        user_id="user-123",
        application_id="app-456",
        test_drive_id="test-drive-789",
        vehicle_id="vehicle-111",
        quote_id="quote-222",
        lead_id="lead-333",
        event_metadata={"source": "web"},
    )

    event_repository.save.assert_called_once()

    saved_event = event_repository.save.call_args.args[0]

    assert saved_event.type == EventType.APPLICATION_CREATED
    assert saved_event.message == "Dossier créé."

    assert saved_event.user_id == "user-123"
    assert saved_event.application_id == "app-456"
    assert saved_event.test_drive_id == "test-drive-789"
    assert saved_event.vehicle_id == "vehicle-111"
    assert saved_event.quote_id == "quote-222"
    assert saved_event.lead_id == "lead-333"

    assert saved_event.event_metadata == {
        "source": "web"
    }

    assert saved_event.id is not None

    assert result is event


def test_log_allows_optional_fields_to_be_none(
    service,
    event_repository,
):
    event_repository.save.side_effect = lambda event: event

    result = service.log(
        type=EventType.APPLICATION_CREATED,
        message="Dossier créé.",
    )

    saved_event = event_repository.save.call_args.args[0]

    assert saved_event.type == EventType.APPLICATION_CREATED
    assert saved_event.message == "Dossier créé."

    assert saved_event.user_id is None
    assert saved_event.application_id is None
    assert saved_event.test_drive_id is None
    assert saved_event.vehicle_id is None
    assert saved_event.quote_id is None
    assert saved_event.lead_id is None
    assert saved_event.event_metadata is None

    assert result is saved_event


def test_log_generates_unique_event_ids(
    service,
    event_repository,
):
    event_repository.save.side_effect = lambda event: event

    first_event = service.log(
        type=EventType.APPLICATION_CREATED,
        message="Premier événement",
    )

    second_event = service.log(
        type=EventType.APPLICATION_CREATED,
        message="Deuxième événement",
    )

    assert first_event.id is not None
    assert second_event.id is not None
    assert first_event.id != second_event.id


def test_log_returns_repository_result(
    service,
    event_repository,
):
    saved_event = Mock()
    event_repository.save.return_value = saved_event

    result = service.log(
        type=EventType.APPLICATION_CREATED,
        message="Dossier créé.",
    )

    assert result is saved_event


def test_log_propagates_repository_exception(
    service,
    event_repository,
):
    error = RuntimeError("Erreur de sauvegarde")
    event_repository.save.side_effect = error

    with pytest.raises(RuntimeError, match="Erreur de sauvegarde"):
        service.log(
            type=EventType.APPLICATION_CREATED,
            message="Dossier créé.",
        )

    event_repository.save.assert_called_once()