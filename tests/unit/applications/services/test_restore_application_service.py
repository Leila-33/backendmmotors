from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from modules.applications.application.services.restore_application_service import (
    RestoreApplicationService,
)
from modules.applications.domain.exceptions import CannotRestoreApplication
from modules.vehicles.domain.enums import VehicleType


@pytest.fixture
def reservation_repository():
    return Mock()


@pytest.fixture
def service(reservation_repository):
    return RestoreApplicationService(
        reservation_repository=reservation_repository,
    )


def make_application(
    vehicle_type=VehicleType.RENT,
    reservation=None,
):
    return SimpleNamespace(
        vehicle=SimpleNamespace(
            type=vehicle_type,
        ),
        reservation=reservation,
    )


def make_reservation(
    vehicle_id="vehicle-123",
    start_date=date(2026, 9, 10),
    end_date=date(2026, 9, 15),
):
    return SimpleNamespace(
        vehicle_id=vehicle_id,
        start_date=start_date,
        end_date=end_date,
    )


def test_validate_rental_does_nothing_for_non_rental_vehicle(
    service,
    reservation_repository,
):
    application = make_application(
        vehicle_type=VehicleType.SALE,
    )

    service.validate_rental(application)

    reservation_repository.exists_overlap.assert_not_called()


def test_validate_rental_raises_when_rental_has_no_reservation(
    service,
    reservation_repository,
):
    application = make_application(
        vehicle_type=VehicleType.RENT,
        reservation=None,
    )

    with pytest.raises(
        CannotRestoreApplication,
        match="Réservation introuvable.",
    ):
        service.validate_rental(application)

    reservation_repository.exists_overlap.assert_not_called()


def test_validate_rental_raises_when_rental_period_has_started(
    service,
    reservation_repository,
):
    reservation = make_reservation(
        start_date=date(2026, 9, 5),
        end_date=date(2026, 9, 15),
    )

    application = make_application(
        vehicle_type=VehicleType.RENT,
        reservation=reservation,
    )

    with patch(
        "modules.applications.application.services.restore_application_service.date"
    ) as mocked_date:
        mocked_date.today.return_value = date(2026, 9, 6)

        with pytest.raises(
            CannotRestoreApplication,
            match="La période de location a commencé.",
        ):
            service.validate_rental(application)

    reservation_repository.exists_overlap.assert_not_called()


def test_validate_rental_raises_when_vehicle_is_no_longer_available(
    service,
    reservation_repository,
):
    reservation = make_reservation(
        vehicle_id="vehicle-123",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
    )

    application = make_application(
        vehicle_type=VehicleType.RENT,
        reservation=reservation,
    )

    reservation_repository.exists_overlap.return_value = True

    with patch(
        "modules.applications.application.services.restore_application_service.date"
    ) as mocked_date:
        mocked_date.today.return_value = date(2026, 9, 1)

        with pytest.raises(
            CannotRestoreApplication,
            match="Le véhicule n'est plus disponible.",
        ):
            service.validate_rental(application)

    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id="vehicle-123",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
    )


def test_validate_rental_succeeds_for_future_available_rental(
    service,
    reservation_repository,
):
    reservation = make_reservation(
        vehicle_id="vehicle-123",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
    )

    application = make_application(
        vehicle_type=VehicleType.RENT,
        reservation=reservation,
    )

    reservation_repository.exists_overlap.return_value = False

    with patch(
        "modules.applications.application.services.restore_application_service.date"
    ) as mocked_date:
        mocked_date.today.return_value = date(2026, 9, 1)

        result = service.validate_rental(application)

    assert result is None

    reservation_repository.exists_overlap.assert_called_once_with(
        vehicle_id="vehicle-123",
        start_date=date(2026, 9, 10),
        end_date=date(2026, 9, 15),
    )