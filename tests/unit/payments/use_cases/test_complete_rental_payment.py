import pytest
from unittest.mock import Mock

from modules.applications.domain.enums import (
    ApplicationStatus,
    EventType,
)
from modules.applications.domain.exceptions import (
    ApplicationNotFound,
)
from modules.vehicles.domain.enums import VehicleStatus

from modules.payments.application.dtos.complete_rental_payment_dto import (
    CompleteRentalPaymentDTO,
)
from modules.payments.application.results.complete_rental_payment_result import (
    CompleteRentalPaymentResult,
)
from modules.payments.application.use_cases.complete_rental_payment import (
    CompleteRentalPaymentUseCase,
)


@pytest.fixture
def vehicle_repository():
    return Mock()


@pytest.fixture
def application_repository():
    return Mock()


@pytest.fixture
def event_service():
    return Mock()


@pytest.fixture
def use_case(
    vehicle_repository,
    application_repository,
    event_service,
):
    return CompleteRentalPaymentUseCase(
        vehicle_repository=vehicle_repository,
        application_repository=application_repository,
        event_service=event_service,
    )


def make_dto(
    application_id="application-123",
    payment_id="payment-123",
):
    return CompleteRentalPaymentDTO(
        application_id=application_id,
        payment_id=payment_id,
    )


def make_vehicle(
    vehicle_id="vehicle-123",
):
    vehicle = Mock()
    vehicle.id = vehicle_id
    vehicle.status = VehicleStatus.AVAILABLE
    return vehicle


def make_application(
    application_id="application-123",
    user_id="user-123",
    vehicle=None,
    status=ApplicationStatus.APPROVED,
):
    application = Mock()

    application.id = application_id
    application.user_id = user_id
    application.status = status
    application.vehicle = vehicle or make_vehicle()

    return application


def test_complete_rental_payment_success(
    use_case,
    vehicle_repository,
    application_repository,
    event_service,
):
    vehicle = make_vehicle()
    application = make_application(
        vehicle=vehicle,
        status=ApplicationStatus.APPROVED,
    )
    dto = make_dto()

    application_repository.get_by_id.return_value = application

    result = use_case.execute(dto)

    # Véhicule
    assert vehicle.status == VehicleStatus.RESERVED
    vehicle_repository.update.assert_called_once_with(vehicle)

    # Application
    assert application.status == ApplicationStatus.COMPLETED
    application_repository.update.assert_called_once_with(application)

    # Événement
    event_service.log.assert_called_once_with(
        type=EventType.RENTAL_PAYMENT_PAID,
        application_id="application-123",
        vehicle_id="vehicle-123",
        user_id="user-123",
        message="Paiement location confirmé",
        event_metadata={
            "payment_id": "payment-123",
            "vehicle_id": "vehicle-123",
        },
    )

    # Résultat
    assert isinstance(result, CompleteRentalPaymentResult)
    assert result.application_id == "application-123"
    assert result.vehicle_id == "vehicle-123"
    assert result.rental_started is True
    assert result.message == "Location activée avec succès"


def test_complete_rental_payment_raises_when_application_not_found(
    use_case,
    application_repository,
    vehicle_repository,
    event_service,
):
    dto = make_dto()

    application_repository.get_by_id.return_value = None

    with pytest.raises(ApplicationNotFound):
        use_case.execute(dto)

    application_repository.get_by_id.assert_called_once_with(
        "application-123"
    )

    vehicle_repository.update.assert_not_called()
    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()


def test_complete_rental_payment_is_idempotent_when_already_completed(
    use_case,
    application_repository,
    vehicle_repository,
    event_service,
):
    vehicle = make_vehicle()
    application = make_application(
        vehicle=vehicle,
        status=ApplicationStatus.COMPLETED,
    )
    dto = make_dto()

    application_repository.get_by_id.return_value = application

    result = use_case.execute(dto)

    assert isinstance(result, CompleteRentalPaymentResult)
    assert result.application_id == "application-123"
    assert result.vehicle_id == "vehicle-123"
    assert result.rental_started is True
    assert result.message == "Location déjà activée"

    # Aucune nouvelle modification
    vehicle_repository.update.assert_not_called()
    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()

    # Le statut reste inchangé
    assert application.status == ApplicationStatus.COMPLETED


def test_complete_rental_payment_propagates_vehicle_update_error(
    use_case,
    application_repository,
    vehicle_repository,
    event_service,
):
    vehicle = make_vehicle()
    application = make_application(
        vehicle=vehicle,
        status=ApplicationStatus.APPROVED,
    )
    dto = make_dto()

    application_repository.get_by_id.return_value = application
    vehicle_repository.update.side_effect = RuntimeError(
        "Vehicle update error"
    )

    with pytest.raises(
        RuntimeError,
        match="Vehicle update error",
    ):
        use_case.execute(dto)

    assert vehicle.status == VehicleStatus.RESERVED

    vehicle_repository.update.assert_called_once_with(vehicle)

    application_repository.update.assert_not_called()
    event_service.log.assert_not_called()


def test_complete_rental_payment_propagates_application_update_error(
    use_case,
    application_repository,
    vehicle_repository,
    event_service,
):
    vehicle = make_vehicle()
    application = make_application(
        vehicle=vehicle,
        status=ApplicationStatus.APPROVED,
    )
    dto = make_dto()

    application_repository.get_by_id.return_value = application

    application_repository.update.side_effect = RuntimeError(
        "Application update error"
    )

    with pytest.raises(
        RuntimeError,
        match="Application update error",
    ):
        use_case.execute(dto)

    # Le véhicule a déjà été modifié et sauvegardé
    assert vehicle.status == VehicleStatus.RESERVED
    vehicle_repository.update.assert_called_once_with(vehicle)

    # L'application a été passée à COMPLETED avant l'erreur
    assert application.status == ApplicationStatus.COMPLETED
    application_repository.update.assert_called_once_with(application)

    # L'événement n'est jamais envoyé
    event_service.log.assert_not_called()


def test_complete_rental_payment_propagates_event_error(
    use_case,
    application_repository,
    vehicle_repository,
    event_service,
):
    vehicle = make_vehicle()
    application = make_application(
        vehicle=vehicle,
        status=ApplicationStatus.APPROVED,
    )
    dto = make_dto()

    application_repository.get_by_id.return_value = application

    event_service.log.side_effect = RuntimeError(
        "Event error"
    )

    with pytest.raises(
        RuntimeError,
        match="Event error",
    ):
        use_case.execute(dto)

    # Les deux mises à jour ont bien eu lieu avant l'erreur
    assert vehicle.status == VehicleStatus.RESERVED
    assert application.status == ApplicationStatus.COMPLETED

    vehicle_repository.update.assert_called_once_with(vehicle)
    application_repository.update.assert_called_once_with(application)

    event_service.log.assert_called_once()