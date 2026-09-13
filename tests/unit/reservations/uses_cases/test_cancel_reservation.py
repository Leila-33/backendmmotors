from datetime import date, timedelta
from unittest.mock import Mock

import pytest

from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.auth.domain.enums import UserRole
from modules.reservations.domain.enums import ReservationStatus
from modules.reservations.domain.exceptions import (
    CannotCancelReservation,
    ReservationAlreadyCancelled,
    ReservationAlreadyStarted,
    ReservationNotFound,
)
from modules.reservations.application.use_cases.cancel_reservation import (
    CancelReservationUseCase,
)


@pytest.fixture
def reservation_repository():
    return Mock()


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    reservation_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    return CancelReservationUseCase(
        reservation_repository=reservation_repository,
        application_repository=application_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def reservation():
    reservation = Mock()

    reservation.id = "reservation-123"
    reservation.application_id = "application-123"
    reservation.vehicle_id = "vehicle-123"
    reservation.status = ReservationStatus.ACTIVE
    reservation.start_date = date.today() + timedelta(days=5)
    reservation.updated_at = None

    return reservation


@pytest.fixture
def application():
    application = Mock()
    application.id = "application-123"
    application.user_id = "user-123"

    return application


def get_non_admin_role():
    return next(
        role for role in UserRole
        if role != UserRole.ADMIN
    )


def configure_repositories(
    reservation_repository,
    application_repository,
    reservation,
    application,
):
    reservation_repository.get_by_id.return_value = reservation
    application_repository.get_by_id.return_value = application


def test_execute_raises_when_reservation_does_not_exist(
    use_case,
    reservation_repository,
    unit_of_work,
):
    reservation_repository.get_by_id.return_value = None

    with pytest.raises(ReservationNotFound):
        use_case.execute(
            reservation_id="reservation-123",
            user_id="user-123",
            role=UserRole.ADMIN,
        )

    unit_of_work.rollback.assert_called_once()


def test_execute_raises_when_application_does_not_exist(
    use_case,
    reservation_repository,
    application_repository,
    reservation,
    unit_of_work,
):
    reservation_repository.get_by_id.return_value = reservation
    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        use_case.execute(
            reservation_id="reservation-123",
            user_id="user-123",
            role=UserRole.ADMIN,
        )

    unit_of_work.rollback.assert_called_once()


def test_execute_rejects_non_owner(
    use_case,
    reservation_repository,
    application_repository,
    reservation,
    application,
    unit_of_work,
):
    configure_repositories(
        reservation_repository,
        application_repository,
        reservation,
        application,
    )

    with pytest.raises(CannotCancelReservation):
        use_case.execute(
            reservation_id="reservation-123",
            user_id="other-user",
            role=get_non_admin_role(),
        )

    unit_of_work.rollback.assert_called_once()


def test_execute_rejects_already_cancelled_reservation(
    use_case,
    reservation_repository,
    application_repository,
    reservation,
    application,
    unit_of_work,
):
    reservation.status = ReservationStatus.CANCELLED

    configure_repositories(
        reservation_repository,
        application_repository,
        reservation,
        application,
    )

    with pytest.raises(ReservationAlreadyCancelled):
        use_case.execute(
            reservation_id="reservation-123",
            user_id="user-123",
            role=get_non_admin_role(),
        )

    unit_of_work.rollback.assert_called_once()


def test_execute_rejects_completed_reservation(
    use_case,
    reservation_repository,
    application_repository,
    reservation,
    application,
    unit_of_work,
):
    reservation.status = ReservationStatus.COMPLETED

    configure_repositories(
        reservation_repository,
        application_repository,
        reservation,
        application,
    )

    with pytest.raises(CannotCancelReservation):
        use_case.execute(
            reservation_id="reservation-123",
            user_id="user-123",
            role=get_non_admin_role(),
        )

    unit_of_work.rollback.assert_called_once()


def test_execute_rejects_invalid_status_for_non_admin(
    use_case,
    reservation_repository,
    application_repository,
    reservation,
    application,
    unit_of_work,
):
    # ACTIVE is allowed, so use a status outside the allowed list.
    reservation.status = ReservationStatus.COMPLETED

    configure_repositories(
        reservation_repository,
        application_repository,
        reservation,
        application,
    )

    with pytest.raises(CannotCancelReservation):
        use_case.execute(
            reservation_id="reservation-123",
            user_id="user-123",
            role=get_non_admin_role(),
        )

    unit_of_work.rollback.assert_called_once()


def test_execute_rejects_reservation_already_started(
    use_case,
    reservation_repository,
    application_repository,
    reservation,
    application,
    unit_of_work,
):
    reservation.start_date = date.today()

    configure_repositories(
        reservation_repository,
        application_repository,
        reservation,
        application,
    )

    with pytest.raises(ReservationAlreadyStarted):
        use_case.execute(
            reservation_id="reservation-123",
            user_id="user-123",
            role=get_non_admin_role(),
        )

    unit_of_work.rollback.assert_called_once()


def test_execute_cancels_reservation_successfully(
    use_case,
    reservation_repository,
    application_repository,
    event_service,
    unit_of_work,
    reservation,
    application,
):
    configure_repositories(
        reservation_repository,
        application_repository,
        reservation,
        application,
    )

    result = use_case.execute(
        reservation_id="reservation-123",
        user_id="user-123",
        role=get_non_admin_role(),
    )

    assert result is reservation
    assert reservation.status == ReservationStatus.CANCELLED
    assert reservation.updated_at is not None
    assert reservation.updated_at.tzinfo is not None

    reservation_repository.update.assert_called_once_with(
        reservation
    )

    event_service.log.assert_called_once_with(
        application_id="application-123",
        user_id="user-123",
        vehicle_id="vehicle-123",
        type=EventType.RENTAL_CANCELLED,
        message="Réservation annulée avec succès.",
        event_metadata={
            "reservation_id": "reservation-123",
            "vehicle_id": "vehicle-123",
            "role": get_non_admin_role().value,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_execute_allows_admin_to_cancel_reservation(
    use_case,
    reservation_repository,
    application_repository,
    event_service,
    unit_of_work,
    reservation,
    application,
):
    configure_repositories(
        reservation_repository,
        application_repository,
        reservation,
        application,
    )

    result = use_case.execute(
        reservation_id="reservation-123",
        user_id="admin-123",
        role=UserRole.ADMIN,
    )

    assert result is reservation
    assert reservation.status == ReservationStatus.CANCELLED

    reservation_repository.update.assert_called_once_with(
        reservation
    )

    event_service.log.assert_called_once_with(
        application_id="application-123",
        user_id="admin-123",
        vehicle_id="vehicle-123",
        type=EventType.RENTAL_CANCELLED,
        message="Réservation annulée avec succès.",
        event_metadata={
            "reservation_id": "reservation-123",
            "vehicle_id": "vehicle-123",
            "role": UserRole.ADMIN.value,
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_execute_rolls_back_when_update_fails(
    use_case,
    reservation_repository,
    application_repository,
    unit_of_work,
    reservation,
    application,
):
    configure_repositories(
        reservation_repository,
        application_repository,
        reservation,
        application,
    )

    reservation_repository.update.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(
            reservation_id="reservation-123",
            user_id="user-123",
            role=get_non_admin_role(),
        )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_execute_rolls_back_when_event_logging_fails(
    use_case,
    reservation_repository,
    application_repository,
    event_service,
    unit_of_work,
    reservation,
    application,
):
    configure_repositories(
        reservation_repository,
        application_repository,
        reservation,
        application,
    )

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(RuntimeError, match="Event error"):
        use_case.execute(
            reservation_id="reservation-123",
            user_id="user-123",
            role=get_non_admin_role(),
        )

    reservation_repository.update.assert_called_once_with(
        reservation
    )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    reservation_repository,
    application_repository,
    unit_of_work,
    reservation,
    application,
):
    configure_repositories(
        reservation_repository,
        application_repository,
        reservation,
        application,
    )

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(RuntimeError, match="Commit error"):
        use_case.execute(
            reservation_id="reservation-123",
            user_id="user-123",
            role=get_non_admin_role(),
        )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()