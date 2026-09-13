from datetime import date, timedelta
from unittest.mock import Mock, call, patch
from datetime import datetime

import pytest

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.reservations.domain.enums import ReservationStatus
from modules.reservations.application.use_cases.complete_expired_rentals import (
    CompleteExpiredRentalsUseCase,
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
    return CompleteExpiredRentalsUseCase(
        reservation_repository=reservation_repository,
        application_repository=application_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


def make_reservation(
    reservation_id="reservation-123",
    application_id="application-123",
    vehicle_id="vehicle-123",
):
    reservation = Mock()
    reservation.id = reservation_id
    reservation.application_id = application_id
    reservation.vehicle_id = vehicle_id
    reservation.status = ReservationStatus.ACTIVE
    return reservation


def make_application(
    application_id="application-123",
    user_id="user-123",
    status=ApplicationStatus.APPROVED,
):
    application = Mock()
    application.id = application_id
    application.user_id = user_id
    application.status = status
    return application


def test_execute_returns_zero_when_no_expired_rentals(
    use_case,
    reservation_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    reservation_repository.find_expired_active.return_value = []

    result = use_case.execute()

    assert result == 0

    reservation_repository.find_expired_active.assert_called_once()
    application_repository.get_by_id.assert_not_called()
    reservation_repository.update.assert_not_called()
    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_execute_completes_expired_rental(
    use_case,
    reservation_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    reservation = make_reservation()
    application = make_application()

    reservation_repository.find_expired_active.return_value = [
        reservation
    ]
    application_repository.get_by_id.return_value = application

    result = use_case.execute()

    assert result == 1
    assert reservation.status == ReservationStatus.COMPLETED
    assert application.status == ApplicationStatus.COMPLETED

    reservation_repository.update.assert_called_once_with(
        reservation
    )

    application_repository.get_by_id.assert_called_once_with(
        "application-123"
    )

    application_repository.update.assert_called_once_with(
        application
    )

    event_service.log.assert_called_once_with(
        application_id="application-123",
        user_id="user-123",
        vehicle_id="vehicle-123",
        type=EventType.RENTAL_COMPLETED,
        message="Location terminée automatiquement.",
        event_metadata={
            "reservation_id": "reservation-123",
            "completed_by": "SYSTEM",
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_execute_does_not_update_application_already_completed(
    use_case,
    reservation_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    reservation = make_reservation()

    application = make_application(
        status=ApplicationStatus.COMPLETED
    )

    reservation_repository.find_expired_active.return_value = [
        reservation
    ]
    application_repository.get_by_id.return_value = application

    result = use_case.execute()

    assert result == 1

    assert reservation.status == ReservationStatus.COMPLETED
    assert application.status == ApplicationStatus.COMPLETED

    reservation_repository.update.assert_called_once_with(
        reservation
    )

    application_repository.update.assert_not_called()

    event_service.log.assert_called_once_with(
        application_id="application-123",
        user_id="user-123",
        vehicle_id="vehicle-123",
        type=EventType.RENTAL_COMPLETED,
        message="Location terminée automatiquement.",
        event_metadata={
            "reservation_id": "reservation-123",
            "completed_by": "SYSTEM",
        },
    )

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_execute_skips_reservation_when_application_does_not_exist(
    use_case,
    reservation_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    reservation = make_reservation()

    reservation_repository.find_expired_active.return_value = [
        reservation
    ]
    application_repository.get_by_id.return_value = None

    result = use_case.execute()

    assert result == 0

    # La réservation est quand même complétée
    assert reservation.status == ReservationStatus.COMPLETED

    reservation_repository.update.assert_called_once_with(
        reservation
    )

    application_repository.get_by_id.assert_called_once_with(
        "application-123"
    )

    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()


def test_execute_completes_multiple_expired_rentals(
    use_case,
    reservation_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    reservation_1 = make_reservation(
        reservation_id="reservation-1",
        application_id="application-1",
        vehicle_id="vehicle-1",
    )

    reservation_2 = make_reservation(
        reservation_id="reservation-2",
        application_id="application-2",
        vehicle_id="vehicle-2",
    )

    application_1 = make_application(
        application_id="application-1",
        user_id="user-1",
    )

    application_2 = make_application(
        application_id="application-2",
        user_id="user-2",
    )

    reservation_repository.find_expired_active.return_value = [
        reservation_1,
        reservation_2,
    ]

    application_repository.get_by_id.side_effect = [
        application_1,
        application_2,
    ]

    result = use_case.execute()

    assert result == 2

    assert reservation_1.status == ReservationStatus.COMPLETED
    assert reservation_2.status == ReservationStatus.COMPLETED

    assert application_1.status == ApplicationStatus.COMPLETED
    assert application_2.status == ApplicationStatus.COMPLETED

    assert reservation_repository.update.call_args_list == [
        call(reservation_1),
        call(reservation_2),
    ]

    assert application_repository.get_by_id.call_args_list == [
        call("application-1"),
        call("application-2"),
    ]

    assert application_repository.update.call_args_list == [
        call(application_1),
        call(application_2),
    ]

    assert event_service.log.call_count == 2

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()




def test_execute_passes_current_utc_datetime_to_repository(
    use_case,
    reservation_repository,
):
    reservation_repository.find_expired_active.return_value = []

    use_case.execute()

    reservation_repository.find_expired_active.assert_called_once()

    now = reservation_repository.find_expired_active.call_args.args[0]

    assert isinstance(now, datetime)
    assert now.tzinfo is not None
    assert now.utcoffset().total_seconds() == 0



def test_execute_rolls_back_when_reservation_update_fails(
    use_case,
    reservation_repository,
    unit_of_work,
):
    reservation = make_reservation()

    reservation_repository.find_expired_active.return_value = [
        reservation
    ]

    reservation_repository.update.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute()

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_execute_rolls_back_when_application_update_fails(
    use_case,
    reservation_repository,
    application_repository,
    unit_of_work,
):
    reservation = make_reservation()
    application = make_application()

    reservation_repository.find_expired_active.return_value = [
        reservation
    ]
    application_repository.get_by_id.return_value = application

    application_repository.update.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute()

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_execute_rolls_back_when_event_logging_fails(
    use_case,
    reservation_repository,
    application_repository,
    event_service,
    unit_of_work,
):
    reservation = make_reservation()
    application = make_application()

    reservation_repository.find_expired_active.return_value = [
        reservation
    ]
    application_repository.get_by_id.return_value = application

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(RuntimeError, match="Event error"):
        use_case.execute()

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()


def test_execute_rolls_back_when_commit_fails(
    use_case,
    reservation_repository,
    application_repository,
    unit_of_work,
):
    reservation = make_reservation()
    application = make_application()

    reservation_repository.find_expired_active.return_value = [
        reservation
    ]
    application_repository.get_by_id.return_value = application

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(RuntimeError, match="Commit error"):
        use_case.execute()

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()