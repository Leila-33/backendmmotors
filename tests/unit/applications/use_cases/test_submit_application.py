import pytest
from unittest.mock import Mock

from modules.applications.application.use_cases.submit_application import (
    SubmitApplicationUseCase,
)
from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.reservations.domain.enums import (
    ReservationStatus,
)


@pytest.fixture
def application_form_service():
    return Mock()


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def reservation_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def uow():
    return Mock()


@pytest.fixture
def use_case(
    application_form_service,
    application_repository,
    reservation_repository,
    event_service,
    uow,
):
    return SubmitApplicationUseCase(
        application_form_service=application_form_service,
        application_repository=application_repository,
        reservation_repository=reservation_repository,
        event_service=event_service,
        uow=uow,
    )


@pytest.fixture
def dto():
    return Mock()


@pytest.fixture
def application():
    application = Mock()

    application.id = "app-123"
    application.user_id = "user-123"
    application.vehicle_id = "vehicle-123"

    application.status = ApplicationStatus.DRAFT
    application.previous_status = None

    application.is_archived = False
    application.deleted_at = None
    application.reservation = None

    return application


@pytest.fixture
def save_result(application):
    result = Mock()
    result.application = application
    return result


def test_submits_application_successfully(
    use_case,
    application_form_service,
    application_repository,
    reservation_repository,
    event_service,
    uow,
    dto,
    application,
    save_result,
):
    application_form_service.save.return_value = save_result

    result = use_case.execute(
        dto=dto,
        current_user_id="user-123",
    )

    assert result is application

    assert application.previous_status == ApplicationStatus.DRAFT
    assert application.status == ApplicationStatus.SUBMITTED

    application_repository.update.assert_called_once_with(
        application
    )

    reservation_repository.update.assert_not_called()

    event_service.log.assert_called_once_with(
        application_id="app-123",
        user_id="user-123",
        vehicle_id="vehicle-123",
        type=EventType.APPLICATION_SUBMITTED,
        message="Dossier soumis.",
    )

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_passes_dto_and_user_id_to_application_form_service(
    use_case,
    application_form_service,
    dto,
    application,
    save_result,
):
    application_form_service.save.return_value = save_result

    use_case.execute(
        dto=dto,
        current_user_id="user-123",
    )

    application_form_service.save.assert_called_once_with(
        dto=dto,
        current_user_id="user-123",
    )


def test_preserves_previous_application_status(
    use_case,
    application_form_service,
    application_repository,
    dto,
    application,
    save_result,
):
    application.status = ApplicationStatus.DRAFT
    application_form_service.save.return_value = save_result

    use_case.execute(
        dto=dto,
        current_user_id="user-123",
    )

    assert application.previous_status == ApplicationStatus.DRAFT
    assert application.status == ApplicationStatus.SUBMITTED


def test_sets_submitted_status(
    use_case,
    application_form_service,
    dto,
    application,
    save_result,
):
    application_form_service.save.return_value = save_result

    use_case.execute(
        dto=dto,
        current_user_id="user-123",
    )

    assert application.status == ApplicationStatus.SUBMITTED


def test_updates_application(
    use_case,
    application_form_service,
    application_repository,
    dto,
    application,
    save_result,
):
    application_form_service.save.return_value = save_result

    use_case.execute(
        dto=dto,
        current_user_id="user-123",
    )

    application_repository.update.assert_called_once_with(
        application
    )


def test_does_not_update_reservation_when_application_has_no_reservation(
    use_case,
    application_form_service,
    reservation_repository,
    dto,
    application,
    save_result,
):
    application.reservation = None
    application_form_service.save.return_value = save_result

    use_case.execute(
        dto=dto,
        current_user_id="user-123",
    )

    reservation_repository.update.assert_not_called()


def test_sets_reservation_to_pending_when_application_has_reservation(
    use_case,
    application_form_service,
    reservation_repository,
    dto,
    application,
    save_result,
):
    reservation = Mock()

    application.reservation = reservation
    application_form_service.save.return_value = save_result

    use_case.execute(
        dto=dto,
        current_user_id="user-123",
    )

    assert reservation.status == ReservationStatus.PENDING

    reservation_repository.update.assert_called_once_with(
        reservation
    )


def test_logs_application_submitted_event(
    use_case,
    application_form_service,
    event_service,
    dto,
    application,
    save_result,
):
    application_form_service.save.return_value = save_result

    use_case.execute(
        dto=dto,
        current_user_id="user-123",
    )

    event_service.log.assert_called_once_with(
        application_id=application.id,
        user_id="user-123",
        vehicle_id=application.vehicle_id,
        type=EventType.APPLICATION_SUBMITTED,
        message="Dossier soumis.",
    )


def test_commits_after_successful_submission(
    use_case,
    application_form_service,
    uow,
    dto,
    application,
    save_result,
):
    application_form_service.save.return_value = save_result

    use_case.execute(
        dto=dto,
        current_user_id="user-123",
    )

    uow.commit.assert_called_once()
    uow.rollback.assert_not_called()


def test_rolls_back_when_application_form_save_fails(
    use_case,
    application_form_service,
    application_repository,
    reservation_repository,
    event_service,
    uow,
    dto,
):
    error = RuntimeError("save error")
    application_form_service.save.side_effect = error

    with pytest.raises(RuntimeError, match="save error"):
        use_case.execute(
            dto=dto,
            current_user_id="user-123",
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()

    application_repository.update.assert_not_called()
    reservation_repository.update.assert_not_called()
    event_service.log.assert_not_called()


def test_rolls_back_when_policy_validation_fails(
    use_case,
    application_form_service,
    application_repository,
    reservation_repository,
    event_service,
    uow,
    dto,
    application,
    save_result,
    monkeypatch,
):
    application_form_service.save.return_value = save_result

    error = RuntimeError("invalid application")

    from modules.applications.application.use_cases import (
        submit_application,
    )

    monkeypatch.setattr(
        submit_application.SubmitApplicationPolicy,
        "validate",
        Mock(side_effect=error),
    )

    with pytest.raises(RuntimeError, match="invalid application"):
        use_case.execute(
            dto=dto,
            current_user_id="user-123",
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()

    application_repository.update.assert_not_called()
    reservation_repository.update.assert_not_called()
    event_service.log.assert_not_called()


def test_rolls_back_when_application_update_fails(
    use_case,
    application_form_service,
    application_repository,
    reservation_repository,
    event_service,
    uow,
    dto,
    application,
    save_result,
):
    application_form_service.save.return_value = save_result

    error = RuntimeError("update error")
    application_repository.update.side_effect = error

    with pytest.raises(RuntimeError, match="update error"):
        use_case.execute(
            dto=dto,
            current_user_id="user-123",
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()

    reservation_repository.update.assert_not_called()
    event_service.log.assert_not_called()


def test_rolls_back_when_reservation_update_fails(
    use_case,
    application_form_service,
    reservation_repository,
    event_service,
    uow,
    dto,
    application,
    save_result,
):
    reservation = Mock()
    application.reservation = reservation

    application_form_service.save.return_value = save_result

    error = RuntimeError("reservation update error")
    reservation_repository.update.side_effect = error

    with pytest.raises(
        RuntimeError,
        match="reservation update error",
    ):
        use_case.execute(
            dto=dto,
            current_user_id="user-123",
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()

    event_service.log.assert_not_called()


def test_rolls_back_when_event_logging_fails(
    use_case,
    application_form_service,
    event_service,
    uow,
    dto,
    application,
    save_result,
):
    application_form_service.save.return_value = save_result

    error = RuntimeError("event error")
    event_service.log.side_effect = error

    with pytest.raises(RuntimeError, match="event error"):
        use_case.execute(
            dto=dto,
            current_user_id="user-123",
        )

    uow.rollback.assert_called_once()
    uow.commit.assert_not_called()


def test_rolls_back_when_commit_fails(
    use_case,
    application_form_service,
    event_service,
    uow,
    dto,
    application,
    save_result,
):
    application_form_service.save.return_value = save_result

    error = RuntimeError("commit error")
    uow.commit.side_effect = error

    with pytest.raises(RuntimeError, match="commit error"):
        use_case.execute(
            dto=dto,
            current_user_id="user-123",
        )

    uow.rollback.assert_called_once()


def test_reservation_is_updated_before_event_is_logged(
    use_case,
    application_form_service,
    application_repository,
    reservation_repository,
    event_service,
    dto,
    application,
    save_result,
):
    reservation = Mock()
    application.reservation = reservation

    application_form_service.save.return_value = save_result

    call_order = []

    application_repository.update.side_effect = (
        lambda *_: call_order.append("application_update")
    )

    reservation_repository.update.side_effect = (
        lambda *_: call_order.append("reservation_update")
    )

    event_service.log.side_effect = (
        lambda **_: call_order.append("event")
    )

    use_case.execute(
        dto=dto,
        current_user_id="user-123",
    )

    assert call_order == [
        "application_update",
        "reservation_update",
        "event",
    ]