from unittest.mock import Mock, patch

import pytest
from datetime import date
from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.reservations.domain.enums import ReservationStatus
from modules.vehicles.domain.exceptions import VehicleNotAvailable
from modules.reservations.application.dtos.create_reservation_dto import (
    CreateReservationDTO,
)
from modules.reservations.application.use_cases.create_reservation import (
    CreateReservationUseCase,
)


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
def unit_of_work():
    return Mock()


@pytest.fixture
def use_case(
    application_repository,
    reservation_repository,
    event_service,
    unit_of_work,
):
    return CreateReservationUseCase(
        application_repository=application_repository,
        reservation_repository=reservation_repository,
        event_service=event_service,
        unit_of_work=unit_of_work,
    )


@pytest.fixture
def dto():
    return CreateReservationDTO(
        application_id="application-123",
        start_date=date(2026, 10, 10),
        end_date=date(2026, 10, 15),
    )


@pytest.fixture
def application():
    application = Mock()
    application.id = "application-123"
    application.user_id = "user-123"
    application.vehicle_id = "vehicle-123"
    return application

def test_execute_raises_application_not_found(
    use_case,
    application_repository,
    unit_of_work,
    dto,
):
    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        use_case.execute(dto)

    application_repository.get_by_id.assert_called_once_with(
        "application-123"
    )

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()

def test_execute_raises_vehicle_not_available_when_overlap_exists(
    use_case,
    application_repository,
    reservation_repository,
    unit_of_work,
    dto,
    application,
):
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = True

    with pytest.raises(VehicleNotAvailable):
        use_case.execute(dto)

    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id="vehicle-123",
        start_date=dto.start_date,
        end_date=dto.end_date,
    )

    reservation_repository.create.assert_not_called()
    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()

def test_execute_creates_reservation_successfully(
    use_case,
    application_repository,
    reservation_repository,
    event_service,
    unit_of_work,
    dto,
    application,
):
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = False

    created_reservation = Mock()
    created_reservation.id = "reservation-123"
    created_reservation.vehicle_id = "vehicle-123"
    created_reservation.start_date = dto.start_date
    created_reservation.end_date = dto.end_date
    created_reservation.status = ReservationStatus.ACTIVE

    reservation_repository.create.return_value = (
        created_reservation
    )

    result = use_case.execute(dto)

    assert result is created_reservation

    reservation_repository.create.assert_called_once()

    reservation = reservation_repository.create.call_args.args[0]

    assert reservation.application_id == "application-123"
    assert reservation.vehicle_id == "vehicle-123"
    assert reservation.start_date == dto.start_date
    assert reservation.end_date == dto.end_date
    assert reservation.status == ReservationStatus.ACTIVE

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_not_called()

def test_execute_logs_rental_created_event(
    use_case,
    application_repository,
    reservation_repository,
    event_service,
    unit_of_work,
    dto,
    application,
):
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = False

    created_reservation = Mock()
    created_reservation.id = "reservation-123"
    created_reservation.vehicle_id = "vehicle-123"
    created_reservation.start_date = dto.start_date
    created_reservation.end_date = dto.end_date
    created_reservation.status = ReservationStatus.ACTIVE

    reservation_repository.create.return_value = (
        created_reservation
    )

    use_case.execute(dto)

    event_service.log.assert_called_once_with(
        type=EventType.RENTAL_CREATED,
        message="Réservation créée",
        user_id="user-123",
        vehicle_id="vehicle-123",
        application_id="application-123",
        event_metadata={
            "reservation_id": "reservation-123",
            "start_date": created_reservation.start_date.isoformat(),
            "end_date": created_reservation.end_date.isoformat(),
            "status": ReservationStatus.ACTIVE.value,
        },
    )

def test_execute_rolls_back_when_reservation_creation_fails(
    use_case,
    application_repository,
    reservation_repository,
    unit_of_work,
    dto,
    application,
):
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = False

    reservation_repository.create.side_effect = RuntimeError(
        "Database error"
    )

    with pytest.raises(RuntimeError, match="Database error"):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()

def test_execute_rolls_back_when_event_logging_fails(
    use_case,
    application_repository,
    reservation_repository,
    event_service,
    unit_of_work,
    dto,
    application,
):
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = False

    created_reservation = Mock()
    created_reservation.id = "reservation-123"
    created_reservation.vehicle_id = "vehicle-123"
    created_reservation.start_date = dto.start_date
    created_reservation.end_date = dto.end_date
    created_reservation.status = ReservationStatus.ACTIVE

    reservation_repository.create.return_value = (
        created_reservation
    )

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(RuntimeError, match="Event error"):
        use_case.execute(dto)

    unit_of_work.rollback.assert_called_once()
    unit_of_work.commit.assert_not_called()

def test_execute_rolls_back_when_commit_fails(
    use_case,
    application_repository,
    reservation_repository,
    unit_of_work,
    dto,
    application,
):
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = False

    created_reservation = Mock()
    created_reservation.id = "reservation-123"
    created_reservation.vehicle_id = "vehicle-123"
    created_reservation.start_date = dto.start_date
    created_reservation.end_date = dto.end_date
    created_reservation.status = ReservationStatus.ACTIVE

    reservation_repository.create.return_value = (
        created_reservation
    )

    unit_of_work.commit.side_effect = RuntimeError(
        "Commit error"
    )

    with pytest.raises(RuntimeError, match="Commit error"):
        use_case.execute(dto)

    unit_of_work.commit.assert_called_once()
    unit_of_work.rollback.assert_called_once()

def test_execute_generates_reservation_id(
    use_case,
    application_repository,
    reservation_repository,
    dto,
    application,
):
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = False

    created_reservation = Mock()
    created_reservation.id = "reservation-123"
    created_reservation.vehicle_id = "vehicle-123"
    created_reservation.start_date = dto.start_date
    created_reservation.end_date = dto.end_date
    created_reservation.status = ReservationStatus.ACTIVE

    reservation_repository.create.return_value = (
        created_reservation
    )

    with patch(
        "modules.reservations.application.use_cases.create_reservation.uuid4",
        return_value="generated-uuid",
    ):
        use_case.execute(dto)

    reservation = reservation_repository.create.call_args.args[0]

    assert reservation.id == "generated-uuid"