
# tests/modules/reservations/application/use_cases/test_create_reservation_use_case.py

from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from modules.reservations.application.dtos.create_reservation_dto import (
    CreateReservationDTO,
)
from modules.reservations.application.use_cases.create_reservation import (
    CreateReservationUseCase,
)
from modules.reservations.domain.enums import ReservationStatus
from modules.applications.domain.enums import EventType
from modules.applications.domain.exceptions import ApplicationNotFound
from modules.vehicles.domain.exceptions import VehicleNotAvailable


# =========================================================
# FIXTURES
# =========================================================


@pytest.fixture
def application_repository():
    return MagicMock()


@pytest.fixture
def reservation_repository():
    return MagicMock()


@pytest.fixture
def event_service():
    return MagicMock()


@pytest.fixture
def unit_of_work():
    return MagicMock()


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
def application():
    return SimpleNamespace(
        id="application-123",
        vehicle_id="vehicle-456",
        user_id="user-789",
    )


@pytest.fixture
def dto():
    return CreateReservationDTO(
        application_id="application-123",
        start_date=date.today() + timedelta(days=1),
        end_date=date.today() + timedelta(days=5),
    )


# =========================================================
# SUCCESS
# =========================================================


def test_execute_creates_reservation_successfully(
    use_case,
    application_repository,
    reservation_repository,
    event_service,
    unit_of_work,
    application,
    dto,
):
    # Arrange
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = False

    def persist_reservation(reservation):
        return reservation

    reservation_repository.create.side_effect = persist_reservation

    # Act
    result = use_case.execute(dto)

    # Assert: application lookup
    application_repository.get_by_id.assert_called_once_with(
        dto.application_id
    )

    # Assert: vehicle availability
    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id=application.vehicle_id,
        start_date=dto.start_date,
        end_date=dto.end_date,
    )

    # Assert: reservation
    reservation_repository.create.assert_called_once()

    created_reservation = reservation_repository.create.call_args.args[0]

    assert result is created_reservation
    assert result.id
    assert result.application_id == application.id
    assert result.vehicle_id == application.vehicle_id
    assert result.start_date == dto.start_date
    assert result.end_date == dto.end_date
    assert result.status == ReservationStatus.ACTIVE

    # Assert: event
    event_service.log.assert_called_once_with(
        type=EventType.RENTAL_CREATED,
        message="Réservation créée",
        user_id=application.user_id,
        vehicle_id=created_reservation.vehicle_id,
        application_id=application.id,
        event_metadata={
            "reservation_id": created_reservation.id,
            "start_date": dto.start_date.isoformat(),
            "end_date": dto.end_date.isoformat(),
            "status": ReservationStatus.ACTIVE.value,
        },
    )

    # Assert: transaction
    unit_of_work.commit.assert_called_once_with()
    unit_of_work.rollback.assert_not_called()


# =========================================================
# APPLICATION NOT FOUND
# =========================================================


def test_execute_raises_application_not_found(
    use_case,
    application_repository,
    reservation_repository,
    event_service,
    unit_of_work,
    dto,
):
    # Arrange
    application_repository.get_by_id.return_value = None

    # Act / Assert
    with pytest.raises(ApplicationNotFound):
        use_case.execute(dto)

    # Assert
    application_repository.get_by_id.assert_called_once_with(
        dto.application_id
    )

    reservation_repository.exists_overlap.assert_not_called()
    reservation_repository.create.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


# =========================================================
# VEHICLE NOT AVAILABLE
# =========================================================


def test_execute_raises_vehicle_not_available_when_overlap_exists(
    use_case,
    application_repository,
    reservation_repository,
    event_service,
    unit_of_work,
    application,
    dto,
):
    # Arrange
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = True

    # Act / Assert
    with pytest.raises(VehicleNotAvailable):
        use_case.execute(dto)

    # Assert
    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id=application.vehicle_id,
        start_date=dto.start_date,
        end_date=dto.end_date,
    )

    reservation_repository.create.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


# =========================================================
# REPOSITORY CREATION ERROR
# =========================================================


def test_execute_rolls_back_when_reservation_creation_fails(
    use_case,
    application_repository,
    reservation_repository,
    event_service,
    unit_of_work,
    application,
    dto,
):
    # Arrange
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = False

    reservation_repository.create.side_effect = RuntimeError(
        "Erreur de persistance"
    )

    # Act / Assert
    with pytest.raises(RuntimeError, match="Erreur de persistance"):
        use_case.execute(dto)

    # Assert
    reservation_repository.create.assert_called_once()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


# =========================================================
# EVENT ERROR
# =========================================================


def test_execute_rolls_back_when_event_logging_fails(
    use_case,
    application_repository,
    reservation_repository,
    event_service,
    unit_of_work,
    application,
    dto,
):
    # Arrange
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = False

    event_service.log.side_effect = RuntimeError(
        "Erreur de journalisation"
    )

    # Act / Assert
    with pytest.raises(RuntimeError, match="Erreur de journalisation"):
        use_case.execute(dto)

    # Assert
    reservation_repository.create.assert_called_once()
    event_service.log.assert_called_once()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()


# =========================================================
# COMMIT ERROR
# =========================================================


def test_execute_rolls_back_when_commit_fails(
    use_case,
    application_repository,
    reservation_repository,
    event_service,
    unit_of_work,
    application,
    dto,
):
    # Arrange
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = False

    unit_of_work.commit.side_effect = RuntimeError(
        "Erreur de transaction"
    )

    # Act / Assert
    with pytest.raises(RuntimeError, match="Erreur de transaction"):
        use_case.execute(dto)

    # Assert
    reservation_repository.create.assert_called_once()
    event_service.log.assert_called_once()

    unit_of_work.commit.assert_called_once_with()
    unit_of_work.rollback.assert_called_once_with()


# =========================================================
# VALIDATION DOMAIN ERROR
# =========================================================


def test_execute_rolls_back_when_reservation_validation_fails(
    use_case,
    application_repository,
    reservation_repository,
    event_service,
    unit_of_work,
    application,
    dto,
    monkeypatch,
):
    # Arrange
    application_repository.get_by_id.return_value = application
    reservation_repository.exists_overlap.return_value = False

    # Empêche la validation de dépendre des règles internes
    # exactes de l'entité Reservation.
    from modules.reservations.domain.entities.reservation import (
        Reservation,
    )

    def invalid_validation(self):
        raise ValueError("Dates de réservation invalides")

    monkeypatch.setattr(
        Reservation,
        "validate_for_creation",
        invalid_validation,
    )

    # Act / Assert
    with pytest.raises(
        ValueError,
        match="Dates de réservation invalides",
    ):
        use_case.execute(dto)

    # Assert
    reservation_repository.create.assert_not_called()
    event_service.log.assert_not_called()

    unit_of_work.commit.assert_not_called()
    unit_of_work.rollback.assert_called_once_with()
